import re
import json
import logging
from api import row
from api.services.gemini import Gemini
from api.models import Student, StudentAnswer
from api.services.cloduinary import CloudinaryConfig

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("extract_data")   
gemini = Gemini()

def extract_data(text):
    try:
        logger.debug(f"Texto recebido para extração:\n{text}")

        json_match = re.search(r'\{[\s\S]*\}', text)

        if json_match:
            json_str = json_match.group(0)
            logger.debug(f"Tentando parsear JSON extraído:\n{json_str}")

            try:
                data = json.loads(json_str)
                logger.debug(f"JSON extraído: {data}")

                nome = data.get("Nome", "---")
                turma = data.get("Turma", "---")
                curso = data.get("Curso", "N/A")
                classe_raw = data.get("Classe", "---")
                respostas = data.get("Respostas", {})

                # Limpeza de strings
                nome = re.sub(r'^["\':\s]*|["\':\s,]*$', '', str(nome))
                turma = re.sub(r'^["\':\s]*|["\':\s,]*$', '', str(turma))
                curso = re.sub(r'^["\':\s]*|["\':\s,]*$', '', str(curso))

                # Formatação da classe
                classe_num = re.sub(r"[^\d]", "", str(classe_raw))
                classe_formated = int(classe_num) if classe_num else None

                # Verifica se precisa extrair respostas manualmente
                if not respostas:
                    respostas = {}
                    questao_blocks = re.findall(r"(\d+)[\):.\-–]*([\s\S]*?)(?=(?:\n\d+[\):.\-–])|\Z)", text, re.IGNORECASE)
                    logger.debug(f"Blocos de questões encontrados: {questao_blocks}")
                    for questao_num, bloco in questao_blocks:
                        logger.debug(f"Questão {questao_num} bloco:\n{bloco}")
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
                logger.error(f"Erro ao fazer parse do JSON: {e_json}")

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
        logger.debug(f"Blocos de questões encontrados: {questao_blocks}")
        for questao_num, bloco in questao_blocks:
            logger.debug(f"Questão {questao_num} bloco:\n{bloco}")
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
        logger.error(f"Erro ao extrair dados: {str(e)}")
        return {
            "Nome": "---",
            "Turma": "---",
            "Curso": "N/A",
            "Classe": None,
            "Respostas": {},
            "Erro": f"Erro ao extrair dados: {str(e)}"
        }


def worker_answer(): 
    while True:
        image, response_list, fase = row.get()

        cloudinary_url = CloudinaryConfig.upload_to_cloudinary_student_answer(image)

        if not cloudinary_url:
            response_list.append({"error": "Erro ao fazer upload no Cloudinary"})
            row.task_done()
            continue

        extracted_text = gemini.gemini_output(cloudinary_url)

        if "Erro" in extracted_text:
            response_list.append({"error": extracted_text})
        else:
            data = extract_data(extracted_text)

            student = Student.objects.filter(name=data["Nome"], turma=data["Turma"], grade=data["Classe"]).first()

            if not student:
               student = Student.objects.create(
                        name=data["Nome"],
                        grade=data["Classe"],
                        turma=data["Turma"],
                        course=data["Curso"]
                ) 

            StudentAnswer.objects.create(
                student_id=student.id,
                answer_img_url=cloudinary_url,
                fase=fase,
                answer_matrix=data.get("Respostas", {})
            )

            response_list.append({"message": "Dados salvos com sucesso!", "dados": data})

        row.task_done()