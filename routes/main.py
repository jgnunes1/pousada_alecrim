# routes/main.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from models import db, Quarto, Hospede, Reserva, Cardapio, StatusReserva, StatusQuarto
from datetime import datetime
import re

main_bp = Blueprint('main', __name__)

@main_bp.context_processor
def inject_pousada_info():
    from config import Config
    info = {
        'nome': Config.POUSADA_NOME,
        'slogan': Config.POUSADA_SLOGAN,
        'diferencial': Config.POUSADA_DIFERENCIAL,
        'endereco': Config.POUSADA_ENDERECO,
        'telefone': Config.POUSADA_TELEFONE,
        'email': Config.POUSADA_EMAIL,
        'descricao': Config.POUSADA_DESCRICAO,
    }

    return {
        'pousada_nome': Config.POUSADA_NOME,
        'pousada_slogan': Config.POUSADA_SLOGAN,
        'pousada_diferencial': Config.POUSADA_DIFERENCIAL,
        'pousada_endereco': Config.POUSADA_ENDERECO,
        'pousada_telefone': Config.POUSADA_TELEFONE,
        'pousada_email': Config.POUSADA_EMAIL,
        'info': info,
    }

@main_bp.route('/')
def index():
    quartos = Quarto.query.filter_by(status=StatusQuarto.DISPONIVEL).limit(3).all()
    return render_template('index.html', quartos_destaque=quartos)

@main_bp.route('/sobre')
def sobre():
    return render_template('sobre.html')

@main_bp.route('/quartos')
def quartos():
    quartos = Quarto.query.order_by(Quarto.tipo, Quarto.numero).all()
    return render_template('quartos.html', quartos=quartos)

@main_bp.route('/cardapio')
def cardapio():
    cardapio_items = Cardapio.query.filter_by(disponivel=True).order_by(Cardapio.categoria, Cardapio.nome).all()
    
    # Agrupar por categoria
    cardapio_agrupado = {}
    for item in cardapio_items:
        categoria = item.categoria.value
        if categoria not in cardapio_agrupado:
            cardapio_agrupado[categoria] = []
        cardapio_agrupado[categoria].append(item)
    
    return render_template('cardapio.html', cardapio=cardapio_agrupado)

@main_bp.route('/contato')
def contato():
    return render_template('contato.html')

@main_bp.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if request.method == 'POST':
        try:
            # Validar dados
            nome = request.form.get('nome', '').strip()
            cpf = request.form.get('cpf', '').strip()
            email = request.form.get('email', '').strip()
            telefone = request.form.get('telefone', '').strip()
            quarto_id = request.form.get('quarto_id')
            checkin = request.form.get('checkin')
            checkout = request.form.get('checkout')
            num_hospedes = request.form.get('num_hospedes', 1)
            
            # Validações básicas
            if not all([nome, cpf, telefone, quarto_id, checkin, checkout]):
                flash('Preencha todos os campos obrigatórios.', 'danger')
                return redirect(url_for('main.reservar'))
            
            # Verificar se quarto existe e está disponível
            quarto = Quarto.query.get_or_404(quarto_id)
            if quarto.status != StatusQuarto.DISPONIVEL:
                flash('Este quarto não está disponível no momento.', 'danger')
                return redirect(url_for('main.reservar'))
            
            # Converter datas
            data_checkin = datetime.strptime(checkin, '%Y-%m-%d').date()
            data_checkout = datetime.strptime(checkout, '%Y-%m-%d').date()
            
            if data_checkin >= data_checkout:
                flash('Data de check-out deve ser posterior ao check-in.', 'danger')
                return redirect(url_for('main.reservar'))
            
            # Verificar se hóspede já existe
            hospede = Hospede.query.filter_by(cpf=cpf).first()
            if not hospede:
                hospede = Hospede(
                    nome_completo=nome,
                    cpf=cpf,
                    email=email,
                    telefone=telefone
                )
                db.session.add(hospede)
                db.session.flush()  # Para obter o ID
            
            # Calcular valor total
            dias = (data_checkout - data_checkin).days
            valor_total = dias * float(quarto.preco_diaria)
            
            # Criar reserva
            reserva = Reserva(
                quarto_id=quarto.id,
                hospede_id=hospede.id,
                data_checkin=data_checkin,
                data_checkout=data_checkout,
                num_hospedes=int(num_hospedes),
                valor_total=valor_total,
                status=StatusReserva.PENDENTE
            )
            
            db.session.add(reserva)
            db.session.commit()
            
            flash(f'Reserva realizada com sucesso! Número: {reserva.id}', 'success')
            return redirect(url_for('main.index'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao realizar reserva: {str(e)}', 'danger')
            return redirect(url_for('main.reservar'))
    
    # GET: mostrar formulário
    quartos_disponiveis = Quarto.query.filter_by(status=StatusQuarto.DISPONIVEL).all()
    return render_template('reservar.html', quartos=quartos_disponiveis)

def verificar_disponibilidade(quarto_id, data_checkin, data_checkout):
    """Verifica se o quarto está disponível para o período"""
    reservas_conflitantes = Reserva.query.filter(
        Reserva.quarto_id == quarto_id,
        Reserva.status.in_(['pendente', 'confirmada']),
        Reserva.data_checkin < data_checkout,
        Reserva.data_checkout > data_checkin
    ).first()
    
    return reservas_conflitantes is None

@main_bp.route('/reserva/confirmacao/<int:reserva_id>')
def confirmacao_reserva(reserva_id):
    """Página de confirmação da reserva"""
    reserva = Reserva.query.get_or_404(reserva_id)
    return render_template('confirmacao_reserva.html', reserva=reserva)

@main_bp.route('/reserva/consultar', methods=['GET', 'POST'])
def consultar_reserva():
    """Página para consultar status da reserva"""
    from forms import BuscaReservaForm
    
    form = BuscaReservaForm()
    reserva = None
    
    if form.validate_on_submit():
        # Buscar por número da reserva
        if form.numero_reserva.data:
            reserva = Reserva.query.get(form.numero_reserva.data)
        
        # Buscar por CPF
        elif form.cpf_hospede.data:
            hospede = Hospede.query.filter_by(cpf=form.cpf_hospede.data).first()
            if hospede:
                reserva = Reserva.query.filter_by(hospede_id=hospede.id)\
                                      .order_by(Reserva.created_at.desc())\
                                      .first()
    
    return render_template('consultar_reserva.html', form=form, reserva=reserva)