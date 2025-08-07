# ai-plugin-collection/Python/OllamaPlugin/ollama_plugin.py

import sys
import time
import subprocess
import platform
from typing import Dict, List, Optional, Any


# === Plugin for Ollama ===
class OllamaPlugin:
    # === Installation & System Checks
    def is_ollama_installed(self) -> bool:
        try:
            # try executing `ollama --version` command
            res = subprocess.run(
                ["ollama", "--version"], 
                capture_output=True, 
                text=True, 
                timeout=10
            )
            
            if res.returncode == 0:
                print("Ollama Binary found.")
                return True
            else:
                print("Ollama Binary not found or incorrect.")
                return False
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError) as e:
            print(f"Error checking Ollama installation: {e}")
            return False

    def install_ollama(self) -> bool:
        try:
            time = 300
            system = platform.system().lower()
            print(f"Starte Ollama Installation für {system}")
            
            if system == "linux" or system == "darwin":  # darwin = macOS
                # download & install for Unix-systems
                install_script = "curl -fsSL https://ollama.ai/install.sh | sh"
                res = subprocess.run(
                    install_script,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=time  # 5 minutes timeout
                )
                
                if res.returncode == 0:
                    print("Ollama installed successfully.")
                    return True
                else:
                    print(f"Installation failed: {res.stderr}")
                    return False
        except subprocess.TimeoutExpired:
            print(f"Installation timeout – The installation took too long ({time} min).")
            return False
        except Exception as e:
            print(f"Unexpected error during installation: {e}")
            return False

    def is_ollama_running(self) -> bool:
        try:
            # Unix-like (Linux/Mac)
            if sys.platform.startswith("linux") or sys.platform == "darwin":
                result = subprocess.run(
                    ["pgrep", "-f", "ollama"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            # Windows
            elif sys.platform.startswith("win"):
                result = subprocess.run(
                    ["tasklist"], capture_output=True, text=True
                )
                return "ollama.exe" in result.stdout.lower()
            else:
                # unsupported system
                return False
        except Exception as e:
            # error searching for the process
            return False

    def start_ollama(self) -> bool:
        try:
            print("Starting Ollama Service...")
            
            # try starting Ollama via `ollama serve`
            process = subprocess.Popen(
                ["ollama", "serve"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # wait a moment and check whether the service is running
            time.sleep(3)
            
            if self.is_ollama_running():
                print("Ollama service successfully launched.")
                return True
            else:
                print("Ollama Service could not be started.")
                return False
                
        except Exception as e:
            print(f"Error starting the Ollama service: {e}")
            return False

    def stop_ollama(self) -> bool:
        try:
            system = platform.system().lower()
            # macOS with homebrew
            if system == "darwin":
                # stop homebrew-service
                result = subprocess.run(
                    ["brew", "services", "stop", "ollama"],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    print("Ollama Brew service stopped.")
                    return True
                
                result = subprocess.run(
                    ["pkill", "-f", "ollama"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            elif system == "linux":
                result = subprocess.run(
                    ["pkill", "-f", "ollama"],
                    capture_output=True,
                    text=True
                )
                return result.returncode == 0
            else:
                print("Stop not implemented for this platform.")
                return False
        except Exception as e:
            print(f"Error stopping the Ollama service: {e}")
            return False

    def get_ollama_version(self) -> Optional[str]:
        try:
            res = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if res.returncode == 0:
                version = res.stdout.strip()
                print(f"Ollama Version: {version}")
                return version
            else:
                print(f"Error retrieving version: {res.stderr}")
                return None
                
        except Exception as e:
            print(f"Error retrieving Ollama version: {e}")
            return None

    # === Model Management
    def get_models(self) -> List[Dict[str, Any]]:
        try:
            res = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=3
            )
            
            if res.returncode != 0:
                return []
            
            models = []
            for line in res.stdout.splitlines():
                if line.strip() and not line.startswith("NAME"):
                    model_name = line.split()[0]
                    if model_name:
                        models.append(model_name)
            
            print(f"Found models: {models}")
            return models
        
        except Exception as e:
            print(f"Error retrieving models: {e}")
            return []

    def get_current_running_models(self) -> List[str]:
        try:
            # exeecute command
            result = subprocess.run(
                ["ollama", "ps"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                print(f"'ollama ps' error: {result.stderr.strip()}")
                return []
            
            output = result.stdout.strip()
            if not output:
                return []
            
            lines = output.splitlines()
            print(lines)
            if len(lines) < 2:
                return []
            
            model_names = []
            for line in lines[1:]:
                parts = line.split()
                if parts:
                    model_names.append(parts[0])
            
            print(f"Current models found: {model_names}")
            return model_names
            
        except subprocess.TimeoutExpired:
            print("'ollama ps' Timeout expired.")
        except FileNotFoundError:
            print("'ollama' command not found – Ollama may not be installed or may not be in your PATH.")
        except Exception as e:
            print(f"Error with 'ollama ps': {e}")
        
        return []

    # === AI Generation
    def send_code_prompt(self, model: str, prompt: str, code: str) -> str:
        try:
            # assemble promptly
            if "{code}" in prompt:
                full_prompt = prompt.replace("{code}", code)
            else:
                full_prompt = f"{prompt}\n\nCode:\n``````"
            # start ollama run <model> and enter the prompt via stdin
            process = subprocess.Popen(
                ["ollama", "run", model],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate(input=full_prompt, timeout=180)
            if process.returncode == 0:
                return stdout.strip()
            else:
                print(f"Error with 'ollama run': {stderr}")
                return ""
        except Exception as e:
            print(f"Error with 'ollama run': {e}")
            return ""
