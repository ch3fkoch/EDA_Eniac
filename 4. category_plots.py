import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

print("\033[1m\033[38;2;224;255;1m=== STARTE KATEGORIE- & RABATT-PLOTS ===\033[0m")

output_dir = "Visualisierungen"
os.makedirs(output_dir, exist_ok=True)

print("1. Lade Master-Tabelle...")
df = pd.read_csv("Daten/clean/master_analysis.csv")

# =========================================================
# PLOT 4: Preisverteilung über Kategorien (Frage 4)
# =========================================================
print("3. Generiere Plot: Preisverteilung über Kategorien...")
sns.set_theme(style="whitegrid", palette="muted")

plt.figure(figsize=(16, 8))

# Wir erstellen einen Boxplot, um zu sehen, ob eine Kategorie nur aus Billigartikeln
# besteht, oder ob es eine große Preisspanne gibt.
ax = sns.boxplot(x='price', y='category', hue='category', data=df, palette='Set3', showfliers=False, legend=False)

plt.title('Preisverteilung der Produkte pro Kategorie (ohne Extrem-Ausreißer)', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Originalpreis in €', fontsize=18, labelpad=15)
plt.ylabel('Kategorie', fontsize=18, labelpad=15)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.tight_layout()
plt.savefig(f"{output_dir}/4_Preisverteilung_Kategorien.png", dpi=300, bbox_inches='tight')
plt.close()

# =========================================================
# PLOT 5: Rabatt-Histogramm (Ergänzung zu Frage 2)
# =========================================================
print("4. Generiere Plot: Rabatt-Verteilung...")

plt.figure(figsize=(14, 7))

# Wir filtern alle Käufe, die GAR KEINEN Rabatt hatten, heraus, um zu sehen,
# wie hoch der Rabatt ist, WENN einer gewährt wird.
rabatte = df[df['discount_percent'] > 0]['discount_percent']

sns.histplot(rabatte, bins=50, kde=True, color='#e74c3c')

plt.title('Verteilung der Rabatte (Wie viel % Rabatt wird meistens gewährt?)', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Rabatt in Prozent (%)', fontsize=18, labelpad=15)
plt.ylabel('Anzahl verkaufter Artikel', fontsize=18, labelpad=15)

plt.xticks(fontsize=14)
plt.yticks(fontsize=14)

plt.tight_layout()
plt.savefig(f"{output_dir}/5_Rabatt_Verteilung.png", dpi=300, bbox_inches='tight')
plt.close()

print(f"\033[1m\033[38;2;46;204;113mFertig! Beide neuen Grafiken wurden in '{output_dir}' gespeichert!\033[0m")
