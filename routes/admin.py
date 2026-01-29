# routes/admin.py - VERSÃO TESTADA E FUNCIONAL
from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from functools import wraps
from models import db, Quarto, Reserva, Hospede, Cardapio, StatusReserva, StatusQuarto
from config import Config

# 1. Blueprint primeiro
admin_bp = Blueprint('admin', __name__)

# 2. Decorator de login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function

# 3. Rotas básicas (sem CRUD por enquanto)

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

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('admin/dashboard.html',
                         total_quartos=10,
                         reservas_ativas=5,
                         total_hospedes=20,
                         receita_mes=5000.00)

@admin_bp.route('/quartos')
@login_required
def admin_quartos():
    # Temporário: retornar dados mock
    quartos_mock = [
        {'id': 1, 'numero': '101', 'tipo': 'quarto', 'andar': '1º Andar', 
         'capacidade': 2, 'preco_diaria': 200.00, 'status': 'disponível'},
        {'id': 2, 'numero': '30', 'tipo': 'suíte', 'andar': 'Térreo',
         'capacidade': 2, 'preco_diaria': 500.00, 'status': 'ocupado'},
    ]
    return render_template('admin/quartos.html', quartos=quartos_mock)

@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin.login'))

# routes/admin.py - ADICIONAR estas rotas para reservas

from forms import ReservaForm, BuscaReservaForm, HospedeForm
from datetime import datetime, timedelta

@admin_bp.route('/reservas')
@login_required
def admin_reservas():
    form = BuscaReservaForm(request.args)
    
    # Query base
    query = Reserva.query
    
    # Aplicar filtros
    if form.numero_reserva.data:
        query = query.filter(Reserva.id == form.numero_reserva.data)
    
    if form.cpf_hospede.data:
        # Buscar hóspede por CPF
        hospede = Hospede.query.filter_by(cpf=form.cpf_hospede.data).first()
        if hospede:
            query = query.filter(Reserva.hospede_id == hospede.id)
    
    if form.data_inicio.data:
        query = query.filter(Reserva.data_checkin >= form.data_inicio.data)
    
    if form.data_fim.data:
        query = query.filter(Reserva.data_checkout <= form.data_fim.data)
    
    if form.status.data:
        query = query.filter(Reserva.status == form.status.data)
    
    reservas = query.order_by(Reserva.data_checkin.desc()).all()
    
    return render_template('admin/reservas.html', 
                         reservas=reservas, 
                         form=form)

