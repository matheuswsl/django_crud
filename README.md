# Django CRUD 

Introdução:
===========

Esse projeto apresenta a possibilidade de execução das funções CRUD para um banco de dados relacional.

Requerimentos:
==============

Esse projeto foi realizado utilizando a versão 3.9.5 do Python.
Alguns outros requerimentos estão presentes no arquivo requirements.txt

Informações:
============

+ O projeto apresenta 3 views: 
    - Main: Com os links para as outras duas views ('/');
    - Lista: com a listagem dos dados cadastrados, opção de atualização 
      e exclusão ('banco_dados/lista/); 
    - Create: onde é realizada a criação e atualização do cadastro ('banco_dados/create/').
    
+ O banco de dados contém 3 tabelas: Cliente, Telefone e Email. A tabela Cliente contém uma chave estrangeira
  para Telefone (telefone) e uma para Email (campo_email);
    
+ Ao tentar criar uma nova entrada em Telefone e Email, são verificadas os valores já cadastrados com o intuito 
  de recuperar os id's. Caso não seja encontrado, é criada uma nova entrada.
   
+ Ao criar ou atualizar um cadastro, é realizada uma verificação de entradas não usadas, pela tabela Cliente,
  nas tabelas Email e Telefone. Caso exista, elas são apagadas para evitar o uso desnecessário de espaço.
   
+ Na view Lista, tem um campo de pesquisa onde, utilizando o nome do cliente, é possível filtrar os cadastros 
  existentes.
