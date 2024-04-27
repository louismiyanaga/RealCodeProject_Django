from django import forms

from .models import Category

# Create your forms here.
class SearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        """
        inputタグにclass属性を追加します。
        """
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-select'})

    category = forms.ModelChoiceField(queryset=Category.objects, label='カテゴリ', empty_label='選択してください')