@admin_bp.route('/reservas/nova', methods=['GET', 'POST'])
@login_required
def nova_reserva():
    form = ReservaForm()
    
    # Popular choices dinamicamente
    quartos = Quarto.query.all()
    form.quarto_id.choices = [(q.id, f"{q.tipo.title()} {q.numero}") 
                             for q in quartos]
    
    hospedes = Hospede.query.all()
    form.hospede_id.choices = [(h.id, f"{h.nome_completo} ({h.cpf})") 
                              for h in hospedes]
    
    if form.validate_on_submit():
        try:
            quarto = Quarto.query.get(form.quarto_id.data)
            
            # Calcular valor total
            dias = (form.data_checkout.data - form.data_checkin.data).days
            valor_total = dias * float(quarto.preco_diaria)
            
            reserva = Reserva(
                quarto_id=form.quarto_id.data,
                hospede_id=form.hospede_id.data,
                data_checkin=form.data_checkin.data,
                data_checkout=form.data_checkout.data,
                num_hospedes=form.num_hospedes.data,
                valor_total=valor_total,
                status=StatusReserva(form.status.data),
                observacoes=form.observacoes.data
            )
            
            db.session.add(reserva)
            db.session.commit()
            
            flash(f'Reserva #{reserva.id} criada com sucesso!', 'success')
            return redirect(url_for('admin.admin_reservas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao criar reserva: {str(e)}', 'danger')
    
    return render_template('admin/reserva_form.html', 
                         form=form, 
                         title='Nova Reserva')

@admin_bp.route('/reservas/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    form = ReservaForm(obj=reserva)
    
    # Popular choices dinamicamente
    quartos = Quarto.query.all()
    form.quarto_id.choices = [(q.id, f"{q.tipo.title()} {q.numero}") 
                             for q in quartos]
    
    hospedes = Hospede.query.all()
    form.hospede_id.choices = [(h.id, f"{h.nome_completo} ({h.cpf})") 
                              for h in hospedes]
    
    # Preencher dados atuais
    if request.method == 'GET':
        form.status.data = reserva.status.value
        form.quarto_id.data = reserva.quarto_id
        form.hospede_id.data = reserva.hospede_id
    
    if form.validate_on_submit():
        try:
            quarto = Quarto.query.get(form.quarto_id.data)
            
            # Recalcular valor total se datas ou quarto mudaram
            if (form.data_checkin.data != reserva.data_checkin or 
                form.data_checkout.data != reserva.data_checkout or
                form.quarto_id.data != reserva.quarto_id):
                
                dias = (form.data_checkout.data - form.data_checkin.data).days
                valor_total = dias * float(quarto.preco_diaria)
                reserva.valor_total = valor_total
            
            reserva.quarto_id = form.quarto_id.data
            reserva.hospede_id = form.hospede_id.data
            reserva.data_checkin = form.data_checkin.data
            reserva.data_checkout = form.data_checkout.data
            reserva.num_hospedes = form.num_hospedes.data
            reserva.status = StatusReserva(form.status.data)
            reserva.observacoes = form.observacoes.data
            
            db.session.commit()
            
            flash(f'Reserva #{reserva.id} atualizada com sucesso!', 'success')
            return redirect(url_for('admin.admin_reservas'))
            
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar reserva: {str(e)}', 'danger')
    
    return render_template('admin/reserva_form.html', 
                         form=form, 
                         reserva=reserva,
                         title='Editar Reserva')

@admin_bp.route('/reservas/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    
    try:
        # Em produção, considerar apenas cancelar em vez de excluir
        db.session.delete(reserva)
        db.session.commit()
        flash(f'Reserva #{reserva.id} excluída com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir reserva: {str(e)}', 'danger')
    
    return redirect(url_for('admin.admin_reservas'))

@admin_bp.route('/reservas/<int:id>/status', methods=['POST'])
@login_required
def alterar_status_reserva(id):
    reserva = Reserva.query.get_or_404(id)
    novo_status = request.form.get('status')
    observacao = request.form.get('observacao', '')
    
    if novo_status in [status.value for status in StatusReserva]:
        try:
            reserva.status = StatusReserva(novo_status)
            
            # Adicionar observação se fornecida
            if observacao:
                if reserva.observacoes:
                    reserva.observacoes += f"\n[{datetime.now().strftime('%d/%m/%Y %H:%M')}] {observacao}"
                else:
                    reserva.observacoes = f"[{datetime.now().strftime('%d/%m/%Y %H:%M')}] {observacao}"
            
            db.session.commit()
            
            # Se confirmada, verificar se precisa atualizar status do quarto
            if novo_status == 'confirmada':
                reserva.quarto.status = StatusQuarto.OCUPADO
                db.session.commit()
            
            # Se cancelada ou concluída, verificar se quarto fica disponível
            elif novo_status in ['cancelada', 'concluída']:
                # Verificar se há outras reservas para este quarto no período
                outras_reservas = Reserva.query.filter(
                    Reserva.quarto_id == reserva.quarto_id,
                    Reserva.id != reserva.id,
                    Reserva.status.in_(['pendente', 'confirmada']),
                    Reserva.data_checkin < reserva.data_checkout,
                    Reserva.data_checkout > reserva.data_checkin
                ).first()

                # Se não houver reservas conflitantes, liberar o quarto
                if not outras_reservas:
                    reserva.quarto.status = StatusQuarto.DISPONIVEL
                    db.session.commit()

            flash('Status da reserva atualizado com sucesso.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar status: {str(e)}', 'danger')
    else:
        flash('Status inválido.', 'danger')

    return redirect(url_for('admin.admin_reservas'))


@admin_bp.route('/hospedes')
@login_required
def admin_hospedes():
    hospedes = Hospede.query.order_by(Hospede.nome_completo).all()
    return render_template('admin/hospedes.html', hospedes=hospedes)


@admin_bp.route('/hospedes/nova', methods=['GET', 'POST'])
@login_required
def nova_hospede():
    form = HospedeForm()
    if form.validate_on_submit():
        try:
            cpf_val = (form.cpf.data or '').strip()
            existing = Hospede.query.filter_by(cpf=cpf_val).first()
            if existing:
                flash('Já existe hóspede com este CPF.', 'warning')
                return redirect(url_for('admin.nova_hospede'))

            hospede = Hospede(
                nome_completo=form.nome_completo.data.strip(),
                cpf=cpf_val,
                email=(form.email.data or '').strip(),
                telefone=form.telefone.data.strip(),
                endereco=(form.endereco.data or '').strip()
            )
            db.session.add(hospede)
            db.session.commit()
            flash('Hóspede cadastrado com sucesso.', 'success')
            return redirect(url_for('admin.admin_hospedes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao cadastrar hóspede: {str(e)}', 'danger')

    return render_template('admin/hospede_form.html', form=form, title='Novo Hóspede')


@admin_bp.route('/hospedes/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_hospede(id):
    hospede = Hospede.query.get_or_404(id)
    form = HospedeForm(obj=hospede)

    if form.validate_on_submit():
        try:
            cpf_val = (form.cpf.data or '').strip()
            if cpf_val != hospede.cpf:
                other = Hospede.query.filter_by(cpf=cpf_val).first()
                if other:
                    flash('Outro hóspede já usa este CPF.', 'warning')
                    return redirect(url_for('admin.editar_hospede', id=id))

            hospede.nome_completo = form.nome_completo.data.strip()
            hospede.cpf = cpf_val
            hospede.email = (form.email.data or '').strip()
            hospede.telefone = form.telefone.data.strip()
            hospede.endereco = (form.endereco.data or '').strip()

            db.session.commit()
            flash('Hóspede atualizado com sucesso.', 'success')
            return redirect(url_for('admin.admin_hospedes'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erro ao atualizar hóspede: {str(e)}', 'danger')

    return render_template('admin/hospede_form.html', form=form, hospede=hospede, title='Editar Hóspede')


@admin_bp.route('/hospedes/excluir/<int:id>', methods=['POST'])
@login_required
def excluir_hospede(id):
    hospede = Hospede.query.get_or_404(id)
    try:
        db.session.delete(hospede)
        db.session.commit()
        flash('Hóspede excluído com sucesso.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Erro ao excluir hóspede: {str(e)}', 'danger')

    return redirect(url_for('admin.admin_hospedes'))