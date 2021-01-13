from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from base import mods
from base.models import Auth, Key
from census.models import Census
import re
import datetime


class Question(models.Model):
    desc = models.TextField()

    def clean(self):
        votings = Voting.objects.all()
        for v in votings:
            if isinstance(v.start_date,datetime.datetime):
                for q in v.question.all():
                    if self.pk == q.pk:
                        raise ValidationError('A question from a voting that has started cannot be updated.')

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)

class Candidatura(models.Model):
    nombre = models.TextField()
    delegadoCentro = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='delegado_centro')
    representanteDelegadoPrimero = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='representante_primero')
    representanteDelegadoSegundo = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='representante_segundo')
    representanteDelegadoTercero = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='representante_tercero')
    representanteDelegadoCuarto = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='representante_cuarto')
    representanteDelegadoMaster = models.ForeignKey(User, blank=True, null=True, on_delete=models.CASCADE, related_name='representante_master')

    def __str__(self):
        return self.nombre


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ManyToManyField(Question, related_name='voting')

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    PRIMRAY_VOTING = 'PV'
    GENERAL_VOTING = 'GV'

    TYPES = [
        (PRIMRAY_VOTING, 'Primary voting'),
        (GENERAL_VOTING, 'General voting')
    ]

    tipo = models.TextField(null=False, choices=TYPES, default=PRIMRAY_VOTING)

    candiancy = models.ForeignKey(Candidatura, related_name='voting', blank=True, on_delete=models.CASCADE, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def clean(self):

        if isinstance(self.start_date,datetime.datetime):
            raise ValidationError('A voting that has already started cannot be updated.')
        if(self.tipo=='PV'):
            if(self.candiancy == None):
                raise ValidationError('Primary votings must have a candidancy')
        if(self.tipo=='GV'):
            if(self.candiancy!=None):
                raise ValidationError('General votings must not have a candidancy')


    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [i['data'] for i in votes]

    def tally_votes(self, token=''):
        """
        The tally is a shuffle and then a decrypt
        """

        votes = self.get_votes(token)
        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        res = []
        for vt in votes:
            # Hacemos una copia para modificarla
            aux = vt.copy()
            for i in aux:
                a = int(aux[i]['a'])
                b = int(aux[i]['b'])
                #  decrypt 
                data = {"msgs": [[a,b]]}
                response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                        response=True)
                aux[i] = response.json()[0]
                if response.status_code != 200:
                    # TODO: manage error
                    pass
                resp = response.json()[0]
                if i=='sex':
                    if resp == 1:
                        aux[i]='Man'
                    if resp == 2:
                        aux[i]='Woman'
                    if resp == 3:
                        aux[i]='Other'
                elif i=='grade':
                    if resp == 1:
                        aux[i]='Software'
                    if resp == 2:
                        aux[i]='Computer Technology'
                    if resp == 3:
                        aux[i]='Information Technology'
                    if resp == 4:
                        aux[i]='Health'
                elif i=='year':
                    if resp == 1:
                        aux[i]='First'
                    if resp == 2:
                        aux[i]='Second'
                    if resp == 3:
                        aux[i]='Third'
                    if resp == 4:
                        aux[i]='Fourth'
                    if resp == 5:
                        aux[i]='Master'
                else:
                    aux[i] = resp
                
            res.append(aux)
        self.tally = res
        self.save()

        self.do_postproc()

    def do_postproc(self):
        from authentication.models import VotingUser
        tally = self.tally
        questions= self.question.all()
        tipo = self.tipo
        primaria=False
        if tipo=='PV':
            primaria=True
        tituloV = self.name
        desc = self.desc
        fecha_inicio = self.start_date.isoformat(' ')
        fecha_fin = self.end_date.isoformat(' ')
        id_votacion = self.id
        votantes = Census.objects.filter(voting_id=self.id).values_list('voter_id', flat=True)
        censados = User.objects.filter(id__in=votantes)
        n_personas_censo = votantes.count()
        if isinstance(tally, list):
            n_votantes = len(tally)
            n_votantes_m = len([i for i in tally if i['sex']== 'Man'])
            n_votantes_f = len([i for i in tally if i['sex']== 'Woman'])
            if n_votantes==0:
                media_edad_votantes = 0.0
            else:
                media_edad_votantes = float(sum(i['age'] for i in tally)/n_votantes)
        else:
            n_votantes = 0
            n_votantes_m = 0
            n_votantes_f = 0
            media_edad_votantes = 0.0
        n_hombres_censo = VotingUser.objects.filter(user__in=censados).filter(sexo='Man').count()
        
        n_mujeres_censo = VotingUser.objects.filter(user__in=censados).filter(sexo='Woman').count()
        
        

        preguntas = []
        
        for pregunta in questions:
            opts = []
            aux = False
            titulo = pregunta.desc
            options = pregunta.options.all()
            numero_candidatos= options.count()
            if "delegación de alumnos" in titulo or "delegado al centro" in titulo or "delegado de centro" in titulo:
                aux = True
            for opt in options:
                voto_curso= []
                if isinstance(tally, list):
                        lvotos_opcion= [vote for vote in tally if titulo in vote and int(vote[titulo])==opt.number]
                        votes =len(lvotos_opcion)
                        n_votantes_m_opcion = len([i for i in lvotos_opcion if i['sex']== 'Man'])
                        n_votantes_f_opcion = len([i for i in lvotos_opcion if i['sex']== 'Woman'])
                        if votes==0:
                            media_edad_votantes_opcion=0.0
                        else:
                            media_edad_votantes_opcion = float(sum(i['age'] for i in lvotos_opcion)/votes)
                else:
                        votes = 0
                        n_votantes_m_opcion = 0
                        n_votantes_f_opcion = 0
                        media_edad_votantes_opcion = 0.0
                if aux:
                    if isinstance(tally, list):
                        n_votos_primero = len([i for i in lvotos_opcion if i['year']=='First'])
                        n_votos_segundo = len([i for i in lvotos_opcion if i['year']=='Second'])
                        n_votos_tercero = len([i for i in lvotos_opcion if i['year']=='Third'])
                        n_votos_cuarto = len([i for i in lvotos_opcion if i['year']=='Fourth'])
                        n_votos_master = len([i for i in lvotos_opcion if i['year']=='Master'])
                    else:
                        n_votos_primero = 0
                        n_votos_segundo = 0
                        n_votos_tercero = 0
                        n_votos_cuarto = 0
                        n_votos_master = 0
                    voto_curso.append({
                    'primero': n_votos_primero,
                    'segundo': n_votos_segundo,
                    'tercero': n_votos_tercero,
                    'cuarto': n_votos_cuarto,
                    'master': n_votos_master
                    })
                    opts.append({
                    'nombre': opt.option,
                    'numero': opt.number,
                    'voto_F': n_votantes_f_opcion,
                    'voto_M': n_votantes_m_opcion,
                    'media_edad': media_edad_votantes_opcion,
                    'voto_curso': voto_curso,
                    'votes': votes
                    })
                else:
                    opts.append({
                    'nombre': opt.option,
                    'numero': opt.number,
                    'voto_F': n_votantes_f_opcion,
                    'voto_M': n_votantes_m_opcion,
                    'media_edad': media_edad_votantes_opcion,
                    'votes': votes
                    })

            if aux:
                preguntas.append({
                'titulo': titulo,
                'numero_candidatos': numero_candidatos,
                'opts': sorted(opts,key = lambda i: i['votes'],reverse=True)
                })
            else:
                if 'primero' in titulo:
                    n_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='First').count()
                    nh_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='First').filter(sexo='Man').count()
                    nm_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='First').filter(sexo='Woman').count()
                    if isinstance(tally, list):
                        lvotos_pregunta= [vote for vote in tally if titulo in vote and vote['year']=='First']
                        n_votantes_pregunta = len(lvotos_pregunta)
                        n_votantes_m_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        n_votantes_f_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        if n_votantes_pregunta==0:
                            media_edad_votantes_pregunta= 0.0
                        else:
                            media_edad_votantes_pregunta = float(sum(i['age'] for i in lvotos_pregunta)/n_votantes_pregunta)
                    else:
                        n_votantes_pregunta = 0
                        n_votantes_m_pregunta = 0
                        n_votantes_f_pregunta = 0
                        media_edad_votantes_pregunta = 0
                elif 'segundo' in titulo:
                    n_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Second').count()
                    nh_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Second').filter(sexo='Man').count()
                    nm_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Second').filter(sexo='Woman').count()
                    if isinstance(tally, list):
                        lvotos_pregunta= [vote for vote in tally if titulo in vote and vote['year']=='Second']
                        n_votantes_pregunta = len(lvotos_pregunta)
                        n_votantes_m_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        n_votantes_f_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        if n_votantes_pregunta==0:
                            media_edad_votantes_pregunta= 0.0
                        else:
                            media_edad_votantes_pregunta = float(sum(i['age'] for i in lvotos_pregunta)/n_votantes_pregunta)
                    else:
                        n_votantes_pregunta = 0
                        n_votantes_m_pregunta = 0
                        n_votantes_f_pregunta = 0
                        media_edad_votantes_pregunta = 0
                elif 'tercero' in titulo:
                    n_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Third').count()
                    nh_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Third').filter(sexo='Man').count()
                    nm_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Third').filter(sexo='Woman').count()
                    if isinstance(tally, list):
                        lvotos_pregunta= [vote for vote in tally if titulo in vote and vote['year']=='Third']
                        n_votantes_pregunta = len(lvotos_pregunta)
                        n_votantes_m_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        n_votantes_f_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        if n_votantes_pregunta==0:
                            media_edad_votantes_pregunta= 0.0
                        else:
                            media_edad_votantes_pregunta = float(sum(i['age'] for i in lvotos_pregunta)/n_votantes_pregunta)
                    else:
                        n_votantes_pregunta = 0
                        n_votantes_m_pregunta = 0
                        n_votantes_f_pregunta = 0
                        media_edad_votantes_pregunta = 0
                elif 'cuarto' in titulo:
                    n_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Fourth').count()
                    nh_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Fourth').filter(sexo='Man').count()
                    nm_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Fourth').filter(sexo='Woman').count()
                    if isinstance(tally, list):
                        lvotos_pregunta= [vote for vote in tally if titulo in vote and vote['year']=='Fourth']
                        n_votantes_pregunta = len(lvotos_pregunta)
                        n_votantes_m_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        n_votantes_f_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        if n_votantes_pregunta==0:
                            media_edad_votantes_pregunta= 0.0
                        else:
                            media_edad_votantes_pregunta = float(sum(i['age'] for i in lvotos_pregunta)/n_votantes_pregunta)
                    else:
                        n_votantes_pregunta = 0
                        n_votantes_m_pregunta = 0
                        n_votantes_f_pregunta = 0
                        media_edad_votantes_pregunta = 0
                else:
                    n_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Master').count()
                    nh_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Master').filter(sexo='Man').count()
                    nm_censo_pregunta = VotingUser.objects.filter(user__in=censados).filter(curso='Master').filter(sexo='Woman').count()
                    if isinstance(tally, list):
                        lvotos_pregunta= [vote for vote in tally if titulo in vote and vote['year']=='Master']
                        n_votantes_pregunta = len(lvotos_pregunta)
                        n_votantes_m_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        n_votantes_f_pregunta = len([i for i in lvotos_pregunta if i['sex']== 'Man'])
                        if n_votantes_pregunta==0:
                            media_edad_votantes_pregunta= 0.0
                        else:
                            media_edad_votantes_pregunta = float(sum(i['age'] for i in lvotos_pregunta)/n_votantes_pregunta)
                    else:
                        n_votantes_pregunta = 0
                        n_votantes_m_pregunta = 0
                        n_votantes_f_pregunta = 0
                        media_edad_votantes_pregunta = 0
                preguntas.append({
                'titulo': titulo,
                'numero_candidatos': numero_candidatos,
                'n_personas_censo': n_censo_pregunta,
                'n_votantes': n_votantes_pregunta,
                'n_hombres_censo': nh_censo_pregunta,
                'n_votantes_m': n_votantes_m_pregunta,
                'n_mujeres_censo': nm_censo_pregunta,
                'n_votantes_f': n_votantes_f_pregunta,
                'media_edad_votantes': media_edad_votantes_pregunta,
                'opts': sorted(opts,key = lambda i: i['votes'],reverse=True)
                })
            if primaria:
                ganador=re.search('\d+',opts[0]['nombre'])
                if ganador:
                    id_ganador=ganador.group(0)
                    c= Candidatura.objects.get(id=self.candiancy.id)
                    if 'primero' in titulo:
                        rep_primero=User.objects.get(id=id_ganador)
                        c.representanteDelegadoPrimero=rep_primero
                        c.save()

                    elif 'segundo' in titulo:
                        rep_segundo=User.objects.get(id=id_ganador)
                        c.representanteDelegadoSegundo=rep_segundo
                        c.save()
                    elif 'tercero' in titulo:
                        rep_tercero=User.objects.get(id=id_ganador)
                        c.representanteDelegadoTercero=rep_tercero
                        c.save()
                    elif 'cuarto' in titulo:
                        rep_cuarto=User.objects.get(id=id_ganador)
                        c.representanteDelegadoCuarto=rep_cuarto
                        c.save()
                    elif 'máster' in titulo:
                        rep_master=User.objects.get(id=id_ganador)
                        c.representanteDelegadoMaster=rep_master
                        c.save()
                    else:
                        rep_delegado_centro=User.objects.get(id=id_ganador)
                        c.delegadoCentro=rep_delegado_centro
                        c.save()
        data = { 'type': 'IDENTITY', 'id': id_votacion, 'titulo': tituloV, 'desc': desc, 'fecha_inicio': fecha_inicio, 'fecha_fin': fecha_fin, 'tipo': tipo, 'n_personas_censo': n_personas_censo, 'n_votantes': n_votantes , 'n_hombres_censo': n_hombres_censo , 'n_votantes_m': n_votantes_m , 'n_mujeres_censo': n_mujeres_censo , 'n_votantes_f': n_votantes_f , 'media_edad_votantes': media_edad_votantes , 'preguntas': preguntas }
        postp = mods.post('postproc', json=data)

        self.postproc = postp
        self.save()

    def __str__(self):
        return self.name