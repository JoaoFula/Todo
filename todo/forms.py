from django.forms import ModelForm
from .models import todo

class todo_form(ModelForm):
    class Meta:
        model = todo
        fields = ['title', 'memo', 'important']