from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import IntegrityError, connection
from django.db.models import Model, Q, ProtectedError
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic, View

from .models import Cliente, Telefone, Email
from .forms import ClienteForm, TelefoneForm, EmailForm

# Create your views here.

class ListView(generic.ListView):
    model = Cliente
    template_name = 'banco_dados/list.html'

    def get(self, request, pk=None, *args, **kwargs):
        if pk:
            self.delete(pk)
            messages.success(request, 'O cadastro foi excluído')
       
        search = request.GET.get("search", False)
        self.object_list = self.get_queryset(search=search)
        allow_empty = self.get_allow_empty()

        context = self.get_context_data()
        return render(request, self.template_name, context)

    def get_queryset(self,*,search):
        if search:
            comando = """
                SELECT * FROM banco_dados_cliente 
                INNER JOIN "banco_dados_telefone"
                ON ("banco_dados_cliente"."telefone_id"="banco_dados_telefone"."id")
                INNER JOIN "banco_dados_email"
                ON ("banco_dados_cliente"."campo_email_id"="banco_dados_email"."id")
                WHERE nome LIKE %s
                """ %(repr('%'+search+'%'))
        else:
            comando = """
                SELECT * FROM banco_dados_cliente
                INNER JOIN "banco_dados_telefone"
                ON ("banco_dados_cliente"."telefone_id"="banco_dados_telefone"."id")
                INNER JOIN "banco_dados_email"
                ON ("banco_dados_cliente"."campo_email_id"="banco_dados_email"."id")
                """
        return Cliente.objects.raw(comando)

    def delete(self, pk):
        try:
            cliente = Cliente.objects.get(id=pk)
        except Cliente.DoesNotExist:
            return None
        else:
            telefone = Telefone.objects.get(id=cliente.telefone.id)
            email = Email.objects.get(id=cliente.campo_email.id)
            cliente.delete()
            try:
                telefone.delete()
            except ProtectedError:
                pass
            try:
                email.delete()
            except ProtectedError:
                pass

