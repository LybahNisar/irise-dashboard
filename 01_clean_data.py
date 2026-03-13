"""
IRise Chaiiwala â€“ Phase 1: Data Cleaning
Cleans all raw 3S-POS CSVs and saves standardised processed files.
"""

import pandas as pd
import os

RAW = r'C:\Users\GEO\Desktop\IRise\data\raw'
OUT = r'C:\Users\GEO\Desktop\IRise\data\processed'
os.makedirs(OUT, exist_ok=True)


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 1. DAILY SALES  (main revenue table)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_daily_sales():
    path = os.path.join(RAW, 'Daily Total Sales By Payment Type.csv')
    if not os.path.exists(path):
        print("[SKIP] daily_sales - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'daily_sales.csv')) if os.path.exists(os.path.join(OUT, 'daily_sales.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'BillingDate':           'date',
        'Numberoftransactions':  'transactions',
        'GrossAmount':           'gross_amount',
        'NetAmount':             'net_amount',
        'TotalVAT':              'tax_amount',
        'Textbox21':             'cash',
        'Textbox34':             'card',
        'Textbox62':             'other',
    })
    keep = ['date', 'transactions', 'gross_amount', 'net_amount', 'tax_amount',
            'cash', 'card', 'other']
    df = df[keep].copy()
    df['date'] = pd.to_datetime(df['date'], dayfirst=False, errors='coerce')
    df = df.dropna(subset=['date'])

    # Convert numeric columns (may be read as strings)
    for col in ['transactions', 'gross_amount', 'net_amount', 'tax_amount',
                'cash', 'card', 'other']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df = df.sort_values('date').reset_index(drop=True)

    # Derived columns
    df['year']        = df['date'].dt.year
    df['month']       = df['date'].dt.month
    df['month_name']  = df['date'].dt.strftime('%b')
    df['week']        = df['date'].dt.isocalendar().week.astype(int)
    df['day_of_week'] = df['date'].dt.day_name()
    df['is_weekend']  = df['date'].dt.dayofweek >= 4   # Fri/Sat in UAE
    df['aov']         = (df['net_amount'] / df['transactions'].replace(0, pd.NA)).round(2)

    df.to_csv(os.path.join(OUT, 'daily_sales.csv'), index=False)
    print("[OK] daily_sales.csv  -> " + str(len(df)) + " rows  |  "
          + str(df['date'].min().date()) + " -> " + str(df['date'].max().date()))
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 2. HOURLY SALES
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_hourly_sales():
    path = os.path.join(RAW, 'Hourly Sales.csv')
    if not os.path.exists(path):
        print("[SKIP] hourly_sales - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'hourly_sales.csv')) if os.path.exists(os.path.join(OUT, 'hourly_sales.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'Hour':           'hour',
        'SalesDate':      'date',
        'Textbox7':       'net_amount',
        'Textbox16':      'transactions',
        'AvgTransValue1': 'aov',
    })
    keep = ['date', 'hour', 'net_amount', 'transactions', 'aov']
    df = df[[c for c in keep if c in df.columns]].copy()
    # Hourly Sales uses DD/MM/YYYY format
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date', 'hour'])

    # Keep only valid integer hour rows (0â€“23)
    df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
    df = df[df['hour'].between(0, 23)].copy()
    df['hour'] = df['hour'].astype(int)

    df['year']        = df['date'].dt.year
    df['day_of_week'] = df['date'].dt.day_name()

    df.to_csv(os.path.join(OUT, 'hourly_sales.csv'), index=False)
    print("[OK] hourly_sales.csv -> " + str(len(df)) + " rows")
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 3. HOURLY AVG PER WEEKDAY
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_hourly_avg():
    path = os.path.join(RAW, 'Hourly Sales Avg Per Weekday.csv')
    if not os.path.exists(path):
        print("[SKIP] hourly_avg - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'hourly_avg_weekday.csv')) if os.path.exists(os.path.join(OUT, 'hourly_avg_weekday.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'SalesDate':    'day_name',
        'Hour1':        'hour',
        'textbox2':     'avg_net_amount',
        'NoOfOrders':   'avg_orders',
        'AvgTransValue':'avg_aov',
    })
    keep = ['day_name', 'hour', 'avg_net_amount', 'avg_orders', 'avg_aov']
    df = df[[c for c in keep if c in df.columns]].copy()

    # Filter out label/summary rows - keep only real day names
    valid_days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df = df[df['day_name'].isin(valid_days)].copy()

    df['hour'] = pd.to_numeric(df['hour'], errors='coerce')
    df = df.dropna(subset=['hour'])
    df['hour'] = df['hour'].astype(int)

    # Convert numeric columns
    for col in ['avg_net_amount', 'avg_orders', 'avg_aov']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.to_csv(os.path.join(OUT, 'hourly_avg_weekday.csv'), index=False)
    print("[OK] hourly_avg_weekday.csv -> " + str(len(df)) + " rows")
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 4. PRODUCT SALES (granular â€“ by date & order type)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_product_sales():
    path = os.path.join(RAW, 'Product Sales By Order Type.csv')
    if not os.path.exists(path):
        print("[SKIP] product_sales - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'product_sales.csv')) if os.path.exists(os.path.join(OUT, 'product_sales.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'BillingDate': 'date',
        'Textbox27':   'product_name',
        'Qty':         'quantity',
        'NetAmount':   'net_amount',
        'VATAmount':   'tax_amount',
        'GrossAmount': 'gross_amount',
        'OrderType':   'order_type',
        'waste':       'is_waste',
    })
    keep = ['date', 'product_name', 'quantity', 'net_amount',
            'tax_amount', 'gross_amount', 'order_type', 'is_waste']
    df = df[[c for c in keep if c in df.columns]].copy()
    # Product Sales uses DD/MM/YYYY format
    df['date'] = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['date', 'product_name'])
    for col in ['quantity', 'net_amount', 'tax_amount', 'gross_amount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['product_name'] = df['product_name'].str.strip()
    df['order_type']   = df['order_type'].str.strip()
    df['year']         = df['date'].dt.year
    df['month']        = df['date'].dt.month

    df.to_csv(os.path.join(OUT, 'product_sales.csv'), index=False)
    print("[OK] product_sales.csv -> " + str(len(df)) + " rows  |  "
          + str(df['product_name'].nunique()) + " unique products")
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 5. PRODUCT SUMMARY (all-time totals by channel)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_product_summary():
    path = os.path.join(RAW, 'Sales by Product.csv')
    if not os.path.exists(path):
        print("[SKIP] product_summary - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'product_summary.csv')) if os.path.exists(os.path.join(OUT, 'product_summary.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'Category':             'category',
        'SubCategory':          'subcategory',
        'ProductDesc':          'product_name',
        'Quantity':             'total_qty',
        'NetAmount':            'total_net',
        'GrossAmount':          'total_gross',
        'QuantityEatIn':        'qty_eat_in',
        'NetAmountEatIn':       'net_eat_in',
        'QuantityEatOut':       'qty_takeout',
        'NetAmountEatOut':      'net_takeout',
        'QuantityDelivery':     'qty_delivery',
        'NetAmountDelivery':    'net_delivery',
    })
    keep = ['category', 'subcategory', 'product_name', 'total_qty', 'total_net',
            'total_gross', 'qty_eat_in', 'net_eat_in', 'qty_takeout',
            'net_takeout', 'qty_delivery', 'net_delivery']
    df = df[[c for c in keep if c in df.columns]].copy()
    df = df.dropna(subset=['product_name'])
    df = df[df['product_name'].str.strip() != '']

    df.to_csv(os.path.join(OUT, 'product_summary.csv'), index=False)
    print("[OK] product_summary.csv -> " + str(len(df)) + " products")
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 6. ORDER TYPE â€“ DAILY
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_order_type_daily():
    path = os.path.join(RAW, 'Daily Sales By Order Type.csv')
    if not os.path.exists(path):
        print("[SKIP] order_type_daily - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'order_type_daily.csv')) if os.path.exists(os.path.join(OUT, 'order_type_daily.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'BillingDate':          'date',
        'OrderType':            'order_type',
        'Numberoftransactions': 'transactions',
        'GrossAmount':          'gross_amount',
        'NetAmount':            'net_amount',
        'VATAmount':            'tax_amount',
    })
    keep = ['date', 'order_type', 'transactions', 'gross_amount',
            'net_amount', 'tax_amount']
    df = df[[c for c in keep if c in df.columns]].copy()
    # Daily Sales By Order Type uses DD/MM/YYYY format
    df['date']       = pd.to_datetime(df['date'], dayfirst=True, errors='coerce')
    df['order_type'] = df['order_type'].str.strip()
    df = df.dropna(subset=['date', 'order_type'])
    for col in ['transactions', 'gross_amount', 'net_amount', 'tax_amount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['year']  = df['date'].dt.year
    df['month'] = df['date'].dt.month

    df.to_csv(os.path.join(OUT, 'order_type_daily.csv'), index=False)
    print("[OK] order_type_daily.csv -> " + str(len(df)) + " rows  |  Types: " + str(df['order_type'].unique().tolist()))
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 7. ORDER TYPE â€“ MONTHLY SUMMARY
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_order_type_monthly():
    path = os.path.join(RAW, 'Sales By Order Type Per Month Report.csv')
    if not os.path.exists(path):
        print("[SKIP] order_type_monthly - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'order_type_monthly.csv')) if os.path.exists(os.path.join(OUT, 'order_type_monthly.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'OrderTypeID':  'order_type',
        'Year':         'year',
        'Month':        'month',
        'NoOfOrders':   'transactions',
        'NetAmount':    'net_amount',
        'VATAmount':    'tax_amount',
        'GrossAmount':  'gross_amount',
    })
    keep = ['year', 'month', 'order_type', 'transactions',
            'net_amount', 'tax_amount', 'gross_amount']
    df = df[[c for c in keep if c in df.columns]].copy()
    df = df.dropna(subset=['year', 'month', 'order_type'])
    df['year']  = df['year'].astype(int)
    df['month'] = df['month'].astype(int)

    df.to_csv(os.path.join(OUT, 'order_type_monthly.csv'), index=False)
    print("[OK] order_type_monthly.csv -> " + str(len(df)) + " rows")
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 8. TRANSACTIONS LIST  (individual orders)
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_transactions():
    path = os.path.join(RAW, 'Transactions List.csv')
    if not os.path.exists(path):
        print("[SKIP] transactions - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'transactions.csv')) if os.path.exists(os.path.join(OUT, 'transactions.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'Name':             'order_name',
        'Textbox3':         'gross_amount',
        'Textbox15':        'net_amount',
        'Textbox17':        'tax_amount',
        'CreationTime':     'created_at',
        'PaymentType':      'payment_type',
        'IsSendBack':       'is_void',
    })
    keep = ['order_name', 'gross_amount', 'net_amount', 'tax_amount',
            'created_at', 'payment_type', 'is_void']
    df = df[[c for c in keep if c in df.columns]].copy()
    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df = df.dropna(subset=['created_at'])

    # Extract order type from order_name (e.g. "Eat In 7", "Delivery 3332")
    df['order_type'] = df['order_name'].str.extract(
        r'^(Eat In|Delivery|Take Out|Collection)', expand=False).fillna('Unknown')

    df['date']        = df['created_at'].dt.date
    df['hour']        = df['created_at'].dt.hour
    df['day_of_week'] = df['created_at'].dt.day_name()
    df['year']        = df['created_at'].dt.year
    df['month']       = df['created_at'].dt.month

    # Remove voided / send-back orders
    df = df[df['is_void'].str.lower() == 'no']

    df.to_csv(os.path.join(OUT, 'transactions.csv'), index=False)
    print("[OK] transactions.csv -> " + str(len(df)) + " rows  |  Payment types: " + str(df['payment_type'].unique().tolist()))
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# 9. CATEGORY SUMMARY
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
def clean_category_summary():
    path = os.path.join(RAW, 'Sales By Category With Drill Down.csv')
    if not os.path.exists(path):
        print("[SKIP] category_summary - Raw file missing")
        return pd.read_csv(os.path.join(OUT, 'category_summary.csv')) if os.path.exists(os.path.join(OUT, 'category_summary.csv')) else None
    df = pd.read_csv(path,
                     encoding='utf-8-sig')
    df = df.rename(columns={
        'Category':    'category',
        'SubCategory': 'subcategory',
        'ProductDesc': 'product_name',
        'Quantity1':   'quantity',
        'GrossAmount1':'gross_amount',
        'NetAmount1':  'net_amount',
    })
    keep = ['category', 'subcategory', 'product_name', 'quantity',
            'gross_amount', 'net_amount']
    df = df[[c for c in keep if c in df.columns]].copy()

    # Filter out report label rows - only keep real categories
    valid_categories = ['Drink', 'Food', 'Non-Menu']
    df = df[df['category'].isin(valid_categories)].copy()

    # Convert numeric columns
    for col in ['quantity', 'gross_amount', 'net_amount']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Drop duplicate rows
    df = df.drop_duplicates()

    df.to_csv(os.path.join(OUT, 'category_summary.csv'), index=False)
    print("[OK] category_summary.csv -> " + str(len(df)) + " rows  |  Categories: " + str(df['category'].unique().tolist()))
    return df


# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# RUN ALL
# â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if __name__ == '__main__':
    print("=" * 55)
    print("  IRise Chaiiwala - Phase 1: Data Cleaning")
    print("=" * 55)

    dfs = {}
    try:
        dfs['daily']            = clean_daily_sales()
        dfs['hourly']           = clean_hourly_sales()
        dfs['hourly_avg']       = clean_hourly_avg()
        dfs['products']         = clean_product_sales()
        dfs['product_summary']  = clean_product_summary()
        dfs['order_daily']      = clean_order_type_daily()
        dfs['order_monthly']    = clean_order_type_monthly()
        dfs['transactions']     = clean_transactions()
        dfs['categories']       = clean_category_summary()

        print()
        print("=" * 55)
        print("  ALL files cleaned and saved to data/processed/")
        print("=" * 55)

        # Quick validation
        daily = dfs['daily']
        print("\nQuick Stats:")
        print("  Total Net Revenue : AED " + f"{daily['net_amount'].sum():,.2f}")
        print("  Total Transactions: " + f"{daily['transactions'].sum():,.0f}")
        print("  Overall AOV       : AED " + f"{daily['aov'].mean():,.2f}")
        print("  Date Range        : " + str(daily['date'].min().date()) + " -> " + str(daily['date'].max().date()))
        print("  Trading Days      : " + str(len(daily)))

    except Exception as e:
        import traceback
        print("\nERROR: " + str(e))
        traceback.print_exc()
