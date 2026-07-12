import pandas as pd

print("\033[1m\033[38;2;224;255;1m=== DATENQUALITÄTS-CHECK ===\033[0m\n")

def check_quality(filename, df, checks):
    total_rows = len(df)
    clean_df = df.copy()
    
    print(f"\033[1mPrüfe {filename}...\033[0m")
    print(f"Ursprüngliche Datensätze: {total_rows:,}")
    
    # 1. Duplikate
    if 'duplicates' in checks:
        before = len(clean_df)
        clean_df = clean_df.drop_duplicates()
        dropped = before - len(clean_df)
        if dropped > 0:
            print(f"- Entfernte Duplikate: {dropped:,}")
            
    # 2. Fehlende Werte (NaN)
    if 'nan' in checks:
        before = len(clean_df)
        clean_df = clean_df.dropna()
        dropped = before - len(clean_df)
        if dropped > 0:
            print(f"- Entfernte Reihen mit fehlenden Werten (NaN): {dropped:,}")
            
    # 3. Korrupte Preise (Mehrere Punkte im String)
    for check in checks:
        if isinstance(check, dict) and 'corrupt_price' in check:
            col = check['corrupt_price']
            before = len(clean_df)
            mask = clean_df[col].astype(str).str.count(r"\.") > 1
            clean_df = clean_df[~mask]
            dropped = before - len(clean_df)
            if dropped > 0:
                print(f"- Entfernte Reihen mit korruptem Preis (z.B. 1.23.45) in Spalte '{col}': {dropped:,}")

        if isinstance(check, dict) and 'corrupt_promo' in check:
            col = check['corrupt_promo']
            before = len(clean_df)
            mask = clean_df[col].astype(str).str.count(r"\.") > 1
            clean_df = clean_df[~mask]
            dropped = before - len(clean_df)
            if dropped > 0:
                print(f"- Entfernte Reihen mit korruptem Promo-Preis in Spalte '{col}': {dropped:,}")

    clean_rows = len(clean_df)
    dirty_rows = total_rows - clean_rows
    clean_pct = (clean_rows / total_rows) * 100
    
    print(f"\033[38;2;46;204;113m-> 100% Saubere Datensätze: {clean_rows:,} ({clean_pct:.1f}%)\033[0m")
    print(f"\033[38;2;231;76;60m-> Unsaubere Datensätze aussortiert: {dirty_rows:,}\033[0m\n")
    return clean_df

# --- 1. ORDERS ---
try:
    orders = pd.read_csv("Daten/orders.csv")
    check_quality("orders.csv", orders, checks=['duplicates', 'nan'])
except Exception as e:
    print(f"Fehler bei orders.csv: {e}")

# --- 2. ORDERLINES ---
try:
    orderlines = pd.read_csv("Daten/orderlines.csv")
    check_quality("orderlines.csv", orderlines, checks=['duplicates', 'nan', {'corrupt_price': 'unit_price'}])
except Exception as e:
    print(f"Fehler bei orderlines.csv: {e}")

# --- 3. PRODUCTS ---
try:
    products = pd.read_csv("Daten/products.csv")
    check_quality("products.csv", products, checks=['duplicates', 'nan', {'corrupt_price': 'price'}, {'corrupt_promo': 'promo_price'}])
except Exception as e:
    print(f"Fehler bei products.csv: {e}")

# --- 4. BRANDS ---
try:
    brands = pd.read_csv("Daten/brands.csv")
    check_quality("brands.csv", brands, checks=['duplicates', 'nan'])
except Exception as e:
    print(f"Fehler bei brands.csv: {e}")
