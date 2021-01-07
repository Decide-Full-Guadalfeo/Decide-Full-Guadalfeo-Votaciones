import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User
from django.test import TestCase
from django.db.utils import IntegrityError
from rest_framework.test import APIClient
from rest_framework.test import APITestCase

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
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import time

from base.tests import BaseTestCase


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
        v1 = VotingUser(user=u1,dni="47348063C",sexo="HOMBRE",titulo="SOFTWARE",curso="PRIMERO", candidatura=c)
        v1.save()

        u2 = User(username="secondVoter", first_name="representante de",last_name="segundo curso")
        u2.save()
        v2 = VotingUser(user=u2,dni="47348063F",sexo="MUJER",titulo="SOFTWARE",curso="SEGUNDO", candidatura=c)
        v2.save()

        u3 = User(username="third", first_name="representante de",last_name="tercer curso")
        u3.save()
        v3 = VotingUser(user=u3,dni="47348068C",sexo="HOMBRE",titulo="SOFTWARE",curso="TERCERO", candidatura=c)
        v3.save()

        u4 = User(username="fourth", first_name="representante de",last_name="cuarto curso")
        u4.save()
        v4 = VotingUser(user=u4,dni="47347963C",sexo="HOMBRE",titulo="SOFTWARE",curso="CUARTO", candidatura=c)
        v4.save()

        u5 = User(username="master", first_name="representante de",last_name="master curso")
        u5.save()
        v5 = VotingUser(user=u5,dni="47297963C",sexo="HOMBRE",titulo="SOFTWARE",curso="MASTER", candidatura=c)
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
        '''test: deja crear candidatura con representantes y delegados'''
        numeroCandidaturas = Candidatura.objects.count()
        c = self.create_candidatura("completo")
        numeroCandidaturasTrasCreate = Candidatura.objects.count()
        self.assertTrue(numeroCandidaturasTrasCreate>numeroCandidaturas)
        self.assertEqual(Candidatura.objects.get(nombre="Candidatura completa").nombre, "Candidatura completa")
        c.delete()

    def test_create_candidaturaSinUsuarios(self):
        '''test: deja crear candidatura sin representantes y delegados'''
        numeroCandidaturas = Candidatura.objects.count()
        c = self.create_candidatura("nulos")
        numeroCandidaturasTrasCreate = Candidatura.objects.count()
        self.assertTrue(numeroCandidaturasTrasCreate>numeroCandidaturas)
        self.assertEqual(Candidatura.objects.get(nombre="Candidatura con nulos").representanteDelegadoCuarto, None)
        c.delete()

    def test_create_candidaturaSinNombre(self):
        '''test: NO deja crear candidatura sin nombre'''
        with self.assertRaises(Exception) as cm:
            self.create_candidatura("sinNombre")
        the_exception = cm.exception
        self.assertEqual(type(the_exception), IntegrityError)

    def test_update_candidatura(self):
        '''test: se puede actualizar una candidatura'''
        c = self.create_candidatura("nulos")
        Candidatura.objects.filter(pk=c.pk).update(nombre="Nombre actualizado")
        c.refresh_from_db()
        self.assertEqual(c.nombre, "Nombre actualizado")
        c.delete()

    def test_delete_candidatura(self):
        '''test: se borra una candidatura'''
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
        for usr in usuarios_candidatura.filter(curso="PRIMERO"):
            qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q2= Question(desc="Elige representante de segundo de la candidatura")
        q2.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="SEGUNDO"):
            qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q3= Question(desc="Elige representante de tercero de la candidatura")
        q3.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="TERCERO"):
            qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q4= Question(desc="Elige representante de cuarto de la candidatura")
        q4.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="CUARTO"):
            qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1

        q5= Question(desc="Elige representante de master de la candidatura")
        q5.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="MASTER"):
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
        '''test: deja crear bien las votaciones primarias desde la API'''
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
        '''test: falla al crear desde la API porque ya se han hecho las primarias y hay representante'''
        c = self.create_candidatura_w_voting_users()
        vu = VotingUser.objects.filter(candidatura=c, curso="PRIMERO").all()[0]
        c.representanteDelegadoPrimero=vu.user
        c.save()
        self.login()
        data = {'action': 'start'}
        response = self.client.post('/voting/candidaturaprimaria/{}/'.format(c.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        
        #FIN TEST VOTACION PRIMARIA
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
        q = Question(desc="test question")
        q.save()
        opt = QuestionOption(question=q, option="test")
        opt.save()
        q2 = Question(desc="test question 2")
        q2.save()
        opt2 = QuestionOption(question=q2, option="test2")
        opt2.save()
        v = Voting(name="Test voting",tipo='PV', candiancy=c)
        v.save()
        v.question.add(q)
        v.question.add(q2)

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

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        v.end_date = timezone.now()
        v.save()

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}
        
        for q in v.question.all():
            for opt in q.options.all():
               self.assertEqual(tally.get(opt.number, 0), clear.get(opt.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

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
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

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

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.json(), 'Voting already tallied')

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
    
    def test_view_CreateGeneralVotingOneCandiancyCorrect(self):
        '''test: se crea correctamente la votación general con una candidatura que ha hecho primarias'''
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
        '''test: no se crea  la votación general con una candidatura que no ha hecho primarias'''
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
        '''test: se crea correctamente la votación general con más de una candidatura que han hecho primarias'''
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
        '''test: no se crea la votación general con varias candidatura si una no ha celebrado primarias'''
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

