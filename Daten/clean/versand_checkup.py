import pandas as pd 
from pathlib import Path
import numpy as np

############################################################
## Einlesen
df_versand = pd.read_csv("order_sort.csv")
## Zielpfad definieren zum speichern
ziel_pfad = Path("order_sort.csv")
############################################################

ausgabe = df_versand[["order_id", "shipping_cost"]]
print(ausgabe)

#versand = df_versand["shipping_cost"].value_counts()
#print(versand.head(20))

"""
WIE KÖNNTE MAN ES NUN VERFEINFERN
Ähnliche Zahlen wie 5.00 und 4.99 zusammenziehen etc
 - 0.01 und 0.01 zu 0.00  
Negative Werte heraus werfen ab -0.10

"""
df_clean = df_versand[df_versand['shipping_cost'] >= -1.00].copy()
df_clean_dx = df_clean["shipping_cost"].value_counts()
print(df_clean_dx.head(20))
print("===================================")

# 1. Wir definieren eine Liste von Bedingungen
bedingungen = [
    (df_clean['shipping_cost'].between(-1.0, 1.00)),    #frei
    (df_clean["shipping_cost"].between(1.50, 2.49)),    #1.99
    (df_clean["shipping_cost"].between(2.50, 3.49)),    #2.99
    (df_clean["shipping_cost"].between(3.50, 4.49)),    #3.99
    (df_clean['shipping_cost'].between(4.50, 5.50)),    #4.99
    (df_clean["shipping_cost"].between(6.50, 7.50)),    #6.99
    (df_clean["shipping_cost"].between(7.90, 9.40)),    #8.99 
    (df_clean["shipping_cost"].between(9.50, 10.50)),    #9.99
    (df_clean["shipping_cost"].between(11.50, 12.50))   #11.99
]

# 2. Wir definieren, was passieren soll, wenn die Bedingung zutrifft
ergebnisse = [
    0.00,   # Wenn Bedingung 1 zutrifft
    1.99,
    2.99,
    3.99,
    4.99,
    6.99,
    8.99,
    9.99,
    11.99    
]
#3. Alles was nichht definiert ist bleibt
df_clean["shipping_cost"] = np.select(bedingungen, ergebnisse, default=df_clean["shipping_cost"])


#4. Neu Auswerten
print("Ausgabe der neuen Versandkosten::")
"""
dx = df_clean["shipping_cost"].value_counts()
print(dx.head(20))
"""

""" AUSKOMMENTIERT"""
# 3. Anwenden! Alles, was nicht zutrifft, bleibt der alte Wert (default)
df_clean['shipping_cost'] = np.select(bedingungen, ergebnisse, default=0.00)
dx = df_clean["shipping_cost"].value_counts()

print("#########")
print(dx.head(20))
""""""

""" SPEICHER AUSKOMMENTIERT
#####################################
##Speichern
if ziel_pfad.exists():
    entscheidung = input(f"Die Datei '{ziel_pfad.name}' existiert bereits. Überschreiben? (j/n): ")
    if entscheidung.lower() == 'j':
        df_clean.to_csv(ziel_pfad, index=False, float_format='%.2f')
        print("Datei erfolgreich überschrieben.")
    else:
        print("Speichern abgebrochen. Datei wurde NICHT verändert.")
else:
    # Verzeichnis automatisch erstellen, falls es noch nicht existiert
    ziel_pfad.parent.mkdir(parents=True, exist_ok=True)
    df_clean.to_csv(ziel_pfad, index=False, float_format='%.2f')
    print("Datei neu angelegt.")

    """