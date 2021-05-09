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
            return Response({
                'data': serializer.data,
                'msg':'successfully created user'
            },status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)    
