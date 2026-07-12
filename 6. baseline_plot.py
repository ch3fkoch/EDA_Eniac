import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

"""
BESCHREIBUNG DES SKRIPTS FÜR DIE PRÄSENTATION:
Dieses Skript beantwortet die weiterführende Business-Frage: 
"Wie würde unser Umsatz aussehen, wenn es Black Friday und Weihnachten nicht gäbe?"

Methode:
Wir berechnen einen gleitenden Durchschnitt (Moving Average) über 30 Tage. 
Das glättet die extremen Ausreißer nach oben weg und zeigt uns die "Baseline".
Die Baseline repräsentiert das "Normalgeschäft" von Eniac.
Alles, was weit über diese Baseline herausschießt (rot markiert), ist 
"Incremental Revenue" (also Umsatz, den wir REIN durch die Saisonalität gemacht haben).

Nutzen für das Board:
Das Management sieht auf einen Blick, ob das Unternehmen in der Substanz wächst, 
oder ob man nur durch den Black Friday am Leben gehalten wird.
"""

print("\033[1m\033[38;2;224;255;1m=== ERSTELLE BASELINE PLOT ===\033[0m")

output_dir = "Visualisierungen"
os.makedirs(output_dir, exist_ok=True)

print("1. Lade Master-Tabelle...")
df = pd.read_csv("Daten/clean/master_analysis.csv")

print("2. Aggregiere Tagesumsätze...")
# Datum auf Tagesebene bringen (Uhrzeit abschneiden für sauberen Plot)
df['date'] = pd.to_datetime(df['created_date']).dt.date

# Täglichen Gesamtumsatz berechnen
daily_revenue = df.groupby('date')['line_total'].sum().reset_index()
daily_revenue['date'] = pd.to_datetime(daily_revenue['date'])
daily_revenue.set_index('date', inplace=True)
daily_revenue = daily_revenue.sort_index()

print("3. Berechne 30-Tage Baseline (Gleitender Durchschnitt)...")
# Ein 30-Tage gleitender Durchschnitt ('rolling mean') nimmt immer den Durchschnitt 
# der 30 umliegenden Tage. Dadurch werden Einzel-Tage mit extremen Spitzen (Black Friday) "plattgedrückt".
daily_revenue['baseline'] = daily_revenue['line_total'].rolling(window=30, center=True, min_periods=1).mean()

print("4. Zeichne den Graphen...")
plt.figure(figsize=(18, 8))

# Linie 1: Der echte, schwankende Tagesumsatz (im Hintergrund in Grau)
plt.plot(daily_revenue.index, daily_revenue['line_total'], color='#bdc3c7', label='Tatsächlicher Tagesumsatz', linewidth=1.5)

# Linie 2: Die geglättete Baseline (Dunkelblau, dick)
plt.plot(daily_revenue.index, daily_revenue['baseline'], color='#2c3e50', label='Baseline (30-Tage Normalgeschäft)', linewidth=3)

# Highlight: Wir färben den Bereich Rot ein, wo der echte Umsatz viel höher als die Baseline ist
plt.fill_between(daily_revenue.index, 
                 daily_revenue['baseline'], 
                 daily_revenue['line_total'], 
                 where=(daily_revenue['line_total'] > daily_revenue['baseline']), 
                 interpolate=True, color='#e74c3c', alpha=0.3, label='Saisonale Effekte (Incremental Sales)')

# Formatierung auf Business-Standard anpassen
plt.title('Baseline-Analyse: Tägliches Grundgeschäft vs. Saisonale Peaks', fontsize=24, fontweight='bold', pad=20)
plt.xlabel('Zeitraum', fontsize=18, labelpad=15)
plt.ylabel('Tagesumsatz in €', fontsize=18, labelpad=15)
plt.legend(fontsize=16, loc='upper left')

# Die X-Achse zwingen, saubere Monats-Namen anzuzeigen
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
plt.xticks(rotation=45, fontsize=14)
plt.yticks(fontsize=14)

# Achse unten auf 0 setzen, damit optisch nichts verfälscht wird
plt.ylim(bottom=0)

plt.tight_layout()
output_file = f"{output_dir}/6_Baseline_vs_Incremental.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"\033[1m\033[38;2;46;204;113mFertig! Baseline-Graph wurde unter '{output_file}' gespeichert.\033[0m")
