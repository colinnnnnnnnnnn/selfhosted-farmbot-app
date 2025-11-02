from django.db import models
from django.contrib.auth.models import User

class Sequence(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Step(models.Model):
    sequence = models.ForeignKey(Sequence, related_name='steps', on_delete=models.CASCADE)
    order = models.PositiveIntegerField()
    command = models.CharField(max_length=100)
    parameters = models.JSONField(default=dict)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f'{self.sequence.name} - Step {self.order} - {self.command}'
