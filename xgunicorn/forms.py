from django.contrib.auth.forms import AuthenticationForm
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Button, Submit, Div, Field, MultiField

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div('email', css_class='form-group'),
            Div('password', css_class='form-group'),
            ButtonHolder(
                Submit('login', 'Login', css_class='btn-primary')
            )
        )


# class SearchForm(forms.Form):

#     search = forms.CharField(
#         max_length=2000,
#         label=''
#     )

#     def __init__(self, *args, **kwargs):
#         self.helper = FormHelper()
#         self.helper.form_class = 'navbar-form'
#         self.helper.layout = Layout(
#             Div(
#                 Div(
#                     Field('search', placeholder='Paste Product URL Here'),
#                     Div( 
#                         Button(name='go', value='Go',
#                             css_class='btn btn-default',
#                             type='submit'
#                         ),
#                         css_class='input-group-btn',
#                     ),
#                     css_class='input-group',
#                 ),
#                 css_class='form-group', style='display:inline;',
#             )
#         )

#         super(SearchForm, self).__init__(*args, **kwargs)

