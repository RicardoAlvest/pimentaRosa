from flask import Flask, render_template, request, redirect, session, jsonify, flash
from bokeh.plotting import figure
from bokeh.embed import components
import mysql.connector
import json
import pandas as pd
import numpy as np


app = Flask(__name__)
app.secret_key = 'mysecretkey'  # Chave secreta para sessões
app.config['DEBUG'] = True
carrinho = []

# Função para estabelecer conexão com o banco de dados MySQL
def get_database_connection():
    connection = mysql.connector.connect(
        pool_name="mypool",
        pool_size=10,
        host="br586.hostgator.com.br",
        user="pimen441_ricardoalvest",
        passwd="Cods4740@",
        port="3306",
        db="pimen441_pimenta_rosa_banco",
    )
    return connection


# Rota da página de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Verificação das credenciais de login no banco de dados
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM usuarios WHERE username=%s AND password=%s"
        values = (username, password)
        cursor.execute(query, values)
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        
        if user:
            session['username'] = user[1]  # Armazena o nome de usuário na sessão
            return redirect('/pagina_inicial')
        else:
            error_message = 'Credenciais inválidas. Tente novamente.'
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

# Rota da página inicial@app.route('/pagina_inicial')
@app.route('/pagina_inicial')
def pagina_inicial():
    username = session.get('username')
    
    
    # Dados de exemplo para o gráfico
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May']
    sales = [1500, 1200, 1800, 2000, 1600]

    # Criação do gráfico de linhas
    p = figure(x_range=months, width=400, height=300, title="Vendas Mensais")
    p.line(months, sales, line_width=2)
    
    # Gera o código HTML e o script do gráfico
    script, div = components(p)
    
    
    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT * FROM `anotacoes`ORDER BY data_solicitacao DESC "
    cursor.execute(query)
    anotacoes = cursor.fetchall()
    # Descrições das colunas
    #nomes_colunas = [desc[0] for desc in cursor.description]  # Descrições das colunas

    # Consulta para buscar as anotações
    query2 = "SELECT (DISPONIBILIDADE), (DESCRICAO_PRODUTO), SUM(QTD), SUM(CUSTO_DA_PECA), SUM(REVENDA), SUM(LUCRO) FROM estoque_pimenta_rosa WHERE DISPONIBILIDADE LIKE 'DISPONIVEL' GROUP BY DESCRICAO_PRODUTO ORDER BY SUM(QTD) DESC"
    cursor.execute(query2)
    pizza_dash = cursor.fetchall()
    
    # Consulta para buscar as anotações
    query3 = "SELECT (DISPONIBILIDADE), (DESCRICAO_PRODUTO), SUM(QTD), SUM(CUSTO_DA_PECA), SUM(REVENDA), SUM(LUCRO) FROM estoque_pimenta_rosa WHERE DISPONIBILIDADE LIKE 'VENDIDO' GROUP BY DESCRICAO_PRODUTO ORDER BY SUM(LUCRO) DESC"
    cursor.execute(query3)
    pizza_dash_vendido = cursor.fetchall()
    
   # Consulta para buscar as vendas
    query1 = "SELECT (DISPONIBILIDADE), SUM(QTD), SUM(CUSTO_DA_PECA), SUM(REVENDA), SUM(LUCRO) FROM estoque_pimenta_rosa GROUP BY DISPONIBILIDADE ORDER BY MONTH(MES_DA_VENDA) DESC"
    cursor.execute(query1)
    tabela_geral = cursor.fetchall()
    
    #GRAFICO DE LUCRO
    query4 = "SELECT MONTH(MES_DA_VENDA),(DISPONIBILIDADE), SUM(QTD), SUM(CUSTO_DA_PECA), SUM(REVENDA), SUM(LUCRO) FROM estoque_pimenta_rosa WHERE DISPONIBILIDADE LIKE 'VENDIDO' GROUP BY MONTH(MES_DA_VENDA) ORDER BY SUM(QTD) DESC"
    cursor.execute(query4)
    tabel_pizza = cursor.fetchall() 
     
    #GRAFICO DE LUCRO
    query5 = "SELECT MONTH(DATA),(GRUPO), SUM(CLASSIFICACAO), SUM(VALOR) FROM financeiro_desp GROUP BY MONTH(DATA) ORDER BY MONTH(DATA)"
    cursor.execute(query5)
    tabel_pizza1 = cursor.fetchall() 
     
    # Cálculo das variáveis
    disponibilidade_total = sum(row[1] for row in tabela_geral)
    total_custo = sum(row[2] for row in tabela_geral)
    total_final = sum(row[3] for row in tabela_geral)
    total_lucro = sum(row[4] for row in tabela_geral)


    cursor.close()
    connection.close()

    if username:
        return render_template('pagina_inicial.html', username=username, script=script, div=div, anotacoes=anotacoes,tabela_geral=tabela_geral, disponibilidade_total=disponibilidade_total, total_custo=total_custo, total_final=total_final, total_lucro=total_lucro,pizza_dash=pizza_dash,pizza_dash_vendido=pizza_dash_vendido,tabel_pizza=tabel_pizza,tabel_pizza1=tabel_pizza1)
    else:
        return redirect('/login')

# ... Existing Flask routes ...

