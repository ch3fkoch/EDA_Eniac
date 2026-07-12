import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("\033[1m\033[38;2;224;255;1m=== STARTE PLOT-GENERATOR ===\033[0m")

output_dir = "Visualisierungen"
os.makedirs(output_dir, exist_ok=True)

# 1. Daten laden mit Fehlerbehandlung
print("Lade Master-Tabelle...")
try:
    df = pd.read_csv("Daten/clean/master_analysis.csv")
except FileNotFoundError:
    print("\033[91mFEHLER: Datei 'Daten/clean/master_analysis.csv' nicht gefunden!\033[0m")
    exit(1)

df['created_date'] = pd.to_datetime(df['created_date'])

sns.set_theme(style="whitegrid", palette="muted")

# ---------------------------------------------------------
# PLOT 1: Saisonalität
# ---------------------------------------------------------
print("Generiere Plot 1: Saisonalität...")
plt.figure(figsize=(24, 12))

df['YearMonth'] = df['created_date'].dt.to_period('M')
monthly_revenue = (df.groupby('YearMonth')['line_total']
                   .sum()
                   .sort_index() / 1_000_000)

ax = monthly_revenue.plot(kind='line', marker='o', markersize=12, 
                         color='#2ecc71', linewidth=4)

plt.title('Gesamtumsatz pro Monat (Saisonalität)', fontsize=32, fontweight='bold', pad=20)
plt.xlabel('Zeitraum', fontsize=24, labelpad=15)
plt.ylabel('Umsatz in Millionen €', fontsize=24, labelpad=15)

# --- ANNOTATIONS (Die Pfeile direkt an der Kurve) ---
for month_str, label in [('2017-11', "Black Friday (Nov '17)"), 
                         ('2017-12', "Weihnachten (Dez '17)"), 
                         ('2018-01', "Neujahr (Jan '18)")]:
    try:
        # 1. Umsatzwert für die Y-Position holen
        val = monthly_revenue[month_str]
        
        # 2. Das korrekte Period-Objekt für die X-Position holen (wichtig für die Achse!)
        period_obj = pd.Period(month_str, freq='M')
        
        # 3. Annotation setzen
        plt.annotate(label, 
                     xy=(period_obj, val),       # Zeigt exakt auf das Datum auf der Kurve
                     xytext=(-60, 40),            # Verschiebt den Text (60px links, 40px hoch)
                     textcoords='offset points',  # Aktiviert stabile Pixel-Verschiebung
                     arrowprops=dict(facecolor='black', shrink=0.08, width=2, headwidth=8), 
                     fontsize=18, fontweight='bold', color='#e74c3c')
    except KeyError:
        print(f"Hinweis: {month_str} nicht in den Daten enthalten.")

# --- ACHSEN-FORMATIERUNG (Aufgeräumte X-Achse) ---
plt.ylim(0, monthly_revenue.max() * 1.25) # Mehr Platz nach oben für die Texte

# Entferne die Zeile mit `ax.set_xticklabels(...)` komplett! 
# Nutze stattdessen das automatische, saubere Datums-Layout von Matplotlib:
plt.xticks(rotation=45, fontsize=18)
plt.yticks(fontsize=18)

#plt.tight_layout() 

plt.ylim(0, monthly_revenue.max() * 1.15)
ax.set_xticklabels([str(x) for x in monthly_revenue.index], rotation=45, fontsize=18)
plt.yticks(fontsize=18)
plt.tight_layout()

plt.savefig(f"{output_dir}/1_Saisonalitaet.png", dpi=300, bbox_inches='tight')
plt.close()
# ---------------------------------------------------------
# PLOT 2: Top 10 Produkte nach Umsatz
# ---------------------------------------------------------
print("Generiere Plot 2: Top Produkte (Umsatz)...")
plt.figure(figsize=(12, 6))

top_revenue = df.groupby('name')['line_total'].sum().sort_values(ascending=False).head(10)

sns.barplot(x=top_revenue.values, y=top_revenue.index, color='#3498db')
plt.title('Top 10 Umsatzstärkste Produkte', fontsize=16, fontweight='bold')
plt.xlabel('Umsatz in €', fontsize=12)
plt.ylabel('')
plt.tight_layout()

plt.savefig(f"{output_dir}/2_Top_Produkte_Umsatz.png", dpi=300)
plt.close()

# ---------------------------------------------------------
# PLOT 3: Rabatt vs. Verkaufte Menge
# ---------------------------------------------------------
print("Generiere Plot 3: Rabatt Analyse...")
plt.figure(figsize=(10, 6))

# Wir runden den Rabatt auf Zehner, um Gruppen zu bilden (0%, 10%, 20%...)
df['Rabatt_Kategorie'] = (df['discount_percent'] // 10) * 10
discount_effect = df.groupby('Rabatt_Kategorie')['product_quantity'].sum()

# Nur realistische Rabatte (0% bis 80%)
discount_effect = discount_effect[discount_effect.index <= 80]

sns.barplot(x=discount_effect.index, y=discount_effect.values, color='#e74c3c')
plt.title('Verkaufte Menge nach Rabatt-Stufen', fontsize=16, fontweight='bold')
plt.xlabel('Gewährter Rabatt (in %)', fontsize=12)
plt.ylabel('Verkaufte Stückzahl', fontsize=12)
plt.tight_layout()

plt.savefig(f"{output_dir}/3_Rabatt_vs_Menge.png", dpi=300)
plt.close()

print(f"\033[1m\033[38;2;46;204;113mFertig! Alle 3 Grafiken wurden im Ordner '{output_dir}' als hochauflösende Bilder (.png) gespeichert!\033[0m")
