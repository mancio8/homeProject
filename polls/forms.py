from django import forms

class AggiungiOreForm(forms.Form):
    TIPO_CHOICES = [
        ('ferie', 'Ferie'),
        ('permessi', 'Permessi'),
    ]
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, label="Tipo di ore")
    ore = forms.FloatField(label="Ore", min_value=0.01)
