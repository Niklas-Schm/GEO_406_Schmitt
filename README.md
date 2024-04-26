# Einleitung:

Der nachfolgende Bericht dokumentiert die Entwicklung einer web-basierten
Software zur Verwaltung von Zeitreihendaten unter Verwendung von Python, 
Flask und Dash. Ziel des Projektes war die Implementierung verschiedener 
Funktionen, darunter die Benutzerverwaltung, Visualisierung von Daten, 
statistische Analysen und die Bereitstellung einer Downloadfunktion. 
Dieser Bericht beschreibt die umgesetzten Features sowie die Erfüllung 
der definierten Projektziele. Zur Umsetzung dieses Projekts wurde Python 
3.12, PyCharm 2024.1 (Community Edition) und GitHub genutzt.

## Installationsanleitung:

Die benötigten Dateien stehen in der Uni-Cloud unter [diesem Link](https://cloud.uni-jena.de/s/EwPqQWKJqjQ4yC3) zum
Download zur Verfügung. Zudem steht ein GitHub Repository zur Verfügung unter
[diesem Link](https://github.com/Niklas-Schm/GEO_406_Schmitt). Nachdem der Ordner `GEO_406_Schmitt` heruntergeladen und 
entpackt wurde, muss ein passendes Python Environment erstellt werden. Hierzu
wird die Datei `GEO_406_Schmitt.yml` genutzt. Nun muss ein passendes 
Environment in Anaconda erstellt werden:


Die Ordnerstruktur des Projekts darf nicht verändert werden und soll wie in Abbildung 1 dargestellt aussehen.

![image](https://github.com/Niklas-Schm/GEO_406_Schmitt/assets/105650987/d44e73b9-f8cf-4100-9355-d3e2062f11b4)

**Abbildung 1: Ordnerstruktur**

Nach erfolgreichem Erstellen des Environments und Setup der Ordnerstruktur kann das Vorbereiten der Daten beginnen. Hierzu muss das Skript `data_preprocessing.py` ausgeführt werden. Dieses Skript erstellt die Datenbankdatei `GEO_406.db` und liest die Pegeldaten sowie die Metadaten in die Datenbank ein. Nach diesem Schritt ist die Installation abgeschlossen und die App kann gestartet werden. Hierzu wird das Skript `GEO_406_Schmitt.py` ausgeführt.

