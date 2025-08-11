from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = 'segredo123'

ARQUIVO_ESTOQUE = 'estoque.xlsx'
COLUNAS = ["Produto", "Quantidade", "Andar", "Prateleira", "Posicao", "UltimaAlteracao"]

def ler_estoque():
    if not os.path.exists(ARQUIVO_ESTOQUE):
        df = pd.DataFrame(columns=COLUNAS)
        df.to_excel(ARQUIVO_ESTOQUE, index=False)
        return []
    df = pd.read_excel(ARQUIVO_ESTOQUE)
    return df.to_dict(orient='records')

def salvar_estoque(produtos):
    df = pd.DataFrame(produtos)
    df.to_excel(ARQUIVO_ESTOQUE, index=False)

@app.route('/', methods=['GET', 'POST'])
def index():
    produtos = ler_estoque()

    # Se o POST for para importação do Excel
    if request.method == 'POST':
        if 'upload_excel' in request.files:
            arquivo = request.files['upload_excel']
            if arquivo and arquivo.filename.endswith('.xlsx'):
                df = pd.read_excel(arquivo)
                if all(col in df.columns for col in COLUNAS):
                    df = df[COLUNAS]
                    salvar_estoque(df.to_dict(orient='records'))
                    flash('Estoque importado com sucesso!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Arquivo Excel inválido: faltam colunas necessárias.', 'danger')
            else:
                flash('Por favor, envie um arquivo Excel (.xlsx).', 'danger')

        else:
            # Pode colocar aqui outras ações POST, como formulário de adicionar produto
            produto = request.form.get('produto', '').strip()
            quantidade = request.form.get('quantidade')
            andar = request.form.get('andar', '').strip()
            prateleira = request.form.get('prateleira', '').strip()
            posicao = request.form.get('posicao', '').strip()
            usuario = request.form.get('usuario', '').strip()

            if not produto or not quantidade or not usuario:
                flash('Produto, quantidade e quem está alterando são obrigatórios.', 'danger')
                return redirect(url_for('index'))

            try:
                quantidade = int(quantidade)
            except:
                flash('Quantidade deve ser um número.', 'danger')
                return redirect(url_for('index'))

            produtos.append({
                "Produto": produto,
                "Quantidade": quantidade,
                "Andar": andar,
                "Prateleira": prateleira,
                "Posicao": posicao,
                "UltimaAlteracao": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })
            salvar_estoque(produtos)
            flash('Produto adicionado com sucesso!', 'success')
            return redirect(url_for('index'))

    return render_template('index.html', produtos=produtos)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    produtos = ler_estoque()
    if id < 0 or id >= len(produtos):
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    produto = produtos[id]

    if request.method == 'POST':
        produto['Produto'] = request.form.get('produto', '').strip()
        quantidade = request.form.get('quantidade')
        produto['Andar'] = request.form.get('andar', '').strip()
        produto['Prateleira'] = request.form.get('prateleira', '').strip()
        produto['Posicao'] = request.form.get('posicao', '').strip()

        if not produto['Produto'] or not quantidade:
            flash('Produto e quantidade são obrigatórios.', 'danger')
            return redirect(url_for('editar', id=id))
        try:
            produto['Quantidade'] = int(quantidade)
        except:
            flash('Quantidade deve ser número.', 'danger')
            return redirect(url_for('editar', id=id))

        produto['UltimaAlteracao'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        salvar_estoque(produtos)
        flash('Produto atualizado com sucesso!', 'success')
        return redirect(url_for('index'))

    return render_template('editar.html', produto=produto, id=id)

@app.route('/remover/<int:id>', methods=['POST'])
def remover(id):
    produtos = ler_estoque()
    if id < 0 or id >= len(produtos):
        flash('Produto não encontrado.', 'danger')
        return redirect(url_for('index'))

    removido = produtos.pop(id)
    salvar_estoque(produtos)
    flash(f'Produto "{removido["Produto"]}" removido com sucesso!', 'success')
    return redirect(url_for('index'))

# Exemplo para rota enviar whatsapp (você ajusta)
@app.route('/enviar_whatsapp', methods=['POST'])
def enviar_whatsapp():
    numero = request.form.get('numero', '').strip()
    produto = request.form.get('produto', '').strip()
    if not numero or not produto:
        flash('Número e produto são obrigatórios para enviar WhatsApp.', 'danger')
        return redirect(url_for('index'))
    # Construir URL whatsapp
    texto = f"Olá, gostaria de informações sobre o produto: {produto}"
    url = f"https://api.whatsapp.com/send?phone={numero}&text={urllib.parse.quote(texto)}"
    return redirect(url)

if __name__ == '__main__':
    app.run(debug=True)
