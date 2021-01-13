import json
import requests

from random import choice

from locust import (
    HttpUser,
    SequentialTaskSet,
    TaskSet,
    task,
    between
)


HOST = "http://localhost:8000"
VOTING = 1
CANDIDATURA = 1


class DefVisualizer(TaskSet):

    @task
    def index(self):
        self.client.get("/visualizer/{0}/".format(VOTING))


class DefVoters(SequentialTaskSet):

    def on_start(self):
        with open('voters.json') as f:
            self.voters = json.loads(f.read())
        self.voter = choice(list(self.voters.items()))

    @task
    def login(self):
        username, pwd = self.voter
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()

    @task
    def getuser(self):
        self.usr= self.client.post("/authentication/getuser/", self.token).json()
        print( str(self.user))

    @task
    def voting(self):
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }
        self.client.post("/store/", json.dumps({
            "token": self.token.get('token'),
            "vote": {
                "a": "12",
                "b": "64"
            },
            "voter": self.usr.get('id'),
            "voting": VOTING
        }), headers=headers)


    def on_quit(self):
        self.voter = None

class DefCreateCandidatura(SequentialTaskSet):

    @task
    def login(self):
        username, pwd = 'root', 'complexpassword'
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()
    
    @task
    def createCandiancy(self):
        
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }

        self.client.post("/voting/candidatura/", json.dumps({
            "token": self.token.get('token'),
            "nombre": "test"
        }), headers=headers)
    
class DefCreatePrimaryVoting(SequentialTaskSet):

    def __init__(self, seq):
        SequentialTaskSet.__init__(self, seq)
        self.idCandidatura = 1

    @task
    def login(self):
        username, pwd = 'root', 'complexpassword'
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()

    @task
    def createCandiancy(self):
        
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }

        response = self.client.post("/voting/candidatura/", json.dumps({
            "token": self.token.get('token'),
            "nombre": "test"
        }), headers=headers)

        self.idCandidatura = response.json()['id']
    
    @task
    def createPrimaryVoting(self):
        
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }

        self.client.post('/voting/candidaturaprimaria/{}/'.format(self.idCandidatura), json.dumps({
            "token": self.token.get('token'),
            'action': 'start'
        }), headers=headers)

class DefCreateGeneralVoting(SequentialTaskSet):

    @task
    def login(self):
        username, pwd = 'root', 'complexpassword'
        self.token = self.client.post("/authentication/login/", {
            "username": username,
            "password": pwd,
        }).json()
    
    @task
    def createGeneralVoting(self):
        
        headers = {
            'Authorization': 'Token ' + self.token.get('token'),
            'content-type': 'application/json'
        }

        self.client.post('/voting/general/', json.dumps({
            "token": self.token.get('token'),
            'ids': [1]
        }), headers=headers)

class Visualizer(HttpUser):
    host = HOST
    tasks = [DefVisualizer]
    wait_time = between(3,5)



class Voters(HttpUser):
    host = HOST
    tasks = [DefVoters]
    wait_time= between(3,5)


# Para ejecutarlo hay que tener un usuario administrador llamado 'root' con pass='complexpassword'
class Candidatura(HttpUser):
    host = HOST
    tasks = [DefCreateCandidatura]
    wait_time= between(3,5)

# Para ejecutarlo hay que tener un usuario administrador llamado 'root' con pass='complexpassword'
class CreatePrimaryVotings(HttpUser):
    host = HOST
    tasks = [DefCreatePrimaryVoting]
    wait_time= between(3,5)

# Para ejecutarlo hay que tener un usuario administrador llamado 'root' con pass='complexpassword'
# y una candidatura con id=1 que tengo representantes elegidos
class CreateGeneralVotings(HttpUser):
    host = HOST
    tasks = [DefCreateGeneralVoting]
    wait_time= between(3,5)