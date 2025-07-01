import threading
from api import row, threads
from rest_framework import status
from api.features import worker_answer
from rest_framework.response import Response
from api.models import StudentAnswer, Student
from rest_framework.decorators import api_view

for _ in range(5):
    t = threading.Thread(target=worker_answer, daemon=True)
    t.start()
    threads.append(t)

@api_view(['POST'])
def upload_images(request):
    if 'image' not in request.FILES:
        return Response({"error": "Nenhuma imagem enviada"}, status=status.HTTP_400_BAD_REQUEST)
    
    fase = request.POST.get('fase')
    
    if not fase:
        return Response({"error": "Campo 'fase' é obrigatório"}, status=status.HTTP_400_BAD_REQUEST)

    images = request.FILES.getlist('image')
    response_list = []

    for image in images:
        row.put((image, response_list, fase))

    row.join()

    return Response(response_list, status=status.HTTP_201_CREATED)
