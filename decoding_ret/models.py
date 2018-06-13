from otree.api import (
    models, widgets, BaseConstants, BaseSubsession, BaseGroup, BasePlayer,
    Currency as c, currency_range
)
from django.db import models as djmodels
import random
from django.db.models.signals import post_save
from .fields import ListField
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
    question = ListField()
    correct_answer = ListField()
    digits = ListField()
    letters = ListField()
    answer = models.StringField(null=True)
    is_correct = models.BooleanField()

    def get_body(self):
        return {
            'question': self.question,
            'digits': self.digits,
            'letters': self.letters,
        }

    def decoding_dict(self):
        keys = self.digits
        values = self.letters
        dictionary = dict(zip(keys, values))
        return dictionary

    def get_decoded(self, to_decode):
        decdict = self.decoding_dict()
        return [decdict[i] for i in to_decode]

    def as_dict(self):
        return {
            'correct_answer': self.correct_answer,
            'body': self.get_body()
        }

    @classmethod
    def post_create(cls, sender, instance, created, *args, **kwargs):
        if not created:
            return
        digs = list(string.digits)
        random.shuffle(digs)
        instance.digits = digs
        lts = random.sample(string.ascii_lowercase, k=Constants.num_letters)
        instance.letters = lts
        instance.question = random.choices(string.digits, k=Constants.task_len)
        instance.correct_answer = instance.get_decoded(instance.question)
        instance.save()


post_save.connect(Task.post_create, sender=Task)
