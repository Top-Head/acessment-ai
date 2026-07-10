from api.models import Student, StudentAnswer, Key, StatusEnum
from rest_framework import status
from rest_framework.response import Response
from api.serializers import (
    StudentSerializer,
    StudentUpdateSerializer,
    ExamResultSerializer,
)
from rest_framework.decorators import api_view


@api_view(["PUT"])
def update_student(request, student_id):

    try:
        student = Student.objects.get(id=student_id)
    except Student.DoesNotExist as e:
        return Response(
            {"error": f"This student not exist: {e}"}, status=status.HTTP_404_NOT_FOUND
        )

    serializer = StudentUpdateSerializer(student, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    return Response(serializer.errors, status=status.HTTP_404_BAD_REQUEST)


@api_view(["GET"])
def get_total_students(request):
    total_student = Student.objects.all().count()

    return Response({"total": total_student})


@api_view(["GET"])
def get_students(request):
    students = Student.objects.all()

    infos = StudentSerializer(students, many=True)
    return Response(infos.data, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_reprovados(request):
    reprovado = StudentAnswer.objects.filter(status=StatusEnum.REPROVADO).count()

    return Response({"total": reprovado}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_aprovados(request):
    aprovado = StudentAnswer.objects.filter(status=StatusEnum.APROVADO).count()

    return Response({"total": aprovado}, status=status.HTTP_200_OK)


@api_view(["GET"])
def get_student_exam_results(request):
    key_id = request.query_params.get("key_id")
    fase = request.query_params.get("fase")
    status_filter = request.query_params.get("status")

    queryset = StudentAnswer.objects.select_related("student", "chave").all()

    if key_id:
        queryset = queryset.filter(chave_id=key_id)

    if fase:
        queryset = queryset.filter(fase=fase)

    if status_filter:
        normalized = status_filter.strip().lower()
        if normalized in ("aprovado", "aprovou"):
            queryset = queryset.filter(status=StatusEnum.APROVADO)
        elif normalized in ("reprovado", "reprovou"):
            queryset = queryset.filter(status=StatusEnum.REPROVADO)

    serializer = ExamResultSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
