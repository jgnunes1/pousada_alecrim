# app.py - Versão atualizada com MySQL
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from config import Config
import MySQLdb.cursors
import re
from datetime import datetime, timedelta

app = Flask(__name__)
app.config.from_object(Config)

# Inicializar MySQL
mysql = MySQL(app)

# Dados estáticos da pousada (mantemos para compatibilidade)
POUSADA_INFO = {
    'nome': 'Pousada Alegrim',
    'slogan': 'Conforto e sabor em Saquarema',
    'diferencial': 'Oferecemos um rico café da manhã como parte da diária',
    'endereco': 'Rua 95, nº 362 - Jaconé, Saquarema - RJ',
    'telefone': '(22) 99999-9999',
    'email': 'contato@pousadaalegrim.com',
    'descricao': 'Uma pousada acolhedora no coração de Saquarema, perfeita para quem busca descanso e contato com a natureza.',
}

# Função para criar tabelas (executar apenas uma vez)
def criar_tabelas():
    try:
        cursor = mysql.connection.cursor()
        
        # Tabela de quartos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS quartos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                numero VARCHAR(10) UNIQUE NOT NULL,
                tipo ENUM('suíte', 'quarto', 'chalé') NOT NULL,
                andar VARCHAR(20),
                descricao TEXT,
                capacidade INT DEFAULT 2,
                preco_diaria DECIMAL(10,2) NOT NULL,
                status ENUM('disponível', 'ocupado', 'manutenção') DEFAULT 'disponível',
                fotos TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de hóspedes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hospedes (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome_completo VARCHAR(100) NOT NULL,
                cpf VARCHAR(14) UNIQUE NOT NULL,
                email VARCHAR(100),
                telefone VARCHAR(20),
                endereco TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de reservas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reservas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                quarto_id INT,
                hospede_id INT,
                data_checkin DATE NOT NULL,
                data_checkout DATE NOT NULL,
                num_hospedes INT DEFAULT 1,
                valor_total DECIMAL(10,2),
                status ENUM('confirmada', 'pendente', 'cancelada', 'concluída') DEFAULT 'pendente',
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quarto_id) REFERENCES quartos(id),
                FOREIGN KEY (hospede_id) REFERENCES hospedes(id)
            )
        ''')
        
        # Tabela de cardápio
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cardapio (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                descricao TEXT,
                categoria ENUM('entrada', 'principal', 'sobremesa', 'bebida') NOT NULL,
                preco DECIMAL(10,2) NOT NULL,
                disponivel BOOLEAN DEFAULT TRUE,
                foto VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de pedidos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pedidos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                reserva_id INT,
                item_id INT,
                quantidade INT DEFAULT 1,
                observacoes TEXT,
                status ENUM('pendente', 'preparando', 'pronto', 'entregue') DEFAULT 'pendente',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (reserva_id) REFERENCES reservas(id),
                FOREIGN KEY (item_id) REFERENCES cardapio(id)
            )
        ''')
        
        mysql.connection.commit()
        print("✅ Tabelas criadas com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")

# Rotas existentes (mantemos as anteriores)
@app.route('/')
def index():
    return render_template('index.html', info=POUSADA_INFO)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', info=POUSADA_INFO)

@app.route('/quartos')
def quartos():
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM quartos ORDER BY tipo, numero')
    quartos_db = cursor.fetchall()
    cursor.close()
    
    return render_template('quartos.html', info=POUSADA_INFO, quartos=quartos_db)

@app.route('/contato')
def contato():
    return render_template('contato.html', info=POUSADA_INFO)

# NOVAS ROTAS PARA GERENCIAMENTO

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Autenticação simples (em produção, usar hash!)
        if username == 'admin' and password == 'pousada123':
            session['admin_logged_in'] = True
            flash('Login realizado com sucesso!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Credenciais inválidas!', 'danger')
    
    return render_template('admin/login.html')

