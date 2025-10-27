from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class SignupForm(UserCreationForm):
    # username is hidden and not required in the POST; we'll derive it from email
    username = forms.CharField(required=False, widget=forms.HiddenInput())
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    country = forms.CharField(max_length=64, required=False)

    # Make timezone non-blocking on the server, JS will still set it when available
    timezone = forms.CharField(max_length=64, required=False)

    terms = forms.BooleanField(required=True)

    class Meta:
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "password1", "password2", "country", "timezone", "terms"
        )

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean(self):
        data = super().clean()
        # Derive username from email to satisfy User.username uniqueness
        email = (data.get("email") or "").lower()
        if email:
            data["username"] = email

        # Fallback timezone if empty (avoid “required” breakage when JS didn’t populate)
        if not data.get("timezone"):
            data["timezone"] = "UTC"
        return data

    def save(self, commit=True):
        user = super().save(commit=False)
        email = self.cleaned_data["email"].lower()
        user.username = email
        user.email = email
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user
