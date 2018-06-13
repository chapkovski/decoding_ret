from channels.generic.websockets import JsonWebsocketConsumer
import random
from decoding_ret.models import Constants, Player
import json



class TaskTracker(JsonWebsocketConsumer):
    url_pattern = (r'^/tasktracker/(?P<player_pk>[0-9]+)$')

    def clean_kwargs(self):
        self.player_pk = self.kwargs['player_pk']

    def get_player(self):
        self.clean_kwargs()
        return Player.objects.get(pk=self.player_pk)

    def prepare_task(self, player, task):
        return {'task': task.as_dict(),
                'num_correct': player.num_correct,
                'num_incorrect': player.num_incorrect,
                }

    def connect(self, message, **kwargs):
        player = self.get_player()
        unanswered_tasks = player.tasks.filter(answer__isnull=True)
        if unanswered_tasks.exists():
            task = unanswered_tasks.first()
        else:
            task = player.tasks.create()
        response = self.prepare_task(player, task)
        self.send(response)

    def receive(self, text=None, bytes=None, **kwargs):
        player = self.get_player()
        oldtask = player.tasks.filter(answer__isnull=True).first()
        oldtask.answer = text
        oldtask.save()
        player.num_answered += 1
        if text == ''.join(oldtask.correct_answer):
            player.num_correct += 1
        else:
            player.num_incorrect += 1
        newtask = task = player.tasks.create()
        response = self.prepare_task(player, newtask)
        player.save()
        self.send(response)
