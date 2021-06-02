from django import forms

from .models import Cliente, Telefone, Email

class ClienteForm(forms.ModelForm):

    class Meta:
        msg = {
                'null':'Este campo não pode ser nulo',
                'blank':'Este campo não pode ser deixado em branco',
                'unique':'%(model_name)s com esse %(field_label)s já existe.',
                }
        model = Cliente
        exclude = ['campo_email', 'telefone']
        error_messages = {
            'nome':msg,
            'rg':msg,
            'cpf':msg,
                }

class TelefoneForm(forms.ModelForm):

    class Meta:
        model=Telefone
        fields='__all__'
        required = {
                'ddd':False
                }
        error_messages = {
                'numero':{
                    'null':'Esse valor é nulo para %(field_label).',
                    },
                'ddd':{
                    'null':'Esse valor é nulo para %(field_label).',
                    }
                }

class EmailForm(forms.ModelForm):
    class Meta:
        model=Email
        fields='__all__'
        error_messages = {
            'null':'Este campo não pode ser nulo',
            'blank':'Este campo não pode ser deixado em branco',
            'unique':'%(model_name)s com %(field_label)s já existe.',
            }

