import streamlit as st
from cadastro import Cadastro
from compras import Compras
from movimentacao import Movimentacao


class Home:
    def home(self):
        st.header('Controle de Estoque')
        tab1, tab2, tab3, tab4 = st.tabs(['Cadastro', 'Compras', 'Movimentações', 'Resumo'])
        with tab1:
            col1, col2 = st.columns([1, 2])
            with col1:
                Cadastro.widget_cadastro(self)
            with col2:
                Cadastro.atualizar(self)
                df = self.df_cadastro_estoque.copy()
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
            col1, col2 = st.columns([0.75, 1.25])
            with col1:
                Movimentacao.widget_movimentacao(self)
            with col2:
                Movimentacao.dataframe_movimentacao(self)
        with tab4:
            Movimentacao.produtos_no_estoque(self)
            st.write('---')
            Movimentacao.custo_estoque(self)