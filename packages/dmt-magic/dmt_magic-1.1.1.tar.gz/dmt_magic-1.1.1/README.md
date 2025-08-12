# DMT-Magic

DMT-Magic ist eine IPython-Erweiterung, die das Jupyter Magic Command **dmt** zur Verfügung stellt, mit dem das E-Assessment-Tool DMT (Data Management Tester) an Notebooks angebunden werden kann.

## Initialisiserung im Jupyter Notebook 

- ``%load_ext dmt`` zum Laden der Erweiterung
- ``%dmt url=<url>`` zur Angabe der URL, unter der die Instanz von DMT erreichbar ist

## Aufruf einer Aufgabe

- ``%dmt <taskid>`` (Line Magic) zur Darstellung einer Aufgabe (referenziert über TaskId)
- ``%%dmt <taskid>`` (Cell Magic) zur Übergabe des Zellinhalts als Nutzerlösung
