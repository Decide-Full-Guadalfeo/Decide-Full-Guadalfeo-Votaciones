from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import QuestionOption, Candidatura
from base.models import Auth
from .models import Question
from .models import Voting

from .filters import StartedFilter
from authentication.models import VotingUser
import datetime
import re
from django.contrib.auth.models import User

GENERAL_QUESTIONS = ['Elige al delegado de primero', 'Elige al delegado de segundo', 'Elige al delegado de tercero', 'Elige al delegado de cuarto','Elige al delegado del master', 'Elige al delegado al centro', 'Elige a los miembros de delegación de alumnos']
PRIMARY_QUESTIONS = ['representante de primero', 'representante de segundo', 'representante de tercero', 'representante de cuarto', 'representante de máster', 'representante de delegado de centro']

def checkVotingQuestionNames(v, descs):
    questions = Question.objects.filter(voting=v)
    for q, d in zip(questions, descs):
        if d not in q.desc:
            return False
    return True

def checkVotingQuestionOptions(v):
    questions = Question.objects.filter(voting=v)
    for q in questions:
        opts = QuestionOption.objects.filter(question=q)
        if len(opts)==0:
            return False
        else:
            for opt in opts:
                desc = opt.option
                if re.match('\D+ \/\ \d+',desc):
                    user_id = desc.split('/')[1].strip()
                    if User.objects.filter(id = user_id).count()!=1:
                        return False
                else:
                    return False
    return True

def start(modeladmin, request, queryset):
    for v in queryset.all():
        if isinstance(v.start_date,datetime.datetime):
            messages.add_message(request, messages.ERROR, v.name+" already started.")
        elif v.tipo=='PV' and Question.objects.filter(voting=v).count()!=6:
            messages.add_message(request, messages.ERROR, "La votación primaria "+v.name+" debe tener 6 preguntas, 1 para cada curso y otra para el delegado de centro.")
        elif v.tipo=='PV' and checkVotingQuestionNames(v, PRIMARY_QUESTIONS)==False:
            messages.add_message(request, messages.ERROR, "Las votaciones primarias deben seguir el formato especificado en el manual de usuario. Se recomienda crearlas de forma automatizada desde el panel de candidaturas")
        elif v.tipo=='GV' and Question.objects.filter(voting=v).count()!=7:
            messages.add_message(request, messages.ERROR, "La votación general "+v.name+" debe tener 7 preguntas, 1 para cada curso, otra para el delegado de centro y otra para la delegación de alumnos.")
        elif v.tipo=='GV' and checkVotingQuestionNames(v, GENERAL_QUESTIONS)==False:
            messages.add_message(request, messages.ERROR, "Las votaciones generales deben seguir el formato especificado en el manual de usuario. Se recomienda crearlas de forma automatizada desde el panel de candidaturas")
        elif checkVotingQuestionOptions(v)==False:
             messages.add_message(request, messages.ERROR, 'Las opciones de las preguntas de la votación deben seguir el formato especificado en el manual de usuario. Se recomienda crear la votación de forma automatizada desde el panel de candidaturas.')
        else:
            v.create_pubkey()
            v.start_date = timezone.now()
            v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        if isinstance(v.end_date,datetime.datetime):
            messages.add_message(request, messages.ERROR, v.name+" already stopped.")
        else:
            if isinstance(v.start_date,datetime.datetime):
                v.end_date = timezone.now()
                v.save()
            else:
                messages.add_message(request, messages.ERROR, "¡No se puede detener una votación antes de que empiece!")

