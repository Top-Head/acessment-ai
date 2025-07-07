from rest_framework import serializers
from api.models import User, Student, Key
from api.models.enums import FaseEnum, CategoryEnum, VariantEnum

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        

class StudentUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name']

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
