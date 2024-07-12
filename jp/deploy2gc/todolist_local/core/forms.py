from django.forms import ModelForm
from .models import Todo


class TodoForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Enter your new plan!'})
    class Meta:
        model = Todo
        fields = ('name',)
        