@app.route('/estoque')
def estoque():
    username = session.get('username')
    
    if not username:
        return redirect('/login')

    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT * FROM `estoque_pimenta_rosa`"
    cursor.execute(query)
    estoque_pimenta_rosa = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('estoque.html', username=username, estoque=estoque_pimenta_rosa)

@app.route('/encomendas')
def encomedas():
    username = session.get('username')
    
    if not username:
        return redirect('/login')

    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT * FROM `banco_encomendas`ORDER BY ID DESC"
    cursor.execute(query)
    banco_encomendas = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('encomendas.html', username=username, encomendas=banco_encomendas)


@app.route('/cadastroproduto')
def cadastroproduto():
    username = session.get('username')
    
    if not username:
        return redirect('/login')

    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT * FROM `estoque_pimenta_rosa` ORDER BY ID DESC"
    cursor.execute(query)
    banco_encomendas = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('cadastroproduto.html', username=username, banco_encomendas=banco_encomendas)

@app.route('/financeiro')
def financeiro():
    username = session.get('username')
    
    if not username:
        return redirect('/login')

    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT * FROM `financeiro_desp`"
    cursor.execute(query)
    finan = cursor.fetchall()
    
    query1 = "SELECT ID,CLASSIFICACAO,GRUPO,DESCRICAO,DATA,SUM(VALOR),CONCLUSAO FROM `financeiro_desp`GROUP BY GRUPO ORDER BY MONTH(DATA) DESC"
    cursor.execute(query1)
    rowa = cursor.fetchall()
    
    query2 = "SELECT ID,CLASSIFICACAO,GRUPO,DESCRICAO,MONTH(DATA) AS MES,SUM(VALOR),CONCLUSAO FROM `financeiro_desp`GROUP BY MONTH(DATA) ORDER BY MONTH(DATA) ASC"
    cursor.execute(query2)
    rowa2 = cursor.fetchall()
    
    query3 = "SELECT MONTH(DATA_VENDA) AS MES, CONCAT(FORMAT(SUM(VALOR_VENDA), 2)) AS VALORES, CONCAT(FORMAT(SUM(VALOR_CUSTO), 2)) AS CUSTOS, CONCAT(FORMAT(SUM(VALOR_VENDA - VALOR_CUSTO), 2)) AS LUCROS, SUM(NOVO_DESCONTO) AS DESCONTOS FROM venda_finalizada_pimentarosa GROUP BY MONTH(DATA_VENDA) ORDER BY MONTH(DATA_VENDA) ASC"
    cursor.execute(query3) 
    tabela_geral= cursor.fetchall()
    
    
    
    cursor.close()
    connection.close()
    
    
    #PARTE ONDE FOI FEITO O CALCULO DA TABELA:
    
    
    # Configuração da conexão com o banco de dados MySQL
    db_config = {
    'host': 'br586.hostgator.com.br',
    'user': 'pimen441_ricardoalvest',
    'password': 'Cods4740@',
    'port': 3306,  # Porta deve ser um número, não uma string
    'database': 'pimen441_pimenta_rosa_banco',
    }

    # Estabelecer conexão com o banco de dados MySQL
    conn = mysql.connector.connect(**db_config)

    # Definir suas consultas SQL
    query12 = "SELECT MONTH(DATA) AS MES, SUM(VALOR) AS TOTAL FROM `financeiro_desp` GROUP BY MES ORDER BY MES ASC"
    query13 = "SELECT MONTH(DATA_VENDA) AS MES, CONCAT(FORMAT(SUM(VALOR_VENDA), 2)) AS VALORES, CONCAT(FORMAT(SUM(VALOR_CUSTO), 2)) AS CUSTOS, CONCAT(FORMAT(SUM(VALOR_VENDA - VALOR_CUSTO), 2)) AS LUCROS, SUM(NOVO_DESCONTO) AS DESCONTOS FROM venda_finalizada_pimentarosa WHERE TIPO_VENDA LIKE 'AVISTA'  AND BAIXA_SIS LIKE 'Baixado' GROUP BY MES ORDER BY MES ASC"

    # Carregar os resultados das consultas em DataFrames
    df1 = pd.read_sql(query12, conn)
    df2 = pd.read_sql(query13, conn)

    # Fechar a conexão com o banco de dados
    conn.close()

    # Realizar o join entre os DataFrames
    df_joined = pd.merge(df2, df1, on='MES', how='outer')  # 'inner' para um inner join
    df_joined['VALORES'] = df_joined['VALORES'].astype(str).str.replace(',', '').astype(float)
    df_joined['VALORES'] = df_joined['VALORES'].fillna(0)
    df_joined['CUSTOS'] = df_joined['CUSTOS'].astype(str).str.replace(',', '').astype(float)
    df_joined['CUSTOS'] = df_joined['CUSTOS'].fillna(0)
    df_joined['LUCROS'] = df_joined['LUCROS'].astype(str).str.replace(',', '').astype(float)
    df_joined['LUCROS'] = df_joined['LUCROS'].fillna(0)
    df_joined['DESCONTOS'] = df_joined['DESCONTOS'].astype(str).str.replace(',', '').astype(float)
    df_joined['DESCONTOS'] = df_joined['DESCONTOS'].fillna(0)
    df_joined['TOTAL'] = df_joined['TOTAL'].astype(str).str.replace(',', '').astype(float)
    df_joined['TOTAL'] = df_joined['TOTAL'].fillna(0)



    df_joined = df_joined.rename(columns={'TOTAL': 'DESPESA'})
    df_joined['LUCRO DEPOIS DESPESA'] = df_joined['LUCROS']-df_joined['DESCONTOS']-df_joined['DESPESA']
    df_joined['LUCRO DEPOIS DESPESA'] = df_joined['LUCRO DEPOIS DESPESA'].fillna(0)
    df_joined['LUCRO DEPOIS DESPESA'] = df_joined['LUCRO DEPOIS DESPESA'].astype(str).str.replace(',', '').astype(float)

    df_joined['INVESTIMENTO 60%'] = df_joined['LUCRO DEPOIS DESPESA']* 0.60
    df_joined['VIAGEM 10%'] = df_joined['LUCRO DEPOIS DESPESA']* 0.10
    df_joined['PROLABORE 30%'] = df_joined['LUCRO DEPOIS DESPESA']* 0.30
    df_joined['DIVISAO'] = df_joined['PROLABORE 30%'] / 2
    
    df_joined['DIVISAO'] = df_joined['DIVISAO'].fillna(0)
    df_joined['DIVISAO'] = df_joined['DIVISAO'].astype(str).str.replace(',', '').astype(float)
    df_joined['PROLABORE 30%'] = df_joined['PROLABORE 30%'].fillna(0)
    df_joined['PROLABORE 30%'] = df_joined['PROLABORE 30%'].astype(str).str.replace(',', '').astype(float)
    df_joined['VIAGEM 10%'] = df_joined['VIAGEM 10%'].fillna(0)
    df_joined['VIAGEM 10%'] = df_joined['VIAGEM 10%'].astype(str).str.replace(',', '').astype(float)
    df_joined['INVESTIMENTO 60%'] = df_joined['INVESTIMENTO 60%'].fillna(0)
    df_joined['INVESTIMENTO 60%'] = df_joined['INVESTIMENTO 60%'].astype(str).str.replace(',', '').astype(float)
    
    
    # Calcula os totais das colunas
    total_despesa = df_joined['DESPESA'].sum()
    total_valores = df_joined['VALORES'].sum()
    total_custos = df_joined['CUSTOS'].sum()
    total_lucros = df_joined['LUCROS'].sum()
    total_descontos = df_joined['DESCONTOS'].sum()
    total_lucrodepoisdesp = df_joined['LUCRO DEPOIS DESPESA'].sum()
    total_investimento = df_joined['INVESTIMENTO 60%'].sum()
    total_viagem = df_joined['VIAGEM 10%'].sum()
    total_prolabore = df_joined['PROLABORE 30%'].sum()
    total_divisao = df_joined['DIVISAO'].sum()

    # Cria uma nova linha para o total e adiciona ao DataFrame
    total_row = {'MES': 'Total',
             'DESPESA': total_despesa,
             'VALORES': total_valores,
             'LUCROS' : total_lucros,
             'CUSTOS': total_custos,
             'DESCONTOS': total_descontos,
             'LUCRO DEPOIS DESPESA': total_lucrodepoisdesp,
             'INVESTIMENTO 60%': total_investimento,
             'VIAGEM 10%': total_viagem,
             'PROLABORE 30%': total_prolabore,
             'DIVISAO': total_divisao}

    df_joined = df_joined.append(total_row, ignore_index=True)


    # Mudar o nome das colunas:
    df_joined = df_joined.rename(columns={'VALORES': 'FATURAMENTO'})
    df_joined = df_joined.rename(columns={'LUCROS': 'DIFERENÇA'})
    
    
    
    
    return render_template('financeiro.html', username=username, finan=finan, rowa=rowa,rowa2=rowa2,tabela_geral=tabela_geral,table=df_joined.to_html(index=False))

