from __future__ import absolute_import

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView, CreateView, FormView

from .forms import SignUpForm, LoginForm


class HomePageView(TemplateView):
    template_name = 'home.html'


class SignUpView(CreateView):
	form_class = SignUpForm
	form_valid_message = 'Thanks for signing up.'
	model = User
	template_name = 'accounts/signup.html'
	success_url = reverse_lazy('login')

	def form_valid(self, form):
		resp = super(SignUpView, self).form_valid(form)
		return resp


class LoginView(FormView):
	form_class = LoginForm
	success_url = reverse_lazy('home')
	template_name = 'accounts/login.html'

	def form_valid(self, form):
		username = form.cleaned_data['username']
		password = form.cleaned_data['password']
		user = authenticate(username=username, password=password)

		if user is not None and user.is_active:
			login(self.request, user)
			return super(LoginView, self).form_valid(form)
		else:
			return self.form_invalid(form)


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, "Hello. You are now logged out. See you later.")
    return HttpResponseRedirect(reverse_lazy('home'))