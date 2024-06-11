import streamlit as st
import pandas as pd
from cadastro import Cadastro
from compras import Compras
from movimentacao import Movimentacao
from filtro import Filtros


class Home:
    def __init__(self):
        self.filtro = Filtros()

    def varProduto(self):
        Cadastro.atualizar(self)
        self.filtro.varProduto = st.multiselect(           
        'Selecione o Produto', 
        self.df_cadastro_estoque['produto'],
        placeholder=''
        )

    def varUnidade(self):
        lista_unidade = ['Peça', 'Kilograma', 'Grama', 'Comprimento', 'Volume', 'Litros', 'Lata']
        self.filtro.varUnidade = st.multiselect(
            'Selecione a Unidade',
            lista_unidade,
            placeholder=''
        )

    def sidebar(self):
        with st.sidebar:
            self.varProduto()
            self.varUnidade()
            # st.write('---')
            # status_estoque = st.radio('Escolha uma opção do Farol',
            #                           ['🔴', '🔵', '🟣'],
            #                           captions=['***Estoque baixo***', '***Estoque bom***', '***Estoque alto***'])

    def home(self):
        st.header('Controle de Estoque')
        tab1, tab2, tab3, tab4 = st.tabs(['Cadastro', 'Compras', 'Movimentações', 'Resumo'])
        with tab1:
            self.sidebar()
            col1, col2 = st.columns([1, 2])
            with col1:
                Cadastro.widget_cadastro(self)
            with col2:
                Cadastro.atualizar(self)
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
                df['dt_atualizado'] = pd.to_datetime(df['dt_atualizado']).dt.strftime('%d/%m/%Y %H:%M:%S')
                df['codigo_produto'] = df['codigo_produto'].astype(str)
                df = df.rename(columns={
                                        'ID_produto': 'ID Produto',
                                        'produto': 'Produto',
                                        'codigo_produto': 'Código Produto',
                                        'qtd_min': 'Qtde Min',
                                        'qtd_max': 'Qtde Max',
                                        'unidade': 'Unidade',
                                        'dt_atualizado': 'Atualizado em:'
                                    })
                st.dataframe(df, hide_index=True)
            
            with st.expander(label='Edição de Cadastro'):
                Cadastro.editar_cadastro(self)

        with tab2:
            col1, col2 = st.columns([1, 2])
            with col1:
                Compras.widget_compras(self)
            with col2:
                Compras.editar_compra_estoque(self)
        with tab3:
            col1, col2 = st.columns([0.6, 1.4])
            with col1:
                Movimentacao.widget_movimentacao(self)
            with col2:
                Movimentacao.dataframe_movimentacao(self)
        with tab4:
            col1, col2, col3 = st.columns(3)
            with col1:
                Movimentacao.produtos_no_estoque(self)
            # st.write('---')
            with col2:
                Movimentacao.custo_estoque(self)
            with col3:
                pass