"""
IRise Chaiiwala â€“ Phase 2â€“7: Sales Analysis
Reads cleaned processed CSVs and produces all analysis outputs.
"""

import pandas as pd
import numpy as np
import os, json, warnings
warnings.filterwarnings('ignore')

PROC = r'C:\Users\GEO\Desktop\IRise\data\processed'
REPORTS = r'C:\Users\GEO\Desktop\IRise\reports'
os.makedirs(REPORTS, exist_ok=True)


def load_data():
    daily       = pd.read_csv(os.path.join(PROC, 'daily_sales.csv'), parse_dates=['date'])
    hourly      = pd.read_csv(os.path.join(PROC, 'hourly_sales.csv'), parse_dates=['date'])
    hourly_avg  = pd.read_csv(os.path.join(PROC, 'hourly_avg_weekday.csv'))
    products    = pd.read_csv(os.path.join(PROC, 'product_sales.csv'), parse_dates=['date'])
    prod_sum    = pd.read_csv(os.path.join(PROC, 'product_summary.csv'))
    order_d     = pd.read_csv(os.path.join(PROC, 'order_type_daily.csv'), parse_dates=['date'])
    order_m     = pd.read_csv(os.path.join(PROC, 'order_type_monthly.csv'))
    txn         = pd.read_csv(os.path.join(PROC, 'transactions.csv'), parse_dates=['created_at'])
    cats        = pd.read_csv(os.path.join(PROC, 'category_summary.csv'))
    return daily, hourly, hourly_avg, products, prod_sum, order_d, order_m, txn, cats


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 2 â€“ SALES PERFORMANCE OVERVIEW
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_sales_overview(daily):
    print("\nâ”€â”€ PHASE 2: Sales Performance Overview â”€â”€")

    total_revenue  = daily['net_amount'].sum()
    total_txn      = daily['transactions'].sum()
    avg_aov        = daily['aov'].mean()
    avg_daily_rev  = daily['net_amount'].mean()
    avg_weekly_rev = daily.groupby('week')['net_amount'].sum().mean()
    date_range     = f"{daily['date'].min().date()} â†’ {daily['date'].max().date()}"

    print(f"  Total Net Revenue  : AED {total_revenue:,.2f}")
    print(f"  Total Transactions : {total_txn:,.0f}")
    print(f"  Overall AOV        : AED {avg_aov:.2f}")
    print(f"  Avg Daily Revenue  : AED {avg_daily_rev:.2f}")
    print(f"  Avg Weekly Revenue : AED {avg_weekly_rev:.2f}")
    print(f"  Date Range         : {date_range}")

    # Year-on-year comparison
    yearly = daily.groupby('year').agg(
        revenue=('net_amount', 'sum'),
        transactions=('transactions', 'sum'),
        trading_days=('date', 'count'),
        avg_aov=('aov', 'mean')
    ).reset_index()

    # Growth %
    if len(yearly) >= 2:
        y1 = yearly.iloc[-2]['revenue']
        y2_full_year = yearly.iloc[-1]['revenue']
        # Partial year adjustment: compare same months
        first_year = yearly.iloc[0]['year']
        last_year  = yearly.iloc[-1]['year']
        last_months = daily[daily['year'] == last_year]['month'].unique()

        same_period_y1 = daily[
            (daily['year'] == first_year) &
            (daily['month'].isin(last_months))
        ]['net_amount'].sum()
        same_period_y2 = daily[
            (daily['year'] == last_year)
        ]['net_amount'].sum()

        growth = ((same_period_y2 - same_period_y1) / same_period_y1) * 100
        print(f"\n  YoY Growth (same months): {growth:+.1f}%")

    print("\n  Yearly Summary:")
    print(yearly.to_string(index=False))

    # Monthly revenue
    monthly = daily.groupby(['year', 'month', 'month_name']).agg(
        revenue=('net_amount', 'sum'),
        transactions=('transactions', 'sum'),
        avg_aov=('aov', 'mean')
    ).reset_index().sort_values(['year', 'month'])

    monthly.to_csv(os.path.join(REPORTS, 'monthly_revenue.csv'), index=False)
    yearly.to_csv(os.path.join(REPORTS, 'yearly_summary.csv'), index=False)
    print("  [âœ“] Saved monthly_revenue.csv, yearly_summary.csv")

    return {'total_revenue': total_revenue, 'total_txn': total_txn,
            'avg_aov': avg_aov, 'avg_daily': avg_daily_rev,
            'avg_weekly': avg_weekly_rev, 'yearly': yearly, 'monthly': monthly}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 3 â€“ TIME-BASED ANALYSIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_time(daily, hourly, hourly_avg):
    print("\nâ”€â”€ PHASE 3: Time-Based Analysis â”€â”€")

    # Day of week order for UAE (Monâ€“Sun start, Fri/Sat weekend)
    DOW_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']

    # Revenue & AOV by day of week
    by_dow = daily.groupby('day_of_week').agg(
        revenue=('net_amount', 'sum'),
        avg_revenue=('net_amount', 'mean'),
        transactions=('transactions', 'sum'),
        avg_aov=('aov', 'mean')
    ).reindex(DOW_ORDER).reset_index()
    by_dow.rename(columns={'day_of_week': 'day'}, inplace=True)

    best_day  = by_dow.loc[by_dow['avg_revenue'].idxmax(), 'day']
    worst_day = by_dow.loc[by_dow['avg_revenue'].idxmin(), 'day']
    print(f"  Best day : {best_day}  |  Worst day: {worst_day}")
    print(by_dow[['day','avg_revenue','avg_aov']].to_string(index=False))

    # Weekend vs weekday (UAE: Fri/Sat are weekend)
    we = daily.groupby('is_weekend')['net_amount'].mean()
    print(f"\n  Avg Weekday Rev : AED {we.get(False, 0):,.2f}")
    print(f"  Avg Weekend Rev : AED {we.get(True, 0):,.2f}")

    # Revenue by hour (from hourly_avg â€“ already averaged per weekday)
    if not hourly.empty:
        hourly_rev = hourly.groupby('hour').agg(
            avg_net=('net_amount', 'mean'),
            total_net=('net_amount', 'sum'),
            avg_txn=('transactions', 'mean')
        ).reset_index()
        peak_hour = hourly_rev.loc[hourly_rev['avg_net'].idxmax(), 'hour']
        slow_hour = hourly_rev.loc[hourly_rev['avg_net'].idxmin(), 'hour']
        print(f"\n  Peak hour: {peak_hour}:00  |  Slowest hour: {slow_hour}:00")
        hourly_rev.to_csv(os.path.join(REPORTS, 'hourly_revenue.csv'), index=False)

    by_dow.to_csv(os.path.join(REPORTS, 'day_of_week_revenue.csv'), index=False)
    print("  [âœ“] Saved day_of_week_revenue.csv, hourly_revenue.csv")

    return {'by_dow': by_dow, 'best_day': best_day, 'worst_day': worst_day}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 4 â€“ PRODUCT PERFORMANCE
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_products(prod_sum, products):
    print("\nâ”€â”€ PHASE 4: Product Performance â”€â”€")

    # Aggregate by product name (full period)
    by_product = prod_sum.groupby('product_name').agg(
        total_qty=('total_qty', 'sum'),
        total_net=('total_net', 'sum'),
    ).reset_index().sort_values('total_net', ascending=False)

    total_revenue = by_product['total_net'].sum()
    by_product['revenue_pct'] = (by_product['total_net'] / total_revenue * 100).round(2)
    by_product['cumulative_pct'] = by_product['revenue_pct'].cumsum()

    # Top 10 & Bottom 10
    top10    = by_product.head(10).copy()
    bottom10 = by_product[by_product['total_net'] > 0].tail(10).copy()

    # Pareto â€“ items generating 80% of revenue
    pareto = by_product[by_product['cumulative_pct'] <= 80]
    print(f"  Items generating 80% of revenue: {len(pareto)} out of {len(by_product)}")

    print("\n  Top 10 Products by Revenue:")
    print(top10[['product_name','total_qty','total_net','revenue_pct']].to_string(index=False))

    print("\n  Bottom 10 Products by Revenue:")
    print(bottom10[['product_name','total_qty','total_net','revenue_pct']].to_string(index=False))

    # YoY product growth (from granular product_sales)
    if not products.empty and 'year' in products.columns:
        yoy = products.groupby(['year', 'product_name'])['net_amount'].sum().unstack(0)
        if yoy.shape[1] >= 2:
            years = sorted(yoy.columns)
            yoy['growth_pct'] = ((yoy[years[-1]] - yoy[years[-2]]) / yoy[years[-2]] * 100).round(1)
            declining = yoy[yoy['growth_pct'] < -10].sort_values('growth_pct').head(10)
            growing   = yoy[yoy['growth_pct'] > 10].sort_values('growth_pct', ascending=False).head(10)
            print(f"\n  Significantly Declining Products (>10% drop):")
            print(declining['growth_pct'].to_string())
            print(f"\n  Significantly Growing Products (>10% rise):")
            print(growing['growth_pct'].to_string())
            yoy.to_csv(os.path.join(REPORTS, 'product_yoy_growth.csv'))

    by_product.to_csv(os.path.join(REPORTS, 'product_ranking.csv'), index=False)
    top10.to_csv(os.path.join(REPORTS, 'top10_products.csv'), index=False)
    bottom10.to_csv(os.path.join(REPORTS, 'bottom10_products.csv'), index=False)
    print("  [âœ“] Saved product_ranking.csv, top10, bottom10, yoy_growth")

    return {'top10': top10, 'bottom10': bottom10, 'pareto_count': len(pareto)}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 5 â€“ AOV ANALYSIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_aov(daily, hourly, txn, order_d):
    print("\nâ”€â”€ PHASE 5: AOV Analysis â”€â”€")

    overall_aov = daily['aov'].mean()
    print(f"  Overall AOV: AED {overall_aov:.2f}")

    # AOV by day of week
    aov_dow = daily.groupby('day_of_week')['aov'].mean().reset_index()
    aov_dow.columns = ['day', 'avg_aov']
    print("\n  AOV by Day of Week:")
    print(aov_dow.to_string(index=False))

    # AOV by hour
    if not hourly.empty and 'aov' in hourly.columns:
        aov_hour = hourly.groupby('hour')['aov'].mean().reset_index()
        aov_hour.columns = ['hour', 'avg_aov']
        low_aov_hours = aov_hour[aov_hour['avg_aov'] < overall_aov * 0.85]
        print(f"\n  Hours with AOV >15% below avg (upsell opportunities): "
              f"{low_aov_hours['hour'].tolist()}")

    # AOV by order type (from daily order type)
    if not order_d.empty:
        order_d['aov'] = order_d['net_amount'] / order_d['transactions'].replace(0, np.nan)
        aov_otype = order_d.groupby('order_type')['aov'].mean().reset_index()
        print("\n  AOV by Order Type:")
        print(aov_otype.to_string(index=False))
        aov_otype.to_csv(os.path.join(REPORTS, 'aov_by_order_type.csv'), index=False)

    aov_dow.to_csv(os.path.join(REPORTS, 'aov_by_day.csv'), index=False)
    print("  [âœ“] Saved aov_by_day.csv, aov_by_order_type.csv")

    return {'overall_aov': overall_aov}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 6 â€“ ORDER TYPE & PLATFORM
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_order_types(order_d, order_m, txn):
    print("\nâ”€â”€ PHASE 6: Order Type & Platform Analysis â”€â”€")

    # Revenue split by order type
    split = order_d.groupby('order_type').agg(
        revenue=('net_amount', 'sum'),
        transactions=('transactions', 'sum')
    ).reset_index()
    total = split['revenue'].sum()
    split['revenue_pct'] = (split['revenue'] / total * 100).round(1)
    print("\n  Revenue Split by Order Type:")
    print(split.to_string(index=False))

    # Monthly trend by order type
    monthly_trend = order_d.groupby(['year', 'month', 'order_type'])['net_amount'].sum().reset_index()
    monthly_trend.to_csv(os.path.join(REPORTS, 'order_type_monthly_trend.csv'), index=False)

    # Delivery platform breakdown from transactions
    if not txn.empty and 'payment_type' in txn.columns:
        platform = txn[txn['order_type'] == 'Delivery'].groupby('payment_type').agg(
            orders=('net_amount', 'count'),
            revenue=('net_amount', 'sum')
        ).reset_index().sort_values('revenue', ascending=False)
        print("\n  Delivery Platform Breakdown:")
        print(platform.to_string(index=False))
        platform.to_csv(os.path.join(REPORTS, 'delivery_platforms.csv'), index=False)

    split.to_csv(os.path.join(REPORTS, 'order_type_split.csv'), index=False)
    print("  [âœ“] Saved order_type_split.csv, delivery_platforms.csv")

    return {'split': split}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 7 â€“ SEASONAL ANALYSIS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_seasonality(daily):
    print("\nâ”€â”€ PHASE 7: Seasonal & Trend Analysis â”€â”€")

    # Monthly revenue heatmap data
    heatmap = daily.groupby(['year', 'month'])['net_amount'].sum().reset_index()
    heatmap.to_csv(os.path.join(REPORTS, 'monthly_heatmap.csv'), index=False)

    # Ramadan periods (approximate)
    # Ramadan 2024: ~11 Mar â€“ 9 Apr  |  Ramadan 2025: ~1 Mar â€“ 29 Mar
    ramadan_periods = [
        ('2024-03-11', '2024-04-09', 'Ramadan 2024'),
        ('2025-03-01', '2025-03-29', 'Ramadan 2025'),
    ]

    print("\n  Ramadan Revenue Analysis:")
    for start, end, label in ramadan_periods:
        mask = (daily['date'] >= start) & (daily['date'] <= end)
        if mask.any():
            r_rev = daily[mask]['net_amount'].sum()
            r_aov = daily[mask]['aov'].mean()
            print(f"  {label}: AED {r_rev:,.2f}  |  AOV: AED {r_aov:.2f}")

    # Month-on-month fluctuations
    monthly_avg = daily.groupby('month')['net_amount'].mean()
    annual_avg  = daily['net_amount'].mean()
    risky_months = monthly_avg[monthly_avg < annual_avg * 0.80].index.tolist()
    peak_months  = monthly_avg[monthly_avg > annual_avg * 1.15].index.tolist()
    print(f"\n  Risk months (>20% below avg): {risky_months}")
    print(f"  Peak months (>15% above avg): {peak_months}")

    # Dual-year overlay
    overlays = daily[daily['year'].isin(daily['year'].unique()[-2:])].copy()
    overlay_data = overlays.groupby(['year', 'month'])['net_amount'].sum().reset_index()
    overlay_data.to_csv(os.path.join(REPORTS, 'year_overlay.csv'), index=False)

    print("  [âœ“] Saved monthly_heatmap.csv, year_overlay.csv")

    return {'risky_months': risky_months, 'peak_months': peak_months}


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  PHASE 8 â€“ STRATEGIC SIMULATIONS
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
def analyse_strategic(daily, overview):
    print("\nâ”€â”€ PHASE 8: Strategic Simulations â”€â”€")

    avg_daily = overview['avg_daily']
    aov       = overview['avg_aov']
    total_rev = overview['total_revenue']

    # AOV uplift simulations
    print("\n  AOV Uplift Simulation (per year, ~365 days):")
    for uplift in [0.05, 0.10]:
        new_aov     = aov * (1 + uplift)
        extra_daily = (new_aov - aov) * (overview['total_txn'] / len(daily))
        extra_yr    = extra_daily * 365
        print(f"    +{uplift*100:.0f}% AOV â†’ extra AED {extra_yr:,.0f}/year")

    # Weakest day simulation
    DOW_ORDER = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    by_dow = daily.groupby('day_of_week')['net_amount'].mean().reindex(DOW_ORDER)
    worst_day_rev = by_dow.min()
    avg_rev       = by_dow.mean()
    worst_day     = by_dow.idxmin()
    uplift_per_wk = avg_rev - worst_day_rev
    annual_uplift = uplift_per_wk * 52
    print(f"\n  Improving {worst_day} to weekly average:")
    print(f"    Extra revenue/year: AED {annual_uplift:,.0f}")

    # Summary of strategies
    strategies = [
        "1. Upsell combos during low-AOV hours (identified in Phase 5)",
        "2. Push highest-AOV order type via promotions",
        f"3. Activate {worst_day} with targeted offer/discount event",
        "4. Remove/rebundle lowest-revenue menu items",
        "5. Pre-Ramadan campaign to capture early spend",
        "6. Introduce loyalty incentives to increase visit frequency",
        "7. Shift delivery customers to direct ordering (reduce commission)",
        "8. Bundle bottom-10 items into promotional meal deals",
        "9. Apply dynamic pricing during peak hours",
        "10. Launch weekday lunch promotion to offset morning slow period",
    ]
    print("\n  Strategic Recommendations:")
    for s in strategies:
        print(f"    {s}")

    with open(os.path.join(REPORTS, 'strategic_recommendations.txt'), 'w') as f:
        f.write("IRise Chaiiwala â€“ Strategic Recommendations\n")
        f.write("=" * 50 + "\n\n")
        for s in strategies:
            f.write(s + "\n")

    print("  [âœ“] Saved strategic_recommendations.txt")


# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#  MAIN
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
if __name__ == '__main__':
    print("=" * 55)
    print("  IRise Chaiiwala â€” Sales Analysis (Phases 2â€“8)")
    print("=" * 55)

    daily, hourly, hourly_avg, products, prod_sum, \
        order_d, order_m, txn, cats = load_data()

    overview = analyse_sales_overview(daily)
    analyse_time(daily, hourly, hourly_avg)
    analyse_products(prod_sum, products)
    analyse_aov(daily, hourly, txn, order_d)
    analyse_order_types(order_d, order_m, txn)
    analyse_seasonality(daily)
    analyse_strategic(daily, overview)

    print("\n" + "=" * 55)
    print("  âœ…  All analysis complete â€” reports saved to reports/")
    print("=" * 55)
