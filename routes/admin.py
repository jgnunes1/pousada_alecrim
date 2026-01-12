# routes/admin.py
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from models import db, Quarto, Reserva, Hospede, Cardapio
from datetime import datetime, timedelta
from config import Config

admin_bp = Blueprint('admin', __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == Config.ADMIN_USERNAME and password == Config.ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Credenciais inválidas!', 'danger')
    
    return render_template('admin/login.html')

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin.login'))

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    # Estatísticas
    total_quartos = Quarto.query.count()
    reservas_ativas = Reserva.query.filter_by(status='confirmada').count()
    total_hospedes = Hospede.query.count()
    
    # Receita do mês
    inicio_mes = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    receita_mes = db.session.query(db.func.sum(Reserva.valor_total)).filter(
        Reserva.created_at >= inicio_mes,
        Reserva.status == 'concluída'
    ).scalar() or 0
    
    # Últimas reservas
    ultimas_reservas = Reserva.query.order_by(Reserva.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_quartos=total_quartos,
                         reservas_ativas=reservas_ativas,
                         total_hospedes=total_hospedes,
                         receita_mes=float(receita_mes),
                         ultimas_reservas=ultimas_reservas)

@admin_bp.route('/quartos')
@login_required
def admin_quartos():
    quartos = Quarto.query.order_by(Quarto.tipo, Quarto.numero).all()
    return render_template('admin/quartos.html', quartos=quartos)

@admin_bp.route('/reservas')
@login_required
def admin_reservas():
    reservas = Reserva.query.order_by(Reserva.data_checkin.desc()).all()
    return render_template('admin/reservas.html', reservas=reservas)

@admin_bp.route('/cardapio')
@login_required
def admin_cardapio():
    cardapio = Cardapio.query.order_by(Cardapio.categoria, Cardapio.nome).all()
    return render_template('admin/cardapio.html', cardapio=cardapio)

@admin_bp.route('/hospedes')
@login_required
def admin_hospedes():
    hospedes = Hospede.query.order_by(Hospede.nome_completo).all()
    return render_template('admin/hospedes.html', hospedes=hospedes)