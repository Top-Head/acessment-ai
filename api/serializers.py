from rest_framework import serializers
from api.models.enums import FaseEnum, CategoryEnum, VariantEnum
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
        fields = ['id', 'student', 'answer_img_url', 'note', 'fase', 'status']


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name']

class StudentSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    class Meta:
        model = Student
        fields = ['id', 'name', 'grade', 'turma', 'course', 'category', 'answers']

class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ['title', 'fase', 'category', 'variant', 'matrix', 'classe', 'key_url']

    def validate(self, data):
        # opcional: garantir que valor enviado está mesmo no Enum
        if data["fase"] not in FaseEnum.values:
            raise serializers.ValidationError({"fase": "Fase inválida"})
        if data["category"] not in CategoryEnum.values:
            raise serializers.ValidationError({"category": "Categoria inválida"})
        if data["variant"] not in VariantEnum.values:
            raise serializers.ValidationError({"variant": "Variante inválida"})
        return data
