import os
import base64
import requests
from dotenv import load_dotenv
import google.generativeai as gemini

load_dotenv()

gemini.configure(api_key=os.getenv('GOOGLE_API_KEY'))

class Gemini:
    def __init__(self):
        self.__model = gemini.GenerativeModel("gemini-1.5-flash")

    def gemini_output(self, image_url):
        try:
            response = requests.get(image_url)
            if response.status_code != 200:
                return "Erro: Falha ao baixar a imagem do Cloudinary"

            image_data = base64.b64encode(response.content).decode("utf-8")

            user_prompt = """
Extraia APENAS as seguintes informações da imagem:

1. Nome do aluno
2. Classe
3. Turma
4. Curso
5. Respostas do aluno (número da questão e alternativa marcada)

**IMPORTANTE:**
- O formato de saída DEVE ser neste exato JSON:

{
  "Nome": "[Nome do aluno]",
  "Classe": [Número da classe, ex: 13],
  "Turma": "[Letra da turma]",
  "Curso": "[Curso do aluno]",
  "Respostas": {
    "1": "A",
    "2": "D"
  }
}

- Nas respostas, a alternativa marcada é a que tem um "X" ou outro símbolo.
- Apenas uma alternativa por questão.
- Ignore questões não respondidas.
"""
            result = self.__model.generate_content([
                user_prompt,
                {"mime_type": "image/jpeg", "data": image_data}
            ])

            if not result or not result.text.strip():
                return "Erro: Resposta vazia do Gemini"

            return result.text

        except Exception as e:
            return f"Erro ao processar a imagem: {e}"

class GeminiKeyExtractor:
    def __init__(self):
        gemini.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        self.__model = gemini.GenerativeModel("gemini-1.5-flash")

    def extract(self, image_bytes_list):
        try:
            prompt = """
Extraia da imagem de uma chave de correção de prova apenas as alternativas que estão marcadas com (x). 

IMPORTANTE:
- Cada questão tem 4 alternativas: A, B, C e D.
- Marcação correta é aquela com um símbolo **(x)** ao lado da letra.
- Ignore totalmente o conteúdo das alternativas.
- Foque **apenas** na letra onde o símbolo (x) está presente.
- Não considere nada sublinhado, em negrito ou com outros símbolos que não sejam (x).
- A cotação está abaixo ou ao lado da pergunta: ex: "Cotação: 1".
- Se a cotação **não aparecer**, **não coloque nada**.
- Ignore questões sem marcação.
- Retorne no formato JSON puro, como:

{
  "Respostas": {
    "1": {"resposta": "C", "cotacao": 1},
    "2": {"resposta": "D"},
    "3": {"resposta": "A", "cotacao": 2}
  }
}

"""
            parts = [{"text": prompt}]
            for img_bytes in image_bytes_list:
                image_base64 = base64.b64encode(img_bytes).decode("utf-8")
                parts.append({"mime_type": "image/jpeg", "data": image_base64})

            response = self.__model.generate_content(parts)
            return response.text

        except Exception as e:
            return f"Erro ao extrair chave: {e}"