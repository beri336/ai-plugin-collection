# ai-plugin-collection/Python/OllamaPlugin/example_usage.py

from ollama_plugin import OllamaPlugin

def get_menu_items():
    return [
        ("Ollama Installation prüfen", "is_ollama_installed", []),
        ("Ollama installieren", "install_ollama", []),
        ("Ollama läuft?", "is_ollama_running", []),
        ("Ollama starten", "start_ollama", []),
        ("Ollama stoppen", "stop_ollama", []),
        ("Ollama Version anzeigen", "get_ollama_version", []),
        ("Modelle anzeigen", "get_models", []),
        ("Laufende Modelle", "get_current_running_models", []),
        ("Prompt + Code: Modell, Prompt, Code kombinieren und per CLI schicken", "send_code_prompt", ["Modellname", "Prompt (nutze ggf. {code})", "Code (als Text, mehrzeilig mit \\n)"]),
        
        ("Beenden", "exit", [])
    ]

def print_menu(menu):
    print("\n=== Ollama Plugin CLI Package ===")
    for idx, (desc, _, _) in enumerate(menu, 1):
        print(f"{idx}. {desc}")

def get_user_inputs(inputs):
    user_inputs = []
    for text in inputs:
        user_input = input(f"{text}: ").strip()
        user_inputs.append(user_input)
    return user_inputs

def main():
    ollama = OllamaPlugin()
    menu = get_menu_items()
    
    while True:
        print_menu(menu)
        choice = input("Wähle eine Option (eine Nummer oder 'exit'): ").strip().lower()
        
        if choice in ("exit", "quit", "q", "e", str(len(menu))):
            print("Beende CLI. Bis bald.")
            break
        
        try:
            # convert input to index
            choice_idx = int(choice) - 1
            
            # validate index
            if 0 <= choice_idx < len(menu) - 1:  # -1 due to “exit” option
                desc, method_name, required_inputs = menu[choice_idx]
                print(f"\n--- {desc} ---")
                
                # check whether method exists
                if hasattr(ollama, method_name):
                    method = getattr(ollama, method_name)
                    
                    # collect necessary input from the user
                    if required_inputs:
                        user_inputs = get_user_inputs(required_inputs)
                        
                        # special treatment for code parameters (\\n to real line breaks)
                        if method_name == "send_code_prompt" and len(user_inputs) >= 3:
                            user_inputs[2] = user_inputs[2].replace("\\n", "\n")
                        
                        # execute method with parameters
                        result = method(*user_inputs)
                    else:
                        # execute method without parameters
                        result = method()
                    
                    # show results
                    if result is not None:
                        if isinstance(result, list):
                            print(f"\nErgebnis: {', '.join(map(str, result))}")
                        else:
                            print(f"\nErgebnis: {result}")
                    else:
                        print("\nAktion ausgeführt.")
                    
                else:
                    print(f"Fehler: Methode '{method_name}' nicht im Plugin gefunden!")
                    
            else:
                print("Ungültige Auswahl! Bitte wähle eine Nummer zwischen 1 und {}.".format(len(menu)-1))
                
        except ValueError:
            print("Ungültige Eingabe! Bitte gib eine gültige Nummer ein.")
        except Exception as e:
            print(f"Fehler beim Ausführen der Funktion: {e}")
        
        # pause before the next menu cycle
        input("\nDrücke Enter um zum Menü zurückzukehren...")


if __name__ == "__main__":
    main()
