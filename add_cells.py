import json

file_path = "Tolga/PROJEKT_Einheitliche_Datei_Komplett_GitHUb.ipynb"
with open(file_path, "r", encoding="utf-8") as f:
    nb = json.load(f)

# Find index of Plot Stephan
insert_idx = -1
for i, cell in enumerate(nb["cells"]):
    if "Stephan" in "".join(cell.get("source", [])):
        insert_idx = i + 1
        break

if insert_idx == -1:
    print("Could not find Plot Stephan")
    exit(1)

new_cells = [
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Datenvorbereitung: Merge mit orders_qu für Zeit- und Umsatzanalysen\n",
            "Um Fragen zu Zeitraum, Gesamtumsatz und Saisonalität zu beantworten, müssen wir das Bestelldatum (`created_date`) und den Bestellstatus (`state`) aus der Tabelle `orders_qu` hinzufügen."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# 1. Merge von orders_qu (enthält created_date und state)\n",
            "df_master = products_and_orderlines_df.merge(orders_qu, left_on='id_order', right_on='order_id', how='inner')\n",
            "\n",
            "# 2. Filtern auf abgeschlossene Bestellungen (sehr wichtig für echten Umsatz!)\n",
            "df_master = df_master[df_master['state'] == 'Completed'].copy()\n",
            "\n",
            "# 3. Datentyp für das Datum konvertieren\n",
            "df_master['created_date'] = pd.to_datetime(df_master['created_date'])\n",
            "\n",
            "# 4. Echten Zeilen-Umsatz berechnen (Menge * bezahlter Einzelpreis)\n",
            "df_master['line_total'] = df_master['product_quantity'] * df_master['unit_price']\n",
            "\n",
            "df_master.head()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Frage 1: Welchen Zeitraum umfasst der Datensatz?\n",
            "### Frage 2: Wie hoch ist der Gesamtumsatz in diesem Zeitraum?"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "min_date = df_master['created_date'].min().strftime('%d.%m.%Y')\n",
            "max_date = df_master['created_date'].max().strftime('%d.%m.%Y')\n",
            "total_revenue = df_master['line_total'].sum()\n",
            "\n",
            "print(f\"--- BUSINESS KPIs ---\")\n",
            "print(f\"Zeitraum: {min_date} bis {max_date}\")\n",
            "print(f\"Gesamtumsatz (abgeschlossene Käufe): {total_revenue:,.2f} €\".replace(',', 'X').replace('.', ',').replace('X', '.'))"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Frage 3: Gibt es saisonale Muster in der Umsatzentwicklung?\n",
            "Wir aggregieren den Umsatz pro Monat, um saisonale Peaks (wie Black Friday und Weihnachten) visuell hervorzuheben."
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "\n",
            "# Umsatz pro Jahr-Monat aggregieren\n",
            "df_master['year_month'] = df_master['created_date'].dt.to_period('M').astype(str)\n",
            "monthly_revenue = df_master.groupby('year_month')['line_total'].sum().reset_index()\n",
            "\n",
            "plt.figure(figsize=(14, 6))\n",
            "sns.set_theme(style=\"whitegrid\")\n",
            "ax = sns.lineplot(data=monthly_revenue, x='year_month', y='line_total', marker='o', color='#2ecc71', linewidth=2.5)\n",
            "\n",
            "# Black Friday / Weihnachten Markierung\n",
            "plt.axvline(x='2017-11', color='#e74c3c', linestyle='--', alpha=0.7)\n",
            "plt.axvline(x='2017-12', color='#e74c3c', linestyle='--', alpha=0.7)\n",
            "plt.text('2017-11', monthly_revenue['line_total'].max() * 0.9, 'Black Friday', color='#e74c3c', rotation=90, va='center', ha='right', fontsize=12)\n",
            "plt.text('2017-12', monthly_revenue['line_total'].max() * 0.9, 'Christmas', color='#e74c3c', rotation=90, va='center', ha='left', fontsize=12)\n",
            "\n",
            "plt.title('Saisonale Umsatzentwicklung (Monatlich)', fontsize=18, fontweight='bold', pad=15)\n",
            "plt.xlabel('Monat', fontsize=12)\n",
            "plt.ylabel('Gesamtumsatz in €', fontsize=12)\n",
            "plt.xticks(rotation=45)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Frage 4: Was sind die meistverkauften Produkte? (Nach Verkaufsmenge)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "top_products_qty = df_master.groupby('name')['product_quantity'].sum().nlargest(10).reset_index()\n",
            "\n",
            "plt.figure(figsize=(12, 6))\n",
            "sns.barplot(data=top_products_qty, y='name', x='product_quantity', palette='Blues_r', hue='name', legend=False)\n",
            "plt.title('Top 10 Meistverkaufte Produkte (Nach Menge)', fontsize=16, fontweight='bold', pad=15)\n",
            "plt.xlabel('Verkaufte Stückzahl', fontsize=12)\n",
            "plt.ylabel('Produktname', fontsize=12)\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    },
    {
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "### Frage 5: Welche Produkte generieren den größten Umsatz? (Nach Euro)"
        ]
    },
    {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "top_products_rev = df_master.groupby('name')['line_total'].sum().nlargest(10).reset_index()\n",
            "\n",
            "plt.figure(figsize=(12, 6))\n",
            "ax = sns.barplot(data=top_products_rev, y='name', x='line_total', palette='Greens_r', hue='name', legend=False)\n",
            "\n",
            "plt.title('Top 10 Umsatzstärkste Produkte (Nach Euro)', fontsize=16, fontweight='bold', pad=15)\n",
            "plt.xlabel('Gesamtumsatz in €', fontsize=12)\n",
            "plt.ylabel('Produktname', fontsize=12)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.show()"
        ]
    }
]

nb["cells"] = nb["cells"][:insert_idx] + new_cells + nb["cells"][insert_idx:]

with open(file_path, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=1)
print(f"Successfully inserted {len(new_cells)} cells into the notebook.")