def realizarEleccionesPrimarias(ModelAdmin, request, queryset):
    for c in queryset.all():

        usuarios_candidatura = VotingUser.objects.filter(candidatura=c)
        first = usuarios_candidatura.filter(curso="First").count()==0
        second = usuarios_candidatura.filter(curso="Second").count()==0
        third = usuarios_candidatura.filter(curso="Third").count()==0
        fourth = usuarios_candidatura.filter(curso="Fourth").count()==0
        master = usuarios_candidatura.filter(curso="Master").count()==0
        if first or second or third or fourth or master:
            messages.add_message(request, messages.ERROR, "Debe haber al menos un miembro de cada curso en la candidatura.")
        else:
            q1 = Question(desc='elige representante de primero de la candidatura "'+ c.nombre+'"')
            q1.save()
            i=1
            for usr in usuarios_candidatura.filter(curso="First"):
                qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
                qo.save()
                i+=1
            q2 = Question(desc='elige representante de segundo de la candidatura "'+c.nombre+'"')
            q2.save()
            i=1
            for usr in usuarios_candidatura.filter(curso="Second"):
                qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
                qo.save()
                i+=1
            q3 = Question(desc='elige representante de tercero de la candidatura "'+ c.nombre+'"')
            q3.save()
            i=1
            for usr in usuarios_candidatura.filter(curso="Third"):
                qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
                qo.save()
                i+=1
            q4 = Question(desc='elige representante de cuarto de la candidatura "'+ c.nombre+'"')
            q4.save()
            i=1
            for usr in usuarios_candidatura.filter(curso="Fourth"):
                qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
                qo.save()
                i+=1
            q5 = Question(desc='elige representante de máster de la candidatura "'+ c.nombre+'"')
            q5.save()
            i=1
            for usr in usuarios_candidatura.filter(curso="Master"):
                qo = QuestionOption(question = q5, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
                qo.save()
                i+=1
            q6 = Question(desc='elige representante de delegado de centro de la candidatura "'+ c.nombre+'"')
            q6.save()
            i=1
            for usr in usuarios_candidatura:
                qo = QuestionOption(question = q6, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
                qo.save()
                i+=1


            voting = Voting(name='Votaciones de la candidatura "'+c.nombre+'"',desc="Elige a los representantes de tu candidatura."
            , tipo="PV", candiancy=c)
            voting.save()
            voting.question.add(q1, q2, q3, q4, q5, q6)

            #No sé si habrá que filtrarlos de alguna manera.
            for auth in Auth.objects.all():
                voting.auths.add(auth)
            messages.add_message(request, messages.SUCCESS, "¡Las elecciones primarias se han creado!")

realizarEleccionesPrimarias.short_description="Realizar las votaciones primarias de candidaturas seleccionadas"

def realizarEleccionGeneral(ModelAdmin, request, queryset):
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
        for c in queryset.all():
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

        # Echarle un vistazo
        for auth in Auth.objects.all():
            votacion.auths.add(auth)
        messages.add_message(request, messages.SUCCESS, "¡La elección general se ha creado!")
    except Exception as e:
        # En el caso de que haya alguna candidatura que no ha celebrado primarias, borramos las prunguntas pues no se creara la votacion general
        q1.delete()
        q2.delete()
        q3.delete()
        q4.delete()
        q5.delete()
        q6.delete()
        q7.delete()
        messages.add_message(request, messages.ERROR, 'Se ha seleccionado alguna candidatura que no había celebrado votaciones primarias para elegir a los representantes')
realizarEleccionGeneral.short_description='Crear votación general con las candidaturas seleccionadas'


def tally(ModelAdmin, request, queryset):
    for v in queryset.filter(end_date__lt=timezone.now()):
        token = request.session.get('auth-token', '')
        v.tally_votes(token)

def borrarVotingPrimary(ModelAdmin, request, queryset):
    opciones=["primero","segundo","tercero","cuarto","máster","delegado de centro"]
    for c in queryset.all():
        for voting in Voting.objects.filter(candiancy=c):
            voting.delete()
        for opcion in opciones:
            for question in Question.objects.filter(desc__regex='elige representante de '+ opcion+' de la candidatura "'+c.nombre+'"'):
                question.delete()
    messages.add_message(request, messages.SUCCESS, "¡Las elecciones primarias se han borrado!")
borrarVotingPrimary.short_description= "Borrar votación de la candidatura completa('Voting', 'Questions' y 'QuestionOptions')"

class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption


class QuestionAdmin(admin.ModelAdmin):
    inlines = [QuestionOptionInline]
    actions = ['delete_selected']

    def delete_selected(self, request, obj):
        for o in obj.all():
            i=0
            votings = Voting.objects.all()
            for v in votings:
                if isinstance(v.start_date,datetime.datetime):
                    if v.question.filter(id = o.id):
                            i+=1
            if i==0:
                o.delete()
            else:
                messages.add_message(request, messages.ERROR, "A question from a voting that has started cannot be deleted.")

class CandidaturaAdmin(admin.ModelAdmin):
    actions = [ realizarEleccionesPrimarias , borrarVotingPrimary, realizarEleccionGeneral]

class VotingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    readonly_fields = ('start_date', 'end_date', 'pub_key',
                       'tally', 'postproc')
    date_hierarchy = 'start_date'
    list_filter = (StartedFilter,)
    search_fields = ('name', )

    actions = [ start, stop, tally ]


admin.site.register(Voting, VotingAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Candidatura, CandidaturaAdmin)
