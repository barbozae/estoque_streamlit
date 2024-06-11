import streamlit as st
import time
from datetime import datetime
from sqlalchemy import text
import pandas as pd
from filtro import Filtros
from compras import Compras


class Movimentacao:
    def __init__(self) -> None:
        self.filtro = Filtros() 

    def widget_movimentacao(self):
        
        with st.form(key='widget_movimentacao', clear_on_submit=True):
            self.nome_produto = st.selectbox(label='Nome do Produto', options=self.df_cadastro['produto'], placeholder='', index=None)
            self.qtd_movimentacao = st.number_input(label='Quantidade', value=float('0.00'), step=1.00,
                                                min_value=-1000.00, max_value=1000.00)
            self.codigo_produto = st.text_input(label='Código do Produto')
            submit_button = st.form_submit_button(label='Salvar')
        self.ajuste_movimentacao = st.toggle(label='Ajuste Movimentação', help='Ative para ajustar valores inconsistentes')

        if submit_button:
            self.salvar_movimentacao()

        if self.ajuste_movimentacao:
            st.write('**_:red[Atenção]_ :red[ajuste ativado]**')

    def salvar_movimentacao(self):
        dt_atualizado = datetime.now().strftime("%Y/%m/%d, %H:%M:%S")
        if self.qtd_movimentacao == 0:
            msg_lancamento = st.empty()
            msg_lancamento.error("Quantidade **:orange[não]** pode ser igual a zero", icon="🚨")
            time.sleep(10)
            msg_lancamento.empty()

        # if self.nome_produto and self.qtd_movimentacao != 0:
        if (self.nome_produto and self.qtd_movimentacao):
            self.conecta_mysql()
            query = text("SELECT c.ID_produto FROM cadastro_estoque c WHERE c.produto = :produto")
            result = self.session.execute(query, {'produto': self.nome_produto})
            ID_produto = result.scalar()

            if ID_produto:
                comando = text("""
                    INSERT INTO movimentacao_estoque (movimentacao, correcao, ID_produto, dt_atualizado) 
                    VALUES (:movimentacao, :correcao, :ID_produto, :dt_atualizado)
                """)

                valores = {
                    'movimentacao': self.qtd_movimentacao,
                    'correcao': self.ajuste_movimentacao,
                    'ID_produto': ID_produto,
                    'dt_atualizado': dt_atualizado
                }

                self.session.execute(comando, valores)
                self.session.commit()
                self.session.close()
                print('Fechado conexão - salvar_cadastro')

                msg_lancamento = st.empty()
                msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
                time.sleep(10)
                msg_lancamento.empty()
            else:
                st.error("Produto não encontrado no cadastro.")

        elif self.codigo_produto:
            try:
                self.conecta_mysql()
                # Verificação se o produto existe no cadastro_estoque
                query = text("SELECT c.ID_produto FROM cadastro_estoque c WHERE c.codigo_produto = :codigo_produto")
                result = self.session.execute(query, {'codigo_produto': self.codigo_produto})
                ID_produto = result.scalar()

                if not ID_produto:
                    msg_lancamento = st.empty()
                    msg_lancamento.error("Código do produto inválido", icon="🚨")
                    time.sleep(10)
                    msg_lancamento.empty()
                else:
                    comando = text("""
                                    INSERT INTO movimentacao_estoque (movimentacao, correcao, ID_produto, dt_atualizado) 
                                    VALUES (:movimentacao, :correcao, :ID_produto, :dt_atualizado)
                                """)

                    valores = {
                        'movimentacao': self.qtd_movimentacao,
                        'correcao': self.ajuste_movimentacao,
                        'ID_produto': ID_produto,
                        'dt_atualizado': dt_atualizado
                    }

                    self.session.execute(comando, valores)
                    self.session.commit()

                    msg_lancamento = st.empty()
                    msg_lancamento.success("Lançamento Realizado com Sucesso!", icon='✅')
                    time.sleep(10)
                    msg_lancamento.empty()
                
            except Exception as e:
                # Em caso de erro, desfazer a transação
                self.session.rollback()
                st.error(f"Ocorreu um erro: {e}")

            finally:
                # Fechando a sessão
                self.session.close()
                print('Fechado Conexão - salvar_cadastro')

        else:
            msg_lancamento = st.empty()
            msg_lancamento.error("Escolha um produto válido", icon='🚨')
            time.sleep(10)
            msg_lancamento.empty()

    def dataframe_movimentacao(self):
        tabela = Compras.atualizar()
        df_movimentacao = tabela[2]
        
        # Substituindo valores 0 e 1 para não e sim
        df_movimentacao['correcao'] = df_movimentacao['correcao'].replace({0: 'Não', 1: 'Sim'})

        # mesclando cadastro_estoque com movimentacao_estoque para pegar os nomes dos produtos
        self.df_movimentacao = pd.merge(self.df_cadastro, df_movimentacao, left_on='ID_produto', right_on='ID_produto', how='right')        

        # Verificar se a lista 'self.filtro.varPeriodo' está vazia
        if self.filtro.varProduto:
            filtro_produto = self.df_movimentacao['produto'].isin(self.filtro.varProduto)
        else:
            filtro_produto = pd.Series([True] * len(self.df_movimentacao)) # se a lista estiver vazia, considera todos os valores como verdadeiros 
        if self.filtro.varUnidade:
            filtro_unidade = self.df_movimentacao['unidade'].isin(self.filtro.varUnidade)
        else:
            filtro_unidade = pd.Series([True] * len(self.df_movimentacao))

        self.df_movimentacao = self.df_movimentacao[filtro_produto & filtro_unidade]

        self.df_movimentacao['dt_atualizado_y'] = pd.to_datetime(self.df_movimentacao['dt_atualizado_y']).dt.strftime('%d/%m/%Y %H:%M:%S')
        self.df_movimentacao['codigo_produto'] = self.df_movimentacao['codigo_produto'].astype(str)

        df = self.df_movimentacao.rename(columns={
            'ID_movimentacao': 'ID Movimentação',
            'movimentacao': 'Movimentação',
            'correcao': 'Correção',
            'produto': 'Produto',
            'codigo_produto': 'Código Produto',
            'qtd_min': 'Qtde Min',
            'qtd_max': 'Qtde Max',
            'unidade': 'Unidade',
            'dt_atualizado_y': 'Atualizado em:'
        })

        # Nova ordem das colunas
        ordem_colunas = ['ID Movimentação', 'Produto', 'Código Produto', 'Movimentação', 'Correção', 'Unidade','Atualizado em:']

        df = df.reindex(columns=ordem_colunas)
        st.dataframe(df.style.apply(
                                lambda x: ["background-color: green" if val == "Sim" else "" for val in x],
                                subset=["Correção"]
                                    ),
                                    hide_index=True, use_container_width=True)

    def produtos_no_estoque(self):
        tabela = Compras.atualizar()
        self.df_compra_estoque = tabela[1]

        # Agrupando as movimentações por produto e unidades
        total_movimentacao = self.df_movimentacao.groupby(['produto', 'unidade'])['movimentacao'].sum().reset_index()

        # Agrupando as compras por produto
        total_compras = self.df_compra_estoque.groupby('produto')['qtd'].sum().reset_index()
        
        # Mesclar com df_cadastro para adicionar qtd_min correspondente ao Produto
        total_movimentacao = pd.merge(total_movimentacao, self.df_cadastro, on='produto')
        # Mesclar com total_compras para adicionar qtd comprada correspondente ao Produto
        total_movimentacao = pd.merge(total_movimentacao, total_compras, on='produto')

        # Subtraindo quantidade comprada com quantidade retirada do estoque para ter o valor de estoque
        total_movimentacao['Qtde Estoque'] = total_movimentacao['qtd'].add(total_movimentacao['movimentacao'])
                                                            
        def status(row):
            qtd_min = row['qtd_min']
            qtd_max = row['qtd_max']

            if row['Qtde Estoque']  <= qtd_min:
                status = '🔴'
            elif row['Qtde Estoque'] <= qtd_max:
                status = '🔵'
            else:
                status = '🟣'
            return status
        
        total_movimentacao['Status'] = total_movimentacao.apply(status, axis=1)
        
        self.df_status_estoque = total_movimentacao.drop(['ID_produto', 'codigo_produto', 'unidade_y', 'movimentacao', 'qtd_min', 
                                                      'qtd', 'qtd_max', 'dt_atualizado'], axis=1)

        df = self.df_status_estoque.rename(columns={
                                                'produto': 'Produto',
                                                'unidade_x': 'Unidade',
                                                'movimentacao': 'Movimentação'
                                                })
        st.caption('Quantidade de produtos em estoque')
        st.dataframe(df,
                     column_config={
                    'Status': st.column_config.Column(
                    help='🔴 Estoque baixo 🔵 Estoque bom 🟣 Estoque alto',
                    width='small',
                    required=True)
                    },
                    hide_index=True)

    def custo_estoque(self):
        df = self.df_compra_estoque.groupby(['produto', 'preco'])['ID_compra'].max().reset_index()
        # manter o agrupamento dos maiores índice
        idx = df.groupby('produto')['preco'].idxmax()
        
        # Selecionar as linhas correspondentes desses índices
        df_estoque = df.loc[idx].reset_index(drop=True)

        df_estoque = pd.merge(df_estoque, self.df_status_estoque, on='produto').drop(['ID_compra', 'unidade_x', 'Status'], axis=1)
        df_estoque['Custo Estocado'] = df_estoque['Qtde Estoque'].where(df_estoque['Qtde Estoque'] > 0, 0) * df_estoque['preco']

        # Calcular a soma de cada coluna
        # linha_total = df_estoque.sum(numeric_only=True)
        # Adicionar a linha de total ao DataFrame
        # df_estoque.loc['Total'] = pd.Series(linha_total)
        # Alterar o valor da coluna 'team' na linha do total
        # df_estoque.loc['Total', 'produto'] = 'Total'

        custo_estoque_parado = df_estoque['Custo Estocado'].sum()
        st.caption('Custo total em estoque')
        df = df_estoque.rename(columns={'produto': 'Produto'}).drop(['preco'], axis=1)
        st.dataframe(df,
                    column_config={
                    'Custo Estocado': st.column_config.ProgressColumn(
                                                                    'Custo Total',
                                                                    help='Total estocado',
                                                                    format='$%d',
                                                                    min_value=0,
                                                                    max_value=10000,)
                                                                    },
                                                                    hide_index=True
                                                                    )
        
        st.write(f'Custo acumulado do estoque é de **R$ {custo_estoque_parado}**')
        # usuario = os.getenv('USER_EMAIL')
        # st.write(usuario)

        # Get the user's email
        # user_email = st.experimental_user.email

        # # Display the user's email
        # st.write(f"Welcome, {user_email}!")