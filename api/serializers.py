from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from api.models import User, Student, Key, StudentAnswer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = ['id', 'student', 'answer_img_url', 'note', 'fase']

class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name']

class StudentSerializer(serializers.ModelSerializer):
    test = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Student
        fields = ['id', 'name', 'grade', 'turma', 'course', 'category', 'test']

class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = '__all__'
        read_only_fields = ['matrix', 'created_at']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Torna todos os campos opcionais (exceto os read_only)
        for field in self.fields:
            if field not in self.Meta.read_only_fields:
                self.fields[field].required = False
