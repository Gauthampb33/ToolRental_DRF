from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.models import User
from Rental.serializers import UserSerializers

# Create your views here.
class SignUpView(APIView):
    def post(self,request):
        form_data=request.data
        Serializer_instance=UserSerializers(data=form_data)
        if Serializer_instance.is_valid():
            Serializer_instance.save()
            return Response({"Messsage":"User Created Successfully."},status=201)
        return Response({"Message":"Invalid Data Provided"},status=400)

class UserListView(APIView):
    def get(self,request):
        users=User.objects.all()
        serializer_instance=UserSerializers(users,many=True)
        return Response(serializer_instance.data,status=200)

