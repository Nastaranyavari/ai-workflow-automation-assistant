from django.shortcuts import render

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import AssistantRequestSerializer
from .services.assistant_service import AssistantService


@api_view(["POST"])
def assistant(request):

    serializer = AssistantRequestSerializer(
        data=request.data
    )

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    message = serializer.validated_data["message"]
    session_id = serializer.validated_data["session_id"]

    file = request.FILES.get("file")

    result = AssistantService.run(
        message=message,
        session_id=session_id,
        file=file,
    )

    return Response(result)


def home(request):
    return render(request, "index.html")