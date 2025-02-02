from rest_framework import serializers
from .models import Figurant, Transaction

class FigurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Figurant
        fields = '__all__'

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
