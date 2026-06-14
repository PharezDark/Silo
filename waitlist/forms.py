from django import forms
from .models import WaitlistEntry


class WaitlistForm(forms.ModelForm):
    class Meta:
        model = WaitlistEntry
        fields = ['email', 'username']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-indigo-500 transition-colors',
                'placeholder': 'you@example.com'
            }),
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 bg-zinc-900 border border-zinc-800 text-white rounded-lg focus:outline-none focus:border-indigo-500 transition-colors',
                'placeholder': 'username'
            }),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username', '').lower().strip()

        # Block obvious system reserves early
        reserved_names = {'admin', 'silo', 'root', 'sysop', 'moderator', 'support', 'help', 'api', 'fediverse'}
        if username in reserved_names:
            raise forms.ValidationError("This username is reserved for system architecture optimization.")

        if WaitlistEntry.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("This username is already reserved.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').lower().strip()
        if WaitlistEntry.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("This email is already registered on the waitlist.")
        return email