from django.db import models
from django.core.validators import RegexValidator, MaxValueValidator
from datetime import datetime


class Telefone(models.Model):
    ddd = models.IntegerField(
            "DDD",
            null=True,
            blank=True,
            default=16,
            validators=[
                MaxValueValidator(99)
                ],
            )
    numero = models.CharField(
            max_length=10,
            help_text='Exemplo de entrada 00000-0000',
            validators=[
                RegexValidator(
                    regex='[0-9]{4,5}-[0-9]{4}',
                    message='O formato do campo está inválido'
                    )
                ],
            null=True,
            blank=True,
            #default=' ',
            )
    opcoes_tipo = [
            ('Cel', 'Celular'),
            ('Res', 'Residencial'),
            ('Com', 'Comercial'),
            ]
    tipo = models.CharField(
            max_length = 11,
            choices = opcoes_tipo,
            default = 'Cel',
            null=True
            )

    def __str__(self):
        return f'({self.ddd}) {self.numero}'

    class Meta:
        unique_together = [['ddd','numero']]

class Email(models.Model):
    email = models.EmailField(null=True, unique=True, blank=True, )

    def __str__(self):
        return f'{self.email}'

class Cliente(models.Model):
    data=datetime.now()
    nome = models.CharField("Nome",max_length=128)
    rg = models.CharField(
            "RG",
            max_length=14,
            help_text='O campo RG tem que ser do tipo 00.000.000-00',
            validators=[
                RegexValidator(
                    regex='[0-9]{2,3}\.[0-9]{3}\.[0-9]{3}-[0-9]{1,2}',
                    message='O formato do campo está inválido'
                )
            ],
            unique=True,
        )
    cpf = models.CharField(
            "CPF",
            max_length=14,
            help_text='O campo CPF tem que ser do tipo 000.000.000-00',
            validators=[
                RegexValidator(
                    regex='[0-9]{2,3}\.[0-9]{3}\.[0-9]{3}-[0-9]{1,2}',
                    message='O formato do campo está inválido'
                )
            ],
            unique=True,
        )

    data_nasc = models.CharField(
            "Data de Nascimento",
            max_length=10,
            validators=[
                RegexValidator(
                    regex='[0-9]{2}/[0-9]{2}/[0-9]{4}',
                    message='O formato do campo está inválido'
                )
            ],
            help_text='Entre com a data de nascimento (e.g. dd/mm/yyyy)'
        )
    sexo = models.CharField(max_length=12)
    telefone = models.ForeignKey(Telefone, on_delete=models.PROTECT, null=True, blank=True)
    campo_email = models.ForeignKey(Email, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.nome

