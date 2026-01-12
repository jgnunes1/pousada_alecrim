# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import enum

db = SQLAlchemy()

class StatusQuarto(enum.Enum):
    DISPONIVEL = 'disponível'
    OCUPADO = 'ocupado'
    MANUTENCAO = 'manutenção'

class StatusReserva(enum.Enum):
    PENDENTE = 'pendente'
    CONFIRMADA = 'confirmada'
    CANCELADA = 'cancelada'
    CONCLUIDA = 'concluída'

class StatusPedido(enum.Enum):
    PENDENTE = 'pendente'
    PREPARANDO = 'preparando'
    PRONTO = 'pronto'
    ENTREGUE = 'entregue'

class CategoriaCardapio(enum.Enum):
    ENTRADA = 'entrada'
    PRINCIPAL = 'principal'
    SOBREMESA = 'sobremesa'
    BEBIDA = 'bebida'

class Quarto(db.Model):
    __tablename__ = 'quartos'
    
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # suíte, quarto, chalé
    andar = db.Column(db.String(20))
    descricao = db.Column(db.Text)
    capacidade = db.Column(db.Integer, default=2)
    preco_diaria = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(StatusQuarto), default=StatusQuarto.DISPONIVEL)
    fotos = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    reservas = db.relationship('Reserva', backref='quarto', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'numero': self.numero,
            'tipo': self.tipo,
            'andar': self.andar,
            'descricao': self.descricao,
            'capacidade': self.capacidade,
            'preco_diaria': float(self.preco_diaria),
            'status': self.status.value,
            'fotos': self.fotos,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Hospede(db.Model):
    __tablename__ = 'hospedes'
    
    id = db.Column(db.Integer, primary_key=True)
    nome_completo = db.Column(db.String(100), nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)
    email = db.Column(db.String(100))
    telefone = db.Column(db.String(20))
    endereco = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    reservas = db.relationship('Reserva', backref='hospede', lazy=True)

class Reserva(db.Model):
    __tablename__ = 'reservas'
    
    id = db.Column(db.Integer, primary_key=True)
    quarto_id = db.Column(db.Integer, db.ForeignKey('quartos.id'), nullable=False)
    hospede_id = db.Column(db.Integer, db.ForeignKey('hospedes.id'), nullable=False)
    data_checkin = db.Column(db.Date, nullable=False)
    data_checkout = db.Column(db.Date, nullable=False)
    num_hospedes = db.Column(db.Integer, default=1)
    valor_total = db.Column(db.Numeric(10, 2))
    status = db.Column(db.Enum(StatusReserva), default=StatusReserva.PENDENTE)
    observacoes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='reserva', lazy=True)
    
    def calcular_valor_total(self):
        if self.quarto and self.data_checkin and self.data_checkout:
            dias = (self.data_checkout - self.data_checkin).days
            return dias * float(self.quarto.preco_diaria)
        return 0

class Cardapio(db.Model):
    __tablename__ = 'cardapio'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    categoria = db.Column(db.Enum(CategoriaCardapio), nullable=False)
    preco = db.Column(db.Numeric(10, 2), nullable=False)
    disponivel = db.Column(db.Boolean, default=True)
    foto = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    pedidos = db.relationship('Pedido', backref='item', lazy=True)

class Pedido(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.Integer, primary_key=True)
    reserva_id = db.Column(db.Integer, db.ForeignKey('reservas.id'), nullable=False)
    item_id = db.Column(db.Integer, db.ForeignKey('cardapio.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    observacoes = db.Column(db.Text)
    status = db.Column(db.Enum(StatusPedido), default=StatusPedido.PENDENTE)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)