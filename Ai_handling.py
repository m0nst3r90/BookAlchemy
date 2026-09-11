import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

def ai_available():
	return bool(os.getenv("GEMINI_API_KEY"))


def get_recommendation(books_json):
	api_key = os.getenv("GEMINI_API_KEY")

	if not api_key:
		return None

	client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

	prompt = f"""
	Du bekommst eine JSON-Liste mit Büchern aus meiner persönlichen Bibliothek.

	Wähle genau ein Buch aus und empfehle es mir. Du darfst dein allgemeines Wissen über die Bücher verwenden, um die Empfehlung zu begründen.

	Bewertungen:
	- Eine Bewertung existiert ausschließlich dann, wenn beim Buch das Feld "rating" vorhanden ist.
	- Das Rating verwendet eine Skala von 1 bis 10.
	- Erfinde niemals Bewertungen.
	- Verwende keine Bewertungen von Goodreads, Amazon oder anderen externen Quellen.
	- Wenn kein Buch ein "rating"-Feld besitzt, erwähne in deiner Antwort überhaupt keine Bewertung.
	- Wenn Ratings vorhanden sind, darfst du sie bei deiner Entscheidung berücksichtigen.
	- Wenn du ein Rating erwähnst, verwende exakt den Wert aus der JSON.

	Wähle ausschließlich ein Buch aus der bereitgestellten Liste.

	Antworte ausschließlich als gültiges JSON in diesem Format:
	{{
	    "book_id": 1,
	    "text": "Kurze Begründung für die Empfehlung."
	}}

	Bücher:
	{json.dumps(books_json, ensure_ascii=False)}
	"""

	try:
		response = client.models.generate_content(
			model="gemini-3.8-flash",
			contents=prompt
		)

		content = response.text.strip()

		if content.startswith("```json"):
			content = content[7:]
		elif content.startswith("```"):
			content = content[3:]

		if content.endswith("```"):
			content = content[:-3]

		return json.loads(content.strip())

	except Exception as error:
		print("Gemini Fehler:", error)
		return None
