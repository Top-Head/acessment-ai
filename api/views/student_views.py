import json
from api.models import Student
from rest_framework import status
from rest_framework.response import Response
from api.serializers import StudentUpdateSerializer
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
    student = Student.objects.all().count()

    return Response({"total": student})