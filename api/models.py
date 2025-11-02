from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import os

class Photo(models.Model):
    image_path = models.CharField(max_length=255)  # Path to the image file
    farmbot_id = models.IntegerField(unique=True)  # FarmBot's image ID
    created_at = models.DateTimeField(default=timezone.now)
    coordinates = models.JSONField(default=dict, blank=True)  # X,Y,Z coordinates where photo was taken
    meta_data = models.JSONField(default=dict, blank=True)  # Additional metadata

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Photo {self.farmbot_id} - {self.created_at}'

    @property
    def filename(self):
        return os.path.basename(self.image_path)

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
