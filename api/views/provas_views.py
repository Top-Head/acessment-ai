from rest_framework import status
from api.tasks import process_student_answer
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def upload_images(request):
    if 'image' not in request.FILES:
        return Response({"error": "Nenhuma imagem enviada"}, status=status.HTTP_400_BAD_REQUEST)
    
    fase = request.POST.get('fase')
    key_id = request.POST.get('key')

    if not fase:
        return Response({"error": "Campo 'fase' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

    images = request.FILES.getlist('image')

    for image in images:
        process_student_answer.delay(image.read(), fase, key_id)

    return Response({"message": "Imagens enviadas para processamento!"}, status=status.HTTP_201_CREATED)