@app.route('/projecao')
def projecao():
    username = session.get('username')
    
    if not username:
        return redirect('/login')

    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT DISTINCT(ID_COCATE),ID_VENDA,DATA_VENDA,MONTH(DATA_VENDA), VALOR_VENDA, FORMA_PAGAMENTO, NOME_VENDA, DESCONTO_VENDA, TIPO_VENDA, MES_VENDA, BAIXA_SIS, NOVO_DESCONTO FROM `venda_finalizada_pimentarosa` ORDER BY DATA_VENDA DESC"
    cursor.execute(query)
    venda_finalizada_pimentarosa = cursor.fetchall()
    # Consulta para buscar as vendas
    query1 = "SELECT DISTINCT COUNT(ID_COCATE), MONTH(DATA_VENDA) AS MES, SUM(VALOR_VENDA) AS TOTAL_VENDAS FROM `venda_finalizada_pimentarosa` GROUP BY MONTH(DATA_VENDA) ORDER BY MES"
    cursor.execute(query1)
    vendas_por_mes = cursor.fetchall()
    #vendas_json = json.dumps(venda_finalizada_pimentarosa)

    cursor.close()
    connection.close()

    return render_template('projecao.html', username=username, projecao=venda_finalizada_pimentarosa,dados_vendas_por_mes=vendas_por_mes)


