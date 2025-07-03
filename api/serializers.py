from rest_framework import serializers
from api.models import User, Student, Key

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', 'name', 'course']

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