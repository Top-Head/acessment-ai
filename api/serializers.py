from rest_framework import serializers
from api.models.enums import FaseEnum, CategoryEnum, VariantEnum, StatusEnum
from django.contrib.auth.hashers import make_password
from api.models import User, Student, Key, StudentAnswer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        return super().create(validated_data)


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentAnswer
        fields = [
            "id", "student", "answer_img_url", "answer_matrix",
            "note", "corrects", "wrongs", "nulls", "fase", "status", "chave",
        ]


class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ["id", "name"]


class StudentSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)
    total_aprovados = serializers.SerializerMethodField()
    total_reprovados = serializers.SerializerMethodField()

    class Meta:
        model = Student
        fields = [
            "id", "name", "grade", "turma", "course", "category",
            "answers", "total_aprovados", "total_reprovados",
        ]

    def get_total_aprovados(self, obj):
        return obj.answers.filter(status=StatusEnum.APROVADO).count()

    def get_total_reprovados(self, obj):
        return obj.answers.filter(status=StatusEnum.REPROVADO).count()


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ["title", "fase", "category", "variant", "matrix", "classe", "key_url"]

    def validate(self, data):
        if data["fase"] not in FaseEnum.values:
            raise serializers.ValidationError({"fase": "Fase inválida"})
        if data["category"] not in CategoryEnum.values:
            raise serializers.ValidationError({"category": "Categoria inválida"})
        if data["variant"] not in VariantEnum.values:
            raise serializers.ValidationError({"variant": "Variante inválida"})
        return data


class KeyBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ["id", "title", "fase", "category", "variant", "matrix", "classe"]


class ExamResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_grade = serializers.IntegerField(source="student.grade", read_only=True)
    student_turma = serializers.CharField(source="student.turma", read_only=True)
    student_category = serializers.CharField(source="student.category", read_only=True)
    gabarito = KeyBriefSerializer(source="chave", read_only=True)

    class Meta:
        model = StudentAnswer
        fields = [
            "id", "student", "student_name", "student_grade",
            "student_turma", "student_category",
            "note", "corrects", "wrongs", "nulls", "fase", "status",
            "answer_matrix", "gabarito",
        ]


class KeySerializer(serializers.ModelSerializer):
    class Meta:
        model = Key
        fields = ["title", "fase", "category", "variant", "matrix", "classe", "key_url"]

    def validate(self, data):
        # opcional: garantir que valor enviado está mesmo no Enum
        if data["fase"] not in FaseEnum.values:
            raise serializers.ValidationError({"fase": "Fase inválida"})
        if data["category"] not in CategoryEnum.values:
            raise serializers.ValidationError({"category": "Categoria inválida"})
        if data["variant"] not in VariantEnum.values:
            raise serializers.ValidationError({"variant": "Variante inválida"})
        return data
