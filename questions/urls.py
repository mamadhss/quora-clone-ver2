from django.urls import path
from . import views


urlpatterns = [
    path('category/',views.AddCategroyAPIView.as_view()),
    path('questions/',views.QuestionAPIView.as_view()),
    path('questions/<slug:cat_slug>/<slug:q_slug>/',views.QuestionDetailAPIView.as_view()),
    path('questions/<slug:cat_slug>/<slug:q_slug>/answers/',views.AnswerAPIView.as_view()),
    path('questions/<slug:cat_slug>/<slug:q_slug>/answers/<int:pk>',views.AnswerRUDAPIView.as_view()),
    path('questions/<slug:cat_slug>/<slug:q_slug>/like/',views.QuestionLikeAPIView.as_view()),
    path('questions/<slug:cat_slug>/<slug:q_slug>/answers/<int:pk>/like',views.AnswerLikeAPIView.as_view()),
    path('author/<slug:username>/',views.UserProfileChangeAPIView.as_view()),
    path('author/<slug:username>/questions/',views.QuestionByAuthorAPIView.as_view()),
    
   
]