import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("\033[1m\033[38;2;224;255;1m=== UMSATZ-ANALYSE NACH 'TYPE' ===\033[0m")

output_dir = "Visualisierungen"
os.makedirs(output_dir, exist_ok=True)

print("1. Lade Master-Tabelle...")
df = pd.read_csv("Daten/clean/master_analysis.csv")

# =========================================================
# BERECHNUNG DES UMSATZES PRO TYPE
# =========================================================
print("2. Aggregiere Umsatz und hole Beispiel-Produkte pro Type...\n")

# Wir berechnen den Gesamtumsatz pro Type
type_revenue = df.groupby('type')['line_total'].sum().reset_index()

# Sortieren nach Umsatz absteigend und die Top 15 nehmen
top_15_types = type_revenue.sort_values(by='line_total', ascending=False).head(15).copy()

# Damit man weiß, was sich hinter "Type 1282" verbirgt, suchen wir uns das meistverkaufte Produkt dieses Typs
def get_most_common_product(t):
    products_of_type = df[df['type'] == t]
    if len(products_of_type) > 0:
        # Das Produkt, das in diesem Type am meisten Umsatz gemacht hat
        top_product = products_of_type.groupby('name')['line_total'].sum().idxmax()
        return top_product
    return "Unbekannt"

top_15_types['beispiel_produkt'] = top_15_types['type'].apply(get_most_common_product)

# Neues Label für den Plot basteln (z.B. "Type 1282 (Apple MacBook Pro...)")
# Wir kürzen den Namen ab, damit der Plot lesbar bleibt
top_15_types['plot_label'] = top_15_types.apply(lambda row: f"Type {row['type']}\n({str(row['beispiel_produkt'])[:30]}...)", axis=1)

# Ausgabe in der Konsole
print(f"\033[1mTOP 10 UMSATZSTÄRKSTE TYPES:\033[0m")
for index, row in top_15_types.head(10).iterrows():
    revenue_mio = row['line_total'] / 1_000_000
    print(f"- Type {row['type']:<10} | Umsatz: {revenue_mio:>5.2f} Mio. € | Bsp: {row['beispiel_produkt'][:40]}")

# =========================================================
# PLOT: Top Types nach Umsatz
# =========================================================
print("\n3. Generiere Bar-Chart für die Präsentation...")

plt.figure(figsize=(16, 10))
sns.set_theme(style="whitegrid")

# Barplot erstellen
ax = sns.barplot(x='line_total', y='plot_label', hue='plot_label', data=top_15_types.head(10), palette='viridis', legend=False)

plt.title('Die Top 10 Produkt-Types nach Gesamtumsatz', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Gesamtumsatz in zig Millionen €', fontsize=18, labelpad=15)
plt.ylabel('Eniac Type ID (inkl. Beispielprodukt)', fontsize=18, labelpad=15)

plt.xticks(fontsize=14)
plt.yticks(fontsize=12)

# Werte als Text an die Balken schreiben
for p in ax.patches:
    width = p.get_width()
    # Formatierung: Wert in Millionen Euro
    ax.text(width + 200000, 
            p.get_y() + p.get_height() / 2, 
            f"{width/1000000:.2f} Mio. €", 
            ha='left', va='center', fontsize=12, fontweight='bold', color='#2c3e50')

plt.tight_layout()
output_file = f"{output_dir}/7_Top_Types_Umsatz.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"\033[1m\033[38;2;46;204;113mFertig! Graph wurde unter '{output_file}' gespeichert.\033[0m")
