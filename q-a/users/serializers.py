from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from .models import UserAccount,Profile
from django.contrib.auth.password_validation import validate_password as v_passwords

User = get_user_model()

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','email','username','password')
        extra_kwargs = {
            'password':{'write_only':True}
        }
    def create(self,validate_data):
        password = validate_data.pop('password',None)
        instance = self.Meta.model(**validate_data)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance
    def update(self,instance,validate_data):
        password = validate_data.pop('password',None)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance    

class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = Profile
        fields = '__all__'
        

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True,required=True)
    password2 = serializers.CharField(write_only=True,required=True)
    old_password = serializers.CharField(write_only=True,required=True)

    class Meta:
        model = User
        fields = ('old_password','password','password2')

    def validate_old_password(self,value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password":"old password not correct!"})   
        return value      

    def validate(self,data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password":"password fields didnt match!"})   
        v_passwords(data['password'],self.context['request'].user)
            
        return data

    def save(self, **kwargs):
        password = self.validated_data['password']
        user = self.context['request'].user
        user.set_password(password)
        user.save()
        return user    

