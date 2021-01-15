from django.urls import path, re_path
from . import views


urlpatterns = [
    path('', views.VotingView.as_view(), name='voting'),
    path('<int:voting_id>/', views.VotingUpdate.as_view(), name='voting'),
    path('candidaturaprimaria/<int:candidatura_id>/', views.CandidaturaPrimaria.as_view(), name='candidaturaprimaria'),
    path('candidatura/', views.CandidaturaView.as_view(), name='candidatura'),
    path('general/', views.GeneralVoting.as_view(), name="generalVoting"),
    re_path(r'^candidatura/(?P<pk>\d+)/$', views.CandidaturaUpdate.as_view(), name='candidatura'),
]
