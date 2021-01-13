from rest_framework import serializers

from .models import Question, QuestionOption, Voting, Candidatura
from base.serializers import KeySerializer, AuthSerializer


class QuestionOptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ('number', 'option')

class CandidaturaSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Candidatura
        fields = ('nombre',)
class QuestionSerializer(serializers.HyperlinkedModelSerializer):
    options = QuestionOptionSerializer(many=True)
    class Meta:
        model = Question
        fields = ('desc', 'options')


class VotingSerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(many=True)
    pub_key = KeySerializer()
    auths = AuthSerializer(many=True)
    candiancy = CandidaturaSerializer()

    class Meta:
        model = Voting
        fields = ('id', 'name', 'desc', 'question', 'start_date',
                  'end_date', 'tipo', 'candiancy', 'pub_key', 'auths', 'tally', 'postproc')


class SimpleVotingSerializer(serializers.HyperlinkedModelSerializer):
    question = QuestionSerializer(many=True)
    candiancy = CandidaturaSerializer()
    
    class Meta:
        model = Voting
        fields = ('name', 'desc', 'question', 'start_date', 'end_date', 'tipo', 'candiancy')
