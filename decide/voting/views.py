import django_filters.rest_framework
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from authentication.models import VotingUser
from .models import Question, QuestionOption, Voting, Candidatura
from .serializers import SimpleVotingSerializer, VotingSerializer, CandidaturaSerializer
from base.perms import UserIsStaff
from base.models import Auth

class CandidaturaPrimaria(generics.ListCreateAPIView):
    queryset = Candidatura.objects.all()
    serializer_class =  CandidaturaSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def post (self, request, candidatura_id, *args, **kwargs):
        self.permission_classes = (IsAdminUser,)
        self.check_permissions(request)
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)
        candidatura = get_object_or_404(Candidatura, pk=candidatura_id)
        msg = ""
        st = status.HTTP_200_OK
        if action == "delete":
            if(Voting.objects.filter(candiancy=candidatura).exists()):
                for voting in Voting.objects.filter(candiancy=candidatura):
                    voting.delete()
                for question1 in Question.objects.filter(desc__regex='elige representante de primero de la candidatura "'+candidatura.nombre+'"'):
                    question1.delete()
                for question2 in Question.objects.filter(desc__regex='elige representante de segundo de la candidatura "'+candidatura.nombre+'"'):
                    question2.delete()
                for question3 in Question.objects.filter(desc__regex='elige representante de tercero de la candidatura "'+candidatura.nombre+'"'):
                    question3.delete()
                for question4 in Question.objects.filter(desc__regex='elige representante de cuarto de la candidatura "'+candidatura.nombre+'"'):
                    question4.delete()
                for question5 in Question.objects.filter(desc__regex='elige representante de máster de la candidatura "'+candidatura.nombre+'"'):
                    question5.delete()
                for question6 in Question.objects.filter(desc__regex='elige representante de delegado de centro de la candidatura "'+candidatura.nombre+'"'):
                    question6.delete()
            else:
                msg = "Es posible que las primarias hayan sido borradas o no hayan sido creadas"
                st = status.HTTP_400_BAD_REQUEST

        if action == "start":
            if candidatura.representanteDelegadoPrimero != None:
                msg = "Las primarias para esta candidatura se han realizado ya"
                st = status.HTTP_400_BAD_REQUEST
            else:
                q1 = Question(desc='elige representante de primero de la candidatura "'+ candidatura.nombre+'"')
                q1.save()
                i=1
                usuarios_candidatura = VotingUser.objects.filter(candidatura=candidatura)    
                for usr in usuarios_candidatura.filter(curso="PRIMERO"):
                    qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q2 = Question(desc='elige representante de segundo de la candidatura "'+candidatura.nombre+'"')
                q2.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="SEGUNDO"):
                    qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q3 = Question(desc='elige representante de tercero de la candidatura "'+ candidatura.nombre+'"')
                q3.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="TERCERO"):
                    qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q4 = Question(desc='elige representante de cuarto de la candidatura "'+ candidatura.nombre+'"')
                q4.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="CUARTO"):
                    qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q5 = Question(desc='elige representante de máster de la candidatura "'+ candidatura.nombre+'"')
                q5.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="MASTER"):
                    qo = QuestionOption(question = q5, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q6 = Question(desc='elige representante de delegado de centro de la candidatura "'+ candidatura.nombre+'"')
                q6.save()
                i=1
                for usr in usuarios_candidatura:
                    qo = QuestionOption(question = q6, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1

                voting = Voting(name='Votaciones de la candidatura "'+candidatura.nombre+'"',desc="Elige a los representantes de tu candidatura."
                , tipo="Primary voting", candiancy=candidatura)
                voting.save()
                voting.question.add(q1, q2, q3, q4, q5, q6)

                for auth in Auth.objects.all():
                    voting.auths.add(auth)
                st = status.HTTP_200_OK
            
        return Response(msg, status=st)


class CandidaturaView(generics.ListCreateAPIView):
    queryset= Candidatura.objects.all()
    serializer_class = CandidaturaSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def get(self, request, *args, **kwargs):
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (IsAdminUser,)
        self.check_permissions(request)
        for data in ['nombre']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        candidatura = Candidatura(nombre=request.data.get('nombre'))
        candidatura.save()

        return Response({}, status=status.HTTP_201_CREATED)


class VotingView(generics.ListCreateAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    filter_fields = ('id', )

    def get(self, request, *args, **kwargs):
        version = request.version
        if version not in settings.ALLOWED_VERSIONS:
            version = settings.DEFAULT_VERSION
        if version == 'v2':
            self.serializer_class = SimpleVotingSerializer

        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.permission_classes = (UserIsStaff,)
        self.check_permissions(request)
        for data in ['name', 'desc', 'question', 'question_opt']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)

        question = Question(desc=request.data.get('question'))
        question.save()
        for idx, q_opt in enumerate(request.data.get('question_opt')):
            opt = QuestionOption(question=question, option=q_opt, number=idx)
            opt.save()
        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),
                question=question)
        voting.save()

        auth, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        auth.save()
        voting.auths.add(auth)
        return Response({}, status=status.HTTP_201_CREATED)

class CandidaturaUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Candidatura.objects.all()
    serializer_class = CandidaturaSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (IsAdminUser,)

    def put(self, request, candidatura_id, *args, **kwargs):
        candidatura = Candidatura.objects.get(pk=candidatura_id)
        for data in ['nombre']:
            if not data in request.data:
                return Response({}, status=status.HTTP_400_BAD_REQUEST)
        candidatura.nombre = request.data.get('nombre')
        candidatura.save()
        return Response({}, status=status.HTTP_200_OK)
    
    def delete(self, request, candidatura_id, *args, **kwargs):
        candidatura = Candidatura.objects.get(pk=candidatura_id)
        candidatura.delete()
        return Response({}, status=status.HTTP_200_OK)

        
        
class VotingUpdate(generics.RetrieveUpdateDestroyAPIView):
    queryset = Voting.objects.all()
    serializer_class = VotingSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)
    permission_classes = (UserIsStaff,)

    def put(self, request, voting_id, *args, **kwars):
        action = request.data.get('action')
        if not action:
            return Response({}, status=status.HTTP_400_BAD_REQUEST)

        voting = get_object_or_404(Voting, pk=voting_id)
        msg = ''
        st = status.HTTP_200_OK
        if action == 'start':
            if voting.start_date:
                msg = 'Voting already started'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.start_date = timezone.now()
                voting.save()
                msg = 'Voting started'
        elif action == 'stop':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.end_date:
                msg = 'Voting already stopped'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.end_date = timezone.now()
                voting.save()
                msg = 'Voting stopped'
        elif action == 'tally':
            if not voting.start_date:
                msg = 'Voting is not started'
                st = status.HTTP_400_BAD_REQUEST
            elif not voting.end_date:
                msg = 'Voting is not stopped'
                st = status.HTTP_400_BAD_REQUEST
            elif voting.tally:
                msg = 'Voting already tallied'
                st = status.HTTP_400_BAD_REQUEST
            else:
                voting.tally_votes(request.auth.key)
                msg = 'Voting tallied'
        else:
            msg = 'Action not found, try with start, stop or tally'
            st = status.HTTP_400_BAD_REQUEST
        return Response(msg, status=st)
