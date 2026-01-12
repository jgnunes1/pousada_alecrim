# routes/admin.py - VERSÃO CORRIGIDA (ORDEM CORRETA)
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from forms import QuartoForm
from models import db, Quarto, Reserva, Hospede, Cardapio, StatusQuarto
from datetime import datetime, timedelta
from config import Config

# 1. PRIMEIRO definir o blueprint
admin_bp = Blueprint('admin', __name__)

# 2. DEPOIS definir as funções auxiliares
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# 3. AGORA definir as rotas

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

# 4. ROTAS CRUD PARA QUARTOS (agora sim, após admin_bp estar definido)

@admin_bp.route('/quartos/novo', methods=['GET', 'POST'])
@login_required
def novo_quarto():
    form = QuartoForm()
    
    if form.validate_on_submit():
        try:
            quarto = Quarto(
                numero=form.numero.data,
                tipo=form.tipo.data,
                andar=form.andar.data,
                descricao=form.descricao.data,
                capacidade=form.capacidade.data,
                preco_diaria=form.preco_diaria.data,
                status=StatusQuarto(form.status.data),
                fotos=form.fotos.data if form.fotos.data else None
            )
            
            db.session.add(quarto)
            db.session.commit()
            
            flash(f'Quarto {quarto.numero} criado com sucesso!', 'success')
            return redirect(url_for('admin.admin_quartos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar quarto: {str(e)}', 'danger')
    
    return render_template('admin/quarto_form.html', 
                         form=form, 
                         title='Novo Quarto')

@admin_bp.route('/quartos/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_quarto(id):
    quarto = Quarto.query.get_or_404(id)
    form = QuartoForm(obj=quarto)
    
    # Preencher dados atuais
    if request.method == 'GET':
        form.status.data = quarto.status.value
        form.fotos.data = quarto.fotos if quarto.fotos else ''
    
    if form.validate_on_submit():
        try:
            quarto.numero = form.numero.data
            quarto.tipo = form.tipo.data
            quarto.andar = form.andar.data
            quarto.descricao = form.descricao.data
            quarto.capacidade = form.capacidade.data
            quarto.preco_diaria = form.preco_diaria.data
            quarto.status = StatusQuarto(form.status.data)
            quarto.fotos = form.fotos.data if form.fotos.data else None
            
            db.session.commit()
            
            flash(f'Quarto {quarto.numero} atualizado com sucesso!', 'success')
            return redirect(url_for('admin.admin_quartos'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar quarto: {str(e)}', 'danger')
    
    return render_template('admin/quarto_form.html', 
                         form=form, 
                         quarto=quarto,
                         title='Editar Quarto')

@admin_bp.route('/quartos/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_quarto(id):
    quarto = Quarto.query.get_or_404(id)
    
    # Verificar se há reservas ativas para este quarto
    reservas_ativas = any(r.status.value in ['pendente', 'confirmada'] 
                         for r in quarto.reservas)
    
    if reservas_ativas:
        flash(f'Não é possível excluir o quarto {quarto.numero} porque há reservas ativas.', 'danger')
        return redirect(url_for('admin.admin_quartos'))
    
    try:
        db.session.delete(quarto)
        db.session.commit()
        flash(f'Quarto {quarto.numero} excluído com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir quarto: {str(e)}', 'danger')
    
    return redirect(url_for('admin.admin_quartos'))

@admin_bp.route('/quartos/<int:id>/status', methods=['POST'])
@login_required
def alterar_status_quarto(id):
    quarto = Quarto.query.get_or_404(id)
    novo_status = request.form.get('status')
    
    if novo_status in [status.value for status in StatusQuarto]:
        try:
            quarto.status = StatusQuarto(novo_status)
            db.session.commit()
            flash(f'Status do quarto {quarto.numero} alterado para {novo_status}!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao alterar status: {str(e)}', 'danger')
    else:
        flash('Status inválido!', 'danger')
    
    return redirect(url_for('admin.admin_quartos'))

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