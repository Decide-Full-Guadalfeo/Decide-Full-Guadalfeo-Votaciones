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
from voting.models import Candidatura, Voting, Question, QuestionOption

class CandidaturaTestCase(BaseTestCase):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()
    
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
            qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name)
            qo.save()
            i+=1

        q2= Question(desc="Elige representante de segundo de la candidatura")
        q2.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="SEGUNDO"):
            qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name)
            qo.save()
            i+=1

        q3= Question(desc="Elige representante de tercero de la candidatura")
        q3.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="TERCERO"):
            qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name)
            qo.save()
            i+=1

        q4= Question(desc="Elige representante de cuarto de la candidatura")
        q4.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="CUARTO"):
            qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name)
            qo.save()
            i+=1

        q5= Question(desc="Elige representante de master de la candidatura")
        q5.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="MASTER"):
            qo = QuestionOption(question = q5, number=i, option=usr.user.first_name+" "+usr.user.last_name)
            qo.save()
            i+=1

        q6= Question(desc="Elige representante de delegado de centro")
        q6.save()
        i=1
        for usr in usuarios_candidatura:
            qo = QuestionOption(question = q6, number=i, option=usr.user.first_name+" "+usr.user.last_name)
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
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

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
        for opt in v.question.options.all():
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

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

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
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

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
