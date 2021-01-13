import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status
from .serializers import CandidaturaSerializer

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from authentication.models import VotingUser
from voting.models import Candidatura, Voting, Question, QuestionOption

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
class VotacionTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
    
    def create_votacion(self, opcion, opcion2):
        usuario = User.objects.all()[1]
        c = Candidatura(nombre="Candidatura completa", delegadoCentro=usuario, representanteDelegadoPrimero=usuario,
            representanteDelegadoSegundo=usuario, representanteDelegadoTercero=usuario, representanteDelegadoCuarto= usuario,
            representanteDelegadoMaster= usuario)
        c.save()
        if(opcion == "one"):
            q = Question(desc="test question")
            q.save()
            opt = QuestionOption(question=q, option="test")
            opt.save()
            if(opcion2=="primary"):
                v = Voting(name="Test primaria 1 pregunta",tipo='PV', candiancy=c)
                v.save()
                v.question.add(q)
            if(opcion2=="general"):
                v = Voting(name="Test genereal 1 pregunta",tipo='GV')
                v.save()
                v.question.add(q)
        if(opcion == "two"):
            q = Question(desc="test question")
            q.save()
            opt = QuestionOption(question=q, option="test")
            opt.save()
            q2 = Question(desc="test question 2")
            q2.save()
            opt2 = QuestionOption(question=q2, option="test2")
            opt2.save()
            if(opcion2=="primary"):
                v = Voting(name="Test primaria 1 pregunta",tipo='PV', candiancy=c)
                v.save()
                v.question.add(q,q2)
            if(opcion2=="general"):
                v = Voting(name="Test genereal 1 pregunta",tipo='GV')
                v.save()
                v.question.add(q,q2)
        return v
      
    def test_create_voting_primary_1question(self):
        v = self.create_votacion("one", "primary")
        self.assertEqual(Voting.objects.get(tipo="PV").tipo, "PV")
        numeroPreguntas = v.question.count()
        self.assertTrue(numeroPreguntas==1)
        v.delete()

    def test_create_voting_general_1question(self):
        v = self.create_votacion("one", "general")
        self.assertEqual(Voting.objects.get(tipo="GV").tipo, "GV")
        numeroPreguntas = v.question.count()
        self.assertTrue(numeroPreguntas==1)
        v.delete()

    def test_create_voting_primary_2question(self):
        v = self.create_votacion("two", "primary")
        self.assertEqual(Voting.objects.get(tipo="PV").tipo, "PV")
        numeroPreguntas = v.question.count()
        self.assertTrue(numeroPreguntas==2)
        v.delete()

    def test_create_voting_general_2question(self):
        v = self.create_votacion("two", "general")
        self.assertEqual(Voting.objects.get(tipo="GV").tipo, "GV")
        numeroPreguntas = v.question.count()
        self.assertTrue(numeroPreguntas==2)
        v.delete()
    
class CandidaturaTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
    def create_candidatura_w_voting_users(self):
        c = Candidatura(nombre="Candidatura con votingusers", delegadoCentro=None, representanteDelegadoPrimero=None,
            representanteDelegadoSegundo=None, representanteDelegadoTercero=None, representanteDelegadoCuarto= None,
            representanteDelegadoMaster= None)
        c.save()

        u1 = User(username="firstVoter", first_name="representante de",last_name="primer curso")
        u1.save()
        v1 = VotingUser(user=u1,dni="47348063C",sexo="Man",titulo="Software",curso="First", candidatura=c)
        v1.save()

        u2 = User(username="secondVoter", first_name="representante de",last_name="segundo curso")
        u2.save()
        v2 = VotingUser(user=u2,dni="47348063F",sexo="Woman",titulo="Software",curso="Second", candidatura=c)
        v2.save()

        u3 = User(username="third", first_name="representante de",last_name="tercer curso")
        u3.save()
        v3 = VotingUser(user=u3,dni="47348068C",sexo="Man",titulo="Software",curso="Third", candidatura=c)
        v3.save()

        u4 = User(username="fourth", first_name="representante de",last_name="cuarto curso")
        u4.save()
        v4 = VotingUser(user=u4,dni="47347963C",sexo="Man",titulo="Software",curso="Fourth", candidatura=c)
        v4.save()

        u5 = User(username="master", first_name="representante de",last_name="master curso")
        u5.save()
        v5 = VotingUser(user=u5,dni="47297963C",sexo="Man",titulo="Software",curso="Master", candidatura=c)
        v5.save()

        return c
        
    def create_candidatura(self, opcion):
        usuario = User.objects.all()[1]
        if(opcion=="completo"):
            c = Candidatura(nombre="Candidatura completa", delegadoCentro=usuario, representanteDelegadoPrimero=usuario,
            representanteDelegadoSegundo=usuario, representanteDelegadoTercero=usuario, representanteDelegadoCuarto= usuario,
            representanteDelegadoMaster= usuario)
        if(opcion=="nulos"):
            c = Candidatura(nombre="Candidatura con nulos", delegadoCentro=None, representanteDelegadoPrimero=None,
            representanteDelegadoSegundo=None, representanteDelegadoTercero=None, representanteDelegadoCuarto= None,
            representanteDelegadoMaster= None)
        if(opcion=="sinNombre"):
            c = Candidatura(nombre=None, delegadoCentro=usuario, representanteDelegadoPrimero=usuario,
            representanteDelegadoSegundo=usuario, representanteDelegadoTercero=usuario, representanteDelegadoCuarto= usuario,
            representanteDelegadoMaster= usuario)
        c.save()
        return c
    def test_create_candidaturaCompleta(self):
        """test: deja crear candidatura con representantes y delegados."""
        numeroCandidaturas = Candidatura.objects.count()
        c = self.create_candidatura("completo")
        numeroCandidaturasTrasCreate = Candidatura.objects.count()
        self.assertTrue(numeroCandidaturasTrasCreate>numeroCandidaturas)
        self.assertEqual(Candidatura.objects.get(nombre="Candidatura completa").nombre, "Candidatura completa")
        c.delete()

    def test_create_candidaturaSinUsuarios(self):
        """test: deja crear candidatura sin representantes y delegados."""
        numeroCandidaturas = Candidatura.objects.count()
        c = self.create_candidatura("nulos")
        numeroCandidaturasTrasCreate = Candidatura.objects.count()
        self.assertTrue(numeroCandidaturasTrasCreate>numeroCandidaturas)
        self.assertEqual(Candidatura.objects.get(nombre="Candidatura con nulos").representanteDelegadoCuarto, None)
        c.delete()

    def test_create_candidaturaSinNombre(self):
        """test: NO deja crear candidatura sin nombre."""
        with self.assertRaises(Exception) as cm:
            self.create_candidatura("sinNombre")
        the_exception = cm.exception
        self.assertEqual(type(the_exception), IntegrityError)

    def test_update_candidatura(self):
        """test: se puede actualizar una candidatura."""
        c = self.create_candidatura("nulos")
        Candidatura.objects.filter(pk=c.pk).update(nombre="Nombre actualizado")
        c.refresh_from_db()
        self.assertEqual(c.nombre, "Nombre actualizado")
        c.delete()

    def test_delete_candidatura(self):
        """test: se borra una candidatura."""
        numeroCandidaturas = Candidatura.objects.count()
        c = self.create_candidatura("nulos")
        numeroCandidaturasTrasCreate = Candidatura.objects.count()
        self.assertTrue(numeroCandidaturasTrasCreate>numeroCandidaturas)
        self.assertEqual(Candidatura.objects.get(nombre="Candidatura con nulos").representanteDelegadoCuarto, None)
        c.delete()
        self.assertFalse(Candidatura.objects.filter(nombre="Candidatura con nulos").exists())
    
   #PRINCIPIO TEST VOTACIONES PRIMARIAS
    
    def create_primary_voting(self,nombreVotacion,candidatura):
        usuarios_candidatura = VotingUser.objects.filter(candidatura=candidatura)   
        q1= Question(desc="Elige representante de primero de la candidatura")
        q1.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="First"):
            qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q2= Question(desc="Elige representante de segundo de la candidatura")
        q2.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="Second"):
            qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q3= Question(desc="Elige representante de tercero de la candidatura")
        q3.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="Third"):
            qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q4= Question(desc="Elige representante de cuarto de la candidatura")
        q4.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="Fourth"):
            qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q5= Question(desc="Elige representante de master de la candidatura")
        q5.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="Master"):
            qo = QuestionOption(question = q5, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q6= Question(desc="Elige representante de delegado de centro")
        q6.save()
        i=1
        for usr in usuarios_candidatura:
            qo = QuestionOption(question = q6, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        vot= Voting(name=nombreVotacion, desc="Elige a los representantes de tu candidatura.",
        tipo='Primary Voting',candiancy=candidatura)
        vot.save()
        vot.question.add(q1,q2,q3,q4,q5,q6)

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL, defaults={'me': True, 'name': 'test auth'})
        a.save()
        vot.auths.add(a)  
        return vot

    def test_create_primary_voting(self):
        num_votaciones= Voting.objects.count()
        candidatura_completa= self.create_candidatura("completo")
        #Creamos la votación añadiendole el nombre
        votacion_primaria= self.create_primary_voting("Votaciones de delegados",candidatura_completa)
        numVotacionesTrasCrear=Voting.objects.count()
        #Comprobamos que se crea correctamente la votacion
        self.assertTrue(numVotacionesTrasCrear>num_votaciones)
        #Vemos que existe la votacion
        self.assertEqual(Voting.objects.get(tipo='Primary Voting').name,"Votaciones de delegados")
        votacion_primaria.delete()

    def test_create_primary_voting_candiancy_null(self):
        num_votaciones= Voting.objects.count()
        candidatura_null= self.create_candidatura("nulos")

        #Creamos la votación añadiendole el nombre y la candidatura sin representantes
        votacion_primaria_sin_representantes= self.create_primary_voting("Votaciones de delegados sin representantes",candidatura_null)
        numVotacionesTrasCrear=Voting.objects.count()

        #Comprobamos que se crea correctamente la votacion
        self.assertTrue(numVotacionesTrasCrear>num_votaciones)

        #Vemos que existe la votacion
        self.assertEqual(Voting.objects.get(tipo='Primary Voting').name,"Votaciones de delegados sin representantes")
        self.assertEqual(Voting.objects.get(tipo='Primary Voting').candiancy.representanteDelegadoPrimero,None)
        votacion_primaria_sin_representantes.delete()

    def test_delete_voting_primary(self):
        num_votaciones= Voting.objects.count()
        candidatura_completa= self.create_candidatura("completo")
        vot= self.create_primary_voting("Votaciones de delegados",candidatura_completa)
        #Comprobamos que crea correctamente la votacion
        numVotacionesTrasCrear=Voting.objects.count()
        self.assertTrue(numVotacionesTrasCrear>num_votaciones)

        #Comprobamos que exista esa votacion y la borramos
        self.assertEqual(Voting.objects.get(tipo='Primary Voting').name,"Votaciones de delegados")
        vot.delete()
        numVotacionesTrasBorrar=Voting.objects.count()
        self.assertTrue(numVotacionesTrasBorrar==num_votaciones)
    def test_create_primary_voting_API(self):
        """test: deja crear bien las votaciones primarias desde la API."""
        c = self.create_candidatura_w_voting_users()
        self.login()
        data = {'action': 'start'}
        response = self.client.post('/voting/candidaturaprimaria/{}/'.format(c.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        q = Question.objects.filter(desc='elige representante de máster de la candidatura "Candidatura con votingusers"')
        self.assertEqual(q.exists(), True)
        CreadoRepresentanteMaster =QuestionOption.objects.filter(question = q.all()[0], option="representante de master curso").exists()
        self.assertEqual(CreadoRepresentanteMaster, True)


    def test_create_primary_voting_API_Fail(self):
        """test: falla al crear desde la API porque ya se han hecho las primarias y hay representante."""
        c = self.create_candidatura_w_voting_users()
        vu = VotingUser.objects.filter(candidatura=c, curso="First").all()[0]
        c.representanteDelegadoPrimero=vu.user
        c.save()
        self.login()
        data = {'action': 'start'}
        response = self.client.post('/voting/candidaturaprimaria/{}/'.format(c.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        
        #FIN TEST VOTACION PRIMARIA

        #PRINCIPIO TEST VOTACION GENERAL API
    
    def test_create_general_voting_API(self):
        """test: deja crear bien las votaciones generales desde la API."""
        antes = Voting.objects.all().count()
        antesQ = Question.objects.all().count()
        c = self.create_candidatura("completo")
        self.login()
        data = {'ids':[c.pk]}
        response = self.client.post('/voting/general/', data, format='json')
        self.assertEqual(response.status_code, 200)
        despues = Voting.objects.all().count()
        despuesQ = Question.objects.all().count()
        self.assertEqual(antes + 1,despues)
        self.assertEqual(antesQ + 7, despuesQ)

    def test_create_general_voting_FAIL_API(self):
        """test: falla al crear las votaciones generales desde la API candidatura nulo."""
        antes = Voting.objects.all().count()
        antesQ = Question.objects.all().count()
        c = self.create_candidatura("nulos")
        self.login()
        data = {'ids':[c.pk]}
        response = self.client.post('/voting/general/', data, format='json')
        self.assertEqual(response.status_code, 400)
        despues = Voting.objects.all().count()
        despuesQ = Question.objects.all().count()
        self.assertEqual(antes,despues)
        self.assertEqual(antesQ, despuesQ)

        #FIN TEST VOTACION GENERAL API

    def test_create_candidatura_api(self):
        self.login()

        data = {
            'nombre': 'Candidatura de prueba',
            'delegadoCentro': 'Pepe Viyuela',
            'representanteDelegadoPrimero': 'Lautaro Gomez',
            'representanteDelegadoSegundo': 'Juan Alberto Garcia',
            'representanteDelegadoTercero': 'Sergio Perez',
            'representanteDelegadoCuarto': 'Ruben Doblas',
            'representanteDelegadoMaster': 'Raul Contreras',
        }
        response = self.client.post('/voting/candidatura/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_get_valid_candidatura_api(self):
        usuario = User(username="master", first_name="representante de",last_name="master curso")
        usuario.save()
        usuario2 = User(username="fourth", first_name="representante de",last_name="cuarto curso")
        usuario2.save()
        self.c1= Candidatura(nombre="CandidaturaPrueba1", delegadoCentro=usuario, representanteDelegadoPrimero=usuario,
            representanteDelegadoSegundo=usuario, representanteDelegadoTercero=usuario, representanteDelegadoCuarto= usuario,
            representanteDelegadoMaster= usuario)
        self.c1.save()
        self.c2=Candidatura(nombre="Candidatura de prueba 2", delegadoCentro=usuario2, representanteDelegadoPrimero=usuario2,
            representanteDelegadoSegundo=usuario2, representanteDelegadoTercero=usuario2, representanteDelegadoCuarto= usuario2,
            representanteDelegadoMaster= usuario2)
        self.c2.save()

        self.login()
        response= self.client.get(reverse('candidatura',kwargs={'pk':self.c2.pk}))
        candidatura=Candidatura.objects.get(pk=self.c2.pk)
        serializer=CandidaturaSerializer(candidatura)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_all_candidaturas_api(self):
        response= self.client.get(reverse('candidatura'))
        candidatura=Candidatura.objects.all()
        serializer=CandidaturaSerializer(candidatura,many=True)
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        c = Candidatura(nombre="Candidatura prueba")
        c.save()
        user = User.objects.get(username='admin')
        q1 = Question(desc='elige representante de primero de la candidatura "'+ c.nombre+'"')
        q1.save()
        q2 = Question(desc='elige representante de segundo de la candidatura "'+c.nombre+'"')
        q2.save()
        q3 = Question(desc='elige representante de tercero de la candidatura "'+ c.nombre+'"')
        q3.save()
        q4 = Question(desc='elige representante de cuarto de la candidatura "'+ c.nombre+'"')
        q4.save()
        q5 = Question(desc='elige representante de máster de la candidatura "'+ c.nombre+'"')
        q5.save()
        q6 = Question(desc='elige representante de delegado de centro de la candidatura "'+ c.nombre+'"')
        q6.save()
        v = Voting(name='Votaciones de la candidatura "'+c.nombre+'"',desc="Elige a los representantes de tu candidatura."
        , tipo="PV", candiancy=c)
        v.save()
        v.question.add(q1, q2, q3, q4, q5, q6)
        for q in v.question.all():
            qo = QuestionOption(question = q, number=1, option=user.first_name+" "+user.last_name+ " / "+str(user.id))
            qo.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for q in v.question.all():
            for opt in q.options.all():
                clear[opt.number] = 0
                for i in range(random.randint(0, 5)):
                    a, b = self.encrypt_msg(opt.number, v)
                    data = {
                        'voting': v.id,
                        'voter': voter.voter_id,
                        'vote': { 'a': a, 'b': b },
                    }
                    clear[opt.number] += 1
                    user = self.get_or_create_user(voter.voter_id)
                    self.login(user=user.username)
                    voter = voters.pop()
                    mods.post('store', json=data)
        return clear

#    def test_complete_voting(self):
#        v = self.create_voting()
#        self.create_voters(v)

#        v.create_pubkey()
#        v.start_date = timezone.now()
#        v.save()

#       clear = self.store_votes(v)

#        v.end_date = timezone.now()
#        v.save()

#        self.login()  # set token
#        v.tally_votes(self.token)

#        tally = v.tally
#        tally.sort()
#        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}
        
#        for q in v.question.all():
#            for opt in q.options.all():
#               self.assertEqual(tally.get(opt.number, 0), clear.get(opt.number, 0))

#        for q in v.postproc:
#            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
        "name": "Votaciones de la candidatura \"Candidatura de prueba\"",
        "desc": "Elige a los representantes de tu candidatura.",
        "question": [
            {
                "desc": "elige representante de primero de la candidatura \"Candidatura de prueba\"",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            },
            {
                "desc": "elige representante de segundo de la candidatura \"Candidatura de prueba\"",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            },
            {
                "desc": "elige representante de tercero de la candidatura \"Candidatura de prueba\"",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            },
            {
                "desc": "elige representante de cuarto de la candidatura \"Candidatura de prueba\"",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            },
            {
                "desc": "elige representante de máster de la candidatura \"Candidatura de prueba\"",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            },
            {
                "desc": "elige representante de delegado de centro de la candidatura \"Candidatura de prueba\"",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            }
        ],
        "tipo": "PV",
        "candiancy": {
            "nombre": "Candidatura de prueba"
        }
    }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)
    
    def test_create_PrimaryVotingWithoutCandidacy_API_Fail(self):
        self.login()

        data = {
        "name": "Votacion de prueba",
        "desc": "Prueba",
        "question": [
            {
                "desc": "pregunta 1",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            }
        ],
        "tipo": "PV"
    }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()[0],'Primary votings must have a candidacy')

    def test_create_GeneralVotingWithCandidacy_API_Fail(self):
        self.login()

        data = {
        "name": "Votacion de prueba",
        "desc": "Prueba",
        "question": [
            {
                "desc": "pregunta 1",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            }
        ],
        "tipo": "GV",
        "candiancy": {
            "nombre": "Candidatura de prueba"
        }
    }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()[0],'General votings must not have a candidacy')
    
    def test_create_GeneralVotingWithoutName_API_Fail(self):
        self.login()

        data = {
        "name": "",
        "desc": "Prueba",
        "question": [
            {
                "desc": "pregunta 1",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            }
        ],
        "tipo": "GV"
    }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_PrimaryVotingWithoutName_API_Fail(self):
        self.login()

        data = {
        "name": "",
        "desc": "Prueba",
        "question": [
            {
                "desc": "pregunta 1",
                "options": [
                    {
                        "number": 1,
                        "option": "A"
                    },
                    {
                        "number": 2,
                        "option": "B"
                    }
                ]
            }
        ],
        "tipo": "PV",
        "candiancy": {
            "nombre": "Candidatura de prueba"
        }
    }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_PrimaryVotingWithoutQuestions_API_Fail(self):
        self.login()

        data = {
        "name": "Votacion de prueba",
        "desc": "Prueba",
        "question": [
            
        ],
        "tipo": "PV",
        "candiancy": {
            "nombre": "Candidatura de prueba"
        }
    }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
#        for action in ['stop', 'tally']:
#            data = {'action': action}
#            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
#            self.assertEqual(response.status_code, 400)
#            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

#        data = {'action': 'tally'}
#        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
#        self.assertEqual(response.status_code, 400)
#        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

#        data = {'action': 'tally'}
#        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
#        self.assertEqual(response.status_code, 200)
#        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
#        data = {'action': 'start'}
#        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
#        self.assertEqual(response.status_code, 400)
#        self.assertEqual(response.json(), 'Voting already started')

#        data = {'action': 'stop'}
#        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
#        self.assertEqual(response.status_code, 400)
#        self.assertEqual(response.json(), 'Voting already stopped')

#        data = {'action': 'tally'}
#        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
#        self.assertEqual(response.status_code, 400)

#        self.assertEqual(response.json(), 'Voting already tallied')

class PrimaryVotingTestCase(StaticLiveServerTestCase):
    
   def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)

        super().setUp()    

   def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

   def create_candidatura(self):
        c = Candidatura(nombre="Candidatura para primarias", delegadoCentro=None, representanteDelegadoPrimero=None,
            representanteDelegadoSegundo=None, representanteDelegadoTercero=None, representanteDelegadoCuarto= None,
            representanteDelegadoMaster= None)
        c.save()

        return c
   def test_update_primaryVoting(self):
        """test: se puede actualizar una votacion con tipo primaria."""
        c=self.create_candidatura()
        v = Voting.objects.create(desc='Una votación primaria', name="Votación primaria", tipo='PV',candiancy=c)
        self.assertEqual(v.name, 'Votación primaria')
        self.assertEqual(v.desc, 'Una votación primaria')
        # Actualizamos la votación
        v.name='Se actualizó el nombre'
        v.desc='Se actualizó la descripción'
        v.save()
        # Y vemos que se han aplicado los cambios
        self.assertEqual(v.name, 'Se actualizó el nombre',)
        self.assertEqual(v.desc, 'Se actualizó la descripción')
        v.delete()

   def create_users(self):
        u1 = User(username="firstVoter", first_name="representante de",last_name="primer curso")
        u1.save()
        v1 = VotingUser(user=u1,dni="47348063A",sexo="Man",titulo="Software",curso="First")
        v1.save()

        u2 = User(username="secondVoter", first_name="representante de",last_name="segundo curso")
        u2.save()
        v2 = VotingUser(user=u2,dni="47348063B",sexo="Woman",titulo="Software",curso="Second")
        v2.save()

        u3 = User(username="third", first_name="representante de",last_name="tercer curso")
        u3.save()
        v3 = VotingUser(user=u3,dni="47348063C",sexo="Man",titulo="Software",curso="Third")
        v3.save()

        u4 = User(username="fourth", first_name="representante de",last_name="cuarto curso")
        u4.save()
        v4 = VotingUser(user=u4,dni="47348063D",sexo="Woman",titulo="Software",curso="Fourth")
        v4.save()

        u5 = User(username="master", first_name="representante de",last_name="master curso")
        u5.save()
        v5 = VotingUser(user=u5,dni="47348063E",sexo="Man",titulo="Software",curso="Master")
        v5.save()

        u6 = User(username="firstVoter2", first_name="representante de",last_name="primer curso")
        u6.save()
        v6 = VotingUser(user=u6,dni="47348063F",sexo="Man",titulo="Software",curso="First")
        v6.save()

        u7 = User(username="secondVoter2", first_name="representante de",last_name="segundo curso")
        u7.save()
        v7 = VotingUser(user=u7,dni="47348063G",sexo="Woman",titulo="Software",curso="Second")
        v7.save()

        u8 = User(username="third2", first_name="representante de",last_name="tercer curso")
        u8.save()
        v8 = VotingUser(user=u8,dni="47348063H",sexo="Man",titulo="Software",curso="Third")
        v8.save()

        u9 = User(username="fourth2", first_name="representante de",last_name="cuarto curso")
        u9.save()
        v9 = VotingUser(user=u9,dni="47348063I",sexo="Woman",titulo="Software",curso="Fourth")
        v9.save()

        u10 = User(username="master2", first_name="representante de",last_name="master curso")
        u10.save()
        v10 = VotingUser(user=u10,dni="47348063J",sexo="Man",titulo="Software",curso="Master")
        v10.save()

        return [v1,v2,v3,v4,v5,v6,v7,v8,v9,v10]


   def test_view_createPrimaryVotingOneCandiancyCorrect(self):
        users = self.create_users()
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Voting users").click()
        for u in users:
            self.driver.find_element(By.LINK_TEXT, u.user.username).click()
            dropdown = self.driver.find_element(By.ID, "id_candidatura")
            dropdown.find_element(By.XPATH, "//option[. = 'Candidatura con representantes elegidos']").click()
            element = self.driver.find_element(By.ID, "id_candidatura")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click_and_hold().perform()
            element = self.driver.find_element(By.ID, "id_candidatura")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            element = self.driver.find_element(By.ID, "id_candidatura")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).release().perform()
            self.driver.find_element(By.ID, "id_candidatura").click()
            self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Realizar las votaciones primarias de candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".success").text == "¡Las elecciones primarias se han creado!"

        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        assert self.driver.find_element(By.LINK_TEXT, 'Votaciones de la candidatura "Candidatura con representantes elegidos"').text == 'Votaciones de la candidatura "Candidatura con representantes elegidos"'
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        
        self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        usuarios_candidatura = VotingUser.objects.filter(candidatura=1)
        for usr in usuarios_candidatura:
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
            
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Master"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Fourth"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Third"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Second"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="First"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"

        self.driver.find_element(By.ID, "id_options-0-option").click()

   def test_view_createPrimaryVotingMoreThanOneCandiancyCorrect(self):
        users = self.create_users()
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)

        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura con representantes elegidos")   
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()

        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()

        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura 2 con representantes elegidos")   
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('noadmin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Voting users").click()
        i=1
        for u in users:
            self.driver.find_element(By.LINK_TEXT, u.user.username).click()
            dropdown = self.driver.find_element(By.ID, "id_candidatura")
            if i<=5:
                dropdown.find_element(By.XPATH, "//option[. = 'Candidatura con representantes elegidos']").click()
            else:
                dropdown.find_element(By.XPATH, "//option[. = 'Candidatura 2 con representantes elegidos']").click()
            element = self.driver.find_element(By.ID, "id_candidatura")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).click_and_hold().perform()
            element = self.driver.find_element(By.ID, "id_candidatura")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).perform()
            element = self.driver.find_element(By.ID, "id_candidatura")
            actions = ActionChains(self.driver)
            actions.move_to_element(element).release().perform()
            self.driver.find_element(By.ID, "id_candidatura").click()
            self.driver.find_element(By.NAME, "_save").click()
            i+=1
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()

        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row2 .action-select").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Realizar las votaciones primarias de candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".success").text == "¡Las elecciones primarias se han creado!"

        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        assert self.driver.find_element(By.LINK_TEXT, 'Votaciones de la candidatura "Candidatura con representantes elegidos"').text == 'Votaciones de la candidatura "Candidatura con representantes elegidos"'
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"'
        assert self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        
        self.driver.find_element(By.LINK_TEXT, 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de delegado de centro de la candidatura "Candidatura con representantes elegidos"'
        
        usuarios_candidatura = VotingUser.objects.filter(candidatura=1)
        nousuarios_candidatura = VotingUser.objects.filter(candidatura=2)
        
        for usr in usuarios_candidatura:
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
        for nousr in nousuarios_candidatura:
            assert self.driver.find_element(By.ID, "id_options-1-option").text ==nousr.user.first_name+" "+nousr.user.last_name+ " / "+str(nousr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
            assert value == "2"
       

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de máster de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Master"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
        for nousr in nousuarios_candidatura.filter(curso="Master"):
            assert self.driver.find_element(By.ID, "id_options-1-option").text ==nousr.user.first_name+" "+nousr.user.last_name+ " / "+str(nousr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
            assert value == "2"
        

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de cuarto de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Fourth"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
        for nousr in nousuarios_candidatura.filter(curso="Fourth"):
            assert self.driver.find_element(By.ID, "id_options-1-option").text ==nousr.user.first_name+" "+nousr.user.last_name+ " / "+str(nousr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
            assert value == "2"
        

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de tercero de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Third"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
        for nousr in nousuarios_candidatura.filter(curso="Third"):
            assert self.driver.find_element(By.ID, "id_options-1-option").text ==nousr.user.first_name+" "+nousr.user.last_name+ " / "+str(nousr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
            assert value == "2"
        

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de segundo de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="Second"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
        for nousr in nousuarios_candidatura.filter(curso="Second"):
            assert self.driver.find_element(By.ID, "id_options-1-option").text ==nousr.user.first_name+" "+nousr.user.last_name+ " / "+str(nousr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
            assert value == "2"
        

        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"').click()
        assert self.driver.find_element(By.ID, "id_desc").text == 'elige representante de primero de la candidatura "Candidatura con representantes elegidos"'
        for usr in usuarios_candidatura.filter(curso="First"):
            assert self.driver.find_element(By.ID, "id_options-0-option").text ==usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
            assert value == "1"
        for nousr in nousuarios_candidatura.filter(curso="First"):
            assert self.driver.find_element(By.ID, "id_options-1-option").text ==nousr.user.first_name+" "+nousr.user.last_name+ " / "+str(nousr.user.pk)
            value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
            assert value == "2"

   def test_primaryvoting_2questions(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Auths").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Test")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys("localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba")
        self.driver.find_element(By.ID, "id_delegadoCentro").click()
        dropdown = self.driver.find_element(By.ID, "id_delegadoCentro")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_delegadoCentro").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoPrimero").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoPrimero")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoPrimero").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoSegundo").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoSegundo")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoSegundo").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoTercero").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoTercero")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoTercero").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoCuarto").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoCuarto")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoCuarto").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoMaster").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoMaster")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoMaster").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Test 1")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.CSS_SELECTOR, "#options-1 > .field-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("0")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        element = self.driver.find_element(By.ID, "id_options-1-number")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("admin")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("admin")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Test 2")
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        element = self.driver.find_element(By.ID, "id_options-1-number")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("admin")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("admin")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Test")
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Test")
        dropdown = self.driver.find_element(By.ID, "id_question")
        dropdown.find_element(By.XPATH, "//option[. = 'Test 1']").click()
        self.driver.find_element(By.ID, "id_tipo").click()
        self.driver.find_element(By.ID, "id_tipo").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        dropdown = self.driver.find_element(By.ID, "id_candiancy")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura de prueba']").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        self.driver.find_element(By.NAME, "_save").click()
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".success")
        assert len(elements) > 0
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > a").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > div").click()
        value = self.driver.find_element(By.ID, "id_name").get_attribute("value")
        assert value == "Test"
        element = self.driver.find_element(By.ID, "id_question")
        locator = "option[@value='{}']".format(element.get_attribute("value"))
        selected_text = element.find_element(By.XPATH, locator).text
        assert selected_text == "Test 1"
        element = self.driver.find_element(By.ID, "id_tipo")
        locator = "option[@value='{}']".format(element.get_attribute("value"))
        selected_text = element.find_element(By.XPATH, locator).text
        assert selected_text == "Primary voting"
        element = self.driver.find_element(By.ID, "id_candiancy")
        locator = "option[@value='{}']".format(element.get_attribute("value"))
        selected_text = element.find_element(By.XPATH, locator).text
        assert selected_text == "Candidatura de prueba"
  
   def test_primaryvoting_errorquestions(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Auths").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Test")
        self.driver.find_element(By.ID, "id_url").click()
        self.driver.find_element(By.ID, "id_url").send_keys("localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba")
        self.driver.find_element(By.ID, "id_delegadoCentro").click()
        dropdown = self.driver.find_element(By.ID, "id_delegadoCentro")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_delegadoCentro").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoPrimero").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoPrimero")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoPrimero").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoSegundo").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoSegundo")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoSegundo").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoTercero").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoTercero")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoTercero").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoCuarto").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoCuarto")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoCuarto").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoMaster").click()
        dropdown = self.driver.find_element(By.ID, "id_representanteDelegadoMaster")
        dropdown.find_element(By.XPATH, "//option[. = 'admin']").click()
        self.driver.find_element(By.ID, "id_representanteDelegadoMaster").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Test 1")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.CSS_SELECTOR, "#options-1 > .field-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("0")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        element = self.driver.find_element(By.ID, "id_options-1-number")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("admin")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("admin")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Test 2")
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        element = self.driver.find_element(By.ID, "id_options-1-number")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("admin")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("admin")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Test Fallo")
        self.driver.find_element(By.ID, "id_candiancy").click()
        dropdown = self.driver.find_element(By.ID, "id_candiancy")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura de prueba']").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-auths").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        self.driver.find_element(By.NAME, "_save").click()
        elements = self.driver.find_elements(By.CSS_SELECTOR, ".errornote")
        assert len(elements) > 0
        elements = self.driver.find_elements(By.CSS_SELECTOR, "li")
        assert len(elements) > 0

   def test_view_createPrimawyWithNoCandiancyFails(self):
        """No se puede crear una votacion primaria sin candidatura."""
        # Log in
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        #Creamos una pregunta
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        # Creamos una auth
        self.driver.find_element(By.CSS_SELECTOR, ".model-auth .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("localhost")
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        # Crear votacion primaria sin candidatura
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Votacion primaria sin candidatura")
        self.driver.find_element(By.ID, "id_desc").send_keys("Va a fallar pues debe tener una candidatura")
        dropdown = self.driver.find_element(By.ID, "id_question")
        dropdown.find_element(By.XPATH, "//option[. = 'Pregunta']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_tipo").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.CSS_SELECTOR, "li").click()
        # Comprobar que no se puede
        assert self.driver.find_element(By.CSS_SELECTOR, "li").text == "Primary votings must have a candidancy"

   def test_view_verifyCantStopVotingBeforeStart(self):
        """test: no se actualiza la fecha de fin de votación si esta no ha empezado."""
        self.driver.implicitly_wait(50)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-auth .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("localhost")
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("prueba")
        self.driver.find_element(By.ID, "id_desc").send_keys("prueba")
        dropdown = self.driver.find_element(By.ID, "id_question")
        dropdown.find_element(By.XPATH, "//option[. = 'Pregunta']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        dropdown = self.driver.find_element(By.ID, "id_candiancy")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura de prueba con representantes elegidos']").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "¡No se puede detener una votación antes de que empiece!"
        assert self.driver.find_element(By.CSS_SELECTOR, ".row1 > .field-end_date").text == "-"

   def test_crear_votacion_de_candidatura_vacia_fail(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura vacía")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Realizar las votaciones primarias de candidaturas seleccionadas']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Debe haber al menos un miembro de cada curso en la candidatura."
        self.driver.close()

   def test_crear_votacion_de_candidatura_incompleta_fail(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura incompleta")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Voting users").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_user").click()
        dropdown = self.driver.find_element(By.ID, "id_user")
        dropdown.find_element(By.XPATH, "//option[. = 'noadmin']").click()
        self.driver.find_element(By.ID, "id_user").click()
        self.driver.find_element(By.ID, "id_dni").click()
        self.driver.find_element(By.ID, "id_dni").send_keys("12345678A")
        dropdown = self.driver.find_element(By.ID, "id_sexo")
        dropdown.find_element(By.XPATH, "//option[. = 'Man']").click()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_sexo").click()
        dropdown = self.driver.find_element(By.ID, "id_candidatura")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura incompleta']").click()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_candidatura").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Realizar las votaciones primarias de candidaturas seleccionadas']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Debe haber al menos un miembro de cada curso en la candidatura."
        self.driver.close()

   def crear_votacion(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Voting users").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_user").click()
        dropdown = self.driver.find_element(By.ID, "id_user")
        dropdown.find_element(By.XPATH, "//option[. = 'noadmin']").click()
        self.driver.find_element(By.ID, "id_user").click()
        self.driver.find_element(By.ID, "id_dni").click()
        self.driver.find_element(By.ID, "id_dni").send_keys("12345678A")
        dropdown = self.driver.find_element(By.ID, "id_sexo")
        dropdown.find_element(By.XPATH, "//option[. = 'Man']").click()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_sexo").click()
        dropdown = self.driver.find_element(By.ID, "id_candidatura")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura de prueba']").click()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_candidatura").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación general con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()

   def test_actualizarStartStop(self):
        """test: no se actualiza la fecha de comienzo de votación si esta ya ha empezado ni la de fin si ya ha acabado."""
        self.crear_votacion()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Votación general 1 already started."
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Votación general 1 already stopped."

   def test_update_voting_started(self):
        self.crear_votacion()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Nuevo nombre")
        self.driver.find_element(By.CSS_SELECTOR, ".field-desc > div").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Nueva descripción")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.ID, "content").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".errorlist > li").text == "A voting that has already started cannot be updated."
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > div").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > div").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").click()
        element = self.driver.find_element(By.ID, "id_name")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-desc > div").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Elige a los representantes de tu centro"
        self.driver.close()
      
   def test_view_verifyCantStartPrimaryVotingWithIncorrectQuestionNumber(self):
        """test: no se empieza la votación primaria si el número de sus preguntas no es el correcto."""
        self.driver.implicitly_wait(50)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-auth .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("localhost")
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("prueba")
        self.driver.find_element(By.ID, "id_desc").send_keys("prueba")
        dropdown = self.driver.find_element(By.ID, "id_question")
        dropdown.find_element(By.XPATH, "//option[. = 'Pregunta']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        dropdown = self.driver.find_element(By.ID, "id_candiancy")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura de prueba con representantes elegidos']").click()
        self.driver.find_element(By.ID, "id_candiancy").click()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "La votación primaria prueba debe tener 6 preguntas, 1 para cada curso y otra para el delegado de centro."
        assert self.driver.find_element(By.CSS_SELECTOR, ".row1 > .field-start_date").text == "-"
            
 
