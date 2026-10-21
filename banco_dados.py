import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3

# Configuração da página
st.set_page_config(
    page_title="Stúdio de Pilates e Fisioterapia Ítalo e Letícia Sampaio",
    page_icon="🧘‍♀️",
    layout="wide"
)

# ==============================================================================
# CONFIGURAÇÃO DO BANCO DE DADOS (SQLite)
# ==============================================================================
def conectar_bd():
    conn = sqlite3.connect("clientes_studio.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            idade INTEGER,
            endereco TEXT,
            telefone TEXT,
            objetivo TEXT,
            plano TEXT
        )
    ''')
    conn.commit()
    return conn

conn = conectar_bd()

def adicionar_cliente(nome, idade, endereco, telefone, objetivo, plano):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clientes (nome, idade, endereco, telefone, objetivo, plano)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (nome, idade, endereco, telefone, objetivo, plano))
    conn.commit()

def carregar_clientes():
    return pd.read_sql_query("SELECT * FROM clientes", conn)

# Título personalizado
st.title("🧘‍♀️ Stúdio de Pilates e Fisioterapia Ítalo e Letícia Sampaio")
st.subheader("Painel de Planejamento Financeiro & Gestão de Pacientes")

# Criação das Abas
aba_financeiro, aba_clientes = st.tabs(["📊 Painel Financeiro", "👥 Cadastro de Clientes"])

# ==============================================================================
# ABA 1: PAINEL FINANCEIRO
# ==============================================================================
with aba_financeiro:
    st.markdown("Ajuste os parâmetros na barra lateral para simular faturamento, custos com professores e margens de lucro.")

    # 1. BARRA LATERAL - INPUT DE DADOS
    st.sidebar.header("⚙️ Parâmetros do Estúdio")

    st.sidebar.subheader("1. Estrutura e Capacidade")
    vagas_por_turma = st.sidebar.number_input("Alunos/Vagas por Turma", min_value=1, max_value=10, value=4)
    horas_por_dia = st.sidebar.number_input("Horas de Aula por Dia", min_value=1, max_value=18, value=10)
    dias_por_semana = st.sidebar.number_input("Dias de Funcionamento/Semana", min_value=1, max_value=7, value=5)

    st.sidebar.subheader("2. Custos e Comissão de Professores")
    comissao_prof_hora = st.sidebar.number_input("Comissão do Professor (R$/hora)", min_value=0.0, value=45.0, step=5.0)
    custos_fixos = st.sidebar.number_input("Custos Fixos Mensais (R$)", min_value=0.0, value=8000.0, step=500.0)
    imposto_pct = st.sidebar.slider("Imposto / Simples Nacional (%)", min_value=0.0, max_value=20.0, value=6.0) / 100

    st.sidebar.subheader("3. Preços dos Planos (Mensalidade)")
    preco_1x = st.sidebar.number_input("Plano 1x por semana (R$)", value=250.0, step=10.0)
    preco_2x = st.sidebar.number_input("Plano 2x por semana (R$)", value=380.0, step=10.0)
    preco_3x = st.sidebar.number_input("Plano 3x por semana (R$)", value=480.0, step=10.0)
    preco_ilimitado = st.sidebar.number_input("Plano Ilimitado (R$)", value=650.0, step=10.0)

    # CÁLCULOS BASE
    aulas_semanais = horas_por_dia * dias_por_semana
    aulas_mensais = aulas_semanais * 4.33
    capacidade_slots_semanais = aulas_semanais * vagas_por_turma
    custo_professores_mes = aulas_mensais * comissao_prof_hora

    cenarios = [
        {"Nome": "1. Baixa Ocupação (~30%)", "Alunos_1x": int(capacidade_slots_semanais * 0.1), "Alunos_2x": int(capacidade_slots_semanais * 0.15), "Alunos_3x": int(capacidade_slots_semanais * 0.05)},
        {"Nome": "2. Ponto de Equilíbrio (~55%)", "Alunos_1x": int(capacidade_slots_semanais * 0.15), "Alunos_2x": int(capacidade_slots_semanais * 0.25), "Alunos_3x": int(capacidade_slots_semanais * 0.15)},
        {"Nome": "3. Alta Ocupação (~85%)", "Alunos_1x": int(capacidade_slots_semanais * 0.2), "Alunos_2x": int(capacidade_slots_semanais * 0.4), "Alunos_3x": int(capacidade_slots_semanais * 0.25)},
        {"Nome": "4. Capacidade Máxima (100%)", "Alunos_1x": int(capacidade_slots_semanais * 0.2), "Alunos_2x": int(capacidade_slots_semanais * 0.5), "Alunos_3x": int(capacidade_slots_semanais * 0.3)}
    ]

    dados_resultados = []
    for c in cenarios:
        total_alunos = c["Alunos_1x"] + c["Alunos_2x"] + c["Alunos_3x"]
        slots_ocupados = (c["Alunos_1x"] * 1) + (c["Alunos_2x"] * 2) + (c["Alunos_3x"] * 3)
        taxa_ocupacao = (slots_ocupados / capacidade_slots_semanais) * 100 if capacidade_slots_semanais > 0 else 0
        fat_bruto = (c["Alunos_1x"] * preco_1x) + (c["Alunos_2x"] * preco_2x) + (c["Alunos_3x"] * preco_3x)
        impostos = fat_bruto * imposto_pct
        custo_total = custos_fixos + impostos + custo_professores_mes
        lucro_liquido = fat_bruto - custo_total
        
        dados_resultados.append({
            "Cenário": c["Nome"],
            "Total Alunos": total_alunos,
            "Ocupação (%)": round(taxa_ocupacao, 1),
            "Faturamento Bruto": fat_bruto,
            "Impostos": impostos,
            "Custo Fixos": custos_fixos,
            "Comissão Professores": custo_professores_mes,
            "Custo Total": custo_total,
            "Lucro Líquido": lucro_liquido,
            "Margem Líquida (%)": round((lucro_liquido / fat_bruto * 100) if fat_bruto > 0 else 0, 1)
        })

    df = pd.DataFrame(dados_resultados)

    # CARDS DE MÉTRICAS
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Capacidade Máxima", f"{capacidade_slots_semanais} vagas/sem")
    m2.metric("Custo Professores", f"R$ {custo_professores_mes:,.2f}")
    m3.metric("Faturamento Máximo", f"R$ {df.iloc[-1]['Faturamento Bruto']:,.2f}")
    m4.metric("Lucro Líquido Máximo", f"R$ {df.iloc[-1]['Lucro Líquido']:,.2f}", delta=f"{df.iloc[-1]['Margem Líquida (%)']}% Margem")

    st.divider()

    # GRÁFICOS
    col_graf1, col_graf2 = st.columns(2)
    with col_graf1:
        st.subheader("📊 Faturamento Bruto vs. Lucro Líquido")
        fig_bar = px.bar(df, x="Cenário", y=["Faturamento Bruto", "Lucro Líquido"], barmode="group",
                         color_discrete_map={"Faturamento Bruto": "#2b5c8f", "Lucro Líquido": "#2ca02c"})
        st.plotly_chart(fig_bar, width='stretch')

    with col_graf2:
        st.subheader("🍩 Composição de Custos (Capacidade Máxima)")
        cenario_max = df.iloc[-1]
        fig_pie = px.pie(names=['Custos Fixos', 'Comissão Professores', 'Impostos', 'Lucro Líquido'],
                         values=[cenario_max['Custo Fixos'], cenario_max['Comissão Professores'], cenario_max['Impostos'], max(0, cenario_max['Lucro Líquido'])],
                         hole=0.4, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig_pie, width='stretch')

# ==============================================================================
# ABA 2: CADASTRO E BANCO DE DADOS DE CLIENTES
# ==============================================================================
with aba_clientes:
    st.header("📋 Cadastro de Clientes e Pacientes")
    
    col_form, col_lista = st.columns([1, 2])
    
    with col_form:
        st.subheader("➕ Novo Cadastro")
        with st.form("form_cliente", clear_on_submit=True):
            nome = st.text_input("Nome Completo*")
            idade = st.number_input("Idade", min_value=1, max_value=120, value=30)
            endereco = st.text_input("Endereço")
            telefone = st.text_input("Telefone / WhatsApp")
            objetivo = st.text_area("Objetivo Clínico / Diagnóstico (Fisioterapia/Pilates)", placeholder="Ex: Reabilitação lombar, ganho de flexibilidade, tratamento de hérnia de disco...")
            plano = st.selectbox("Plano Contratado", ["Plano 1x por semana", "Plano 2x por semana", "Plano 3x por semana", "Plano Ilimitado"])
            
            btn_salvar = st.form_submit_button("💾 Salvar Cliente")
            
            if btn_salvar:
                if nome.strip() != "":
                    adicionar_cliente(nome, idade, endereco, telefone, objetivo, plano)
                    st.success(f"Cliente **{nome}** cadastrado(a) com sucesso!")
                else:
                    st.warning("Por favor, preencha o nome do cliente.")

    with col_lista:
        st.subheader("👥 Clientes Cadastrados")
        df_clientes = carregar_clientes()
        
        if not df_clientes.empty:
            # Filtro por busca
            busca = st.text_input("🔍 Buscar cliente por nome:", "")
            if busca:
                df_clientes = df_clientes[df_clientes['nome'].str.contains(busca, case=False, na=False)]
            
            st.dataframe(df_clientes, hide_index=True, width='stretch')
            
            # Resumo rápido por plano
            st.markdown("### 📊 Distribuição de Alunos por Plano")
            resumo_planos = df_clientes['plano'].value_counts().reset_index()
            resumo_planos.columns = ['Plano', 'Quantidade de Alunos']
            st.dataframe(resumo_planos, hide_index=True)
        else:
            st.info("Nenhum cliente cadastrado até o momento.")