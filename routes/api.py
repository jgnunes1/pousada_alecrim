# routes/api.py
from flask import Blueprint, jsonify, request
from models import db, Quarto, Reserva
from datetime import datetime

api_bp = Blueprint('api', __name__)

@api_bp.route('/quartos/disponiveis', methods=['GET'])
def quartos_disponiveis():
    try:
        checkin = request.args.get('checkin')
        checkout = request.args.get('checkout')
        
        if not checkin or not checkout:
            return jsonify({'error': 'Datas necessárias'}), 400
        
        data_checkin = datetime.strptime(checkin, '%Y-%m-%d').date()
        data_checkout = datetime.strptime(checkout, '%Y-%m-%d').date()
        
        # Buscar quartos que não têm reservas conflitantes
        quartos_ocupados = db.session.query(Reserva.quarto_id).filter(
            Reserva.status.in_(['confirmada', 'pendente']),
            Reserva.data_checkin < data_checkout,
            Reserva.data_checkout > data_checkin
        ).subquery()
        
        quartos_disponiveis = Quarto.query.filter(
            Quarto.status == 'disponível',
            ~Quarto.id.in_(quartos_ocupados)
        ).all()
        
        return jsonify({
            'success': True,
            'quartos': [q.to_dict() for q in quartos_disponiveis]
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api_bp.route('/reserva/<int:id>/status', methods=['PUT'])
def atualizar_status_reserva(id):
    try:
        reserva = Reserva.query.get_or_404(id)
        novo_status = request.json.get('status')
        
        if novo_status in ['pendente', 'confirmada', 'cancelada', 'concluída']:
            reserva.status = novo_status
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Status inválido'}), 400
            
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500