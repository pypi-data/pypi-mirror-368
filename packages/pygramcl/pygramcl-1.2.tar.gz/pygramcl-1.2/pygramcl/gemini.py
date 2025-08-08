import google.generativeai as gemini_ai

class Gemini:
    
    def __init__(self, api_key: str, model_name: str = 'gemini-2.0-flash'):
        self.gemini_ai = gemini_ai
        self.gemini_ai.configure(api_key=api_key)
        self.gemini = self.gemini_ai.GenerativeModel(model_name=model_name)

    def chat(self, prompt: str) -> str:
        try:
            output = self.gemini.generate_content(prompt)
            return output.text.strip()
        except Exception:
            return None