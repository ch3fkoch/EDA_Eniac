# Eniac E-Commerce: Data Analysis & Discount Strategy 

![Python](https://img.shields.io/badge/Python-3.x-blue.svg)
![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-yellow.svg)
![Seaborn](https://img.shields.io/badge/Seaborn-Visualization-green.svg)
![License](https://img.shields.io/badge/License-MIT-purple.svg)

Willkommen im Eniac-Datenanalyseprojekt! 

Dieses Repository enthält eine modulare Daten-Pipeline, um Rohtransaktionsdaten in visuelle Business-Insights und KPIs für das E-Commerce-Management zu verwandeln.

## Business Case
Das Unternehmen **Eniac** stand vor einem strategischen Konflikt zwischen Marketing (Wachstum durch Rabatte) und Investoren (Schutz der Marke und Marge). Dieses Projekt analysiert einen großen Datensatz an Bestellungen und leitet daraus harte Fakten ab:
- **Datenbereinigung:** Entfernung von fehlerhaften Preisformatierungen und fehlenden Daten (~60-70% Ausschuss bei Rohdaten, um eine verlässliche 100%-saubere Baseline zu schaffen).
- **Saisonalität vs. Baseline:** Beweisführung, dass der Kernumsatz stabil ist, das echte Wachstum aber rein durch Q4-Events (Black Friday) getrieben wird.
- **Strategie:** Datengestützte Empfehlung zum Event-Driven Discounting.

---

## Die Ausführungs-Pipeline

Um reproduzierbare und korrekte Ergebnisse für Dashboards und Präsentationen zu generieren, müssen die Skripte in der unten definierten Reihenfolge ausgeführt werden.

### Phase 1: Datenaufbereitung
Zunächst müssen die Rohdaten (`orders.csv`, `orderlines.csv`, `products.csv`) eingelesen, von Ausreißern befreit und vorbereitet werden. Dies passiert interaktiv in Jupyter Notebooks.
- **Skripte:** `1.data_check_final.ipynb` & `2. merge_orders_olines.ipynb` 
- **Ziel:** Fehlende Werte entfernen, Outlier (Ausreißer) glätten, fehlerhafte Preise (mit doppelten Punkten) filtern.
- **Output:** Saubere Roh-Dateien im Ordner `Daten/clean/` (z.B. `order_sort.csv`).

---

### Phase 2: Core Business Logic (WICHTIGSTES SKRIPT)
Das ist das **Herzstück der Architektur**. Dieses Skript **muss** immer als Erstes von allen Python-Skripten ausgeführt werden.
- **Skript:** `3. final_business_analysis.py`
- **Was es macht:** 
  - Führt die Tabellen zusammen und wendet den kritischen `state == 'Completed'` Filter an.
  - Wendet eine regelbasierte **Kategorisierung** (Zubehör, Apple, etc.) an.
  - Berechnet wichtige Sales-KPIs (`discount_euro`, `discount_percent`, `line_total`).
  - Sortiert alle Spalten in eine saubere, logische Reihenfolge.
  - Gibt auf der Konsole die "Elevator Pitch" KPIs (Gesamtumsatz, Top-Produkte) für Präsentationen aus.
- **Output:** Generiert die finale, kategorisierte Single-Source-Of-Truth Tabelle `Daten/clean/master_analysis.csv`. **Ohne diese Datei funktionieren die Plot-Skripte nicht!**

---

### Phase 3: Visualisierung & Deep-Dive Analysen 
Sobald die `master_analysis.csv` durch Phase 2 generiert wurde, können die Visualisierungs-Skripte in völlig **beliebiger Reihenfolge** (oder parallel) ausgeführt werden. **Wichtig:** Diese Skripte sind strikt "Read-Only". Sie greifen auf die Master-Tabelle zu, verändern sie aber nicht.

- **`4. category_plots.py`:** Generiert die Haupt-Grafiken für die Präsentation (Preisverteilung über Kategorien via Boxplots & generelles Rabatt-Histogramm).
- **`5. type_revenue_analysis.py`:** Aggregiert den Umsatz pro interner `type`-ID, verknüpft dies mit Top-Produkten zur Lesbarkeit und erstellt ein horizontales Bar-Chart für das Management (`7_Top_Types_Umsatz.png`).
- **`6. baseline_plot.py`:** Generiert eine "Sales-First" Zeitreihen-Analyse (Time-Series) über den täglichen Umsatz. Trennt durch einen Moving-Average das echte Grundwachstum (Baseline) von reinen Event-Umsätzen (Incremental Sales durch Black Friday/Weihnachten).
- **`7. dashboard_plots.py`:** Weitere aggregierte Skripte für spezifische Auswertungen (Top-Produkte, grobe Saisonalität).
- **`10. data_quality_counter.py`:** Zeigt detailliert auf, wie viele Datensätze in der Bereinigung verworfen werden mussten (Quality-Check vs. Rohdaten).

