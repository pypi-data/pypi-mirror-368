#!/usr/bin/env python3
import subprocess
import requests
import json
import time
import sys
from typing import Optional

def start_ollama_server():
    """Start the Ollama server"""
    print("Starting Ollama server...")
    try:
        # Start Ollama in the background
        process = subprocess.Popen(["ollama", "serve"], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        
        # Wait a moment for the server to start
        time.sleep(2)
        
        # Check if server is running
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                print("Ollama server started successfully!")
                return process
        except requests.RequestException:
            print("Failed to connect to Ollama server")
            return None
            
    except FileNotFoundError:
        print("Ollama not found. Please install Ollama first.")
        return None
    except Exception as e:
        print(f"Error starting Ollama server: {e}")
        return None

def query_model(prompt: str, model: str = "mistral") -> Optional[str]:
    """Query the local Ollama model"""
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "")
        else:
            print(f"Error querying model: {response.status_code}")
            return None
            
    except requests.RequestException as e:
        print(f"Error connecting to Ollama: {e}")
        return None

def main():
    """Main function to run the model server"""
    if len(sys.argv) < 2:
        print("Usage: python run.py [start|query]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "start":
        process = start_ollama_server()
        if process:
            try:
                # Keep the server running
                process.wait()
            except KeyboardInterrupt:
                print("\nShutting down Ollama server...")
                process.terminate()
    
    elif command == "query":
        if len(sys.argv) < 3:
            print("Usage: python run.py query <prompt>")
            sys.exit(1)
        
        prompt = sys.argv[2]
        response = query_model(prompt)
        if response:
            print(response)
        else:
            print("Failed to get response from model")
    
    else:
        print("Unknown command. Use 'start' or 'query'")

if __name__ == "__main__":
    main() 