from django import forms

from .models import Category

# Create your forms here.
class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        """
        Add a class attribute to an input element
        """
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-select'})

    category = forms.ModelChoiceField(queryset=Category.objects)