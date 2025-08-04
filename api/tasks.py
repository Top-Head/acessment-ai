# api/tasks.py
from celery import shared_task
from api.models import Student, Key, StudentAnswer
from api.services.cloduinary import CloudinaryConfig
from api.services.gemini import Gemini
from api.features import extract_data

@shared_task
def process_student_answer(image_data, fase, key_id):
    gemini = Gemini()
    cloudinary_url = CloudinaryConfig.upload_to_cloudinary_student_answer(image_data)
    if not cloudinary_url:
        return {"error": "Erro ao fazer upload no Cloudinary"}

    extracted_text = gemini.gemini_output(cloudinary_url)
    if "Erro" in extracted_text:
        return {"error": extracted_text}

    data = extract_data(extracted_text)

    student = Student.objects.filter(name=data["Nome"], turma=data["Turma"], grade=data["Classe"]).first()
    if not student:
        student = Student.objects.create(
            name=data["Nome"],
            grade=data["Classe"],
            turma=data["Turma"],
            course=data["Curso"]
        )

    try:
        key_id_int = int(key_id)
    except (TypeError, ValueError):
        return {"error": "ID da chave inválido"}

    key = Key.objects.filter(id=key_id_int).first()
    if not key:
        return {"error": "Chave não encontrada"}

    key_matrix = key.matrix
    student_matrix = data.get("Respostas", {})

    corrects = 0
    wrongs = 0
    nulls = 0
    note = 0

    for q_num, q_data in key_matrix.items():
        student_answer = student_matrix.get(str(q_num), "").strip().lower()
        correct = q_data["resposta"].strip()
        value = q_data["cotacao"]

        if not student_answer:
            nulls += 1
        elif student_answer == correct:
            corrects += 1
            note += value
        else:
            wrongs += 1

    try:
        student_answer_obj = StudentAnswer(
            student=student,
            chave=key,
            answer_matrix=data.get("Respostas", {}),
            answer_img_url=cloudinary_url,
            note=note,
            corrects=corrects,
            wrongs=wrongs,
            nulls=nulls,
            fase=fase
        )
        student_answer_obj.status = student_answer_obj.get_status_from_note()
        student_answer_obj.save()
        return {
            "message": "Dados salvos com sucesso!",
            "student_id": student.id,
            "student_nome": student.name,
            "chave_id": key.id,
            "imagem_url": cloudinary_url,
            "fase": fase,
            "note": note,
            "corretas": corrects,
            "erradas": wrongs,
            "nulas": nulls,
            "respostas": data.get('Respostas', {})
        }
    except Exception as e:
        return {"error": f"Erro ao salvar StudentAnswer: {str(e)}"}