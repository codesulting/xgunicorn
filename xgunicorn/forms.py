from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Div, ButtonHolder


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Div('username', css_class='form-group'),
            Div('password', css_class='form-group'),
            ButtonHolder(
                Submit('login', 'Login', css_class='btn-primary')
            )
        )


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password1',
            'password2',
            ButtonHolder(
                Submit('signup', 'Sign Up', css_class='btn-primary')
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

