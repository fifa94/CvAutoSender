import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from WebScraperEasy import JobScraper
from email_generator import generate_email_ollama, generate_email_gemini, test_gemini_api
import threading
import ollama

try:
    from config import GEMINI_API_KEY, OLLAMA_API_KEY
except ImportError:
    GEMINI_API_KEY = ""
    OLLAMA_API_KEY = ""

class GuiScraperApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Job Scraper GUI")
        self.root.geometry("800x600")
        self.urls = []
        self.selected_model = tk.StringVar(value="ollama")

        self.create_widgets()

    def create_widgets(self):
        # Frame pro URL a hlavní tlačítka
        url_frame = ttk.Frame(self.root)
        url_frame.pack(pady=10, fill="x", padx=10)
        ttk.Label(url_frame, text="URL:").pack(side="left", padx=5)
        self.url_entry = ttk.Entry(url_frame)
        self.url_entry.pack(side="left", fill="x", expand=True, padx=5)
        ttk.Button(url_frame, text="+", command=self.add_url).pack(side="left", padx=2)
        ttk.Button(url_frame, text="–", command=self.remove_url).pack(side="left", padx=2)
        ttk.Button(url_frame, text="Scrape", command=self.start_scrape).pack(side="left", padx=2)
        ttk.Button(url_frame, text="Generate Email", command=self.generate_email).pack(side="left", padx=2)
        ttk.Button(url_frame, text="Test Connection", command=self.test_connection).pack(side="left", padx=2)

        # Frame pro výběr modelu
        model_frame = ttk.Frame(self.root)
        model_frame.pack(pady=5, fill="x", padx=10)
        ttk.Label(model_frame, text="Model:").pack(side="left", padx=5)
        ttk.Radiobutton(model_frame, text="Ollama", variable=self.selected_model, value="ollama").pack(side="left", padx=5)
        ttk.Radiobutton(model_frame, text="Gemini 2.5 Flash", variable=self.selected_model, value="gemini").pack(side="left", padx=5)

        # Seznam URL a výstupní pole
        self.url_listbox = tk.Listbox(self.root, height=8)
        self.url_listbox.pack(pady=10, fill="x", padx=10)
        ttk.Label(self.root, text="Výsledky a vygenerovaný e-mail:").pack(pady=5)
        self.output_text = scrolledtext.ScrolledText(self.root, wrap=tk.WORD)
        self.output_text.pack(pady=10, fill="both", expand=True, padx=10)

    def test_connection(self):
        """Testuje připojení k aktuálně vybranému modelu."""
        model = self.selected_model.get()
        self.output_text.insert(tk.END, f"\n--- Testuji připojení k {model.upper()}... ---\n")
        if model == "gemini":
            success, message = test_gemini_api(GEMINI_API_KEY)
            if success:
                self.output_text.insert(tk.END, f"✓ {message}\n")
            else:
                self.output_text.insert(tk.END, f"✗ {message}\n")
        else:  # Ollama
            try:
                # Pokus o použití Ollama Cloud API
                if OLLAMA_API_KEY:
                    # Použijeme Ollama Cloud API
                    client = ollama.Client(
                        host="https://ollama.com",
                        headers={'Authorization': 'Bearer ' + OLLAMA_API_KEY}
                    )
                    response = client.generate(model="gpt-oss:120b-cloud", prompt="Test")
                    if response:
                        self.output_text.insert(tk.END, "✓ Připojení k Ollama je funkční.\n")
                    else:
                        self.output_text.insert(tk.END, "✗ Chyba: Nepodařilo se získat odpověď z Ollama.\n")
                else:
                    # Použijeme lokální Ollama server
                    response = requests.get("http://localhost:11434/api/tags", timeout=10)
                    if response.status_code == 200:
                        self.output_text.insert(tk.END, "✓ Připojení k Ollama je funkční.\n")
                    else:
                        self.output_text.insert(tk.END, f"✗ Chyba: {response.status_code}\n")
            except Exception as e:
                self.output_text.insert(tk.END, f"✗ Chyba při připojení k Ollama: {e}\n")

    def generate_email(self):
        if not hasattr(self, 'last_scraped_jobs') or not self.last_scraped_jobs:
            messagebox.showwarning("Upozornění", "Nejprve proveďte scrapování.")
            return

        model = self.selected_model.get()
        job = self.last_scraped_jobs[0]
        self.output_text.insert(tk.END, f"\n--- Generuji e-mail pomocí {model.upper()}... ---\n")
        threading.Thread(target=self.run_email_generation, args=(job, model), daemon=True).start()

    def run_email_generation(self, job, model):
        email = generate_email_gemini(job, GEMINI_API_KEY) if model == "gemini" else generate_email_ollama(job)
        self.root.after(0, lambda: self.output_text.insert(tk.END, email + "\n"))

    # --- Ostatní metody (beze změny) ---
    def add_url(self):
        url = self.url_entry.get().strip()
        if url: self.urls.append(url); self.url_listbox.insert(tk.END, url); self.url_entry.delete(0, tk.END)
        else: messagebox.showwarning("Upozornění", "Zadejte platnou URL.")

    def remove_url(self):
        selected_index = self.url_listbox.curselection()
        if selected_index: self.urls.pop(selected_index[0]); self.url_listbox.delete(selected_index[0])
        else: messagebox.showwarning("Upozornění", "Vyberte URL k odstranění.")

    def start_scrape(self):
        if not self.urls: messagebox.showwarning("Upozornění", "Nejprve přidejte alespoň jednu URL."); return
        threading.Thread(target=self.scrape, daemon=True).start()

    def scrape(self):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, "Scrapování zahájeno...\n")
        scraper = JobScraper(self.urls, delay=1.5)
        results = scraper.scrape_all()
        for job in results: self.output_text.insert(tk.END, f"\nURL: {job.url}\nHeading: {job.heading}\n" + "-" * 80 + "\n")
        self.output_text.insert(tk.END, "\nScrapování dokončeno.\n")
        self.last_scraped_jobs = results

if __name__ == "__main__":
    root = tk.Tk()
    app = GuiScraperApp(root)
    root.mainloop()
