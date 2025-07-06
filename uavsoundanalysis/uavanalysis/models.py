from django.db import models


class Coordinates(models.Model):
    id = models.AutoField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    label = models.CharField(max_length=255)

    def __str__(self):
        return self.label
