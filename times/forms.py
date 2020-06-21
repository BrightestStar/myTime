from django import forms

class ItemForm(forms.Form):
    item_name = forms.CharField()
    duration = forms.DecimalField(decimal_places=2, max_digits=64)
    day = forms.IntegerField()