class GeneralVotingTestCase(StaticLiveServerTestCase):
    def setUp(self):
        #Load base test functionality for decide
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()    

    def tearDown(self):
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def test_update_generalVoting(self):
        """test: se puede actualizar una votacion con tipo general."""
        v = Voting.objects.create(desc='Descripcion de prueba', name="Votacion de prueba", tipo='GV')
        self.assertEqual(v.name, 'Votacion de prueba')
        self.assertEqual(v.desc, 'Descripcion de prueba')
        # Actualizamos la votación
        v.name='Nuevo nombre'
        v.desc='Nueva descripcion'
        v.save()
        # Y vemos que se han aplicado los cambios
        self.assertEqual(v.name, 'Nuevo nombre',)
        self.assertEqual(v.desc, 'Nueva descripcion')
        v.delete()

    def test_delete_generalVoting(self):
        """test: se puede borrar una votacion con tipo general."""
        v = Voting.objects.create(desc='Descripcion de prueba', name="Votacion de prueba", tipo='GV')
        v_pk = v.pk
        self.assertEqual(Voting.objects.filter(pk=v_pk).count(), 1)
        # Borramos la votacion
        v.delete()
        # Y comprobamos que se ha borrado 
        self.assertEqual(Voting.objects.filter(pk=v_pk).count(), 0)
  
    def test_view_CreateGeneralVotingOneCandiancyCorrect(self):
        """test: se crea correctamente la votación general con una candidatura que ha hecho primarias."""
        adminId = str(User.objects.get(username='admin').id)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación general con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".success").text == "¡La elección general se ha creado!"
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1").text == "Votación general 1"
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige a los miembros de delegación de alumnos").text == "Votación general 1: Elige a los miembros de delegación de alumnos"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado al centro").text == "Votación general 1: Elige al delegado al centro"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado del master").text == "Votación general 1: Elige al delegado del master"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de cuarto").text == "Votación general 1: Elige al delegado de cuarto"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de tercero").text == "Votación general 1: Elige al delegado de tercero"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de segundo").text == "Votación general 1: Elige al delegado de segundo"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de primero").text == "Votación general 1: Elige al delegado de primero"
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige a los miembros de delegación de alumnos").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige a los miembros de delegación de alumnos"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado al centro").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado al centro"
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname admin_lastname / ' + adminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de cuarto").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de cuarto"
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname admin_lastname / ' + adminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de tercero").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de tercero"
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname admin_lastname / ' + adminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de segundo").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de segundo"
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname admin_lastname / ' + adminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de primero").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de primero"
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'admin_firstname admin_lastname / ' + adminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        self.driver.find_element(By.ID, "id_options-0-option").click()
    def test_view_createGeneralVotingOneCandiancyIncorrect(self):
        """test: no se crea  la votación general con una candidatura que no ha hecho primarias."""
        self.driver.implicitly_wait(30)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes sin elegir") 
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación general con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        element = self.driver.find_element(By.CSS_SELECTOR, ".error")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Se ha seleccionado alguna candidatura que no había celebrado votaciones primarias para elegir a los representantes"
          
    def test_view_createGeneralVotingMoreThenOneCandiancyCorrect(self):
        """test: se crea correctamente la votación general con más de una candidatura que han hecho primarias."""
        adminId = str(User.objects.get(username='admin').id)
        noAdminId = str(User.objects.get(username='noadmin').id)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba 2 con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('noadmin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('noadmin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row2 .action-select").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación general con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".success").text == "¡La elección general se ha creado!"
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1").text == "Votación general 1"
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige a los miembros de delegación de alumnos").text == "Votación general 1: Elige a los miembros de delegación de alumnos"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado al centro").text == "Votación general 1: Elige al delegado al centro"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado del master").text == "Votación general 1: Elige al delegado del master"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de cuarto").text == "Votación general 1: Elige al delegado de cuarto"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de tercero").text == "Votación general 1: Elige al delegado de tercero"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de segundo").text == "Votación general 1: Elige al delegado de segundo"
        assert self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de primero").text == "Votación general 1: Elige al delegado de primero"
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige a los miembros de delegación de alumnos").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige a los miembros de delegación de alumnos"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado al centro").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado al centro"
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname admin_lastname / ' + adminId
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'noadmin_firstname noadmin_lastname / ' + noAdminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de cuarto").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de cuarto"
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname admin_lastname / ' +adminId
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'noadmin_firstname noadmin_lastname / ' + noAdminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de tercero").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de tercero"
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname admin_lastname / ' + adminId
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'noadmin_firstname noadmin_lastname / ' + noAdminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de segundo").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de segundo"
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname admin_lastname / ' + adminId
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'noadmin_firstname noadmin_lastname / ' + noAdminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de primero").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de primero"
        assert self.driver.find_element(By.ID, "id_options-1-option").text == 'admin_firstname admin_lastname / ' + adminId
        assert self.driver.find_element(By.ID, "id_options-0-option").text == 'noadmin_firstname noadmin_lastname / ' + noAdminId
        value = self.driver.find_element(By.ID, "id_options-0-number").get_attribute("value")
        assert value == "1"
        value = self.driver.find_element(By.ID, "id_options-1-number").get_attribute("value")
        assert value == "2"
    def test_view_createGeneralVotingMoreThenOneCandiancyIncorrect(self):
        """test: no se crea la votación general con varias candidatura si una no ha celebrado primarias."""
        self.driver.implicitly_wait(30)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes elegidos") 
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba con representantes elegidos")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.CSS_SELECTOR, ".row2 .action-select").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación general con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        element = self.driver.find_element(By.CSS_SELECTOR, ".error")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Se ha seleccionado alguna candidatura que no había celebrado votaciones primarias para elegir a los representantes"
    def test_view_verifyCantStartGeneralVotingWithIncorrectQuestionNumber(self):
        """test: no se empieza la votación general si el número de sus preguntas no es el correcto."""
        self.driver.implicitly_wait(50)
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-question .addlink").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Pregunta")
        self.driver.find_element(By.ID, "id_options-0-number").click()
        self.driver.find_element(By.ID, "id_options-0-number").send_keys("1")
        self.driver.find_element(By.ID, "id_options-0-option").click()
        self.driver.find_element(By.ID, "id_options-0-option").send_keys("Opcion1")
        self.driver.find_element(By.ID, "id_options-1-number").click()
        self.driver.find_element(By.ID, "id_options-1-number").send_keys("2")
        self.driver.find_element(By.ID, "id_options-1-option").click()
        self.driver.find_element(By.ID, "id_options-1-option").send_keys("Opcion2")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-auth .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("localhost")
        self.driver.find_element(By.ID, "id_url").send_keys("http://localhost:8000")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.CSS_SELECTOR, ".model-voting .addlink").click()
        self.driver.find_element(By.ID, "id_name").send_keys("prueba")
        self.driver.find_element(By.ID, "id_desc").send_keys("prueba")
        dropdown = self.driver.find_element(By.ID, "id_question")
        dropdown.find_element(By.XPATH, "//option[. = 'Pregunta']").click()
        dropdown = self.driver.find_element(By.ID, "id_auths")
        dropdown.find_element(By.XPATH, "//option[. = 'http://localhost:8000']").click()
        dropdown = self.driver.find_element(By.ID, "id_tipo")
        dropdown.find_element(By.XPATH, "//option[. = 'General voting']").click()
        element = self.driver.find_element(By.ID, "id_tipo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "La votación general prueba debe tener 7 preguntas, 1 para cada curso, otra para el delegado de centro y otra para la delegación de alumnos."
        assert self.driver.find_element(By.CSS_SELECTOR, ".row1 > .field-start_date").text == "-"

    def crear_votacion(self):
        self.driver.get(f'{self.live_server_url}/admin/')
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.ID, "id_password").send_keys(Keys.ENTER)
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_nombre").send_keys("Candidatura de prueba")
        select = Select(self.driver.find_element(By.ID, "id_delegadoCentro"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoPrimero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoSegundo"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoTercero"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoCuarto"))
        select.select_by_visible_text('admin')
        select = Select(self.driver.find_element(By.ID, "id_representanteDelegadoMaster"))
        select.select_by_visible_text('admin')
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Voting users").click()
        self.driver.find_element(By.CSS_SELECTOR, ".addlink").click()
        self.driver.find_element(By.ID, "id_user").click()
        dropdown = self.driver.find_element(By.ID, "id_user")
        dropdown.find_element(By.XPATH, "//option[. = 'noadmin']").click()
        self.driver.find_element(By.ID, "id_user").click()
        self.driver.find_element(By.ID, "id_dni").click()
        self.driver.find_element(By.ID, "id_dni").send_keys("12345678A")
        dropdown = self.driver.find_element(By.ID, "id_sexo")
        dropdown.find_element(By.XPATH, "//option[. = 'Man']").click()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_sexo")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_sexo").click()
        dropdown = self.driver.find_element(By.ID, "id_candidatura")
        dropdown.find_element(By.XPATH, "//option[. = 'Candidatura de prueba']").click()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.ID, "id_candidatura")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.ID, "id_candidatura").click()
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.LINK_TEXT, "Home").click()
        self.driver.find_element(By.LINK_TEXT, "Candidaturas").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Crear votación general con las candidaturas seleccionadas']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()

    def test_actualizarStartStop(self):
        """test: no se actualiza la fecha de comienzo de votación si esta ya ha empezado ni la de fin si ya ha acabado."""
        self.crear_votacion()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Votación general 1 already started."
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Stop']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "Votación general 1 already stopped."

    def test_update_voting_started(self):
        self.crear_votacion()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").send_keys("Nuevo nombre")
        self.driver.find_element(By.CSS_SELECTOR, ".field-desc > div").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Nueva descripción")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.ID, "content").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".errorlist > li").text == "A voting that has already started cannot be updated."
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > div").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-name > div").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.ID, "id_name").click()
        element = self.driver.find_element(By.ID, "id_name")
        actions = ActionChains(self.driver)
        actions.double_click(element).perform()
        self.driver.find_element(By.ID, "id_name").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-desc > div").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Elige a los representantes de tu centro"
        self.driver.close()
   
    def test_update_question_voting_started(self):
        self.crear_votacion()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de cuarto").click()
        self.driver.find_element(By.CSS_SELECTOR, ".field-desc").click()
        self.driver.find_element(By.ID, "id_desc").send_keys("Nueva descripción")
        self.driver.find_element(By.NAME, "_save").click()
        self.driver.find_element(By.ID, "content").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".errorlist > li").text == "A question from a voting that has started cannot be updated."
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.LINK_TEXT, "Votación general 1: Elige al delegado de cuarto").click()
        self.driver.find_element(By.CSS_SELECTOR, ".form-row > div").click()
        assert self.driver.find_element(By.ID, "id_desc").text == "Votación general 1: Elige al delegado de cuarto"

    def test_delete_question_voting_started_fail(self):
        self.crear_votacion()
        num_q = Question.objects.count()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Votings").click()
        self.driver.find_element(By.ID, "action-toggle").click()
        self.driver.find_element(By.NAME, "action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Start']").click()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.LINK_TEXT, "Voting").click()
        self.driver.find_element(By.LINK_TEXT, "Questions").click()
        self.driver.find_element(By.NAME, "_selected_action").click()
        dropdown = self.driver.find_element(By.NAME, "action")
        dropdown.find_element(By.XPATH, "//option[. = 'Delete selected']").click()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).click_and_hold().perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
        element = self.driver.find_element(By.NAME, "action")
        actions = ActionChains(self.driver)
        actions.move_to_element(element).release().perform()
        self.driver.find_element(By.NAME, "action").click()
        self.driver.find_element(By.NAME, "index").click()
        self.driver.find_element(By.CSS_SELECTOR, ".error").click()
        assert self.driver.find_element(By.CSS_SELECTOR, ".error").text == "A question from a voting that has started cannot be deleted."
        num_q2 = Question.objects.count()
        self.assertEqual(num_q,num_q2)