from django.shortcuts import render, redirect
from django.views.generic import View
from django.contrib import messages
from .forms import WaitlistForm

# Create your views here.

class LandingPageView(View):
    template_name = 'waitlist/landing.html'

    def get(self, request, *args, **kwargs):
        form = WaitlistForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = WaitlistForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Secure node allocation complete. Your spot is locked in.")
            return redirect('waitlist:landing')

        # If invalid, pass the form back with errors natively rendered via context
        return render(request, self.template_name, {'form': form})