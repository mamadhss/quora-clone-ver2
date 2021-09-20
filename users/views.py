from rest_framework import response
from rest_framework.views import APIView
from .serializers import ProfileSerializer, RegisterSerializer, UserSerializer
from rest_framework.response import Response
from rest_framework import serializers, status,exceptions
from rest_framework.permissions import IsAuthenticated


class RegisterAPIView(APIView):
    serializer_class = RegisterSerializer
    def post(self,request):
        data = request.data
        serializer = RegisterSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)    

class whoIAM(APIView):
    serializer_class = UserSerializer

    def get(self,request):
        user = self.request.user
        serializer = UserSerializer(user)
        return Response(serializer.data) 



    