@app.route('/receber_valores')
def receber_valores():
    username = session.get('username')
    
    if not username:
        return redirect('/login')

    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as anotações
    query = "SELECT DISTINCT(ID_COCATE),ID_VENDA,DATA_VENDA,MONTH(DATA_VENDA), VALOR_VENDA, FORMA_PAGAMENTO, NOME_VENDA, DESCONTO_VENDA, TIPO_VENDA, MES_VENDA, BAIXA_SIS, NOVO_DESCONTO, COMENTARIO, PENDENTE_VALOR FROM `venda_finalizada_pimentarosa` WHERE TIPO_VENDA LIKE 'RECEBER' ORDER BY DATA_VENDA DESC"
    cursor.execute(query)
    venda_finalizada_pimentarosa = cursor.fetchall()
    # Consulta para buscar as vendas
    query1 = "SELECT DISTINCT COUNT(ID_COCATE), MONTH(DATA_VENDA) AS MES, SUM(VALOR_VENDA) AS TOTAL_VENDAS FROM `venda_finalizada_pimentarosa` WHERE TIPO_VENDA LIKE 'RECEBER' GROUP BY MONTH(DATA_VENDA) ORDER BY MES"
    cursor.execute(query1)
    vendas_por_mes = cursor.fetchall()
    #vendas_json = json.dumps(venda_finalizada_pimentarosa)

    cursor.close()
    connection.close()

    return render_template('projecao.html', username=username, projecao=venda_finalizada_pimentarosa,dados_vendas_por_mes=vendas_por_mes)


@app.route('/projecao_dashboard')
def projecao_dashboard():
    username = session.get('username')
    
   
    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()
    cursor1 = connection.cursor()
    # Consulta para buscar as anotações
    query = "SELECT DISPONIBILIDADE,(DESCRICAO_PRODUTO), SUM(QTD), SUM(CUSTO_DA_PECA), SUM(REVENDA), SUM(LUCRO) FROM estoque_pimenta_rosa GROUP BY DESCRICAO_PRODUTO ORDER BY DISPONIBILIDADE"
    cursor.execute(query)
    pizza_dash = cursor.fetchall()
    
   # Consulta para buscar as vendas
    query1 = "SELECT (DISPONIBILIDADE), SUM(QTD), SUM(CUSTO_DA_PECA), SUM(REVENDA), SUM(LUCRO) FROM estoque_pimenta_rosa GROUP BY DISPONIBILIDADE ORDER BY MONTH(MES_DA_VENDA) DESC"
    cursor1.execute(query1)
    tabela_geral = cursor1.fetchall()
     # Cálculo das variáveis
    disponibilidade_total = sum(row[2] for row in tabela_geral)
    total_custo = sum(row[3] for row in tabela_geral)
    total_frete = sum(row[4] for row in tabela_geral)
    total_final = sum(row[5] for row in tabela_geral)
    total_lucro = sum(row[6] for row in tabela_geral)

    cursor.close()
    cursor1.close()
    connection.close()

    return render_template('pagina_inicial.html', username=username, tabela_geral=tabela_geral, disponibilidade_total=disponibilidade_total, total_custo=total_custo, total_frete=total_frete, total_final=total_final, total_lucro=total_lucro)

@app.route('/vendas')
def vendas():
    username = session.get('username')

    if not username:
        return redirect('/login')

    # Obter o carrinho da sessão
    carrinho = session.get('carrinho', [])
    
    # Conexão com o banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Consulta para buscar as vendas
    query = "SELECT * FROM `estoque_pimenta_rosa` WHERE DISPONIBILIDADE LIKE 'DISPONIVEL'"
    cursor.execute(query)
    vendas = cursor.fetchall()

    cursor.close()
    connection.close()

    valor_total = calcular_valor_total(carrinho)

    return render_template('vendas.html', username=username, vendas=vendas, carrinho=carrinho, valor_total=valor_total)



# Função para estabelecer conexão com o banco de dados MySQL
def get_database_connection():
    connection = mysql.connector.connect(
        pool_name="mypool",
        pool_size=10,
        host="br586.hostgator.com.br",
        user="pimen441_ricardoalvest",
        passwd="Cods4740@",
        port="3306",
        db="pimen441_pimenta_rosa_banco",
    )
    return connection


@app.route('/get_estoque_data')
def get_estoque_data():
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "SELECT * FROM estoque_pimenta_rosa"
    cursor.execute(query)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()

    data = []

    for row in rows:
        data.append({
            'id': row[0],
            'nome': row[1],
            'descricao': row[2],
            'quantidade': row[3]
        })

    return jsonify(data)


