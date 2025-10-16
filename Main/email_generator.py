import requests
import json
import ollama  # ✅ Přidáno pro komunikaci s Ollama Cloud API

try:
    from config import GEMINI_API_KEY, OLLAMA_API_KEY
except ImportError:
    GEMINI_API_KEY = ""
    OLLAMA_API_KEY = ""

def generate_email_ollama(job):
    """Generuje e-mail přes Ollama API (lokální nebo cloud)"""
    # Zjednodušený prompt
    prompt = f"""Napiš krátký motivační e-mail v češtině pro pozici "{job.heading}". Detaily: {job.text[:300]}"""
    try:
        # Pokus o použití Ollama Cloud API
        if OLLAMA_API_KEY:
            # Použijeme Ollama Cloud API
            client = ollama.Client(
                host="https://ollama.com",
                headers={'Authorization': 'Bearer ' + OLLAMA_API_KEY}
            )
            response = client.generate(model="gpt-oss:120b-cloud", prompt=prompt)
            return response['response']
        else:
            # Použijeme lokální Ollama server
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={"model": "jobautomation/OpenEuroLLM", "prompt": prompt, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            return response.json().get("response", "Nepodařilo se získat odpověď z Ollama.")
    except requests.exceptions.ConnectionError:
        return "Chyba: Nelze se připojit k Ollama. Ujisti se, že server běží na http://localhost:11434 nebo že máš platný API klíč."
    except Exception as e:
        return f"Chyba při komunikaci s Ollama: {e}"

def generate_email_gemini(job, api_key):
    """Generuje e-mail přes Gemini API"""
    # Zjednodušený prompt
    prompt = f"""Napiš krátký motivační e-mail v češtině pro pozici "{job.heading}". Detaily: {job.text[:300]}"""
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(api_url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as http_err:
        # Zpracujeme chybu, aniž bychom ukázali API klíč
        try:
            error_details = response.json()  # response je zde definována, protože jsme v except bloku po requestu
            error_message = error_details.get("error", {}).get("message", "Neznámá chyba API.")
        except (ValueError, AttributeError):
            error_message = "Nezdařilo se zpracovat chybovou odpověď serveru."
        return f"Chyba Gemini API: {error_message}"
    except Exception as e:
        return f"Obecná chyba při volání Gemini API: {e}"

def test_gemini_api(api_key):
    """Otestuje, zda je API klíč pro Gemini platný a zda je dostupný model gemini-2.5-flash."""
    if not api_key:
        return False, "API klíč chybí v souboru config.py."
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash?key={api_key}"
    try:
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            return True, "Připojení je funkční a model gemini-2.5-flash je dostupný."
        else:
            try:
                error_details = response.json()
                error_message = error_details.get("error", {}).get("message", "Neznámá chyba.")
            except (ValueError, AttributeError):
                error_message = "Nezdařilo se zpracovat chybovou odpověď serveru."
            return False, f"Chyba: {error_message}"
    except requests.exceptions.RequestException as e:
        return False, f"Chyba připojení k serveru Google."