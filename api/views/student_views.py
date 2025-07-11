from api.models import Student, StudentAnswer, StatusEnum
from rest_framework import status
from rest_framework.response import Response
from api.serializers import StudentSerializer, StudentUpdateSerializer
from rest_framework.decorators import api_view

@api_view(['PUT'])
def update_student(request, student_id):

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist as e:
        return Response({"error": f"This student not exist: {e}"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)

@api_view(['GET'])
def get_total_students(request):
    total_student = Student.objects.all().count()

    return Response({"total": total_student})

@api_view(['GET'])
def get_students(request):
    students = Student.objects.all()

    infos = StudentSerializer(students, many=True)
    return Response(infos.data, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_reprovados():
    reprovado = StudentAnswer.objects.filter(status=StatusEnum.REPROVADO).count()

    return Response({"total": reprovado}, status=status.HTTP_200_OK)

@api_view(['GET'])
def get_aprovados():
    aprovado = StudentAnswer.objects.filter(status=StatusEnum.APROVADO).count()

    return Response({"total": aprovado}, status=status.HTTP_200_OK)
