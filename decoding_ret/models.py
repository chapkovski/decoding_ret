from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
import random
from django.db.models.signals import post_save
from django.db.models import Sum
import string
import json

author = 'Philipp Chapkovski, chapkovski@gmail.com'

doc = """
Real Effort Task; decoding letters
"""


class Constants(BaseConstants):
    name_in_url = 'decoding_ret'
    players_per_group = None
    num_rounds = 1
    task_len = 8
    num_digits = 10
    num_letters = 10


class Subsession(BaseSubsession):
    ...


class Group(BaseGroup):
    pass


class Player(BasePlayer):
    dump_tasks = models.LongStringField()
    num_answered = models.IntegerField(initial=0)
    num_correct = models.IntegerField(initial=0)
    num_incorrect = models.IntegerField(initial=0)


class Task(djmodels.Model):
    player = djmodels.ForeignKey(to=Player, related_name='tasks')
    question = models.StringField()
    correct_answer = models.StringField()
    digits = models.StringField()
    letters = models.StringField()
    answer = models.StringField(null=True)

    def get_body(self):
        return {
            'question': json.loads(self.question),
            'digits': json.loads(self.digits),
            'letters': json.loads(self.letters),
        }

    def decoding_dict(self):
        keys = json.loads(self.digits)
        values = json.loads(self.letters)
        dictionary = dict(zip(keys, values))
        return dictionary

    def get_decoded(self, to_decode):
        decdict = self.decoding_dict()
        return [decdict[i] for i in to_decode]

    def as_dict(self):
        return {
            'correct_answer': json.loads(self.correct_answer),
            'body': self.get_body()
        }

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if not created:
            return
        digs = list(string.digits)
        random.shuffle(digs)
        instance.digits = json.dumps(digs)
        lts = random.sample(string.ascii_lowercase, k=Constants.num_letters)
        instance.letters = json.dumps(lts)
        instance.question = json.dumps(random.choices(string.digits, k=Constants.task_len))
        instance.correct_answer = json.dumps(instance.get_decoded(json.loads(instance.question)))
        instance.save()


post_save.connect(Task.post_create, sender=Task)
