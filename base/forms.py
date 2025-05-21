from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from .models import Room, User, ContactSubmission, Message
from django import forms

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']

class RoomForm(ModelForm):
    class Meta:
        model = Room
        exclude = ['host', 'participants', 'doc_type', 'topic']

    # def clean_media(self):
    #     media = self.cleaned_data.get('media')
    #     if media:
    #         max_size = 50 * 1024 * 1024  # 50MB in bytes
    #         if media.size > max_size:
    #             raise UserForm.ValidationError('File size exceeds 50MB limit.')
    #     return media

class UserForm(ModelForm):
    # PRIVACY_CHOICES = [
    #     (False, "Public"),
    #     (True, "Private"),
    # ]
    
    # is_private = forms.ChoiceField(
    #     choices=PRIVACY_CHOICES, 
    #     widget=forms.Select(attrs={"class": "form-control"})
    # )

    class Meta:
        model = User
        fields = ['avatar','name', 'username', 'email','bio', 'auth_status', ]
        

class ContactForm(ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'phone', 'email', 'message']

    # Optional: Add custom validation or styling
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'custom-label'})  

    # Add a field for the terms agreement (checkbox)
    agree_terms = forms.BooleanField(
        required=True,
        label='I agree to receive communications from Share Wisdom'
    )

