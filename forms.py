# forms.py - VERSÃO COMPLETA E CORRIGIDA
from flask_wtf import FlaskForm
from wtforms import (
    StringField, TextAreaField, SelectField, 
    IntegerField, DecimalField, SubmitField,
    BooleanField, DateField, TimeField, HiddenField
)
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email
from datetime import datetime
from models import StatusQuarto, StatusReserva, CategoriaCardapio

class QuartoForm(FlaskForm):
    """Formulário para criar/editar quartos"""
    numero = StringField('Número do Quarto', 
                        validators=[DataRequired(), Length(min=1, max=10)],
                        render_kw={"placeholder": "Ex: 101, 30, 01"})
    
    tipo = SelectField('Tipo', 
                      choices=[
                          ('suíte', 'Suíte'),
                          ('quarto', 'Quarto'),
                          ('chalé', 'Chalé')
                      ],
                      validators=[DataRequired()])
    
    andar = StringField('Andar/Localização',
                       validators=[Optional(), Length(max=20)],
                       render_kw={"placeholder": "Ex: 1º Andar, Térreo, Área externa"})
    
    descricao = TextAreaField('Descrição',
                             validators=[Optional(), Length(max=500)],
                             render_kw={"placeholder": "Descreva o quarto, comodidades, vista, etc.",
                                       "rows": 4})
    
    capacidade = IntegerField('Capacidade',
                             validators=[DataRequired(), NumberRange(min=1, max=10)],
                             default=2)
    
    preco_diaria = DecimalField('Preço da Diária (R$)',
                               validators=[DataRequired(), NumberRange(min=0.01)],
                               places=2,
                               render_kw={"placeholder": "Ex: 200.00"})
    
    status = SelectField('Status',
                        choices=[(status.value, status.value.title()) 
                                for status in StatusQuarto],
                        default=StatusQuarto.DISPONIVEL.value)
    
    fotos = TextAreaField('Links das Fotos (um por linha)',
                         validators=[Optional()],
                         render_kw={"placeholder": "Cole os links das fotos, um por linha",
                                   "rows": 3})
    
    submit = SubmitField('Salvar Quarto')

class HospedeForm(FlaskForm):
    """Formulário para criar/editar hóspedes"""
    nome_completo = StringField('Nome Completo',
                               validators=[DataRequired(), Length(max=100)],
                               render_kw={"placeholder": "Nome completo do hóspede"})
    
    cpf = StringField('CPF',
                     validators=[DataRequired(), Length(min=11, max=14)],
                     render_kw={"placeholder": "000.000.000-00"})
    
    email = StringField('E-mail',
                       validators=[Optional(), Email(), Length(max=100)],
                       render_kw={"placeholder": "hospede@email.com"})
    
    telefone = StringField('Telefone',
                          validators=[DataRequired(), Length(max=20)],
                          render_kw={"placeholder": "(00) 00000-0000"})
    
    endereco = TextAreaField('Endereço',
                            validators=[Optional(), Length(max=500)],
                            render_kw={"placeholder": "Endereço completo",
                                      "rows": 3})
    
    submit = SubmitField('Salvar Hóspede')

class CardapioForm(FlaskForm):
    """Formulário para criar/editar itens do cardápio"""
    nome = StringField('Nome do Prato',
                      validators=[DataRequired(), Length(max=100)],
                      render_kw={"placeholder": "Ex: Filé Mignon, Salada Caesar"})
    
    descricao = TextAreaField('Descrição',
                             validators=[Optional(), Length(max=500)],
                             render_kw={"placeholder": "Descreva o prato, ingredientes, etc.",
                                       "rows": 3})
    
    categoria = SelectField('Categoria',
                           choices=[(cat.value, cat.value.title()) 
                                   for cat in CategoriaCardapio],
                           validators=[DataRequired()])
    
    preco = DecimalField('Preço (R$)',
                        validators=[DataRequired(), NumberRange(min=0.01)],
                        places=2,
                        render_kw={"placeholder": "Ex: 85.00"})
    
    disponivel = BooleanField('Disponível', default=True)
    
    foto = StringField('Link da Foto',
                      validators=[Optional(), Length(max=255)],
                      render_kw={"placeholder": "URL da foto do prato"})
    
    submit = SubmitField('Salvar Item')

