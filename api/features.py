import re
from api import row
from api.services.gemini import Gemini
from api.models import Student, StudentAnswer
from api.services.cloduinary import CloudinaryConfig

gemini = Gemini()

def extract_data(text):
    nome = re.search(r"(?i)Nome[:\s]*(.+)", text)
    classe = re.search(r"(?i)Classe[:\s]*(.+)", text)
    turma = re.search(r"(?i)Turma[:\s]*(.+)", text)
    curso = re.search(r"(?i)Curso[:\s]*(\d+)", text)

    if classe:
        classe_val = classe.group(1).strip()
        classe_num = re.sub(r"[^\d]", "", classe_val)
        classe_formated = int(classe_num) if classe_num else "---"
    else:
        classe_formated = "---"

    return {
        "Nome": nome.group(1).strip() if nome else "---",
        "Classe": classe_formated,
        "Turma": turma.group(1).strip() if turma else "---",
        "Curso": curso.group(1).strip() if curso else "N/A"
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
                fase=fase
            )

            response_list.append({"message": "Dados salvos com sucesso!", "dados": data})

        row.task_done()