@app.route('/excluir_estoque', methods=['POST'])
def excluir_estoque():
    data = request.get_json()
    id = data['id']

    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM estoque_pimenta_rosa WHERE ID=%s"
    values = (id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return jsonify({'success': True})


@app.route('/editar_estoque/<int:id>', methods=['GET', 'POST'])
def editar_estoque(id):
    if request.method == 'POST':
        nome = request.form['nome']
        descricao = request.form['descricao']
        quantidade = request.form['quantidade']

        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE estoque_pimenta_rosa SET nome=%s, descricao=%s, quantidade=%s WHERE id=%s"
        values = (nome, descricao, quantidade, id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

        return redirect('/estoque')
    else:
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM estoque_pimenta_rosa WHERE id=%s"
        values = (id,)
        cursor.execute(query, values)
        row = cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template('editar_estoque.html', row=row)


@app.route('/editar_anotacao/<int:anotacao_id>', methods=['GET', 'POST'])
def editar_anotacao(anotacao_id):
    if request.method == 'POST':
        # Retrieve the updated annotation details from the form
        nome = request.form['nome']
        notas = request.form['notas']
        status = request.form['status']

        # Update the annotation in the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE anotacoes SET nome=%s, notas=%s, Status_mensagem=%s WHERE ID=%s"
        values = (nome, notas, status, anotacao_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

        return redirect('/pagina_inicial')
    else:
        # Retrieve the annotation from the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM anotacoes WHERE ID=%s"
        values = (anotacao_id,)
        cursor.execute(query, values)
        anotacao = cursor.fetchone()
        cursor.close()
        connection.close()

        return render_template('editar_anotacao.html', anotacao=anotacao)


@app.route('/excluir_anotacao/<int:anotacao_id>', methods=['POST'])
def excluir_anotacao(anotacao_id):
    # Delete the annotation from the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM anotacoes WHERE ID=%s"
    values = (anotacao_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/pagina_inicial')


@app.route('/alterar_status_anotacao/<int:anotacao_id>', methods=['POST'])
def alterar_status_anotacao(anotacao_id):
    # Update the status of the annotation in the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE anotacoes SET Status_mensagem = 'Concluido' WHERE ID=%s"
    values = (anotacao_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/pagina_inicial')

@app.route('/alterar_status_projecao/<int:anotacao_id>', methods=['POST'])
def alterar_status_projecao(anotacao_id):
    # Update the status of the annotation in the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE `venda_finalizada_pimentarosa` SET `TIPO_VENDA` = 'AVISTA' WHERE `venda_finalizada_pimentarosa`.`ID_VENDA` = %s"
    values = (anotacao_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/projecao')

@app.route('/alterar_status_projecao_receber/<int:anotacao_id>', methods=['POST'])
def alterar_status_projecao_receber(anotacao_id):
    # Update the status of the annotation in the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE `venda_finalizada_pimentarosa` SET `TIPO_VENDA` = 'RECEBER' WHERE `venda_finalizada_pimentarosa`.`ID_VENDA` = %s"
    values = (anotacao_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/projecao')

@app.route('/alterar_baixa_projecao/<int:projecao_id>', methods=['POST'])
def alterar_baixa_projecao(projecao_id):
    # Update the status of the annotation in the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE `venda_finalizada_pimentarosa` SET `BAIXA_SIS` = 'Baixado' WHERE `venda_finalizada_pimentarosa`.`ID_VENDA` = %s"
    values = (projecao_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/projecao')

@app.route('/inserir_encomenda', methods=['POST'])
def inserir_encomendas():
    # Retrieve the new annotation details from the form
    nome = request.form['nome']
    anotacoes = request.form['anotacoes']
    status = request.form['status']
    fornecedor = request.form['fornecedor']
    data_finalizacao = request.form['data_finalizacao']
    frete = request.form['frete']
    valor = request.form['valor']


    # Insert the new annotation into the database
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO banco_encomendas (NOME_USER, ANOTACAO, STATUS, FORNECEDOR, DATA_PRENCHIMENTO, DATA_FINALIZACAO, FRETE, VALOR) VALUES (%s, %s,%s,%s,CURRENT_TIMESTAMP(),%s,%s,%s)"

    values = (nome, anotacoes, status, fornecedor, data_finalizacao, frete, float(valor))
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/encomendas')

@app.route('/inserir_novo_produto', methods=['POST'])
def inserir_novo_produto():
    # Retrieve the new annotation details from the form
    
    fornecedor = request.form['fornecedor']
    cod_interno = request.form['cod_interno']
    descricao = request.form['descricao']
    tamanho = request.form['tamanho']
    Cor = request.form['Cor']
    qtd = request.form['qtd']
    compra = request.form['compra']
    frete = request.form['frete']
    custo_fixo = request.form['custo_fixo']
    valor_peca = request.form['valor_peca']
    revenda = request.form['revenda']
    markup = request.form['markup']
    estampa = request.form['estampa']
    lucro = request.form['lucro']
    disponibilidade = request.form['disponibilidade']


    # Insert the new annotation into the database
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO `estoque_pimenta_rosa` (`ID`, `FORNECEDOR`, `COD_INTERNO`, `DESCRICAO_PRODUTO`, `TAMANHO`, `COR`, `QTD`, `COMPRA`, `FRETE`, `CUSTO_FIXO`, `CUSTO_DA_PECA`, `REVENDA`, `MARKUP`, `ESTAMPA`, `LUCRO`, `DISPONIBILIDADE`, `DATA_INIC`,`VALOR_FINAL`) VALUES (NULL, %s, %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,CURRENT_TIMESTAMP(),%s)"
    values = (fornecedor,cod_interno, descricao, tamanho, Cor, float(qtd), float(compra), float(frete), float(custo_fixo), float(valor_peca), float(revenda), markup, estampa, float(lucro), disponibilidade,float(revenda))
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/cadastroproduto')

@app.route('/inserir_despesa', methods=['POST'])
def inserir_despesa():
    # Retrieve the new annotation details from the form
    classificacao = request.form['classificacao']
    grupo = request.form['grupo']    
    descricao = request.form['descricao']
    data = request.form['data']    
    valor = request.form['valor']
    status = request.form['status']


    # Insert the new annotation into the database
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO `financeiro_desp` (`ID`, `CLASSIFICACAO`, `GRUPO`, `DESCRICAO`, `DATA`, `VALOR`, `CONCLUSAO`) VALUES (NULL,%s, %s,%s,%s,%s,%s)"

    values = (classificacao, grupo, descricao, data, float(valor), status)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/financeiro')

@app.route('/excluir_despesa/<int:despesa_id>', methods=['POST'])
def excluir_despesa(despesa_id):
    # Delete the annotation from the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM `financeiro_desp` WHERE ID=%s"
    values = (despesa_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/financeiro')

@app.route('/excluir_encomendas/<int:despesa_id>', methods=['POST'])
def excluir_encomendas(despesa_id):
    # Delete the annotation from the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "DELETE FROM `banco_encomendas` WHERE ID=%s"
    values = (despesa_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/encomendas')

@app.route('/excluir_produto/<int:despesa_id>', methods=['POST'])
def excluir_produto(despesa_id):
     # Connect to the MySQL database
        connection = get_database_connection()
        cursor = connection.cursor()

        # SQL query to get the product data
        query1 = "SELECT * FROM `estoque_pimenta_rosa` WHERE ID = %s"
        values = (despesa_id,)
        cursor.execute(query1, values)
        produtos1 = cursor.fetchall()

        for produto in produtos1:
            produto2 = produto[15]  # Substitua o índice pelo índice correto do elemento desejado
            

        # Close the database connection
        cursor.close()
        connection.close()
    
        if produto2 == 'DISPONIVEL':
            # Delete the annotation from the database using the anotacao_id
            connection = get_database_connection()
            cursor = connection.cursor()
            query = "DELETE FROM `estoque_pimenta_rosa` WHERE ID=%s"
            values = (despesa_id,)
            cursor.execute(query, values)
            connection.commit()
            cursor.close()
            connection.close()
        
            return redirect('/cadastroproduto')
        else:   
            print("Erro não pode excluir produto Vendido")
            return redirect('/cadastroproduto')

@app.route('/alterar_status_despesa/<int:despesa_id>', methods=['POST'])
def alterar_status_despesa(despesa_id):
    # Update the status of the annotation in the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE `financeiro_desp` SET CONCLUSAO = 'PAGO' WHERE ID=%s"
    values = (despesa_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/financeiro')

@app.route('/alterar_status_encomendas/<int:despesa_id>', methods=['POST'])
def alterar_status_encomendas(despesa_id):
    # Update the status of the annotation in the database using the anotacao_id
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "UPDATE `banco_encomendas` SET `STATUS` = 'CONCLUIDO' WHERE ID=%s"
    values = (despesa_id,)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/encomendas')

@app.route('/editar_financeiro/<int:despesa_id>', methods=['POST'])
def editar_financeiro(despesa_id):
    if request.method == 'POST':
        # Retrieve the updated annotation details from the form
        classificacao = request.form['classificacao']
        grupo = request.form['grupo']    
        descricao = request.form['descricao']
        data = request.form['data']    
        valor = request.form['valor']
        status = request.form['status']
        # Update the annotation in the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE `financeiro_desp` SET classificacao=%s, grupo=%s, descricao=%s, data=%s, valor=%s, CONCLUSAO=%s WHERE ID=%s"
        values = (classificacao, grupo, descricao, data, float(valor),status, despesa_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

   
    return redirect('/financeiro')

@app.route('/editar_desconto/<int:despesa_id>', methods=['POST'])
def editar_desconto(despesa_id):
    if request.method == 'POST':
        # Retrieve the updated annotation details from the form
       
        desconto_extra = request.form['desconto_extra']
        
        # Update the annotation in the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE `venda_finalizada_pimentarosa` SET `NOVO_DESCONTO` =%s WHERE `venda_finalizada_pimentarosa`.`ID_VENDA` =%s"
        values = (float(desconto_extra), despesa_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

   
    return redirect('/projecao')

@app.route('/editar_receber_valores/<int:despesa_id>', methods=['POST'])
def editar_receber_valores(despesa_id):
    if request.method == 'POST':
        # Retrieve the updated annotation details from the form
        data = request.form['data']
        desconto_extra = request.form['desconto_extra']
        mensagem = request.form['mensagem']
        pendente_valor = request.form['pendente_valor']
        
        
        # Update the annotation in the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE `venda_finalizada_pimentarosa` SET DATA_VENDA = %s,`NOVO_DESCONTO` = %s, COMENTARIO = %s, PENDENTE_VALOR = %s WHERE `venda_finalizada_pimentarosa`.`ID_VENDA` =%s"
        values = (data,float(desconto_extra),mensagem,float(pendente_valor), despesa_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

   
    return redirect('/receber_valores')

@app.route('/editar_cadastrarproduto/<int:despesa_id>', methods=['POST'])
def editar_cadastrarproduto(despesa_id):
    if request.method == 'POST':
        # Retrieve the updated annotation details from the form
        fornecedor = request.form['fornecedor']
        cod_interno = request.form['cod_interno']
        descricao = request.form['descricao']
        tamanho = request.form['tamanho']
        Cor = request.form['Cor']
        qtd = request.form['qtd']
        compra = request.form['compra']
        frete = request.form['frete']
        custo_fixo = request.form['custo_fixo']
        valor_peca = request.form['valor_peca']
        revenda = request.form['revenda']
        markup = request.form['markup']
        estampa = request.form['estampa']
        lucro = request.form['lucro']
        #disponibilidade = request.form['disponibilidade']
        
        
        # Update the annotation in the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE `estoque_pimenta_rosa` SET `FORNECEDOR` = %s, `COD_INTERNO` = %s, `DESCRICAO_PRODUTO` = %s, `TAMANHO` = %s, `COR` = %s,`QTD` = %s, `COMPRA` = %s, `FRETE` = %s, `CUSTO_FIXO` = %s, `CUSTO_DA_PECA` = %s, `REVENDA` = %s, `MARKUP` = %s, `ESTAMPA` = %s, `LUCRO` = %s, `VALOR_FINAL` = %s WHERE `estoque_pimenta_rosa`.`ID` =%s"
        values = (fornecedor, cod_interno, descricao, tamanho, Cor, float(qtd), float(compra), float(frete), float(custo_fixo), float(valor_peca), float(revenda), markup, estampa, float(lucro),float(revenda), despesa_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

   
    return redirect('/cadastroproduto')

@app.route('/editar_encomedas/<int:despesa_id>', methods=['POST'])
def editar_encomedas(despesa_id):
    if request.method == 'POST':
        # Retrieve the updated annotation details from the form
        nome = request.form['nome']
        anotacoes = request.form['anotacoes']    
        status = request.form['status']
        fornecedor = request.form['fornecedor']    
        data_finalizacao = request.form['data_finalizacao']
        frete = request.form['frete']
        valor = request.form['valor']
        # Update the annotation in the database using the anotacao_id
        connection = get_database_connection()
        cursor = connection.cursor()
        query = "UPDATE `banco_encomendas` SET `NOME_USER` = %s, `ANOTACAO` = %s, `STATUS` = %s, `FORNECEDOR` = %s, `DATA_FINALIZACAO` = %s, `FRETE` = %s, `VALOR` = %s WHERE `banco_encomendas`.`ID`=%s"
        values = (nome, anotacoes, status, fornecedor, data_finalizacao,frete,valor, despesa_id)
        cursor.execute(query, values)
        connection.commit()
        cursor.close()
        connection.close()

   
    return redirect('/encomendas')

@app.route('/inserir_anotacao', methods=['POST'])
def inserir_anotacao():
    # Retrieve the new annotation details from the form
    nome = request.form['nome']
    notas = request.form['notas']
    status = request.form['status']

    # Insert the new annotation into the database
    connection = get_database_connection()
    cursor = connection.cursor()
    query = "INSERT INTO anotacoes (nome, notas, data_solicitacao, Status_mensagem) VALUES (%s, %s,CURRENT_TIMESTAMP(),%s)"

    values = (nome, notas, status)
    cursor.execute(query, values)
    connection.commit()
    cursor.close()
    connection.close()

    return redirect('/pagina_inicial')


@app.route('/produtos')
def get_produtos():
    try:
        # Connect to the MySQL database
        connection = get_database_connection()
        cursor = connection.cursor()

        # SQL query to get the product data
        query = "SELECT * FROM `estoque_pimenta_rosa` WHERE DISPONIBILIDADE LIKE 'DISPONIVEL'"
        cursor.execute(query)
        produtos = cursor.fetchall()

        # Close the database connection
        cursor.close()
        connection.close()

        # Return the product data in JSON format
        return jsonify(produtos)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/login')


@app.route('/')
def index():
    return render_template('index.html', vendas=vendas)

@app.route('/adicionar_ao_carrinho', methods=['POST'])
def adicionar_ao_carrinho():
    # Obter os detalhes do produto do formulário
    produto_id = int(request.form['produto_id'])
    descricao = request.form['descricao']
    disponibilidade = request.form['disponibilidade']
    valor_final = float(request.form['valor_final'])
    valor_custo = float(request.form['valor_custo'])

    # Obter o carrinho da sessão
    carrinho = session.get('carrinho', [])

    # Adicionar o produto ao carrinho
    carrinho.append((produto_id, descricao, disponibilidade, valor_final,valor_custo))
    session['carrinho'] = carrinho

    # Recalcular o valor total
    valor_total = calcular_valor_total(carrinho)
    valor_custo = calcular_valor_custo(carrinho)

    return redirect('/vendas')

def exibir_carrinho():
    carrinho = session.get('carrinho', [])  # Obter o carrinho da sessão
    valor_total = calcular_valor_total(carrinho, desconto)  # Calcular o valor total do carrinho (sem desconto)
    return render_template('vendas.html', carrinho=carrinho, valor_total=valor_total)

def calcular_valor_total(carrinho,desconto=0):
    valor_total = 0.0
    
    for produto in carrinho:
        valor_produto = produto[3]
        valor_total += valor_produto

    desconto = float(desconto)
    valor_total -= desconto
    return valor_total

def calcular_valor_custo(carrinho):
    valor_total = 0.0
    
    for produto in carrinho:
        valor_produto = produto[4]
        valor_total += valor_produto


    return valor_total

def obter_valor_produto(produto_id):
    connection = get_database_connection()
    cursor = connection.cursor()

    sql_select = "SELECT VALOR_FINAL FROM estoque_pimenta_rosa WHERE ID = %s"
    cursor.execute(sql_select, (produto_id,))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if result:
        valor_produto = result[0]
        return valor_produto
    else:
        # Product not found, return a default value or handle as per your needs
        return 0

@app.route('/finalizarvenda', methods=['POST'])
def finalizarvenda():
    # Logic to finalize the sale
    carrinho = session.get('carrinho', [])  # Get the cart from the session

    if not carrinho:
        return render_template('erro.html', mensagem='O carrinho está vazio')

    # Conecte-se ao banco de dados
    connection = get_database_connection()
    cursor = connection.cursor()

    # Percorra os produtos no carrinho e atualize o banco de dados
    for produto in carrinho:
        produto_id = produto[0]

        # Verifique se o produto está disponível antes de atualizar
        sql_select_disponibilidade = "SELECT DISPONIBILIDADE FROM estoque_pimenta_rosa WHERE ID = %s"
        cursor.execute(sql_select_disponibilidade, (produto_id,))
        disponibilidade = cursor.fetchone()

        if disponibilidade and disponibilidade[0] == 'DISPONIVEL':
            # O produto está disponível, pode ser atualizado
            sql_update = "UPDATE estoque_pimenta_rosa SET `DISPONIBILIDADE` = 'VENDIDO', MES_DA_VENDA = CURRENT_DATE WHERE ID = %s"
            cursor.execute(sql_update, (produto_id,))
            connection.commit()
        else:
            # O produto não está disponível
            print("Produto não disponível para venda:", produto_id)

    desconto = request.form.get('desconto')
    nomecliente = request.form.get('nome_cliente')
    telefone_davenda = request.form.get('telefonedavenda1')
    cpf_cliente = request.form.get('cpf_cliente')    
    formapagamento = request.form.get('tipo_pagamento')
    tipodevenda = request.form.get('statusdavenda')
    criarcadastrocliente = request.form.get('cadastrarcliente')
    
    if nomecliente is None or nomecliente == "":
        nomecliente = "NaoPreenchido"
        
    if telefone_davenda is None or telefone_davenda == "":
        telefone_davenda = 000    
        
    if cpf_cliente is None or cpf_cliente == "":
        cpf_cliente = "000"
    
    if tipodevenda is None or tipodevenda == "":
        tipodevenda = "AVISTA"

    if formapagamento is None or formapagamento == "":
        formapagamento = "NaoPreenchido"
    
    if desconto:
        desconto = float(desconto)
    else:
        desconto = 0.0
     
    valor_total = calcular_valor_total(carrinho, desconto)
    valor_custo = calcular_valor_custo(carrinho)
    # Obter os IDs dos produtos no carrinho
    ids_produtos = [str(produto[0]) for produto in carrinho]
    
    # Concatenar os IDs em uma única string separada por vírgulas
    dadosconcatenados = ','.join(ids_produtos)

    baixa_sis=str('Pendente') 
    valor_produto = valor_total
    lucro_calculado=float(valor_produto)-float(valor_custo)
    sql_insert = "INSERT INTO venda_finalizada_pimentarosa (ID_VENDA, DATA_VENDA, ID_PRODUTO, VALOR_VENDA, VALOR_LUCRO, VALOR_CUSTO, FORMA_PAGAMENTO, NOME_VENDA, TELEFONE_VENDA, CPF_VENDA, DESCONTO_VENDA, TIPO_VENDA, ID_COCATE, MES_VENDA, BAIXA_SIS) VALUES (NULL, CURRENT_TIMESTAMP(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,CURRENT_DATE(), %s)"
    #for produto in carrinho:
    produto_id = str(carrinho)    
    print("SQL Query:", sql_insert)  # Print the SQL query before execution
    cursor.execute(sql_insert, (produto_id, float(valor_produto),float(lucro_calculado),float(valor_custo), formapagamento, nomecliente, telefone_davenda, cpf_cliente, float(desconto), tipodevenda, dadosconcatenados,baixa_sis))
    connection.commit()
    
    if criarcadastrocliente == "on":
        connection = get_database_connection()
        cursor = connection.cursor()
        sql_insert1 = "INSERT INTO cadastro_clientes_pimentarosa (`ID`, `NOME`,`CPF`, `TELEFONE`, `DIA_VENDA`) VALUES (NULL, %s, %s, %s,CURRENT_TIMESTAMP())"
        cursor.execute(sql_insert1, (nomecliente, cpf_cliente, telefone_davenda))
        connection.commit()

        
    # Feche a conexão com o banco de dados 
    cursor.close()
    connection.close()

    # Limpe o carrinho após finalizar a venda
    limparcarrinho()
    mensagem_popup = "Venda concluída com sucesso!"
    render_template('vendas.html', mensagem_popup=mensagem_popup)
    return redirect('/vendas')



@app.route('/confirmarvenda', methods=['POST'])
def confirmarvenda():
    # Lógica para finalizar a venda
    venda_id = request.form['venda_id']  # Obtém o ID da venda do formulário

    # Resto do seu código...

    return render_template('venda_finalizada.html', venda_id=venda_id)


@app.route('/limparcarrinho', methods=['POST'])
def limparcarrinho():
    # Logic to clear the cart
    # For example, you can simply reinitialize the 'carrinho' list to an empty list
    carrinho.clear()
    session['carrinho'] = carrinho
    return redirect('/vendas')


if __name__ == '__main__':
    app.run(debug=True)
