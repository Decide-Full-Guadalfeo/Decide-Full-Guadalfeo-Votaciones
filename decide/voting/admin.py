from django.contrib import admin
from django.utils import timezone
from django.contrib import messages
from .models import QuestionOption
from base.models import Auth
from .models import Question
from .models import Voting
from .models import Candidatura
from .filters import StartedFilter


def start(modeladmin, request, queryset):
    for v in queryset.all():
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()


def stop(ModelAdmin, request, queryset):
    for v in queryset.all():
        v.end_date = timezone.now()
        v.save()

def realizarEleccionesPrimarias(ModelAdmin, request, queryset):
    
    for c in queryset.all():
        q1 = Question(desc='elige representante de primero de la candidatura "'+ c.nombre+'"')
        q1.save()
        i=1
        from authentication.models import VotingUser
        usuarios_candidatura = VotingUser.objects.filter(candidatura=c)    
        for usr in usuarios_candidatura.filter(curso="PRIMERO"):
            qo = QuestionOption(question = q1, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1
        q2 = Question(desc='elige representante de segundo de la candidatura "'+c.nombre+'"')
        q2.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="SEGUNDO"):
            qo = QuestionOption(question = q2, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1
        q3 = Question(desc='elige representante de tercero de la candidatura "'+ c.nombre+'"')
        q3.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="TERCERO"):
            qo = QuestionOption(question = q3, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1
        q4 = Question(desc='elige representante de cuarto de la candidatura "'+ c.nombre+'"')
        q4.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="CUARTO"):
            qo = QuestionOption(question = q4, number=i, option=usr.user.first_name+" "+usr.user.last_name+ " / "+str(usr.user.pk))
            qo.save()
            i+=1
        q5 = Question(desc='elige representante de máster de la candidatura "'+ c.nombre+'"')
        q5.save()
        i=1
        for usr in usuarios_candidatura.filter(curso="MASTER"):
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
        , tipo="Primary voting", candiancy=c)
        voting.save()
        voting.question.add(q1, q2, q3, q4, q5, q6)

        #No sé si habrá que filtrarlos de alguna manera.
        for auth in Auth.objects.all():
            voting.auths.add(auth)
        messages.add_message(request, messages.SUCCESS, "¡Las elecciones primarias se han creado!")


realizarEleccionesPrimarias.short_description="Realizar las votaciones primarias de candidaturas seleccionadas"

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

class CandidaturaAdmin(admin.ModelAdmin):
    actions = [ realizarEleccionesPrimarias , borrarVotingPrimary]

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
