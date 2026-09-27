from django import forms
from .models import Bus, Stop

class BusForm(forms.ModelForm):
    class Meta:
        model = Bus
        fields = ['bus_number', 'route_name', 'first_bus_time', 'last_bus_time', 'is_active']
        widgets = {
            'bus_number': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'e.g. 20, 10H, 218'
            }),
            'route_name': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'e.g. Miyapur to Secunderabad'
            }),
            'first_bus_time': forms.TimeInput(attrs={
                'class': 'form-input', 
                'type': 'time'
            }),
            'last_bus_time': forms.TimeInput(attrs={
                'class': 'form-input', 
                'type': 'time'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
        }


class StopForm(forms.ModelForm):
    class Meta:
        model = Stop
        fields = ['name', 'code']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'e.g. Ameerpet'
            }),
            'code': forms.TextInput(attrs={
                'class': 'form-input', 
                'placeholder': 'e.g. AMP'
            }),
        }
