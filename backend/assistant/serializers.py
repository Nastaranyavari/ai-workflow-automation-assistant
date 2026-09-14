from rest_framework import serializers


class AssistantRequestSerializer(serializers.Serializer):
    message = serializers.CharField()
    session_id = serializers.CharField()