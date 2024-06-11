import streamlit as st
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import select, insert, Table, MetaData, Column, Integer, String, DateTime, Float
from conexao import Conexao


class Cadastro:
    def atualizar(self):
        consulta = Conexao.conecta_bd()
        self.df_cadastro_estoque = consulta[12]
        return self.df_cadastro_estoque
    
    def widget_cadastro(self):
        with st.form(key='widget_produto', clear_on_submit=True):
            self.lista_unidade = ['Peça', 'Kilograma', 'Grama', 'Comprimento', 'Volume', 'Litros', 'Lata']
            self.produto = st.text_input(label='Nome do Produto')
            # self.codigo_produto = st.number_input(label='Código do Produto', value=int(0))
            self.unidade = st.selectbox('Unidade de Medida', self.lista_unidade, index=None, placeholder='')
            self.qtd_min = st.number_input(label='Quantidade Minímo', value=float('0.00'), step=1.0)
            self.qtd_max = st.number_input(label='Quantidade Máxima', value=float('0.00'), step=1.0)
            button_salvar_cadastro = st.form_submit_button(label='Salvar')
        self.codigo_produto = st.number_input(label='Código do Produto', value=int(0))
            
        if button_salvar_cadastro:
            self.salvar_cadastro()

    def salvar_cadastro(self):
        if self.produto == '':
            st.error(':red[Produto] precisa ser informado!', icon="🚨")
        elif self.codigo_produto in (None, ''):
            st.error('Definir :red[código do produto!]', icon="🚨")
        elif self.qtd_min <= 0:
            st.error(':red[Qtde Min] precisa ser maior que zero')
        elif self.qtd_max < self.qtd_min:
            st.error(':red[Qtde Max] tem que ser maior que Qtde Min')
        elif self.codigo_produto <= 0:
            st.error(':red[Código de barra] tem que ser maior que zero')
        else:            
            dt_atualizo = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")

            self.conecta_mysql()
            metadata = MetaData()
            cadastro_table = Table('cadastro_estoque', metadata,
                Column('ID_produto', Integer, primary_key=True),
                Column('produto', String),
                Column('codigo_produto', Integer),
                Column('qtd_min', Float),
                Column('qtd_max', Float),
                Column('unidade', String),
                Column('dt_atualizado', DateTime)
            )

            # Definindo os valores para inserção
            valores = {
                'produto': self.produto,
                'codigo_produto': int(self.codigo_produto),
                'qtd_min': float(self.qtd_min),
                'qtd_max': float(self.qtd_max),
                'unidade': self.unidade,
                'dt_atualizado': dt_atualizo
            }

            try:
                # Verificar se o nome do funcionário já existe na tabela
                stmt_select = select(cadastro_table).where(cadastro_table.c.produto == self.produto and cadastro_table.c.codigo_produto == self.codigo_produto)
                resultado = self.session.execute(stmt_select)
                existe_nome = resultado.fetchone() is not None

                if not existe_nome:
                    # Criando uma instrução de INSERT
                    stmt = insert(cadastro_table).values(valores)
                    # Executando a instrução de INSERT
                    self.session.execute(stmt)
                    # Confirmar a transação
                    self.session.commit()

                    # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                    msg_lancamento = st.empty()
                    msg_lancamento.success("Lançamento Realizado com Sucesso!")
                    time.sleep(5)
                    msg_lancamento.empty()
                    msg_lancamento.info('Não esqueça de limpar o código de barra.')
                    time.sleep(5)
                    msg_lancamento.empty()
                else:
                    msg_lancamento = st.empty()
                    msg_lancamento.error("Produto já cadastrado", icon="🚨")
                    time.sleep(5)
                    msg_lancamento.empty()
                
            except Exception as e:
                # Em caso de erro, desfazer a transação
                self.session.rollback()
                st.error(f"Ocorreu um erro: {e}")
            finally:
                # Fechando a sessão
                self.session.close()
                print('Fechado Conexão - salvar_cadastro')
    
    def editar_cadastro(self):
        df = self.df_cadastro_estoque.copy()
        
        # Verificar se a lista 'self.filtro.varPeriodo' está vazia
        if self.filtro.varProduto:
            filtro_produto = df['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(df)) # se a lista estiver vazia, considera todos os valores como verdadeiros 

        if self.filtro.varUnidade:
            filtro_unidade = df['unidade'].isin(self.filtro.varUnidade)
        else:
            filtro_unidade = pd.Series([True] * len(df))

        df = df[filtro_produto & filtro_unidade]

        col1, col2 = st.columns([0.75, 1.25])
        with col1:
            filtro_ID = st.multiselect(label='ID para edição', options=df['ID_produto'], placeholder='')
            if filtro_ID:
                df = df[df['ID_produto'].isin(filtro_ID)]
            filtro_produto = st.multiselect(label='Produto', options=df['produto'], placeholder='')
            if filtro_produto:
                df = df[df['produto'].isin(filtro_produto)]
            filtro_codigo_produto = st.multiselect(label='Código do Produto', options=df['codigo_produto'], placeholder='')
            if filtro_codigo_produto:
                df = df[df['codigo_produto'].isin(filtro_codigo_produto)]

        with col2:
            # Bloquear algumas colunas da edição
            colunas_bloqueadas = {
            'dt_atualizado': {'editable': False},
            'ID_produto': {'editable': False},
            'produto': {'editable': False},
            'codigo_produto': {'editable': False},
            }
            df['dt_atualizado'] = pd.to_datetime(df['dt_atualizado']).dt.strftime('%d/%m/%Y %H:%M:%S')
            colunas_formatada = {
                    'ID_produto': st.column_config.NumberColumn('ID Produto', format='%d'),
                    'produto': st.column_config.TextColumn('Produto'),
                    'codigo_produto': st.column_config.NumberColumn('Código Produto', format='%d'),
                    'qtd_min': st.column_config.NumberColumn('Qtde Min', format='%d'),
                    'qtd_max': st.column_config.NumberColumn('Qtde Max', format='%d'),
                    'unidade': st.column_config.SelectboxColumn('Unidade', options=self.lista_unidade, required=True), 
                    'dt_atualizado:':st.column_config.DatetimeColumn('Atualizado em:', format='DD/MM/YYYY h:mm a')}
            
            # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
            # disabled = deixa as colunas ineditavel
            tabela_editavel = st.data_editor(df, 
                                                disabled=colunas_bloqueadas, 
                                                column_config=colunas_formatada,
                                                use_container_width=True,
                                                hide_index=True)

            def update_cadastro(df):
                # atualização acontece apenas nas colunas disponivel
                self.conecta_mysql2()
                cursor = self.conn.cursor()
                data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Obter as colunas disponíveis
                colunas_disponiveis = df.columns.tolist()

                for index, row in df.iterrows():
                    query = "UPDATE cadastro_estoque SET "
                    valores = []
                    for coluna in colunas_disponiveis:
                        # Verificar se a coluna está presente no índice da linha atual
                        if coluna in row.index:
                            valor = row[coluna]
                            # Se o valor for uma string, adicione aspas simples ao redor dele
                            if isinstance(valor, str):
                                valor = f"'{valor}'"
                            # Se a coluna for uma coluna de data ou hora, formate-a corretamente
                            if 'data' in coluna or 'dt_atualizado' in coluna:
                                valor = f"STR_TO_DATE('{valor}', '%Y-%m-%d %H:%i:%s')"
                            valores.append(f"{coluna} = {valor}")
                    # Adicionar a data_atual à lista de valores
                    valores.append(f"dt_atualizado = STR_TO_DATE('{data_atual}', '%Y-%m-%d %H:%i:%s')")
                    # Construir a parte SET da query
                    query += ', '.join(valores)
                    # Adicionar a condição WHERE ID = {row['ID']}
                    query += f" WHERE ID_produto = {row['ID_produto']}"
                    try:
                        cursor.execute(query)
                        self.conn.commit()
                    except Exception as e:
                        print(f"Erro ao executar a query: {query}")
                        print(f"Erro detalhado: {e}")
                        self.conn.rollback() # Desfazer a transação em caso de erro

                cursor.close()
                self.conn.close()
                print('Fechado conexão - editar_cadastro')

            with col1:
                if st.button('Editar', use_container_width=True):
                    if len(filtro_ID) > 0 or len(filtro_produto) > 0 or len(filtro_codigo_produto) > 0:
                        update_cadastro(tabela_editavel)
                        with col1:
                            # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                            msg_lancamento = st.empty()
                            msg_lancamento.success("Edição realizada com Sucesso!")
                            time.sleep(10)
                            msg_lancamento.empty() 
                    else:
                        with col1:
                            msg_lancamento = st.empty()
                            msg_lancamento.warning('Selecione uma data ou ID que deseja editar!', icon="🚨")
                            time.sleep(10)
                            msg_lancamento.empty()