class FiltroForm(FlaskForm):
    """Formulário para filtros"""
    tipo = SelectField('Tipo', 
                      choices=[
                          ('', 'Todos'),
                          ('suíte', 'Suíte'),
                          ('quarto', 'Quarto'),
                          ('chalé', 'Chalé')
                      ],
                      default='')
    
    status = SelectField('Status',
                        choices=[
                            ('', 'Todos'),
                            ('disponível', 'Disponível'),
                            ('ocupado', 'Ocupado'),
                            ('manutenção', 'Manutenção')
                        ],
                        default='')
    
    andar = SelectField('Andar',
                       choices=[
                           ('', 'Todos'),
                           ('Térreo', 'Térreo'),
                           ('1º Andar', '1º Andar'),
                           ('2º Andar', '2º Andar'),
                           ('Área externa', 'Área externa')
                       ],
                       default='')
    
    filtrar = SubmitField('Filtrar')

    # forms.py - ADICIONAR estes formulários

from datetime import datetime, date
from wtforms.validators import ValidationError

class ReservaForm(FlaskForm):
    """Formulário para criar/editar reservas"""
    quarto_id = SelectField('Quarto', 
                           coerce=int,
                           validators=[DataRequired()],
                           choices=[])  # Preenchido dinamicamente
    
    hospede_id = SelectField('Hóspede', 
                            coerce=int,
                            validators=[DataRequired()],
                            choices=[])  # Preenchido dinamicamente
    
    data_checkin = DateField('Data de Check-in',
                            format='%Y-%m-%d',
                            validators=[DataRequired()],
                            default=datetime.today)
    
    data_checkout = DateField('Data de Check-out',
                             format='%Y-%m-%d',
                             validators=[DataRequired()],
                             default=lambda: datetime.today() + timedelta(days=1))
    
    num_hospedes = IntegerField('Número de Hóspedes',
                               validators=[DataRequired(), NumberRange(min=1, max=10)],
                               default=1)
    
    status = SelectField('Status',
                        choices=[(status.value, status.value.title()) 
                                for status in StatusReserva],
                        default=StatusReserva.PENDENTE.value)
    
    observacoes = TextAreaField('Observações',
                               validators=[Optional(), Length(max=500)],
                               render_kw={"placeholder": "Pedidos especiais, comemorações, etc.",
                                         "rows": 3})
    
    submit = SubmitField('Salvar Reserva')
    
    def validate_data_checkout(self, field):
        if field.data <= self.data_checkin.data:
            raise ValidationError('Data de check-out deve ser posterior ao check-in.')
        
        # Máximo de 30 dias
        max_dias = (field.data - self.data_checkin.data).days
        if max_dias > 30:
            raise ValidationError('Reserva máxima: 30 dias.')

class BuscaReservaForm(FlaskForm):
    """Formulário para busca de reservas"""
    numero_reserva = StringField('Número da Reserva',
                                validators=[Optional()],
                                render_kw={"placeholder": "Ex: 123"})
    
    cpf_hospede = StringField('CPF do Hóspede',
                             validators=[Optional()],
                             render_kw={"placeholder": "000.000.000-00"})
    
    data_inicio = DateField('Data Inicial',
                           format='%Y-%m-%d',
                           validators=[Optional()])
    
    data_fim = DateField('Data Final',
                        format='%Y-%m-%d',
                        validators=[Optional()])
    
    status = SelectField('Status',
                        choices=[
                            ('', 'Todos'),
                            ('pendente', 'Pendente'),
                            ('confirmada', 'Confirmada'),
                            ('cancelada', 'Cancelada'),
                            ('concluída', 'Concluída')
                        ],
                        default='')
    
    buscar = SubmitField('Buscar')