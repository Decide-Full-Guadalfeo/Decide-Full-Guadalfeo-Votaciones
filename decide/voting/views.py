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

class GeneralVoting(generics.ListCreateAPIView):
    queryset = Candidatura.objects.all()
    serializer_class =  CandidaturaSerializer
    filter_backends = (django_filters.rest_framework.DjangoFilterBackend,)

    def post (self, request, *args, **kwargs):
        self.permission_classes = (IsAdminUser,)
        self.check_permissions(request)
        candidaturas_id = request.data.get('ids')
        if not candidaturas_id:
            return Response({'No se aportan las ids de las candidaturas'}, status=status.HTTP_400_BAD_REQUEST)
        candidaturas = []
        for i in candidaturas_id:
            cand = get_object_or_404(Candidatura, pk = i)
            candidaturas.append(cand)

        msg = ''
        st = status.HTTP_200_OK
        
        numero_votaciones_generales = Voting.objects.filter(tipo='GV').count()
        indice_votacion = str(numero_votaciones_generales + 1)
        q1 = Question(desc='Votación general ' + indice_votacion + ': Elige al delegado de primero')
        q1.save()
        q2 = Question(desc='Votación general ' + indice_votacion + ': Elige al delegado de segundo')
        q2.save()
        q3 = Question(desc='Votación general ' + indice_votacion + ': Elige al delegado de tercero')
        q3.save()
        q4 = Question(desc='Votación general ' + indice_votacion + ': Elige al delegado de cuarto')
        q4.save()
        q5 = Question(desc='Votación general ' + indice_votacion + ': Elige al delegado del master')
        q5.save()
        q6 = Question(desc='Votación general ' + indice_votacion + ': Elige al delegado al centro')
        q6.save()
        q7 = Question(desc='Votación general ' + indice_votacion + ': Elige a los miembros de delegación de alumnos')
        q7.save()
        try:
            contador = 1
            for c in candidaturas:
                qo1 = QuestionOption(question=q1, number=contador, option=c.representanteDelegadoPrimero.first_name
                                        + ' ' + c.representanteDelegadoPrimero.last_name + ' / ' + str(c.representanteDelegadoPrimero.id))
                qo1.save()
                qo2 = QuestionOption(question=q2, number=contador, option=c.representanteDelegadoSegundo.first_name
                                        + ' ' + c.representanteDelegadoSegundo.last_name + ' / ' + str(c.representanteDelegadoSegundo.id))
                qo2.save()
                qo3 = QuestionOption(question=q3, number=contador, option=c.representanteDelegadoTercero.first_name
                                        + ' ' + c.representanteDelegadoTercero.last_name + ' / ' + str(c.representanteDelegadoTercero.id)) 
                qo3.save()
                qo4 = QuestionOption(question=q4, number=contador, option=c.representanteDelegadoCuarto.first_name
                                        + ' ' + c.representanteDelegadoCuarto.last_name + ' / ' + str(c.representanteDelegadoCuarto.id))
                qo4.save()
                qo5 = QuestionOption(question=q5, number=contador, option=c.representanteDelegadoMaster.first_name
                                        + ' ' + c.representanteDelegadoMaster.last_name + ' / ' + str(c.representanteDelegadoMaster.id))
                qo5.save()
                qo6 = QuestionOption(question=q6, number=contador, option=c.delegadoCentro.first_name
                                        + ' ' + c.delegadoCentro.last_name + ' / ' + str(c.delegadoCentro.id))
                qo6.save()
                #Para delegacion de alumno hay que poner una opcion por cada alumno de la candidatura que no se presente a ninguno de los cargos previos
                alumnos_candidatura_sin_cargo = VotingUser.objects.filter(candidatura=c)
                i = 0
                for alumno in alumnos_candidatura_sin_cargo:
                    if (alumno.user!=c.representanteDelegadoPrimero and alumno.user!=c.representanteDelegadoSegundo and alumno.user!=c.representanteDelegadoTercero and alumno.user!=c.representanteDelegadoCuarto and alumno.user!=c.representanteDelegadoMaster and alumno.user!=c.delegadoCentro):
                        qo7 = QuestionOption(question=q7, number=(contador+i), option=alumno.user.first_name
                                        + ' ' + alumno.user.last_name + ' / ' + str(alumno.user.id))
                        qo7.save()
                        i+=1
                contador += 1
            
            votacion = Voting(name='Votación general ' + indice_votacion, desc='Elige a los representantes de tu centro', tipo='GV')
            votacion.save()
            votacion.question.add(q1, q2, q3, q4, q5, q6, q7)

            for auth in Auth.objects.all():
                votacion.auths.add(auth)

        except Exception as e:
            # En el caso de que haya alguna candidatura que no ha celebrado primarias, borramos las prunguntas pues no se creara la votacion general
            q1.delete()
            q2.delete()
            q3.delete()
            q4.delete()
            q5.delete()
            q6.delete()
            q7.delete()
            # Lo indicamos
            msg = 'Alguna de las candidaturas que se han seleccionado no ha celebrado primarias para elegir a sus representantes'
            st = status.HTTP_400_BAD_REQUEST

        return Response(msg, status=st)


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
                Voting.objects.filter(candiancy=candidatura).all().delete()
                Question.objects.filter(desc__regex='elige representante de primero de la candidatura "'+candidatura.nombre+'"').all().delete()
                Question.objects.filter(desc__regex='elige representante de segundo de la candidatura "'+candidatura.nombre+'"').all().delete()
                Question.objects.filter(desc__regex='elige representante de tercero de la candidatura "'+candidatura.nombre+'"').all().delete()
                Question.objects.filter(desc__regex='elige representante de cuarto de la candidatura "'+candidatura.nombre+'"').all().delete()
                Question.objects.filter(desc__regex='elige representante de máster de la candidatura "'+candidatura.nombre+'"').all().delete()
                Question.objects.filter(desc__regex='elige representante de delegado de centro de la candidatura "'+candidatura.nombre+'"').all().delete()
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
                for usr in usuarios_candidatura.filter(curso="First"):
                    qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q2 = Question(desc='elige representante de segundo de la candidatura "'+candidatura.nombre+'"')
                q2.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="Second"):
                    qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q3 = Question(desc='elige representante de tercero de la candidatura "'+ candidatura.nombre+'"')
                q3.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="Third"):
                    qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q4 = Question(desc='elige representante de cuarto de la candidatura "'+ candidatura.nombre+'"')
                q4.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="Fourth"):
                    qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name)
                    qo.save()
                    i+=1
                q5 = Question(desc='elige representante de máster de la candidatura "'+ candidatura.nombre+'"')
                q5.save()
                i=1
                for usr in usuarios_candidatura.filter(curso="Master"):
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
                , tipo="PV", candiancy=candidatura)
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

        resposne = Response({}, status=status.HTTP_201_CREATED)
        resposne.data['id'] = candidatura.pk
        return resposne


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
        self.permission_classes = (IsAdminUser,)
        self.check_permissions(request)
        for data in ['name', 'tipo', 'question']:
            if not data in request.data or request.data.get(data) =="":
                return Response({data+" is required."}, status=status.HTTP_400_BAD_REQUEST)
        
        if len(request.data.get("question"))==0:
                return Response({"Question is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        for i, quest in enumerate(request.data.get('question')):
                if not 'options' in quest or len(quest.get('options'))==0:
                    return Response({"Each question must have at least one option"}, status=status.HTTP_400_BAD_REQUEST)
        
        candidat = None
        candi = 'candiancy' in request.data and request.data.get('candiancy') != None and 'nombre' in request.data.get('candiancy') and request.data.get('candiancy').get('nombre')!=""
        if candi:
            candidat = Candidatura(nombre=request.data.get('candiancy').get('nombre'))
            candidat.save()

        tipo = request.data.get('tipo')
        if tipo != "GV" and tipo != "PV":
            if candi:
                candidat.delete()
            return Response({"Type must be GV for general voting or PV for primary voting"}, status=status.HTTP_400_BAD_REQUEST)

        if tipo == "GV" and candi:
            candidat.delete()
            return Response({"General votings must not have a candidacy"}, status=status.HTTP_400_BAD_REQUEST)

        if tipo == "PV" and not candi:
            return Response({"Primary votings must have a candidacy"}, status=status.HTTP_400_BAD_REQUEST)

        voting = Voting(name=request.data.get('name'), desc=request.data.get('desc'),tipo=tipo,candiancy=candidat)
        voting.save()
    
        for i,quest in enumerate(request.data.get('question')):
            question = Question(desc=quest.get('desc'))
            question.save()
            for idx, q_opt in enumerate(quest.get('options')):
                opt = QuestionOption(question=question, option=q_opt.get('option'), number=idx)
                opt.save()
            voting.question.add(question)

        if 'auths' in request.data and len(request.data.get("auths"))!=0:
            for i,dat in enumerate(request.data.get('auths')):
                auth,_ = Auth.objects.get_or_create(url=dat.get('url'),me=dat.get('me'),name=dat.get('name'))
                auth.save()
                voting.auths.add(auth)
        
        for aut in Auth.objects.all():
           voting.auths.add(aut)

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
    permission_classes = (IsAdminUser,)

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
