from django import forms


class MyForm(forms.Form):
    CHOICES = (
        ('Notebook', 'notebook'),
        ('Smartphones', 'smartphones'),
        ('Category', 'category'),
        ('Cart', 'cart'),
        ('testmodel', 'testmodel'),
        ('Hui', 'hui'),
    )
    field = forms.ChoiceField(choices=CHOICES)

