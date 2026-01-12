# app.py - Versão refatorada
import os
from flask import Flask
from config import Config
from models import db
from routes import init_app
from datetime import datetime

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensões
    db.init_app(app)
    
    # Registrar blueprints
    init_app(app)
    
    # Criar banco de dados e dados iniciais
    with app.app_context():
        criar_banco_dados(app)
    
    # Filtros de template
    @app.template_filter('format_currency')
    def format_currency(value):
        return f'R$ {float(value):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    
    @app.template_filter('format_date')
    def format_date(value, format='%d/%m/%Y'):
        if isinstance(value, str):
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        return value.strftime(format)
    
    return app

def criar_banco_dados(app):
    """Cria tabelas e insere dados iniciais"""
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas/verificadas")
            
            # Inserir dados iniciais se as tabelas estiverem vazias
            from models import Quarto, Cardapio
            
            if Quarto.query.count() == 0:
                inserir_dados_iniciais()
                print("✅ Dados iniciais inseridos")
                
        except Exception as e:
            print(f"⚠️  Erro ao criar banco: {e}")

def inserir_dados_iniciais():
    """Insere dados iniciais no banco"""
    from models import Quarto, Cardapio, StatusQuarto, CategoriaCardapio
    from datetime import datetime
    
    # Quartos
    quartos = [
        # Suítes
        Quarto(numero='30', tipo='suíte', andar='Térreo', 
               descricao='Suíte Luxo com hidromassagem e vista para o mar', 
               capacidade=2, preco_diaria=500.00),
        Quarto(numero='31', tipo='suíte', andar='Térreo',
               descricao='Suíte Conforto com varanda privativa',
               capacidade=2, preco_diaria=450.00),
        Quarto(numero='32', tipo='suíte', andar='Térreo',
               descricao='Suíte Familiar (até 4 pessoas)',
               capacidade=4, preco_diaria=600.00),
        Quarto(numero='33', tipo='suíte', andar='Térreo',
               descricao='Suíte Premium com jacuzzi',
               capacidade=2, preco_diaria=700.00),
        
        # Quartos 1º andar (101-105)
        *[Quarto(numero=f'10{i}', tipo='quarto', andar='1º Andar',
                descricao=f'Quarto standard {i} com vista para o jardim',
                capacidade=2, preco_diaria=200.00) for i in range(1, 6)],
        
        # Quartos 2º andar (201-206)
        *[Quarto(numero=f'20{i}', tipo='quarto', andar='2º Andar',
                descricao=f'Quarto superior {i} com varanda',
                capacidade=2, preco_diaria=250.00) for i in range(1, 7)],
        
        # Chalés
        Quarto(numero='01', tipo='chalé', andar='Área externa',
               descricao='Chalé familiar com cozinha e lareira',
               capacidade=6, preco_diaria=800.00),
        Quarto(numero='02', tipo='chalé', andar='Área externa',
               descricao='Chalé romântico com banheira',
               capacidade=2, preco_diaria=650.00),
    ]
    
    for quarto in quartos:
        db.session.add(quarto)
    
    # Cardápio
    cardapio_items = [
        # Entradas
        Cardapio(nome='Salada Caesar', 
                descricao='Alface romana, croutons, parmesão e molho Caesar',
                categoria=CategoriaCardapio.ENTRADA, preco=25.00),
        Cardapio(nome='Carpaccio de carne',
                descricao='Finas fatias de carne com rúcula e parmesão',
                categoria=CategoriaCardapio.ENTRADA, preco=35.00),
        
        # Principais
        Cardapio(nome='Filé Mignon',
                descricao='200g com molho madeira e purê de batatas',
                categoria=CategoriaCardapio.PRINCIPAL, preco=85.00),
        Cardapio(nome='Risoto de camarão',
                descricao='Risoto cremoso com camarões frescos',
                categoria=CategoriaCardapio.PRINCIPAL, preco=75.00),
        Cardapio(nome='Moqueca de peixe',
                descricao='Típica moqueca capixaba com arroz e pirão',
                categoria=CategoriaCardapio.PRINCIPAL, preco=70.00),
        Cardapio(nome='Frango à parmegiana',
                descricao='Filé de frango com molho de tomate e queijo',
                categoria=CategoriaCardapio.PRINCIPAL, preco=55.00),
        
        # Sobremesas
        Cardapio(nome='Pudim de leite',
                descricao='Tradicional pudim de leite condensado',
                categoria=CategoriaCardapio.SOBREMESA, preco=15.00),
        Cardapio(nome='Mousse de chocolate',
                descricao='Mousse cremosa de chocolate belga',
                categoria=CategoriaCardapio.SOBREMESA, preco=18.00),
        
        # Bebidas
        Cardapio(nome='Suco natural',
                descricao='Laranja, limão ou abacaxi com hortelã',
                categoria=CategoriaCardapio.BEBIDA, preco=12.00),
        Cardapio(nome='Refrigerante',
                descricao='Lata 350ml',
                categoria=CategoriaCardapio.BEBIDA, preco=8.00),
        Cardapio(nome='Cerveja artesanal',
                descricao='Chopp 500ml',
                categoria=CategoriaCardapio.BEBIDA, preco=20.00),
    ]
    
    for item in cardapio_items:
        db.session.add(item)
    
    db.session.commit()

# Ponto de entrada da aplicação
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)