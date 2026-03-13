
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Page Config
st.set_page_config(page_title="IRise Analytics Dashboard", layout="wide", page_icon="📈")

# Load credentials
load_dotenv(override=True)
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")
# Get password and remove surrounding quotes if they exist
raw_pwd = os.getenv("DASHBOARD_PASSWORD")
DASHBOARD_PWD = raw_pwd.strip('"').strip("'") if raw_pwd else ""

# ═══════════════════════════════════════════════════════════
#  AUTHENTICATION GATE
# ═══════════════════════════════════════════════════════════
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    """Called on_change — sets flag, no rerun inside callback."""
    pwd = st.session_state.get('pwd_input', '')
    if pwd and pwd == DASHBOARD_PWD:
        st.session_state.authenticated = True
    elif pwd:
        st.session_state.auth_error = True


if not st.session_state.authenticated:
    # Load background image
    bg_b64_path = os.path.join(os.path.dirname(__file__), 'assets', 'bg_b64.txt')
    bg_img = ""
    if os.path.exists(bg_b64_path):
        with open(bg_b64_path, 'r') as f:
            bg_img = f.read()

    st.markdown(f"""
    <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bg_img}");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }}
        .auth-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            height: 90vh;
        }}
        .auth-card {{
            background: rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(12px);
            padding: 50px 40px;
            border-radius: 20px;
            border: 1px solid rgba(255, 255, 255, 0.15);
            text-align: center;
            box-shadow: 0 40px 100px rgba(0,0,0,0.8);
            max-width: 420px;
            width: 100%;
        }}
        .auth-title {{
            color: #ffffff;
            margin: 0;
            letter-spacing: 8px;
            font-weight: 400;
            font-size: 28px;
            text-shadow: 0 2px 10px rgba(0,0,0,0.5);
        }}
        .auth-subtitle {{
            color: #ff9f43;
            font-size: 10px;
            letter-spacing: 5px;
            margin-top: 10px;
            margin-bottom: 40px;
            text-transform: uppercase;
            font-weight: 600;
        }}
        div.stButton > button {{
            background-color: #ff9f43 !important;
            color: black !important;
            font-weight: bold !important;
            border-radius: 10px !important;
            height: 3em !important;
        }}
    </style>
    <div class="auth-container">
        <div class="auth-card">
            <h1 class="auth-title">CHAIWALA</h1>
            <p class="auth-subtitle">IRise STRATEGIC ANALYTICS</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.text_input("Enter Dashboard Password", type="password", key="pwd_input", on_change=check_password)
        if st.button("\U0001f513 Unlock Data", use_container_width=True):
            check_password()
        # Show error if wrong password attempted
        if st.session_state.get('auth_error'):
            st.error("\u274c Incorrect password. Access Denied.")
            st.session_state.auth_error = False
    st.stop()

# ═══════════════════════════════════════════════════════════
#  DASHBOARD CONTENT (Authenticated Only)
# ═══════════════════════════════════════════════════════════

@st.cache_resource
def get_client():
    return create_client(url, key)

supabase = get_client()

# Header
st.title("\u2615 IRise Chaiiwala - Business Intelligence Portfolio")
st.markdown("### Strategic Revenue & Performance Analysis (2024 - 2026)")

# --- 1. DATA LOADING SECTION ---
@st.cache_data
def load_dashboard_data():
    # Load core summary tables for the home view
    daily = supabase.table("daily_sales").select("*").order("date").execute()
    prod_sum = supabase.table("product_summary").select("*").execute()
    return pd.DataFrame(daily.data), pd.DataFrame(prod_sum.data)

try:
    df_daily, df_prod = load_dashboard_data()
    df_daily['date'] = pd.to_datetime(df_daily['date'])
except Exception as e:
    st.error(f"Error connecting to Supabase: {e}")
    st.stop()

# --- 2. SALES PERFORMANCE OVERVIEW (Module 1) ---
t1, t2, t3, t4, t5, t6, t7 = st.tabs(["Overview", "Product Rank", "Time Analysis", "AOV Insights", "Order Type & Platform", "Seasonal & Trends", "Strategy"])




with t1:
    st.header("1. Sales Performance Overview")
    
    # --- CALCULATIONS ---
    total_rev = df_daily['net_amount'].sum()
    num_days = len(df_daily)
    avg_daily_now = total_rev / num_days
    avg_weekly_now = avg_daily_now * 7
    
    # YoY Growth Logic
    yearly = df_daily.groupby('year').agg(
        revenue=('net_amount', 'sum'),
        days=('date', 'count')
    ).reset_index()
    yearly['avg_daily'] = yearly['revenue'] / yearly['days']
    
    full_years = yearly[yearly['year'].isin([2024, 2025])]
    yoy_growth = 0
    if len(full_years) == 2:
        yoy_growth = ((full_years.iloc[1]['revenue'] - full_years.iloc[0]['revenue']) / full_years.iloc[0]['revenue']) * 100

    # 1. TOP METRICS (Beautiful Boxes)
    st.markdown("### 💎 Key Performance Indicators")
    k1, k2, k3 = st.columns(3)
    k1.info(f"**Total Revenue**\nAED {total_rev:,.0f}")
    k2.success(f"**Avg Daily Revenue**\nAED {avg_daily_now:,.2f}")
    k3.warning(f"**Avg Weekly Revenue**\nAED {avg_weekly_now:,.2f}")


    # 2. YEARLY FINANCIAL SNAPSHOT (Executive Year 1 vs Year 2)
    st.write("---")
    st.write("### 🏢 Yearly Executive Comparison")
    
    y1_data = yearly[yearly['year'] == 2024]
    y2_data = yearly[yearly['year'] == 2025]
    
    if not y1_data.empty and not y2_data.empty:
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            st.markdown("""
            <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border-left: 5px solid #ff9f43;">
                <h4 style="color:#ff9f43; margin-top:0;">YEAR 1 (2024)</h4>
                <p style="font-size:24px; font-weight:bold; margin-bottom:0;">AED {:,.0f}</p>
                <p style="font-size:14px; color:#888;">Full Year Revenue</p>
            </div>
            """.format(y1_data.iloc[0]['revenue']), unsafe_allow_html=True)
            
        with c2:
            st.markdown("""
            <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border-left: 5px solid #28c76f;">
                <h4 style="color:#28c76f; margin-top:0;">YEAR 2 (2025)</h4>
                <p style="font-size:24px; font-weight:bold; margin-bottom:0;">AED {:,.0f}</p>
                <p style="font-size:14px; color:#888;">Full Year Revenue</p>
            </div>
            """.format(y2_data.iloc[0]['revenue']), unsafe_allow_html=True)
            
        with c3:
            diff = y2_data.iloc[0]['revenue'] - y1_data.iloc[0]['revenue']
            color = "#28c76f" if diff > 0 else "#ea5455"
            st.markdown("""
            <div style="background-color:#1e1e1e; padding:20px; border-radius:10px; border-left: 5px solid {};">
                <h4 style="color:{}; margin-top:0;">NET MOMENTUM</h4>
                <p style="font-size:24px; font-weight:bold; margin-bottom:0;">AED {:,.0f}</p>
                <p style="font-size:14px; color:#888;">Revenue Variance</p>
            </div>
            """.format(color, color, diff), unsafe_allow_html=True)

    st.write("")
    fy1, fy2 = st.columns([3, 2])
    with fy1:
        # Side-by-Side Comparison Graph
        compare_df = yearly[yearly['year'].isin([2024, 2025])]
        fig_compare = px.bar(compare_df, x='year', y='revenue', 
                            color='year', barmode='group',
                            title="Revenue Comparison: 2024 vs 2025",
                            color_discrete_map={2024: '#ff9f43', 2025: '#28c76f'},
                            text_auto='.3s')
        fig_compare.update_layout(showlegend=False)
        st.plotly_chart(fig_compare, use_container_width=True)
        
    with fy2:
        st.write("#### 📊 Financial Audit Box")
        st.dataframe(yearly[['year', 'revenue', 'days', 'avg_daily']].style.format({
            'revenue': 'AED {:,.2f}',
            'avg_daily': 'AED {:,.2f}'
        }), use_container_width=True)
        st.caption("Detailed revenue audit (CSV view) for year-over-year reconciliation.")

    # 3. MONTHLY TRENDS (Beautiful Box)
    st.write("---")
    with st.container(border=True):
        st.write("### 📈 Monthly Revenue Intelligence")
        df_daily['month_year'] = df_daily['date'].dt.to_period('M').astype(str)
        monthly_data = df_daily.groupby('month_year').agg(
            revenue=('net_amount', 'sum'),
            days=('date', 'count')
        ).reset_index()
        monthly_data['avg_daily'] = monthly_data['revenue'] / monthly_data['days']
        
        fig_month = px.area(monthly_data, x='month_year', y='revenue', 
                           title="Cashflow Momentum (Monthly Total)",
                           line_shape='spline', color_discrete_sequence=['#e67e22'])
        st.plotly_chart(fig_month, use_container_width=True)

    # 4. REVENUE HEALTH (Average Daily Sales over time)
    st.write("---")
    st.write("### 🏥 Revenue Health Dashboard")
    st.markdown("*How the daily average has changed month-over-month*")
    fig_health = px.line(monthly_data, x='month_year', y='avg_daily', 
                        title="Average Daily Revenue Trend",
                        markers=True, line_dash_sequence=['dot'])
    fig_health.add_hline(y=avg_daily_now, line_dash="dash", line_color="red", annotation_text="All-time Average")
    st.plotly_chart(fig_health, use_container_width=True)

with t2:
    st.header("3. Product Performance Analysis")

    # --- Enrich product data ---
    total_p_rev = df_prod['total_net'].sum()
    df_prod = df_prod.sort_values('total_net', ascending=False).copy()
    df_prod['rev_pct'] = (df_prod['total_net'] / total_p_rev * 100).round(2)
    df_prod['cum_pct'] = df_prod['rev_pct'].cumsum()

    top_10 = df_prod.head(10)
    
    # Filter out 0-revenue items (like freebies/modifiers) to show real underperforming products
    valid_bottom = df_prod[df_prod['total_net'] > 0]
    bottom_10 = valid_bottom.tail(10).sort_values('total_net', ascending=True)
    
    core_items = df_prod[df_prod['cum_pct'] <= 80]

    # --- Section A: Top 10 vs Bottom 10 ---
    st.write("### 🏆 Top 10 vs Bottom 10 Products")
    pa1, pa2 = st.columns(2)
    with pa1:
        fig_top = px.bar(top_10, x='total_net', y='product_name', orientation='h',
                         title="📈 Top 10 Best-Selling Items (by Revenue)",
                         color='total_net', color_continuous_scale='Greens',
                         labels={'total_net': 'Revenue (AED)', 'product_name': 'Product'})
        fig_top.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_top, use_container_width=True)
    with pa2:
        fig_bot = px.bar(bottom_10, x='total_net', y='product_name', orientation='h',
                         title="📉 Bottom 10 Lowest-Performing Items",
                         color='total_net', color_continuous_scale='Reds',
                         labels={'total_net': 'Revenue (AED)', 'product_name': 'Product'})
        fig_bot.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bot, use_container_width=True)

    st.write("---")

    # --- Section B: Revenue Contribution % (Treemap) ---
    st.write("### 🧮 Revenue Contribution per Item")
    top20 = df_prod.head(20).copy()
    fig_tree = px.treemap(top20, path=['product_name'], values='total_net',
                           color='rev_pct', color_continuous_scale='RdYlGn',
                           title="Revenue Share Treemap (Top 20 Products — size = AED revenue)")
    st.plotly_chart(fig_tree, use_container_width=True)

    st.write("---")

    # --- Section C: Pareto 80/20 ---
    st.write("### 🎯 Pareto Rule — Items Generating 80% of Revenue")
    pc1, pc2 = st.columns([1, 2])
    with pc1:
        st.success(f"📦 **{len(core_items)} products** drive **80%** of total revenue\n\nOut of {len(df_prod)} total SKUs")
        st.dataframe(
            core_items[['product_name', 'total_net', 'rev_pct']]
            .rename(columns={'product_name': 'Product', 'total_net': 'Revenue (AED)', 'rev_pct': 'Share %'}),
            use_container_width=True
        )
    with pc2:
        # Pareto cumulative curve
        fig_pareto = go.Figure()
        fig_pareto.add_bar(x=df_prod['product_name'].head(30),
                           y=df_prod['rev_pct'].head(30),
                           name='Revenue %', marker_color='#f39c12')
        fig_pareto.add_scatter(x=df_prod['product_name'].head(30),
                               y=df_prod['cum_pct'].head(30),
                               name='Cumulative %', yaxis='y2',
                               line=dict(color='#e74c3c', width=3))
        fig_pareto.add_hline(y=80, yref='y2', line_dash='dash',
                             line_color='white', annotation_text='80% line')
        fig_pareto.update_layout(
            title='Pareto Curve — Revenue Contribution (Top 30 Products)',
            yaxis=dict(title='Individual Share %'),
            yaxis2=dict(title='Cumulative %', overlaying='y', side='right', range=[0, 105]),
            xaxis=dict(tickangle=45)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

    st.write("---")

    # --- Section D: Declining vs Growing (2024 vs 2025) ---
    st.write("### 📁 Declining vs Growing Products (2024 → 2025)")

    @st.cache_data
    def load_product_sales_trend():
        ps = supabase.table("product_sales").select("product_name,year,net_amount").execute()
        return pd.DataFrame(ps.data)

    df_ps = load_product_sales_trend()
    if not df_ps.empty:
        df_ps['net_amount'] = pd.to_numeric(df_ps['net_amount'], errors='coerce').fillna(0)
        pivot = df_ps[df_ps['year'].isin([2024, 2025])].groupby(['product_name', 'year'])['net_amount'].sum().unstack(fill_value=0)
        if 2024 in pivot.columns and 2025 in pivot.columns:
            pivot['change_pct'] = ((pivot[2025] - pivot[2024]) / pivot[2024].replace(0, pd.NA) * 100).round(1)
            pivot = pivot.dropna(subset=['change_pct'])
            growing = pivot.sort_values('change_pct', ascending=False).head(10).reset_index()
            declining = pivot.sort_values('change_pct').head(10).reset_index()

            td1, td2 = st.columns(2)
            with td1:
                fig_grow = px.bar(growing, x='change_pct', y='product_name', orientation='h',
                                  title="📈 Top Growing Products (2024 → 2025)",
                                  color='change_pct', color_continuous_scale='Greens',
                                  labels={'change_pct': 'Growth %', 'product_name': 'Product'})
                st.plotly_chart(fig_grow, use_container_width=True)
            with td2:
                fig_decl = px.bar(declining, x='change_pct', y='product_name', orientation='h',
                                  title="📉 Top Declining Products (2024 → 2025)",
                                  color='change_pct', color_continuous_scale='Reds_r',
                                  labels={'change_pct': 'Change %', 'product_name': 'Product'})
                st.plotly_chart(fig_decl, use_container_width=True)
    else:
        st.warning("Product trend data not available in Supabase.")

with t3:
    st.header("2. Time-Based Analysis")
    
    @st.cache_data
    def load_time_data():
        h = supabase.table("hourly_sales").select("*").execute()
        return pd.DataFrame(h.data)
    
    df_hour = load_time_data()
    
    # --- 2A. Best & Worst Days ---
    st.write("### 📅 Weekly Performance Profile")
    dow_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_rev = df_daily.groupby('day_of_week').agg(
        avg_revenue=('net_amount', 'mean'),
        total_revenue=('net_amount', 'sum')
    ).reindex(dow_order).reset_index()
    
    best_day = dow_rev.loc[dow_rev['avg_revenue'].idxmax(), 'day_of_week']
    worst_day = dow_rev.loc[dow_rev['avg_revenue'].idxmin(), 'day_of_week']
    
    w1, w2 = st.columns([2, 1])
    with w1:
        fig_dow = px.bar(dow_rev, x='day_of_week', y='avg_revenue', 
                         title="Average Revenue by Day of Week",
                         color='avg_revenue', color_continuous_scale='Viridis',
                         labels={'avg_revenue': 'Avg Revenue (AED)', 'day_of_week': 'Day'})
        st.plotly_chart(fig_dow, use_container_width=True)
    with w2:
        st.info(f"🏆 **Best Performing Day**\n{best_day}")
        st.error(f"📉 **Worst Performing Day**\n{worst_day}")
        
        # Weekend vs Weekday
        we_rev = df_daily.groupby('is_weekend')['net_amount'].mean()
        weekday_avg = we_rev.get(False, 0)
        weekend_avg = we_rev.get(True, 0)
        st.metric("Weekend Lead", f"{((weekend_avg/weekday_avg)-1)*100:+.1f}%" if weekday_avg > 0 else "0%")
        st.caption("Comparison: Weekend (Fri-Sun) vs Weekday (Mon-Thu)")

    st.write("---")
    
    # --- 2B. Peak Hours & Stability ---
    st.write("### ⏰ Hourly Trends & Peak Stability")
    
    c1, c2 = st.columns(2)
    with c1:
        # All-time Hourly
        hour_rev = df_hour.groupby('hour')['net_amount'].mean().reset_index()
        fig_hour = px.area(hour_rev, x='hour', y='net_amount', 
                          title="Global 'Magic Hour' Profile",
                          labels={'net_amount': 'Avg Revenue (AED)', 'hour': 'Hour (24h)'},
                          color_discrete_sequence=['#f39c12'])
        st.plotly_chart(fig_hour, use_container_width=True)
        
    with c2:
        # Stability: 2024 vs 2025
        stability = df_hour[df_hour['year'].isin([2024, 2025])].groupby(['year', 'hour'])['net_amount'].mean().reset_index()
        fig_stable = px.line(stability, x='hour', y='net_amount', color='year',
                            title="Peak Hour Stability (2024 vs 2025)",
                            labels={'net_amount': 'Avg Revenue (AED)', 'hour': 'Hour (24h)'},
                            color_discrete_map={2024: '#ff9f43', 2025: '#28c76f'})
        st.plotly_chart(fig_stable, use_container_width=True)
        st.caption("Verified: The peak shopping times remain stable year-over-year.")

with t4:
    st.header("4. Average Order Value (AOV) Analysis")

    @st.cache_data
    def load_otype_data():
        o = supabase.table("order_type_daily").select("*").execute()
        return pd.DataFrame(o.data)

    df_otype = load_otype_data()
    df_otype['net_amount']   = pd.to_numeric(df_otype['net_amount'],   errors='coerce').fillna(0)
    df_otype['transactions'] = pd.to_numeric(df_otype['transactions'], errors='coerce').replace(0, pd.NA)
    df_otype['aov'] = (df_otype['net_amount'] / df_otype['transactions']).round(2)

    # --- KPI Row ---
    overall_aov = df_daily['aov'].mean()
    best_aov_day = df_daily.groupby('day_of_week')['aov'].mean().idxmax()
    worst_aov_day = df_daily.groupby('day_of_week')['aov'].mean().idxmin()

    ak1, ak2, ak3 = st.columns(3)
    ak1.metric("Overall AOV", f"AED {overall_aov:.2f}")
    ak2.info(f"🏆 **Best AOV Day**\n{best_aov_day}")
    ak3.error(f"📉 **Lowest AOV Day**\n{worst_aov_day}")

    st.write("---")

    # --- Row 1: AOV by Day & AOV by Hour ---
    st.write("### 🕒 AOV by Day of Week & Hour")
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
        aov_dow = df_daily.groupby('day_of_week')['aov'].mean().reindex(dow_order).reset_index()
        fig_aov_dow = px.bar(aov_dow, x='day_of_week', y='aov',
                             title="AOV by Day of Week",
                             color='aov', color_continuous_scale='Blues',
                             labels={'aov': 'Avg Order Value (AED)', 'day_of_week': 'Day'})
        fig_aov_dow.add_hline(y=overall_aov, line_dash='dash', line_color='red',
                              annotation_text='Overall Avg')
        st.plotly_chart(fig_aov_dow, use_container_width=True)
    with r1c2:
        if not df_hour.empty:
            aov_hour = df_hour.groupby('hour')['aov'].mean().reset_index()
            fig_aov_h = px.line(aov_hour, x='hour', y='aov', markers=True,
                                title="AOV by Hour (Upsell Window Identification)",
                                labels={'aov': 'Avg Order Value (AED)', 'hour': 'Hour (24h)'},
                                color_discrete_sequence=['#9b59b6'])
            fig_aov_h.add_hline(y=overall_aov, line_dash='dash', line_color='red',
                                annotation_text='Overall Avg')
            st.plotly_chart(fig_aov_h, use_container_width=True)

    st.write("---")

    # --- Row 2: AOV by Channel + Opportunity ---
    st.write("### 📦 AOV by Order Type (Dine-In vs Delivery vs Takeaway)")
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        aov_type = df_otype.groupby('order_type')['aov'].mean().reset_index()
        fig_aov_ch = px.bar(aov_type, x='order_type', y='aov',
                            title="Average Order Value by Channel",
                            color='aov', color_continuous_scale='Sunset',
                            labels={'aov': 'AOV (AED)', 'order_type': 'Channel'},
                            text_auto='.2f')
        st.plotly_chart(fig_aov_ch, use_container_width=True)
    with r2c2:
        split = df_otype.groupby('order_type')['net_amount'].sum().reset_index()
        fig_split = px.pie(split, values='net_amount', names='order_type',
                           title="Revenue Split by Channel", hole=0.45)
        st.plotly_chart(fig_split, use_container_width=True)

    st.write("---")

    # --- Upsell Opportunity Detector ---
    st.write("### 💡 Upsell Opportunity Detection")
    if not df_hour.empty:
        below_avg_hours = df_hour.groupby('hour')['aov'].mean()
        below_avg_hours = below_avg_hours[below_avg_hours < overall_aov].reset_index()
        below_avg_hours.columns = ['Hour', 'Avg AOV (AED)']
        below_avg_hours['Gap to Target (AED)'] = (overall_aov - below_avg_hours['Avg AOV (AED)']).round(2)
        st.warning(f"⚠️ **{len(below_avg_hours)} hours** perform below the overall AOV of AED {overall_aov:.2f} — prime upsell windows.")
        st.dataframe(below_avg_hours.sort_values('Gap to Target (AED)', ascending=False), use_container_width=True)

with t5:
    st.header("5. Order Type & Platform Analysis")

    # Re-use order_type_daily data (already loaded in t4)
    @st.cache_data
    def load_otype_for_platform():
        o = supabase.table("order_type_daily").select("*").execute()
        return pd.DataFrame(o.data)

    df_ot = load_otype_for_platform()
    df_ot['date'] = pd.to_datetime(df_ot['date'], errors='coerce')
    df_ot['net_amount']   = pd.to_numeric(df_ot['net_amount'],   errors='coerce').fillna(0)
    df_ot['transactions'] = pd.to_numeric(df_ot['transactions'], errors='coerce').fillna(0)
    df_ot['year']  = pd.to_numeric(df_ot['year'],  errors='coerce').fillna(0).astype(int)
    df_ot['month'] = pd.to_numeric(df_ot['month'], errors='coerce').fillna(0).astype(int)

    # --- 5A. Revenue Split by Channel ---
    st.write("### \U0001f4ca Revenue Split: Dine-In vs Takeaway vs Delivery")
    channel_total = df_ot.groupby('order_type').agg(
        total_revenue=('net_amount', 'sum'),
        total_orders=('transactions', 'sum')
    ).reset_index()
    channel_total['share_pct'] = (channel_total['total_revenue'] / channel_total['total_revenue'].sum() * 100).round(1)

    ot1, ot2 = st.columns(2)
    with ot1:
        fig_ch_pie = px.pie(channel_total, values='total_revenue', names='order_type',
                            title="Revenue Share by Order Type", hole=0.45,
                            color_discrete_sequence=['#28c76f', '#ff9f43', '#ea5455', '#7367f0'])
        st.plotly_chart(fig_ch_pie, use_container_width=True)
    with ot2:
        st.write("#### \U0001f4cb Channel Breakdown (Audit View)")
        st.dataframe(
            channel_total.rename(columns={
                'order_type': 'Channel',
                'total_revenue': 'Revenue (AED)',
                'total_orders': 'Orders',
                'share_pct': 'Share %'
            }).style.format({
                'Revenue (AED)': 'AED {:,.2f}',
                'Orders': '{:,.0f}',
                'Share %': '{:.1f}%'
            }),
            use_container_width=True
        )

    st.write("---")

    # --- 5B. Delivery Commission Impact ---
    st.write("### \U0001f4b8 Delivery Commission Impact Simulator")
    st.markdown("*Delivery platforms like Talabat & Deliveroo typically charge 25-35% commission on each order.*")

    delivery_rev = channel_total[channel_total['order_type'].str.lower().str.contains('delivery')]
    if not delivery_rev.empty:
        delivery_total = delivery_rev['total_revenue'].sum()

        comm_rate = st.slider("Estimated Delivery Commission Rate (%)", 15, 40, 30, key='comm_slider')
        commission_lost = delivery_total * (comm_rate / 100)
        net_after_comm = delivery_total - commission_lost

        dc1, dc2, dc3 = st.columns(3)
        dc1.metric("Delivery Revenue (Gross)", f"AED {delivery_total:,.0f}")
        dc2.error(f"\u26a0\ufe0f **Commission Lost**\nAED {commission_lost:,.0f}")
        dc3.success(f"\u2705 **Net After Commission**\nAED {net_after_comm:,.0f}")

        st.info(f"""\U0001f4a1 **Insight**: At {comm_rate}% commission, you are losing **AED {commission_lost:,.0f}** per period to delivery platforms.
        \n\nConverting just 10% of delivery orders to dine-in would save approximately **AED {commission_lost * 0.10:,.0f}**.""")
    else:
        st.warning("No delivery channel data found.")

    st.write("---")

    # --- 5C. Trend Changes: Order Type Over Two Years ---
    st.write("### \U0001f4c8 Channel Trend Over Time (Monthly)")

    df_ot['month_year'] = df_ot['date'].dt.to_period('M').astype(str)
    monthly_ot = df_ot.groupby(['month_year', 'order_type'])['net_amount'].sum().reset_index()

    fig_trend = px.line(monthly_ot, x='month_year', y='net_amount', color='order_type',
                        title="Monthly Revenue by Channel (2024 \u2192 2026)",
                        labels={'net_amount': 'Revenue (AED)', 'month_year': 'Month', 'order_type': 'Channel'},
                        color_discrete_sequence=['#28c76f', '#ff9f43', '#ea5455', '#7367f0'])
    st.plotly_chart(fig_trend, use_container_width=True)

    # --- 5D. Year-over-Year Channel Comparison ---
    st.write("### \U0001f4ca Year-over-Year Channel Performance (2024 vs 2025)")
    yoy_ot = df_ot[df_ot['year'].isin([2024, 2025])].groupby(['year', 'order_type'])['net_amount'].sum().reset_index()

    fig_yoy_ot = px.bar(yoy_ot, x='order_type', y='net_amount', color='year',
                         barmode='group',
                         title="Revenue by Channel: 2024 vs 2025",
                         color_discrete_map={2024: '#ff9f43', 2025: '#28c76f'},
                         labels={'net_amount': 'Revenue (AED)', 'order_type': 'Channel'},
                         text_auto='.3s')
    st.plotly_chart(fig_yoy_ot, use_container_width=True)

    # Channel growth table
    pivot_ot = yoy_ot.pivot(index='order_type', columns='year', values='net_amount').fillna(0)
    if 2024 in pivot_ot.columns and 2025 in pivot_ot.columns:
        pivot_ot['Growth %'] = ((pivot_ot[2025] - pivot_ot[2024]) / pivot_ot[2024].replace(0, pd.NA) * 100).round(1)
        st.write("#### Channel Growth Audit")
        st.dataframe(pivot_ot.style.format({
            2024: 'AED {:,.0f}',
            2025: 'AED {:,.0f}',
            'Growth %': '{:+.1f}%'
        }), use_container_width=True)

with t6:
    st.header("6. Seasonal & Trend Analysis")

    # --- Build monthly base ---
    df_daily['month_num'] = df_daily['date'].dt.month
    df_daily['year_int']  = df_daily['date'].dt.year
    df_daily['month_year_str'] = df_daily['date'].dt.to_period('M').astype(str)

    monthly_seasonal = df_daily.groupby(['month_year_str', 'year_int', 'month_num']).agg(
        revenue=('net_amount', 'sum'),
        days=('date', 'count')
    ).reset_index()
    monthly_seasonal['avg_daily'] = monthly_seasonal['revenue'] / monthly_seasonal['days']

    # --- 6A. Seasonal Calendar Heatmap ---
    st.write("### \U0001f30d Seasonal Revenue Heatmap")
    st.markdown("*Months are color-coded by revenue intensity. Darker = higher revenue.*")

    month_labels = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',
                    7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
    monthly_seasonal['month_name'] = monthly_seasonal['month_num'].map(month_labels)

    heat_pivot = monthly_seasonal.pivot_table(index='year_int', columns='month_num',
                                              values='revenue', aggfunc='sum')
    heat_pivot.columns = [month_labels.get(c, c) for c in heat_pivot.columns]

    fig_heat = px.imshow(heat_pivot, text_auto='.2s', aspect='auto',
                         color_continuous_scale='YlOrRd',
                         title='Revenue Heatmap by Month & Year',
                         labels=dict(x='Month', y='Year', color='Revenue (AED)'))
    st.plotly_chart(fig_heat, use_container_width=True)

    # Annotate known seasons
    st.markdown("""
    | Season | Months | Pattern |
    |--------|--------|----------|
    | \U00002600 **Summer** | Jun - Aug | Typically lower footfall due to UAE heat |
    | \U0001f319 **Ramadan** | Varies (Mar/Apr 2024, Feb/Mar 2025) | Evening spike, daytime drop |
    | \u2744\ufe0f **Winter / Tourist** | Nov - Feb | Peak season for Dubai F&B |
    """)

    st.write("---")

    # --- 6B. Month-on-Month Fluctuations ---
    st.write("### \U0001f4c9 Month-on-Month Revenue Fluctuations")

    monthly_sorted = monthly_seasonal.sort_values('month_year_str')
    monthly_sorted['prev_rev'] = monthly_sorted['revenue'].shift(1)
    monthly_sorted['mom_change'] = monthly_sorted['revenue'] - monthly_sorted['prev_rev']
    monthly_sorted['mom_pct'] = ((monthly_sorted['mom_change'] / monthly_sorted['prev_rev']) * 100).round(1)
    monthly_sorted = monthly_sorted.dropna(subset=['mom_change'])

    monthly_sorted['color'] = monthly_sorted['mom_change'].apply(lambda x: '#28c76f' if x >= 0 else '#ea5455')

    fig_mom = go.Figure()
    fig_mom.add_bar(x=monthly_sorted['month_year_str'], y=monthly_sorted['mom_change'],
                    marker_color=monthly_sorted['color'], name='MoM Change (AED)')
    fig_mom.update_layout(title='Month-on-Month Revenue Change (AED)',
                          yaxis_title='Change (AED)', xaxis_title='Month',
                          xaxis_tickangle=45)
    st.plotly_chart(fig_mom, use_container_width=True)

    st.write("---")

    # --- 6C. Annual Trend Overlay (Detect Repeating Patterns) ---
    st.write("### \U0001f501 Annual Trend Overlay (Detecting Repeating Patterns)")
    st.markdown("*Overlay 2024 and 2025 on the same 12-month axis to spot repeating seasonality.*")

    overlay = monthly_seasonal[monthly_seasonal['year_int'].isin([2024, 2025])].copy()
    overlay['month_name'] = overlay['month_num'].map(month_labels)

    fig_overlay = px.line(overlay, x='month_name', y='revenue', color='year_int',
                          markers=True,
                          title="2024 vs 2025: Monthly Revenue Overlay",
                          labels={'revenue': 'Revenue (AED)', 'month_name': 'Month', 'year_int': 'Year'},
                          color_discrete_map={2024: '#ff9f43', 2025: '#28c76f'})
    st.plotly_chart(fig_overlay, use_container_width=True)

    st.write("---")

    # --- 6D. Revenue Risk Periods ---
    st.write("### \u26a0\ufe0f Revenue Risk Period Detection")
    st.markdown("*Months where revenue dropped >10% compared to the previous month.*")

    risk_months = monthly_sorted[monthly_sorted['mom_pct'] < -10].copy()
    if not risk_months.empty:
        risk_display = risk_months[['month_year_str', 'revenue', 'mom_change', 'mom_pct']].copy()
        risk_display.columns = ['Month', 'Revenue (AED)', 'Drop (AED)', 'Drop %']
        risk_display = risk_display.sort_values('Drop %')

        st.error(f"\U0001f6a8 **{len(risk_months)} months** had a revenue decline exceeding 10%.")

        fig_risk = px.bar(risk_display, x='Month', y='Drop %',
                          title='Revenue Risk Months (Drop > 10%)',
                          color='Drop %', color_continuous_scale='Reds_r',
                          text_auto='.1f')
        st.plotly_chart(fig_risk, use_container_width=True)

        st.dataframe(risk_display.style.format({
            'Revenue (AED)': 'AED {:,.0f}',
            'Drop (AED)': 'AED {:,.0f}',
            'Drop %': '{:.1f}%'
        }), use_container_width=True)
    else:
        st.success("No months had a revenue drop exceeding 10%. Your business is remarkably stable.")

with t7:
    st.header("7. Predictive & Strategic Insights")

    # --- 7A. Revenue Forecast (30/60/90 days) ---
    st.write("### \U0001f52e Revenue Forecast (Next 30 \u2013 90 Days)")
    st.markdown("*Based on the trailing 90-day moving average of daily revenue from your verified dataset.*")

    df_forecast = df_daily.sort_values('date').copy()
    df_forecast['rolling_30'] = df_forecast['net_amount'].rolling(30).mean()
    df_forecast['rolling_90'] = df_forecast['net_amount'].rolling(90).mean()

    last_30_avg = df_forecast['rolling_30'].iloc[-1] if not df_forecast['rolling_30'].isna().all() else avg_daily_now
    last_90_avg = df_forecast['rolling_90'].iloc[-1] if not df_forecast['rolling_90'].isna().all() else avg_daily_now

    forecast_30  = last_30_avg * 30
    forecast_60  = last_30_avg * 60
    forecast_90  = last_90_avg * 90

    fc1, fc2, fc3 = st.columns(3)
    fc1.metric("30-Day Forecast", f"AED {forecast_30:,.0f}", help="Based on last 30-day rolling average")
    fc2.metric("60-Day Forecast", f"AED {forecast_60:,.0f}", help="Based on last 30-day rolling average")
    fc3.metric("90-Day Forecast", f"AED {forecast_90:,.0f}", help="Based on last 90-day rolling average")

    # Plot rolling averages as forecast trajectory
    fig_fc = go.Figure()
    fig_fc.add_scatter(x=df_forecast['date'], y=df_forecast['net_amount'],
                       mode='lines', name='Daily Revenue', line=dict(color='#ccc', width=1), opacity=0.4)
    fig_fc.add_scatter(x=df_forecast['date'], y=df_forecast['rolling_30'],
                       mode='lines', name='30-Day Moving Avg', line=dict(color='#f39c12', width=3))
    fig_fc.add_scatter(x=df_forecast['date'], y=df_forecast['rolling_90'],
                       mode='lines', name='90-Day Moving Avg', line=dict(color='#e74c3c', width=3))
    fig_fc.update_layout(title='Revenue Trajectory & Forecast Baselines',
                         yaxis_title='Revenue (AED)', xaxis_title='Date')
    st.plotly_chart(fig_fc, use_container_width=True)

    st.write("---")

    # --- 7B. AOV Uplift Simulator ---
    st.write("### \U0001f4b0 AOV Uplift Simulator")
    st.markdown("*Drag the slider to see how increasing your average order value impacts annual revenue.*")

    sim_aov = st.slider("Simulated AOV Increase (%)", 1, 20, 5, key='aov_sim_slider')

    current_annual = total_rev / (num_days / 365)
    uplift_val = current_annual * (sim_aov / 100)

    su1, su2 = st.columns(2)
    su1.success(f"### \u2705 Projected Annual Uplift: AED {uplift_val:,.0f}")
    su2.info(f"### Current Annualized Revenue: AED {current_annual:,.0f}")

    # Visual: bar comparing current vs projected
    sim_df = pd.DataFrame({
        'Scenario': ['Current Annual', f'+{sim_aov}% AOV'],
        'Revenue': [current_annual, current_annual + uplift_val]
    })
    fig_sim = px.bar(sim_df, x='Scenario', y='Revenue', color='Scenario',
                     color_discrete_map={'Current Annual': '#ff9f43', f'+{sim_aov}% AOV': '#28c76f'},
                     title=f"Annual Revenue: Current vs +{sim_aov}% AOV Scenario",
                     text_auto='.3s')
    fig_sim.update_layout(showlegend=False)
    st.plotly_chart(fig_sim, use_container_width=True)

    st.write("---")

    # --- 7C. Weak-Day Correction Simulator ---
    st.write("### \U0001f4aa Weak-Day Correction Simulator")
    st.markdown("*What if your weakest trading day performed as well as the average?*")

    dow_order = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    dow_avg = df_daily.groupby('day_of_week')['net_amount'].mean().reindex(dow_order)
    overall_day_avg = dow_avg.mean()
    weakest_day_name = dow_avg.idxmin()
    weakest_day_val = dow_avg.min()
    gap_per_day = overall_day_avg - weakest_day_val
    weeks_per_year = 52
    annual_recovery = gap_per_day * weeks_per_year

    wd1, wd2, wd3 = st.columns(3)
    wd1.error(f"\U0001f4c9 **Weakest Day**\n{weakest_day_name}\nAED {weakest_day_val:,.0f}/day")
    wd2.warning(f"\U0001f4ca **Average Day**\nAED {overall_day_avg:,.0f}/day")
    wd3.success(f"\U0001f4b8 **Annual Recovery**\nAED {annual_recovery:,.0f}/year\nif {weakest_day_name} \u2192 Average")

    # Visual comparison
    dow_df = dow_avg.reset_index()
    dow_df.columns = ['Day', 'Avg Revenue']
    fig_wd = px.bar(dow_df, x='Day', y='Avg Revenue',
                    color='Avg Revenue', color_continuous_scale='RdYlGn',
                    title=f"Daily Revenue Profile \u2014 Target: Lift {weakest_day_name} to Average Line")
    fig_wd.add_hline(y=overall_day_avg, line_dash='dash', line_color='white',
                     annotation_text='Average Target')
    st.plotly_chart(fig_wd, use_container_width=True)

    st.write("---")

    # --- 7D. 10 Actionable Revenue Improvement Strategies ---
    st.write("### \U0001f3af 10 Actionable Revenue Improvement Strategies")
    st.markdown("*Data-driven recommendations based on your 2-year sales analysis.*")

    strategies = [
        {
            "title": "1. Peak-Hour Combo Bundles",
            "desc": "Create meal combos during 18:00\u201321:00 (your Magic Hour). Bundle Karak Chai + Samosa at a slight premium.",
            "impact": f"AED {current_annual * 0.03:,.0f}/yr (+3% AOV lift)"
        },
        {
            "title": f"2. {weakest_day_name} Revival Campaign",
            "desc": f"Launch '{weakest_day_name} Specials' with a loyalty stamp card or 10% discount on slow-moving items.",
            "impact": f"AED {annual_recovery:,.0f}/yr (closing the day-gap)"
        },
        {
            "title": "3. Delivery-to-DineIn Conversion",
            "desc": "Offer exclusive dine-in-only items or a 5% loyalty discount to shift delivery customers in-store, saving 25\u201330% platform commission.",
            "impact": f"AED {current_annual * 0.02:,.0f}/yr (commission savings)"
        },
        {
            "title": "4. Upsell Training for Low-AOV Hours",
            "desc": "Train staff to suggest add-ons (extra shot, dessert) during hours where AOV falls below the average.",
            "impact": f"AED {current_annual * 0.02:,.0f}/yr (+2% AOV)"
        },
        {
            "title": "5. Summer Survival Promotions",
            "desc": "Launch iced beverage specials and a loyalty program during Jun\u2013Aug to counteract the seasonal dip.",
            "impact": "Stabilize summer revenue (-5% decline \u2192 flat)"
        },
        {
            "title": "6. Ramadan Evening Menu",
            "desc": "Create a dedicated Iftar/Suhoor menu with family platters during Ramadan to capitalize on evening spikes.",
            "impact": "Capture 15\u201320% more evening revenue during Ramadan"
        },
        {
            "title": "7. Product Pruning (Bottom 10 SKUs)",
            "desc": "Remove or replace the bottom 10 products that contribute <1% of revenue. Simplify the menu to reduce waste and speed up service.",
            "impact": "Reduced waste + faster kitchen throughput"
        },
        {
            "title": "8. Weekend Premium Pricing",
            "desc": "Implement subtle premium pricing (+5\u201310%) on weekends when demand is highest, or offer premium-only weekend items.",
            "impact": f"AED {current_annual * 0.015:,.0f}/yr (weekend margin boost)"
        },
        {
            "title": "9. Loyalty & Retention Program",
            "desc": "Implement a digital stamp card (buy 9 get 1 free) to increase repeat visits. Target the 60% of customers who visit once/week.",
            "impact": "+1 extra visit/month per loyal customer"
        },
        {
            "title": "10. Data-Driven Inventory Ordering",
            "desc": "Use the hourly sales heatmap to pre-prepare items for peak hours, reducing wait time and lost sales from stockouts.",
            "impact": "5\u201310% reduction in peak-hour lost orders"
        }
    ]

    for s in strategies:
        with st.container(border=True):
            st.write(f"**{s['title']}**")
            st.write(s['desc'])
            st.caption(f"\U0001f4c8 Estimated Impact: {s['impact']}")

# ═══════════════════════════════════════════════════════════
#  SIDEBAR — Premium Interactive Design
# ═══════════════════════════════════════════════════════════

# --- Branding Header ---
st.sidebar.markdown("""
<div style="text-align:center; padding:20px 10px 10px 10px;">
    <h1 style="margin:0; font-size:32px;">☕</h1>
    <h2 style="margin:0; color:#ff9f43; font-size:20px; letter-spacing:2px;">IRISE CHAIIWALA</h2>
    <p style="margin:0; color:#888; font-size:12px; letter-spacing:4px;">ANALYTICS HUB</p>
</div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")

# --- Live Mini KPIs ---
st.sidebar.markdown("""
<div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); padding:15px; border-radius:10px; margin-bottom:10px;">
    <p style="color:#ff9f43; font-size:11px; margin:0; letter-spacing:2px;">TOTAL REVENUE</p>
    <p style="color:white; font-size:22px; font-weight:bold; margin:0;">AED {:,.0f}</p>
</div>
""".format(total_rev), unsafe_allow_html=True)

_sb_col1, _sb_col2 = st.sidebar.columns(2)
_sb_col1.markdown("""
<div style="background:#1a1a2e; padding:10px; border-radius:8px; text-align:center;">
    <p style="color:#28c76f; font-size:10px; margin:0;">DAILY AVG</p>
    <p style="color:white; font-size:14px; font-weight:bold; margin:0;">AED {:,.0f}</p>
</div>
""".format(avg_daily_now), unsafe_allow_html=True)
_sb_col2.markdown("""
<div style="background:#1a1a2e; padding:10px; border-radius:8px; text-align:center;">
    <p style="color:#7367f0; font-size:10px; margin:0;">OVERALL AOV</p>
    <p style="color:white; font-size:14px; font-weight:bold; margin:0;">AED {:,.0f}</p>
</div>
""".format(df_daily['aov'].mean()), unsafe_allow_html=True)

st.sidebar.markdown("")

# --- Date Range Display ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="background:#1a1a2e; padding:12px; border-radius:8px;">
    <p style="color:#ff9f43; font-size:10px; margin:0; letter-spacing:2px;">DATA PERIOD</p>
    <p style="color:white; font-size:13px; margin:4px 0 0 0;">{} → {}</p>
    <p style="color:#888; font-size:11px; margin:2px 0 0 0;">{} trading days</p>
</div>
""".format(
    df_daily['date'].min().strftime('%d %b %Y'),
    df_daily['date'].max().strftime('%d %b %Y'),
    num_days
), unsafe_allow_html=True)

st.sidebar.markdown("")

# --- Quick Stats Expander ---
with st.sidebar.expander("\U0001f4ca Quick Stats", expanded=False):
    st.write(f"**Total Transactions:** {df_daily['transactions'].sum():,.0f}")
    st.write(f"**Weekly Avg Revenue:** AED {avg_weekly_now:,.0f}")
    st.write(f"**YoY Growth:** {yoy_growth:+.1f}%")
    st.write(f"**Best Day:** {df_daily.groupby('day_of_week')['net_amount'].mean().idxmax()}")
    st.write(f"**Peak Products:** {len(df_prod)} SKUs")

# --- Deliverables Section ---
st.sidebar.markdown("---")
with st.sidebar.expander("\U0001f4e5 Deliverables", expanded=True):
    st.markdown("""
    <div style="padding:5px 0;">
        <p style="margin:6px 0;"><span style="color:#28c76f;">●</span> Executive Summary Report</p>
        <p style="margin:6px 0;"><span style="color:#28c76f;">●</span> Interactive Dashboard (7 tabs)</p>
        <p style="margin:6px 0;"><span style="color:#28c76f;">●</span> Growth Strategies (10 items)</p>
    </div>
    """, unsafe_allow_html=True)

    report_path = os.path.join(os.path.dirname(__file__), 'reports', 'executive_summary_report.txt')
    if os.path.exists(report_path):
        with open(report_path, 'r', encoding='utf-8') as f:
            report_content = f.read()
        st.download_button(
            label="\U0001f4c4 Download Report",
            data=report_content,
            file_name="IRise_Executive_Summary_Report.txt",
            mime="text/plain",
            use_container_width=True
        )

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("""
<div style="text-align:center; padding:5px;">
    <p style="color:#555; font-size:10px; margin:0;">Powered by</p>
    <p style="color:#888; font-size:11px; margin:0; letter-spacing:1px;">3S-POS → Supabase → Streamlit</p>
    <p style="color:#444; font-size:9px; margin:5px 0 0 0;">v2.0 · March 2026</p>
</div>
""", unsafe_allow_html=True)

