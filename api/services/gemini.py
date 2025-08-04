import json
import os
import base64
import re
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
Você está vendo uma ou mais imagens de uma chave de correção de prova.

Sua tarefa é:
- Identificar todas as QUESTÕES.
- Para cada questão, identificar a alternativa marcada como CORRETA.
- Quando possível, identificar a COTAÇÃO (valor da questão).

 Considere que:
- A alternativa correta pode estar marcada com "X", círculo, sublinhado, ou outra marcação visual.
- As alternativas podem ser A, B, C, D, E — varie conforme o layout.
- As questões podem estar em qualquer formato visual (colunas, linhas, numeração com parênteses, etc).
- Cotações podem aparecer como: “Cotação: 2”, “(1 valor)”, “vale 2 pontos”, ou similares.

 Importante:
- Ignore questões sem marcação clara de resposta.
- Se não encontrar cotação, não inclua o campo.
- NUNCA invente respostas ou valores.
- Formato de saída deve ser estritamente este:

```json
{
  "Respostas": {
    "1": {"resposta": "A", "cotacao": 2},
    "2": {"resposta": "D"},
    "3": {"resposta": "E", "cotacao": 1}
  }
}

"""

            parts = [{"text": prompt}]
            for img_bytes in image_bytes_list:
                image_base64 = base64.b64encode(img_bytes).decode("utf-8")
                parts.append({"mime_type": "image/jpeg", "data": image_base64})

            response = self.__model.generate_content(parts)
            result = response.text

            # 🔎 Extrair JSON do texto
            json_match = re.search(r'{.*}', result, re.DOTALL)
            if not json_match:
                return {"error": "JSON não encontrado na resposta do Gemini."}

            try:
                data = json.loads(json_match.group())
            except Exception as e:
                return {"error": f"Erro ao converter resposta em JSON: {e}"}

            respostas = data.get("Respostas", {})
            if not isinstance(respostas, dict):
                return {"error": "'Respostas' não é um dicionário válido."}

            # ✅ Validação e limpeza
            respostas_validas = {}
            for numero, conteudo in respostas.items():
                letra = conteudo.get("resposta", "").upper()
                cotacao = conteudo.get("cotacao", None)

                if letra in ["A", "B", "C", "D"]:
                    entrada = {"resposta": letra}
                    if isinstance(cotacao, int):
                        entrada["cotacao"] = cotacao
                    respostas_validas[str(numero)] = entrada

            return {"Respostas": respostas_validas}

        except Exception as e:
            return {"error": f"Erro ao extrair chave: {e}"}