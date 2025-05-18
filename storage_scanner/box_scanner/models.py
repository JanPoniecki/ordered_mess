from django.db import models
import json

class Room(models.Model):
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7)  # Kolor w formacie HEX np. "#FF5733"

    def __str__(self):
        return self.name

class Container(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(Room, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} ({self.location.name})"

class Item(models.Model):
    name = models.CharField(max_length=255)
    features = models.JSONField(default=list)  # Store features as a JSON array
    image = models.ImageField(upload_to='items/')
    container = models.ForeignKey(Container, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    def add_feature(self, feature):
        """Add a new feature to the list"""
        if not isinstance(self.features, list):
            self.features = []
        self.features.append(feature)
        self.save()

    def get_features(self):
        """Get features as a list"""
        return self.features if isinstance(self.features, list) else []
