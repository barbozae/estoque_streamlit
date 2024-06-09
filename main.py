import streamlit as st

st.set_page_config(
    page_title="Controle de Estoque",
    page_icon="📦",
    layout='wide',
    initial_sidebar_state='expanded',
    menu_items={
        'Report a Bug': "mailto:edsonbarboza2006@hotmail.com",
        'About': 'Aplicativo desenvolvido por Edson Barboza com objetivo de realizar a Gestão e Controle de estoque. Entre em contato (11-9696-51094) e deixe-me saber como esta sendo sua experiência com o aplicativo.'
    })

from home import Home
from cadastro import Cadastro
from movimentacao import Movimentacao
from conexao import Conexao
from compras import Compras


class Aplication(Home, Cadastro, Movimentacao, Conexao, Compras):
    def __init__(self):
        self.home()
        
    

if __name__ == "__main__":
    Aplication()