import re
import json

def extract_data(text: str) -> dict:
    try:
        json_match = re.search(r'\{[\s\S]*\}', text)

        if json_match:
            json_str = json_match.group(0)

            try:
                data = json.loads(json_str)

                nome = data.get("Nome", "---")
                turma = data.get("Turma", "---")
                curso = data.get("Curso", "N/A")
                classe_raw = data.get("Classe", "---")
                respostas = data.get("Respostas", {})

                nome = re.sub(r'^["\':\s]*|["\':\s,]*$', '', str(nome))
                turma = re.sub(r'^["\':\s]*|["\':\s,]*$', '', str(turma))
                curso = re.sub(r'^["\':\s]*|["\':\s,]*$', '', str(curso))

                classe_num = re.sub(r"[^\d]", "", str(classe_raw))
                classe_formated = int(classe_num) if classe_num else None

                if not respostas:
                    respostas = {}
                    questao_blocks = re.findall(r"(\d+)[\):.\-–]*([\s\S]*?)(?=(?:\n\d+[\):.\-–])|\Z)", text, re.IGNORECASE)
                    for questao_num, bloco in questao_blocks:
                        alternativa_marcada = re.search(r"([a-dA-D])\)\s*[xX]", bloco)
                        if alternativa_marcada:
                            respostas[questao_num] = alternativa_marcada.group(1).upper()

                return {
                    "Nome": nome,
                    "Turma": turma,
                    "Curso": curso,
                    "Classe": classe_formated,
                    "Respostas": respostas
                }

            except Exception as e_json:
                return {"error": f"{e_json}"}

        nome = re.search(r"(?i)Nome[:\s]*([^\n\r]+)", text)
        turma = re.search(r"(?i)Turma[:\s]*([^\n\r]+)", text)
        curso = re.search(r"(?i)Curso[:\s]*([^\n\r]+)", text)
        classe = re.search(r"(?i)Classe[:\s]*([^\n\r]+)", text)

        nome_val = nome.group(1).strip() if nome else "---"
        turma_val = turma.group(1).strip() if turma else "---"
        curso_val = curso.group(1).strip() if curso else "N/A"

        nome_val = re.sub(r'^["\':\s]*|["\':\s,]*$', '', nome_val)
        turma_val = re.sub(r'^["\':\s]*|["\':\s,]*$', '', turma_val)
        curso_val = re.sub(r'^["\':\s]*|["\':\s,]*$', '', curso_val)

        if classe:
            classe_val = classe.group(1).strip()
            classe_num = re.sub(r"[^\d]", "", classe_val)
            classe_formated = int(classe_num) if classe_num else None
        else:
            classe_formated = None

        respostas = {}
        questao_blocks = re.findall(r"(\d+)[\):.\-–]*([\s\S]*?)(?=(?:\n\d+[\):.\-–])|\Z)", text, re.IGNORECASE)
        for questao_num, bloco in questao_blocks:
            alternativa_marcada = re.search(r"([a-dA-D])\)\s*[xX]", bloco)
            if alternativa_marcada:
                respostas[questao_num] = alternativa_marcada.group(1).upper()

        return {
            "Nome": nome_val,
            "Turma": turma_val,
            "Curso": curso_val,
            "Classe": classe_formated,
            "Respostas": respostas
        }

    except Exception as e:
        return {
            "Nome": "---",
            "Turma": "---",
            "Curso": "N/A",
            "Classe": None,
            "Respostas": {},
            "Erro": f"Erro ao extrair dados: {str(e)}"}       