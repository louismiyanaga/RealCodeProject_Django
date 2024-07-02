from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from core.models import Cart

# Create your forms here.
User = get_user_model()


class SignupForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        """
        Add a class attribute to an input element
        """
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        """
        You can also code as below:

        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        """
        
    def save(self):
        """
        Create a user account with a cart
        [Procedure]
        1. Create a user object (not saved at this point)
        2. Create a cart object and assign it to the user's cart field
        3. Save the user object
        """
        user = super().save(commit=False)   # Use default save method of parent class
                                            # (not saved at this point due to commit=False)
        user.cart = Cart.objects.create()
        user.save() # Saved to database here
        return user
    
    class Meta:
        model = User
        fields = ('username',)