# app.py - Código principal
from flask import Flask, render_template
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'senha-secreta-pousada'

# Dados da pousada
POUSADA_INFO = {
    'nome': 'Pousada Alegrim',
    'slogan': 'Conforto e sabor em Saquarema',
    'diferencial': 'Oferecemos um rico café da manhã como parte da diária',
    'endereco': 'Rua 95, nº 362 - Jaconé, Saquarema - RJ',
    'telefone': '(22) 99999-9999',
    'email': 'contato@pousadaalegrim.com',
    'descricao': 'Uma pousada acolhedora no coração de Saquarema, perfeita para quem busca descanso e contato com a natureza.',
    'servicos': [
        'Café da manhã completo incluso',
        'Wi-Fi gratuito',
        'Estacionamento',
        'Quintal com jardim',
        'Proximidade da praia',
        'Ar-condicionado',
        'TV a cabo'
    ]
}

@app.route('/')
def index():
    return render_template('index.html', info=POUSADA_INFO)

@app.route('/sobre')
def sobre():
    return render_template('sobre.html', info=POUSADA_INFO)

@app.route('/quartos')
def quartos():
    quartos = [
        {
            'nome': 'Quarto Standard',
            'descricao': 'Ideal para casais, com cama de casal e vista para o jardim.',
            'preco': 'R$ 200/noite',
            'comodidades': ['Cama de casal', 'TV', 'Frigobar', 'Banheiro privativo']
        },
        {
            'nome': 'Quarto Familiar',
            'descricao': 'Espaçoso, acomoda até 4 pessoas, perfeito para famílias.',
            'preco': 'R$ 350/noite',
            'comodidades': ['2 camas de casal', 'TV', 'Frigobar', 'Varanda', 'Banheiro privativo']
        },
        {
            'nome': 'Suíte Luxo',
            'descricao': 'Nossa melhor acomodação, com hidromassagem e vista para o mar.',
            'preco': 'R$ 500/noite',
            'comodidades': ['Cama king size', 'Hidromassagem', 'Varanda ampla', 'TV 50"', 'Cafeteira']
        }
    ]
    return render_template('quartos.html', info=POUSADA_INFO, quartos=quartos)

@app.route('/contato')
def contato():
    return render_template('contato.html', info=POUSADA_INFO)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)