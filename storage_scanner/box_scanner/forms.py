from django import forms
from .models import Room, Container, Item

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = ['name', 'color']

class ContainerForm(forms.ModelForm):
    class Meta:
        model = Container
        fields = ['name', 'location']

class ItemContainerForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['container']  