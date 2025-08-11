#!/usr/bin/env python3
import subprocess
import sys
import platform
import os

def install_ollama():
    """Install Ollama based on the operating system"""
    system = platform.system().lower()
    
    if system == "darwin":  # macOS
        print("Installing Ollama on macOS...")
        try:
            subprocess.run(["brew", "install", "ollama"], check=True)
            print("Ollama installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install via Homebrew. Please install manually from https://ollama.ai")
            return False
        except FileNotFoundError:
            print("Homebrew not found. Please install Homebrew first or install Ollama manually.")
            return False
    
    elif system == "linux":
        print("Installing Ollama on Linux...")
        try:
            # Download and install Ollama
            subprocess.run([
                "curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"
            ], shell=True, check=True)
            print("Ollama installed successfully!")
        except subprocess.CalledProcessError:
            print("Failed to install Ollama. Please install manually from https://ollama.ai")
            return False
    
    elif system == "windows":
        print("Please install Ollama manually from https://ollama.ai")
        return False
    
    else:
        print(f"Unsupported operating system: {system}")
        return False
    
    return True

def pull_model(model_name="mistral"):
    """Pull the specified model"""
    print(f"Pulling {model_name} model...")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"{model_name} model pulled successfully!")
        return True
    except subprocess.CalledProcessError:
        print(f"Failed to pull {model_name} model")
        return False
    except FileNotFoundError:
        print("Ollama not found. Please install Ollama first.")
        return False

def main():
    """Main installation function"""
    print("Installing TestGenie local model dependencies...")
    
    # Install Ollama
    if not install_ollama():
        sys.exit(1)
    
    # Pull the model
    if not pull_model():
        sys.exit(1)
    
    print("Installation completed successfully!")
    print("You can now use 'test_genie offline generate' to generate tests locally.")

if __name__ == "__main__":
    main() 