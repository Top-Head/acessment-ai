import os
import base64
import json
import re
import requests
from dotenv import load_dotenv
from groq import Groq as GroqClient

load_dotenv()


class Groq:
    """Extrai dados do aluno a partir da imagem da folha de prova."""

    def __init__(self):
        self.__client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))

    def groq_output(self, image_url):
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

- Nas respostas, a alternativa marcada é a que tem um "X", bolinha, ponto ou outro símbolo.
- Apenas uma alternativa por questão.
- Ignore questões não respondidas.
- Responde APENAS com o JSON, sem texto adicional.
"""

            response = self.__client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_data}"
                                },
                            },
                            {"type": "text", "text": user_prompt},
                        ],
                    }
                ],
                temperature=0,
            )

            result = response.choices[0].message.content
            if not result or not result.strip():
                return "Erro: Resposta vazia do Groq"

            return result

        except Exception as e:
            return f"Erro ao processar a imagem: {e}"


class GroqKeyExtractor:
    """Extrai a chave de correção (respostas correctas + cotações) a partir das imagens."""

    def __init__(self):
        self.__client = GroqClient(api_key=os.getenv("GROQ_API_KEY"))

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
- Cotações podem aparecer como: "Cotação: 2", "(1 valor)", "vale 2 pontos", ou similares.

Importante:
- Ignore questões sem marcação clara de resposta.
- Se não encontrar cotação, não inclua o campo.
- NUNCA invente respostas ou valores.
- Responde APENAS com o JSON abaixo, sem texto adicional, sem markdown:

{
  "Respostas": {
    "1": {"resposta": "A", "cotacao": 2},
    "2": {"resposta": "D"},
    "3": {"resposta": "E", "cotacao": 1}
  }
}
"""

            content = [{"type": "text", "text": prompt}]

            for img_bytes in image_bytes_list:
                image_base64 = base64.b64encode(img_bytes).decode("utf-8")
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                    }
                )

            response = self.__client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{"role": "user", "content": content}],
                temperature=0,
            )

            result = response.choices[0].message.content

            json_match = re.search(r"\{.*\}", result, re.DOTALL)
            if not json_match:
                return {"error": "JSON não encontrado na resposta do Groq."}

            try:
                data = json.loads(json_match.group())
            except Exception as e:
                return {"error": f"Erro ao converter resposta em JSON: {e}"}

            respostas = data.get("Respostas", {})
            if not isinstance(respostas, dict):
                return {"error": "'Respostas' não é um dicionário válido."}

            # Validação e limpeza
            respostas_validas = {}
            for numero, conteudo in respostas.items():
                letra = conteudo.get("resposta", "").upper()
                cotacao = conteudo.get("cotacao", None)

                if letra in ["A", "B", "C", "D", "E"]:
                    entrada = {"resposta": letra}
                    if isinstance(cotacao, (int, float)):
                        entrada["cotacao"] = cotacao
                    respostas_validas[str(numero)] = entrada

            return {"Respostas": respostas_validas}

        except Exception as e:
            return {"error": f"Erro ao extrair chave: {e}"}