class CreateView(View):
    """View para criação e alteração de cadastros"""

    template_name = 'banco_dados/create.html'
    
    def get(self, request, pk=None):
        context = self.get_context_data(pk)
        return render(request, self.template_name, context)

    def post(self, request, pk=None):

        context = self.get_context_data(pk, request.POST)
        fc, ft, fe = context.values() #ft = form_telefone; fe = form_email; fc = form_cliente

        #Salva os dados em Telefone
        request, ft, tel_id, r = self.salva_alteracao(request, ft, context, Telefone)
        if r:
            return r

        #Salva os dados em Email
        request, fe, email_id, r = self.salva_alteracao(request, fe, context, Email)
        if r:
            return r

        #Salva os dados em Cliente
        telefone = Telefone.objects.get(id=tel_id)
        email = Email.objects.get(id=email_id)

        if fc.is_valid():
            fc.save()
            if fc.instance.id:
                c = Cliente.objects.filter(**fc.data).update(telefone=telefone, campo_email=email)
            else:
                c = Cliente(**fc.data, telefone=telefone, campo_email=email)
                c.save()
            messages.success(request, 'O cadastro foi alterado')
        else:
            for erro in fc.errors.values():
                messages.error(request, erro[0])
            return render(request, 'banco_dados/create.html', context)
        
        self._exclui_nao_usadas()
        return redirect(reverse('banco_dados:lista'))

    def _itera(self, dicionario):
        """Cria um iterador para recuperação dos erros de campo 
        não único.
        Retorna uma lista contendo os campos."""

        for campo, erros in dicionario.items():
            for erro in erros:
                if 'already exists' in erro:
                    yield campo

    def salva_alteracao(self, request, form, context, instance):
        """Salva as alterações no formulário ou recupera o id se 
        existente"""

        #Set contendo campos não únicos
        if form.is_valid():
            salvo = form.save()
            valor_id = salvo.id
            print('valor_id: ', valor_id)
        else:
            campos_erros = { x for x in self._itera(form.errors) }
            if campos_erros:
                valor_id = instance.objects.get(**form.data).id
                for campo in campos_erros:
                    del form.errors[campo]
            else:
                messages.error(request, "Algo está errado com os dados informados")
                r = render(request, 'banco_dados/create.html', context)
                return request, form, None, r
        
        return request, form, valor_id, None

    def recupera_dados(self, pk, post_data):
        """Tenta criar uma instancia de Cliente usando pk ou retorna None."""

        obj = Cliente.objects
        if pk: 
            try:
                #Verifica se o cliente com id=pk existe.
                cliente = obj.get(id=pk)
            except Cliente.DoesNotExist:
                return None, None, None

            # Caso exista...
            else: 
                # Se tiver enviado dados pelo metodo POST...
                if post_data:

                    #Conferir que as entradas estão associadas com apenas 
                    #um cliente
                    if len(obj.filter(telefone_id=cliente.telefone_id)) > 1:
                        telefone = None      
                    else:
                        telefone = Telefone.objects.get(id=cliente.telefone.id)
    
                    if len(obj.filter(campo_email_id=cliente.campo_email_id)) > 1:
                        email = None
                    else:
                        email = Email.objects.get(id=cliente.campo_email.id)
                
                #Caso esteja visualizando para atualização.
                else:
                    telefone = Telefone.objects.get(id=cliente.telefone.id)
                    email = Email.objects.get(id=cliente.campo_email.id)

                return cliente, telefone, email

        # Se pk=None retorna...
        else:
            return None, None, None

    def get_context_data(self, pk, post_data=None):

        cliente, telefone, email = self.recupera_dados(pk, post_data)

        campos_cliente, campos_tel, campos_email = None, None, None

        if post_data:
            #Recupera os campos de cada formulário
            campos_cliente = {x:post_data[x] for x in ClienteForm().fields.keys()} 
            campos_tel = {x:post_data[x] for x in TelefoneForm().fields.keys()} 
            campos_email = {x:post_data[x] for x in EmailForm().fields.keys()} 

        #Monta o dicionário de context
        context = {
                "form_cliente":ClienteForm(campos_cliente, instance=cliente),
                "form_telefone":TelefoneForm(campos_tel, instance=telefone),
                "form_email":EmailForm(campos_email, instance=email),
                }
        return context

    def _exclui_nao_usadas(self):
        """Exclui do banco de dados (Email e Telefone) as entradas
        não usadas.
        """

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT telefone_id, campo_email_id 
                FROM banco_dados_cliente
                """
                )
            usados = cursor.fetchall()

        tel_usados = [ x[0] for x in usados ]
        email_usados = [ x[1] for x in usados ]

        tel_existentes = [ x['id'] for x in Telefone.objects.values('id') ]
        email_existentes = [ x['id'] for x in Email.objects.values('id') ]

        #Exclui os dados em telefone
        for i in tel_existentes:
            if i not in tel_usados:
                Telefone.objects.filter(id=i).delete()

        #Exclui os dados em Email
        for i in email_existentes:
            if i not in email_usados:
                Email.objects.filter(id=i).delete()




class UpdateView(View):
    template_name = 'banco_dados/update.html'

    def get(self, request, pk):
        try:
            cliente = Cliente.objects.get(id=pk)
        except Cliente.DoesNotExist:
            return None
        else:
            telefone = Telefone.objects.get(id=cliente.telefone.id)
            email = Email.objects.get(id=cliente.campo_email.id)
            form_cliente = ClienteForm(cliente)
            form_telefone = TelefoneForm(telefone)
            form_email = EmailForm(email)
            context = {
                    'form_cliente':form_cliente,
                    'form_telefone':form_telefone,
                    'form_email':form_email,
                    }
            return render(request, 'banco_dados/update.html', context)
 

        
