import streamlit as st
import time
import pandas as pd
from datetime import datetime
from sqlalchemy import text
from conexao import Conexao


class Compras:
    def atualizar():
        consulta = Conexao.conecta_bd()
        df_cadastro_estoque = consulta[12]
        df_compra_estoque = consulta[13]
        df_movimentacao_estoque = consulta[14]
        return df_cadastro_estoque, df_compra_estoque, df_movimentacao_estoque

    def widget_compras(self):
        df_cadastro = Compras.atualizar()
        self.df_cadastro = df_cadastro[0]

        with st.form(key='widget_compras', clear_on_submit=True):
            self.produto = st.selectbox(label='Nome do Produto',
                                        options=self.df_cadastro['produto'],
                                        index=None,
                                        placeholder='Selecione o Produto')
            self.qtd_comprada = st.number_input(label='Quantidade Comprada',
                                                value=float('0.00'),
                                                step=1.00,
                                                min_value=0.00,
                                                max_value=1000.00)
            self.preco = st.number_input(label='Preço',
                                            value=float('0.00'),
                                            step=1.00,
                                            min_value=0.00,
                                            max_value=1000.00)
            self.codigo_produto = st.text_input(label='Código do Produto', placeholder='Informe o código do produto')

            button_salvar_compra = st.form_submit_button(label='Salvar')

            if button_salvar_compra:
                self.salvar_compra()

    def salvar_compra(self):
        if not (self.produto or self.codigo_produto):
            st.error("Produto ou código de barra é obrigatório!", icon="🚨")
        elif self.qtd_comprada == 0:
            st.error('Informe a qtde da compra', icon='🚨')
        elif self.preco == 0:
            st.error('Informe preço unitário', icon='🚨')
        else:
            dt_atualizado = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
            if self.produto:
                self.conecta_mysql()
                # Construir a consulta SQL usando text()
                comando = text("""
                    INSERT INTO compra_estoque (produto, qtd, preco, ID_produto, dt_atualizado) 
                    VALUES (
                        :produto,
                        :qtd, 
                        :preco, 
                        (SELECT c.ID_produto FROM cadastro_estoque c WHERE c.produto = :produto),
                        :dt_atualizado
                            )
                    """)

                query = text(f"SELECT c.ID_produto FROM cadastro_estoque c WHERE c.produto = :produto")
                result = self.session.execute(query, {'produto': self.produto})
                ID_produto = result.scalar()

                valores = {
                    'produto': self.produto,
                    'qtd': self.qtd_comprada,
                    'preco': self.preco,
                    'ID_produto': ID_produto,
                    'dt_atualizado': dt_atualizado
                }

                # Execute a instrução SQL usando os valores e placeholders seguros
                self.session.execute(comando, valores)
                # Confirmar a transação
                self.session.commit()
                # Fechando a sessão
                self.session.close()
                print('Fechado conexão - salvar_cadastro')

                # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                msg_lancamento = st.empty()
                msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
                time.sleep(10)
                msg_lancamento.empty()

            elif self.codigo_produto:
                try:
                    self.conecta_mysql()
                    # Verificação se o código de barra existe no cadastro_estoque
                    query = text(f"SELECT c.produto, ID_produto FROM cadastro_estoque c WHERE c.codigo_produto = :codigo_produto")
                    # o metodo .fetchone() pega o primeiro valor valido caso fosse necessario pegar todos valores válidos usaria .fetchall()
                    result = self.session.execute(query, {'codigo_produto': self.codigo_produto}).fetchone()

                    if not result:
                        msg_lancamento = st.empty()
                        msg_lancamento.error("Código do produto inválido", icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()
                    else:
                        nome_produto, ID_produto = result
                        comando = text("""
                            INSERT INTO compra_estoque (produto, qtd, preco, ID_produto, dt_atualizado) 
                            VALUES (:produto, :qtd, :preco, :ID_produto, :dt_atualizado)
                            """)
                        valores = {
                            'produto': nome_produto,
                            'qtd': self.qtd_comprada,
                            'preco': self.preco,
                            'ID_produto': ID_produto,
                            'dt_atualizado': dt_atualizado
                        }
                        # Execute a instrução SQL usando os valores e placeholders seguros
                        self.session.execute(comando, valores)
                        # Confirmar a transação
                        self.session.commit()

                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
                        time.sleep(10)
                        msg_lancamento.empty()

                except Exception as e:
                    # Em caso de erro, desfazer a transação
                    self.session.rollback()
                    st.error(f'Ocorreu um erro: {e}')
                finally:
                        # Fechando a sessão
                        self.session.close()
                        print('Fechado conexão - salvar_cadastro')
            else:
                msg_lancamento = st.empty()
                msg_lancamento.error("Escolha um produto válido", icon='🚨')
                time.sleep(10)
                msg_lancamento.empty()
    
    def editar_compra_estoque(self):
        tabela = Compras.atualizar()
        df = tabela[1]

        # Verificar se a lista 'self.filtro.varPeriodo' está vazia
        if self.filtro.varProduto:
            filtro_produto = df['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(df)) # se a lista estiver vazia, considera todos os valores como verdadeiros 

        df = df[filtro_produto]

        df = df.drop(['ID_produto'], axis=1)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            filtro_ID = st.multiselect('ID para edição', df['ID_compra'], placeholder='', key='ID_compras')
            if filtro_ID:
                df = df[df['ID_compra'].isin(filtro_ID)]
        with col2:
            filtro_produto = st.multiselect('Produto', df['produto'], placeholder='', key='Produto_compra')
            if filtro_produto:
                df = df[df['produto'].isin(filtro_produto)]

        # Bloquear algumas colunas da edição
        colunas_bloqueadas = {
        'ID_compra': {'editable': False},
        'produto': {'editable': False},
        'dt_atualizado:': {'editable': False},
        }

        df['dt_atualizado'] = pd.to_datetime(df['dt_atualizado']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        colunas_formatada = {
                'ID_compra': st.column_config.NumberColumn('ID Compra', format='%d'),
                'produto': st.column_config.TextColumn('Produto'),
                'qtd': st.column_config.NumberColumn('Qtde ', format='%f'),
                'preco': st.column_config.NumberColumn('Preço', format='$ %.2f'),
                'unidade': st.column_config.SelectboxColumn('Unidade', options=self.lista_unidade, required=True), 
                'dt_atualizado:':st.column_config.DatetimeColumn('Atualizado em:', format='DD/MM/YYYY- h:mm A')}
        
        # num_rows = 'dynamic' é um parametro para habilitar a inclusão de linhas
        tabela_editavel = st.data_editor(df, 
                                            disabled=colunas_bloqueadas, 
                                            column_config=colunas_formatada, 
                                            hide_index=True)

        def update_cadastro(df):
            # atualização acontece apenas nas colunas disponivel
            self.conecta_mysql2()
            cursor = self.conn.cursor()
            data_atual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Obter as colunas disponíveis
            colunas_disponiveis = df.columns.tolist()

            for index, row in df.iterrows():
                query = "UPDATE compra_estoque SET "
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
                query += f" WHERE ID_compra = {row['ID_compra']}"
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

        with col3:
            if st.button('Editar', use_container_width=True, key='Botão edição compra'):
                if len(filtro_ID) > 0 or len(filtro_produto) > 0:
                    update_cadastro(tabela_editavel)
                    with col4:
                        # precisei criar uma mensagem vazia para depois deixa-la vazia novamente depois de utiliza-la
                        msg_lancamento = st.empty()
                        msg_lancamento.success("Edição realizada com Sucesso!")
                        time.sleep(10)
                        msg_lancamento.empty() 
                else:
                    with col4:
                        msg_lancamento = st.empty()
                        msg_lancamento.warning('Selecione o ID que deseja editar!', icon="🚨")
                        time.sleep(10)
                        msg_lancamento.empty()