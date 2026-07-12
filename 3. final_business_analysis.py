import pandas as pd
import time 

### Variable und Formatierung definieren
start_zeit = time.perf_counter()
LEMON = "\033[38;2;224;255;1m"
BLAUGRAU = "\033[38;2;82;98;123m"
HELLGRAU = "\033[38;2;237;238;240m"
GRUEN    = "\033[38;2;46;204;113m"   
ROT      = "\033[38;2;231;76;60m"    
BOLD = "\033[1m"
RESET = "\033[0m"

def format_euro(zahl):
    return f"{zahl:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

print(f"{BOLD}{LEMON}=== GESAMTE BUSINESS INTELLIGENCE ANALYSE ==={RESET}")
print("1. Lade Datensätze...")

# 1. Daten laden
df_order_sort = pd.read_csv("Daten/clean/order_sort.csv")
if 'id_order' in df_order_sort.columns:
    df_order_sort = df_order_sort.rename(columns={'id_order': 'order_id'})
if 'name' in df_order_sort.columns:
    df_order_sort = df_order_sort.drop(columns=['name'])

df_products = pd.read_csv("Daten/clean/products_clean.csv")
df_orders = pd.read_csv("Daten/clean/orders_clean.csv")

# Falls line_total fehlt (weil es im Notebook nicht exportiert wurde), berechnen wir es
if 'line_total' not in df_order_sort.columns and 'product_quantity' in df_order_sort.columns and 'unit_price' in df_order_sort.columns:
    df_order_sort['line_total'] = df_order_sort['product_quantity'] * df_order_sort['unit_price']

# 2. Datum und State aus orders_clean rüberziehen (Merge on order_id)
print("2. Stelle Datum (created_date) und State wieder her...")
df_orders_dates = df_orders[['order_id', 'created_date', 'state']]
df_master = pd.merge(df_order_sort, df_orders_dates, on='order_id', how='left')

print("-> Filtere Verkäufe nach Status 'Completed'...")
df_master = df_master[df_master['state'] == 'Completed']

# 3. Produkt-Infos (Name, Price, Type) anfügen (Merge on sku)
print("3. Füge Produktnamen, Originalpreise und Type hinzu...")
df_master = pd.merge(df_master, df_products[['sku', 'name', 'price', 'type']], on='sku', how='left')

print("-> Entferne alle Verkäufe ohne bekannten Produktnamen (Bootcamp-Style)...")
df_master = df_master.dropna(subset=['name'])

# Datentyp von created_date zu datetime konvertieren
df_master['created_date'] = pd.to_datetime(df_master['created_date'])

# 4. Rabatt-Logik
print("4. Berechne Rabatte...")
df_master['price'] = pd.to_numeric(df_master['price'], errors='coerce')
df_master['discount_euro'] = df_master['price'] - df_master['unit_price']
df_master['discount_euro'] = df_master['discount_euro'].clip(lower=0)

df_master['discount_percent'] = (df_master['discount_euro'] / df_master['price']) * 100
df_master['discount_percent'] = df_master['discount_percent'].fillna(0)

# 5. Kategorisierung (Neu hier hinzugefügt, um Zirkelbezüge zu vermeiden)
print("5. Führe regelbasierte Kategorisierung durch...")
def categorize_product(name):
    if not isinstance(name, str):
        return "Sonstiges"
    name_lower = name.lower()
    
    if any(kw in name_lower for kw in ['case', 'cover', 'cable', 'charger', 'adapter', 'keyboard', 'mouse', 'screen', 'band', 'strap', 'protector', 'dock']):
        return "Zubehör"
    elif any(kw in name_lower for kw in ['memory', 'ssd', 'drive', 'storage', 'ram', 'hdd']):
        return "Speicher & Laufwerke"
    elif any(kw in name_lower for kw in ['headphone', 'earpod', 'airpod', 'speaker', 'audio', 'beats']):
        return "Audio"
    elif any(kw in name_lower for kw in ['watch', 'smartwatch']):
        return "Wearables"
    elif any(kw in name_lower for kw in ['iphone', 'smartphone']):
        return "Smartphones"
    elif any(kw in name_lower for kw in ['ipad', 'tablet']):
        return "Tablets"
    elif any(kw in name_lower for kw in ['mac', 'imac', 'laptop', 'pc', 'display', 'monitor']):
        return "Computer & Laptops"
    else:
        return "Sonstiges"

df_master['category'] = df_master['name'].apply(categorize_product)