@app.route('/admin/dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()
    
    # Estatísticas
    cursor.execute('SELECT COUNT(*) as total FROM quartos')
    total_quartos = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM reservas WHERE status = "confirmada"')
    reservas_ativas = cursor.fetchone()['total']
    
    cursor.execute('SELECT COUNT(*) as total FROM hospedes')
    total_hospedes = cursor.fetchone()['total']
    
    cursor.execute('SELECT SUM(valor_total) as total FROM reservas WHERE MONTH(created_at) = MONTH(CURDATE())')
    receita_mes = cursor.fetchone()['total'] or 0
    
    cursor.close()
    
    return render_template('admin/dashboard.html',
                         total_quartos=total_quartos,
                         reservas_ativas=reservas_ativas,
                         total_hospedes=total_hospedes,
                         receita_mes=receita_mes)

@app.route('/admin/quartos')
def admin_quartos():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM quartos ORDER BY tipo, numero')
    quartos = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/quartos.html', quartos=quartos)

@app.route('/admin/reservas')
def admin_reservas():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT r.*, q.numero, h.nome_completo 
        FROM reservas r
        JOIN quartos q ON r.quarto_id = q.id
        JOIN hospedes h ON r.hospede_id = h.id
        ORDER BY r.data_checkin DESC
    ''')
    reservas = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/reservas.html', reservas=reservas)

@app.route('/admin/cardapio')
def admin_cardapio():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM cardapio ORDER BY categoria, nome')
    cardapio = cursor.fetchall()
    cursor.close()
    
    return render_template('admin/cardapio.html', cardapio=cardapio)

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logout realizado com sucesso!', 'success')
    return redirect(url_for('admin_login'))

# ROTA PÚBLICA PARA RESERVAS
@app.route('/reservar', methods=['GET', 'POST'])
def reservar():
    if request.method == 'POST':
        # Capturar dados do formulário
        nome = request.form['nome']
        cpf = request.form['cpf']
        email = request.form['email']
        telefone = request.form['telefone']
        quarto_id = request.form['quarto_id']
        checkin = request.form['checkin']
        checkout = request.form['checkout']
        num_hospedes = request.form['num_hospedes']
        
        try:
            cursor = mysql.connection.cursor()
            
            # Verificar se hóspede já existe
            cursor.execute('SELECT id FROM hospedes WHERE cpf = %s', (cpf,))
            hospede = cursor.fetchone()
            
            if not hospede:
                # Inserir novo hóspede
                cursor.execute('''
                    INSERT INTO hospedes (nome_completo, cpf, email, telefone)
                    VALUES (%s, %s, %s, %s)
                ''', (nome, cpf, email, telefone))
                hospede_id = cursor.lastrowid
            else:
                hospede_id = hospede['id']
            
            # Calcular valor total
            cursor.execute('SELECT preco_diaria FROM quartos WHERE id = %s', (quarto_id,))
            quarto = cursor.fetchone()
            preco_diaria = quarto['preco_diaria']
            
            # Calcular dias
            data_inicio = datetime.strptime(checkin, '%Y-%m-%d')
            data_fim = datetime.strptime(checkout, '%Y-%m-%d')
            dias = (data_fim - data_inicio).days
            valor_total = dias * preco_diaria
            
            # Inserir reserva
            cursor.execute('''
                INSERT INTO reservas (quarto_id, hospede_id, data_checkin, data_checkout, 
                                    num_hospedes, valor_total, status)
                VALUES (%s, %s, %s, %s, %s, %s, 'pendente')
            ''', (quarto_id, hospede_id, checkin, checkout, num_hospedes, valor_total))
            
            mysql.connection.commit()
            cursor.close()
            
            flash('Reserva realizada com sucesso! Aguarde confirmação.', 'success')
            return redirect(url_for('index'))
            
        except Exception as e:
            flash(f'Erro ao realizar reserva: {str(e)}', 'danger')
    
    # GET: mostrar formulário de reserva
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT * FROM quartos WHERE status = "disponível"')
    quartos_disponiveis = cursor.fetchall()
    cursor.close()
    
    return render_template('reservar.html', quartos=quartos_disponiveis)

# ROTA PÚBLICA PARA CARDÁPIO
@app.route('/cardapio')
def ver_cardapio():
    cursor = mysql.connection.cursor()
    cursor.execute('''
        SELECT * FROM cardapio 
        WHERE disponivel = TRUE 
        ORDER BY categoria, nome
    ''')
    cardapio = cursor.fetchall()
    cursor.close()
    
    # Agrupar por categoria
    cardapio_agrupado = {
        'entrada': [],
        'principal': [],
        'sobremesa': [],
        'bebida': []
    }
    
    for item in cardapio:
        cardapio_agrupado[item['categoria']].append(item)
    
    return render_template('cardapio.html', cardapio=cardapio_agrupado)

# EXECUTAR APLICAÇÃO
if __name__ == '__main__':
    # Criar tabelas na primeira execução
    with app.app_context():
        criar_tabelas()
        popular_dados_iniciais()  # Criaremos esta função
    app.run(debug=True, host='0.0.0.0', port=5000)