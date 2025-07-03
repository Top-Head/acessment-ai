import os
import base64
import requests
from dotenv import load_dotenv
import google.generativeai as gemini

load_dotenv()

class Gemini:
    def __init__(self):
        self.__model = gemini.GenerativeModel("gemini-1.5-flash")
        gemini.configure(api_key=os.getenv('GOOGLE_API_KEY'))

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
                            "2": "D",
                            ...
                        }
                        }

                        - Nas respostas, a alternativa marcada é a que tem um "X" ou outro símbolo.
                        - Apenas uma alternativa por questão.
                        - Ignore questões não respondidas.
            """

            response = self.__model.generate_content([user_prompt, {"mime_type": "image/jpeg", "data": image_data}])

            if not response or not response.text.strip():
                return "Erro: Resposta vazia do Gemini"

            return response.text

        except Exception as e:
            return f"Erro ao processar a imagem: {e}"