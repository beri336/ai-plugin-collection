# Ollama Plugin CLI

## Inhaltsverzeichnis

- [Über das Plugin](#über-das-plugin)
- [Installation](#installation)
- [Klassen und Methoden](#klassen-und-methoden)
  - [OllamaPlugin](#ollamaplugin)
    - [Installation und Systemprüfungen](#installation-und-systemprüfungen)
    - [Service-Management](#service-management)
    - [Modellverwaltung](#modellverwaltung)
    - [KI-Generierung](#ki-generierung)
- [CLI-Interface](#cli-interface)
- [Beispiel zur Nutzung](#beispiel-zur-nutzung)
- [Autoren und Lizenz](#autoren-und-lizenz)

---

## Über das Plugin

Das `Ollama Plugin CLI` ist eine Python-Schnittstelle zur Verwaltung und Interaktion mit Ollama über die Kommandozeile. Es bietet eine CLI-Oberfläche für:

- Installation und Systemprüfung von Ollama
- Service-Management (Start/Stop)
- Modellverwaltung und -übersicht
- KI-Code-Generierung und -Analyse
- Interaktive Menüführung

Das Plugin ist darauf ausgelegt, Ollama-Verwaltungsaufgaben zu vereinfachen und eine intuitive Benutzeroberfläche für alltägliche Ollama-Operationen zu bieten.

## Installation

Das Plugin nutzt ausschließlich Python-Standardbibliotheken:

- `subprocess` für Systemaufrufe
- `platform` für Betriebssystemerkennung
- `sys` für Systeminformationen
- `time` für Wartevorgänge

---

## Klassen und Methoden

### Klasse `OllamaPlugin`

Die Hauptklasse für alle Ollama-Operationen über CLI-Befehle.

---

### Installation und Systemprüfungen

- `is_ollama_installed() -> bool`  
  Prüft, ob das Ollama-Binary installiert ist durch Ausführung von `ollama --version`.
- `install_ollama() -> bool`  
  Installiert Ollama automatisch auf Linux/ macOS über das offizielle Installationsskript.

- `get_ollama_version() -> Optional[str]`  
  Gibt die installierte Ollama-Version zurück.

- `check_is_model_installed() -> bool`  
  Überprüft, ob ein spezifisches Modell installiert ist.

---

### Service-Management

- `is_ollama_running() -> bool`  
  Prüft, ob der Ollama-Service läuft:

  - Linux/ macOS: Verwendet `pgrep -f ollama`
  - Windows: Verwendet `tasklist` und sucht nach `ollama.exe`

- `start_ollama() -> bool`  
  Startet den Ollama-Service über `ollama serve` im Hintergrund.
  Wartet 3 Sekunden und prüft dann den Service-Status.

- `stop_ollama() -> bool`  
  Stoppt den Ollama-Service:
  - macOS: Versucht erst `brew services stop ollama`, dann `pkill -f ollama`
  - Linux: Verwendet `pkill -f ollama`
  - Windows: Nicht implementiert

---

### Modellverwaltung

- `get_models() -> List[str]`  
  Gibt eine Liste aller installierten Modelle zurück über `ollama list`.
  Filtert automatisch Header-Zeilen heraus.

- `get_current_running_models() -> List[str]`  
  Zeigt aktuell laufende/ geladene Modelle über `ollama ps`.
  Gibt die Modellnamen der ersten Spalte zurück.

- `start_running_model() -> bool`  
  Startet ein spezifisches Modell über `ollama run`.

  - Timeout: 60 Sekunden
  - Behandelt "already running" als Erfolg

- `stop_running_model() -> bool`  
  Stoppt ein laufendes Modell über `ollama stop`.

  - Timeout: 20 Sekunden
  - Behandelt "no running model" als erfolgreich gestoppt

- `stop_running_ollama() -> bool`  
  Forciert das Beenden von Ollama-Prozessen für ein Modell:
  - Linux/macOS: Verwendet `pgrep` und `kill -9` für spezifische PIDs
  - Windows: Verwendet `tasklist` und `taskkill /F` für forcierte Beendigung

---

### AI-Generierung

- `send_code_prompt() -> str`  
  Sendet einen Prompt mit Code an ein Ollama-Modell:
  - Ersetzt `{code}` im Prompt mit dem tatsächlichen Code
  - Verwendet `ollama run` mit stdin-Eingabe
  - Timeout: 180 Sekunden (3 Minuten)
  - Unterstützt mehrzeiligen Code

---

## CLI-Interface

### Menüoptionen

Das CLI bietet folgende Optionen:

1. **Ollama Installation prüfen** - Prüft ob Ollama installiert ist
2. **Ollama installieren** - Installiert Ollama automatisch
3. **Ollama läuft?** - Prüft Service-Status
4. **Ollama starten** - Startet den Service
5. **Ollama stoppen** - Stoppt den Service
6. **Ollama Version anzeigen** - Zeigt installierte Version
7. **Modelle anzeigen** - Liste aller installierten Modelle
8. **Laufende Modelle** - Zeigt aktiv geladene Modelle
9. **Prompt + Code** - Sendet Anfragen an Modelle
10. **Starte ein Modell** - Startet spezifisches Modell
11. **Stoppe ein Modell** - Stoppt laufendes Modell graceful
12. **Stoppe Ollama Client** - Forciert Beendigung von Modell-Prozessen
13. **Überprüfe Modell-Installation** - Verifiziert ob Modell installiert ist
14. **Beenden** - Verlässt die CLI

### Eingabeformate

- **Modellname**: Name des zu verwendenden Modells (z.B. `llama3`)
- **Prompt**: Eingabetext mit optionalem `{code}` Platzhalter
- **Code**: Mehrzeliger Code, `\\n` wird zu echten Zeilenumbrüchen konvertiert

---

## Beispiel zur Nutzung

- siehe [Beispielnutzung](Pictures/created-by.svg)

---

## Verwendung

1. **CLI starten**:

```bash
python3 example_usage.py
```

2. **Als Modul verwenden**:

```py
from app import OllamaPlugin

plugin = OllamaPlugin()
if plugin.is_ollama_installed():
    models = plugin.get_models()
    print(f"Modelle: {models}")
```

3. **Installation prüfen und durchführen**:

```py
plugin = OllamaPlugin()

if not plugin.is_ollama_installed():
    print("Installiere Ollama...")
    plugin.install_ollama()

if not plugin.is_ollama_running():
    print("Starte Ollama...")
    plugin.start_ollama()
```

---

## Autoren und Lizenz

**Autor:**

![created-by](/Pictures/created-by.svg)

**Version:** 1.1.0

---

## Hinweise

- Windows-Support ist eingeschränkt
- Lange Operationen (Installation, Modell-Downloads) haben entsprechende Timeouts
- Die CLI unterstützt mehrere Exit-Kommandos: `exit`, `quit`, `q`, `e`

---
