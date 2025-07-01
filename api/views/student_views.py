from api.models import Student
from rest_framework import status
from rest_framework.response import Response
from api.serializers import StudentSerializer
from rest_framework.decorators import api_view

@api_view(['PUT'])
def update_student(request, student_id):

    try:
        student = Student.objects.filter(id=student_id)
    except Student.DoesNotExist as e:
        return Response({"error": f"This student not exist: {e}"}, status=status.HTTP_404_NOT_FOUND)
    
    serializer = StudentSerializer(student)

    return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

