from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

from django.core.validators import MaxValueValidator, MinValueValidator
from voting.models import Candidatura


class VotingUser(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    dni = models.CharField(max_length=9, unique=True, validators=[
        RegexValidator(
            regex='^\d{8}[A-Z]{1}$',
            message='El formato debe ser 8 digitos y una letra mayuscula.'
        )

    ])

    Sexo_Enum = (
        ('NONE', 'None'),
        ('HOMBRE', 'Hombre'),
        ('MUJER', 'Mujer'),
        ('OTRO', 'Otro'),
    )
    sexo = models.CharField(max_length=6, choices=Sexo_Enum, default='NONE', blank=False)
    titulo = models.CharField(max_length=100, blank=False)

    Curso_Enum = (
        ('PRIMERO', 'Primero'),
        ('SEGUNDO', 'Segundo'),
        ('TERCERO', 'Tercero'),
        ('CUARTO', 'Cuarto'),
        ('MASTER', 'Master'),
    )

    curso = models.CharField(max_length=7, choices=Curso_Enum, default='PRIMERO', blank=False)
    candidatura = models.ForeignKey(Candidatura, blank=True, null=True, on_delete=models.SET_NULL)


    def __str__(self):
        return self.user.__str__()