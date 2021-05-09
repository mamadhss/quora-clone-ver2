from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import CategorySerializer,QuestionSerializer,AnswerSerializer,QuestionLikeSerializer,AnswerLikeSerializer
from rest_framework.response import Response
from .models import Category,Question,Answer
from .permissions import IsAdminUserOrReadOnly,IsOwnerOrReadOnly,UserIsOwnerOrReadonly
from rest_framework import permissions,viewsets,status,generics,mixins
from rest_framework.exceptions import ValidationError,NotFound
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from users.serializers import ProfileSerializer
from users.models import Profile
from django.db.models import Q
from .task import question_created,answer_created,question_liked
from django_filters.rest_framework import DjangoFilterBackend
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie




User = get_user_model()


class AddCategroyAPIView(APIView):
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def post(self,request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'data':serializer.data,
                'msg':'Category Created',
            },status=status.HTTP_201_CREATED)

        return Response(serializer.errors)    

    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def get(self,request):
        categories = Category.objects.all()
        serializer = CategorySerializer(categories,many=True,context={'request':request})
        return Response(serializer.data)

class CategoryDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = CategorySerializer
    
    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def get(self,request,cat_slug):
        category = Category.objects.get(slug=cat_slug)
        serializer = CategorySerializer(category,context={'request':request})
        return Response(serializer.data)



class QuestionAPIView(APIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Question.objects.all()


    def post(self,request):
        serializer = QuestionSerializer(data=request.data,context={'request':request})
        if serializer.is_valid():
            question = serializer.save(
                author=self.request.user
            )
            question_created.delay(question.id)

            return Response({
                'data':serializer.data,
                'msg':'question created',
            },status=status.HTTP_201_CREATED)

    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def get(self,request):
        s = request.GET.get('s')
        sort = request.GET.get('sort')
        questions = Question.objects.all()
        if s:
            questions = questions.filter(Q(content__icontains=s) | Q(author__username=s))
        if sort == 'asc':
            questions = questions.order_by('created_at')
        elif sort == 'desc' :
            questions = questions.order_by('-created_at')

        serializer = QuestionSerializer(questions,many=True,context={'request':request})
        return Response(serializer.data)

class QuestionDetailAPIView(APIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwnerOrReadOnly]

    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def get(self,request,cat_slug,q_slug):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)
        serializer = QuestionSerializer(question,context={'request':request})
        return Response(serializer.data)

    def put(self,request,cat_slug,q_slug):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)
        serializer = QuestionSerializer(question,data=request.data,partial=True,context={'request':request})
        if serializer.is_valid():
            serializer.save()
            return Response({
                'data':serializer.data,
                'msg':'Updated!'
            })
        return Response(serializer.errors)

    def delete(self,request,cat_slug,q_slug):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)
        question.delete()
        return Response({
            'msg':'Question Deleted!'
        },status=status.HTTP_204_NO_CONTENT)    

class AnswerAPIView(generics.ListCreateAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Answer.objects.all().order_by('-created_at')


    def get_queryset(self):
        answer = self.queryset.filter(question__category__slug=self.kwargs['cat_slug'])
        queryset = answer.filter(question__slug=self.kwargs['q_slug'])
        return queryset


    def perform_create(self,serializer):
        question = Question.objects.filter(category__slug=self.kwargs['cat_slug']).get(slug=self.kwargs['q_slug'])
        answer = serializer.save(
            author=self.request.user,
            question = question
        )    
        answer_created.delay(answer.id)

        
class AnswerRUDAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnswerSerializer
    permission_classes = [permissions.IsAuthenticated,IsOwnerOrReadOnly]
    queryset = Answer.objects.all()

    def get_queryset(self):
        answer = self.queryset.filter(question__category__slug=self.kwargs['cat_slug'])
        queryset = answer.filter(question__slug=self.kwargs['q_slug'])
        return queryset


class QuestionLikeAPIView(APIView):
    serializer_class = QuestionLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request,cat_slug,q_slug):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)
        if question.q_likes.filter(liker=self.request.user).exists():
            raise ValidationError('You Already Liked this Question')
        serializer = QuestionLikeSerializer(data=request.data)
        if serializer.is_valid():
            qlike = serializer.save(
                question = question,
                liker = self.request.user
            )
            question_liked.delay(qlike.id)
            return Response({
                'data':serializer.data,
                'msg':'Liked Question!'
            },status=status.HTTP_200_OK)
        return Response(serializer.errors)    

    def delete(self,request,cat_slug,q_slug):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)    
        qs = question.q_likes.filter(liker=self.request.user)
        if qs.exists():
            qs.delete()
            return Response({
                'msg':'Unliked!'
            },status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You never liked this question!')   

class AnswerLikeAPIView(APIView):
    serializer_class = AnswerLikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self,request,cat_slug,q_slug,pk):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)
        answer = Answer.objects.filter(question=question).get(pk=pk)
        if answer.a_likes.filter(liker=self.request.user).exists():
            raise ValidationError('You already Liked this Answer')
        serializer = AnswerLikeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(
                answer=answer,
                liker = self.request.user
            )
            return Response({
                'data':serializer.data,
                'msg':'Liked!'
            })

    def delete(self,request,cat_slug,q_slug,pk):
        question = Question.objects.filter(category__slug=cat_slug).get(slug=q_slug)
        answer = Answer.objects.filter(question=question).get(pk=pk)
        qs = answer.a_likes.filter(liker=self.request.user)
        if qs.exists():
            qs.delete()
            return Response({
                'msg':'Unliked!'
            },status=status.HTTP_204_NO_CONTENT)
        else:
            raise ValidationError('You never liked this answer!')    

''' questions of specfic user '''
class QuestionByAuthorAPIView(APIView):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    @method_decorator(cache_page(60*60*2))
    @method_decorator(vary_on_cookie)
    def get(self,request,username):
        try:
            author = User.objects.get(username=username)
            questions = Question.objects.filter(author=author)
            serializer = QuestionSerializer(questions,many=True,context={'request':request})
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND) 

class UserProfileChangeAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated,UserIsOwnerOrReadonly]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get(self,request,username):
        
        user = User.objects.get(username=username)
        profile = Profile.objects.get(user=user)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)
          
        
    def put(self,request,username):
        user = User.objects.get(username=username)
        instance = Profile.objects.get(user=user)
        serializer = ProfileSerializer(data=request.data,instance=instance,partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'data':serializer.data,
                'msg':'Profile Updated!'
            })
        return Response(serializer.errors)    


    




                                                        