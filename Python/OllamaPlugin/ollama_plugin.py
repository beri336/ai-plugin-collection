# ai-plugin-collection/Python/OllamaPlugin/ollama_plugin.py

# === Built-in Dependencies
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

    def start_running_model(self, model: str) -> bool:
        try:
            result = subprocess.run(
                ["ollama", "run", model],
                capture_output=True,
                text=True,
                timeout=60  # increase sufficiently if necessary
            )
            if result.returncode == 0:
                return True
            else:
                # if the model is already loaded, for example, the CLI may return an error, but can still be considered “started.”
                if "already running" in result.stderr.lower():
                    return True
                return False
        except Exception as e:
            print("Error during execution – e.g. incorrect model name, CLI not in the path, etc.")
            return False

    def stop_running_model(self, model: str) -> bool:
        try:
            result = subprocess.run(
                ["ollama", "stop", model],
                capture_output=True,
                text=True,
                timeout=20
            )
            if result.returncode == 0:
                # successfully stopped
                return True
            else:
                # model may not exist, continue processing error log
                if "no running model" in result.stderr.lower():
                    # model was already inactive -> considered successfully stopped
                    return True
                # other error
                return False
        except Exception as e:
            print(f"Error executing command to stop {model}.")
            return False

    def stop_running_ollama(self, model: str) -> bool:
        try:
            # Unix/Linux/macOS: find and kill the ollama process that is using the model
            if sys.platform.startswith("linux") or sys.platform == "darwin":
                # find process ID(s) with the model name in the command
                ps = subprocess.run(
                    ["pgrep", "-f", f"ollama.*{model}"],
                    capture_output=True, text=True
                )
                if ps.returncode != 0:
                    # no process found
                    return True
                pids = [pid for pid in ps.stdout.split() if pid.isdigit()]
                for pid in pids:
                    subprocess.run(["kill", "-9", pid])
                return True if pids else False

            # Windows: taskkill for processes containing model names
            elif sys.platform.startswith("win"):
                result = subprocess.run(
                    ["tasklist"], capture_output=True, text=True
                )
                # search for lines that match ollama.exe and model names
                matching = [line for line in result.stdout.splitlines()
                            if "ollama.exe" in line.lower() and model.lower() in line.lower()]
                if matching:
                    # force quit all related processes
                    for line in matching:
                        columns = line.split()
                        if columns:
                            pid = columns[1]
                            subprocess.run(["taskkill", "/PID", pid, "/F"])
                    return True
                else:
                    return True  # no model process found - considered closed
            else:
                print("Unsupported system.")
                return False
        except Exception as e:
            print("Errors when stopping (e.g., permissions or subprocess errors).")
            return False

    def check_is_model_installed(self, model: str) -> bool:
        return model in self.get_models()


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
