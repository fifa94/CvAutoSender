import unittest
import requests
from email_generator import generate_email_ollama, generate_email_gemini, test_gemini_api

# Zde můžeš nastavit testovací data
TEST_JOB_HEADING = "Testovací pozice"
TEST_JOB_TEXT = "Testovací popis pozice, který je dost dlouhý, aby se vešel do prvních 500 znaků."

class TestEmailGenerator(unittest.TestCase):

    def test_generate_email_ollama(self):
        """Testuje, zda funkce generate_email_ollama vrací řetězec."""
        # Vytvoříme fiktivní JobPosting objekt
        class MockJob:
            def __init__(self, heading, text):
                self.heading = heading
                self.text = text

        job = MockJob(TEST_JOB_HEADING, TEST_JOB_TEXT)
        result = generate_email_ollama(job)
        self.assertIsInstance(result, str, "Výsledek musí být řetězec.")
        # Pokud je Ollama dostupná, výsledek by neměl být chybová zpráva
        if "Chyba" not in result and "Nepodařilo se" not in result:
            self.assertGreater(len(result), 10, "E-mail by měl být delší než 10 znaků.")

    def test_generate_email_gemini(self):
        """Testuje, zda funkce generate_email_gemini vrací řetězec."""
        # Vytvoříme fiktivní JobPosting objekt
        class MockJob:
            def __init__(self, heading, text):
                self.heading = heading
                self.text = text

        job = MockJob(TEST_JOB_HEADING, TEST_JOB_TEXT)
        # Použijeme prázdný API klíč, aby se testovalo chybové chování
        result = generate_email_gemini(job, "")
        self.assertIsInstance(result, str, "Výsledek musí být řetězec.")
        # Očekáváme chybovou zprávu
        self.assertIn("Chyba", result, "Při prázdném API klíči by měla být chybová zpráva.")

    def test_test_gemini_api(self):
        """Testuje, zda funkce test_gemini_api vrací správný typ výstupu."""
        # Test s prázdným API klíčem
        success, message = test_gemini_api("")
        self.assertIsInstance(success, bool, "První návratová hodnota musí být bool.")
        self.assertIsInstance(message, str, "Druhá návratová hodnota musí být řetězec.")
        self.assertFalse(success, "S prázdným API klíčem by měl být success False.")

        # Test s neplatným API klíčem (pokud máš přístup k internetu)
        # success, message = test_gemini_api("neplatny_klic")
        # self.assertFalse(success, "S neplatným API klíčem by měl být success False.")

if __name__ == "__main__":
    unittest.main()