# 6. Spalten logisch sortieren
print("6. Sortiere Spalten in eine logische Reihenfolge...")
col_order = [
    'order_id', 'created_date', 'state',  # Order-Infos
    'sku', 'name', 'type', 'category',    # Produkt-Infos
    'product_quantity', 'price',          # Mengen & Originalpreis
    'unit_price', 'discount_euro',        # Bezahlter Preis & Rabatt absolut
    'discount_percent', 'line_total'      # Rabatt % & Gesamtumsatz der Zeile
]
# Nur Spalten behalten und sortieren, die auch wirklich existieren
final_cols = [c for c in col_order if c in df_master.columns]
# Falls es Spalten gibt, die nicht in col_order standen, diese hinten dranhängen
remaining_cols = [c for c in df_master.columns if c not in final_cols]
df_master = df_master[final_cols + remaining_cols]

# 6. Speichern der Master-Tabelle für Dashboards
output_path = "Daten/clean/master_analysis.csv"
print(f"6. Speichere finale Master-Tabelle nach: {output_path}...\n")
df_master.to_csv(output_path, index=False, float_format='%.2f')

# ---------------------------------------------------------
# TEIL 1: SCHNELLE BUSINESS AUSWERTUNG (KPIs)
# ---------------------------------------------------------
print(f"{BOLD}{LEMON}=== ENIAC E-COMMERCE KPIs ==={RESET}")

# Zeitraum
min_date = df_master['created_date'].min().strftime('%d.%m.%Y')
max_date = df_master['created_date'].min().strftime('%d.%m.%Y') if pd.isna(df_master['created_date'].max()) else df_master['created_date'].max().strftime('%d.%m.%Y')
print(f"{BOLD}Zeitraum:{RESET} {min_date} bis {max_date}")

# Gesamtumsatz
total_revenue = df_master['line_total'].sum()
print(f"{BOLD}Gesamtumsatz:{RESET} {GRUEN}{format_euro(total_revenue)} €uro{RESET}")

# Meistverkaufte Produkte (Menge)
print(f"\n{BOLD}Top 3 Meistverkaufte Produkte (nach Menge):{RESET}")
top_qty = df_master.groupby('name')['product_quantity'].sum().sort_values(ascending=False).head(3)
for name, qty in top_qty.items():
    print(f"- {name}: {int(qty)} Stück")

# Umsatzstärkste Produkte (Euro)
print(f"\n{BOLD}Top 3 Umsatzstärkste Produkte (nach Euro):{RESET}")
top_rev = df_master.groupby('name')['line_total'].sum().sort_values(ascending=False).head(3)
for name, rev in top_rev.items():
    print(f"- {name}: {format_euro(rev)} €uro")

# Rabatt Statistik (Durchschnitt)
avg_discount = df_master['discount_euro'].mean()
print(f"\n{BOLD}Durchschnittlicher Rabatt pro Artikel:{RESET} {format_euro(avg_discount)} €uro")

# ---------------------------------------------------------
# TEIL 2: FEHLENDE GESCHÄFTSFRAGEN (RABATTE IN PROZENT)
# ---------------------------------------------------------
print(f"\n{BOLD}{LEMON}=== RABATT-TIEFEN-ANALYSE ==={RESET}")

# Frage 1: Wie viele Produkte werden mit Rabatt verkauft?
discounted_items = df_master[df_master['discount_percent'] > 0]['product_quantity'].sum()
total_items = df_master['product_quantity'].sum()
discounted_items_pct = (discounted_items / total_items) * 100

unique_skus_discounted = df_master[df_master['discount_percent'] > 0]['sku'].nunique()
total_skus = df_master['sku'].nunique()
unique_skus_pct = (unique_skus_discounted / total_skus) * 100

print(f"{BOLD}Frage 1: Wie viele Produkte werden mit Rabatt verkauft?{RESET}")
print(f"-> Von insgesamt {int(total_items):,} verkauften Artikeln wurden {int(discounted_items):,} mit einem Rabatt verkauft ({discounted_items_pct:.1f}%).")
print(f"-> Das betrifft {unique_skus_discounted} von {total_skus} unterschiedlichen Produkten im Sortiment ({unique_skus_pct:.1f}%).\n")

# Frage 2: Wie hoch sind die angebotenen Rabatte als Prozentsatz?
avg_discount_pct = df_master[df_master['discount_percent'] > 0]['discount_percent'].mean()
median_discount_pct = df_master[df_master['discount_percent'] > 0]['discount_percent'].median()

print(f"{BOLD}Frage 2: Wie hoch sind die angebotenen Rabatte als Prozentsatz der Produktpreise?{RESET}")
print(f"-> Wenn ein Rabatt gewährt wird, liegt er im Durchschnitt bei {avg_discount_pct:.1f}% des Originalpreises.")
print(f"-> Der Median liegt bei {median_discount_pct:.1f}%")

end_zeit = time.perf_counter()
print(f"\n{HELLGRAU}Gesamtes Skript ausgeführt in {end_zeit - start_zeit:.2f} Sekunden.{RESET}")
