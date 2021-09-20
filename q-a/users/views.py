from rest_framework.utils.serializer_helpers import ReturnDict
from rest_framework.views import APIView
from .serializers import RegisterSerializer
from rest_framework.response import Response
from rest_framework import status,exceptions
from rest_framework.permissions import IsAuthenticated


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer
    def post(self,request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)    