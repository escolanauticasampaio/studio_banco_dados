import streamlit as st
import pandas as pd
import plotly.express as px
import sqlite3
from datetime import datetime, time, timedelta, date

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
    conn = sqlite3.connect("clientes_studio_v2.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf TEXT UNIQUE NOT NULL,
            nome TEXT NOT NULL,
            email TEXT,
            data_nascimento TEXT,
            idade INTEGER,
            endereco TEXT,
            telefone TEXT,
            contato_emergencia TEXT,
            objetivo TEXT,
            plano TEXT,
            dias_semana TEXT,
            horarios TEXT
        )
    ''')
    
    cursor.execute("PRAGMA table_info(clientes)")
    colunas_existentes = [coluna[1] for coluna in cursor.fetchall()]
    for col, tipo in {"email": "TEXT", "data_nascimento": "TEXT", "contato_emergencia": "TEXT"}.items():
        if col not in colunas_existentes:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} {tipo}")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS profissionais (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome_prof TEXT NOT NULL,
            conselho TEXT NOT NULL,
            registro TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS prontuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cpf_cliente TEXT NOT NULL,
            data_atendimento TEXT NOT NULL,
            profissional TEXT NOT NULL,
            atividades TEXT NOT NULL,
            evolucao TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    return conn

conn = conectar_bd()

def adicionar_cliente(cpf, nome, email, data_nasc, idade, endereco, telefone, contato_emergencia, objetivo, plano, dias_semana, horarios):
    cursor = conn.cursor()
    dias_str = ", ".join(dias_semana)
    horarios_str = ", ".join(horarios)
    try:
        cursor.execute('''
            INSERT INTO clientes (cpf, nome, email, data_nascimento, idade, endereco, telefone, contato_emergencia, objetivo, plano, dias_semana, horarios)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cpf, nome, email, data_nasc, idade, endereco, telefone, contato_emergencia, objetivo, plano, dias_str, horarios_str))
        conn.commit()
        return True, "Cliente cadastrado com sucesso!"
    except sqlite3.IntegrityError:
        return False, "Erro: Já existe um cliente cadastrado com este CPF!"

def atualizar_cliente(cpf_antigo, nome, email, data_nasc, idade, endereco, telefone, contato_emergencia, objetivo, plano, dias_semana, horarios):
    cursor = conn.cursor()
    dias_str = ", ".join(dias_semana)
    horarios_str = ", ".join(horarios)
    cursor.execute('''
        UPDATE clientes 
        SET nome = ?, email = ?, data_nascimento = ?, idade = ?, endereco = ?, telefone = ?, contato_emergencia = ?, objetivo = ?, plano = ?, dias_semana = ?, horarios = ?
        WHERE cpf = ?
    ''', (nome, email, data_nasc, idade, endereco, telefone, contato_emergencia, objetivo, plano, dias_str, horarios_str, cpf_antigo))
    conn.commit()
    return True, "Cliente atualizado com sucesso!"

def deletar_cliente(cpf):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE cpf = ?", (cpf,))
    conn.commit()

def carregar_clientes():
    return pd.read_sql_query("SELECT * FROM clientes", conn)

def adicionar_profissional(nome, conselho, registro):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO profissionais (nome_prof, conselho, registro)
        VALUES (?, ?, ?)
    ''', (nome, conselho, registro))
    conn.commit()

def atualizar_profissional(prof_id, nome, conselho, registro):
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE profissionais 
        SET nome_prof = ?, conselho = ?, registro = ?
        WHERE id = ?
    ''', (nome, conselho, registro, prof_id))
    conn.commit()

def deletar_profissional(prof_id):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM profissionais WHERE id = ?", (prof_id,))
    conn.commit()

def carregar_profissionais():
    return pd.read_sql_query("SELECT * FROM profissionais", conn)

def adicionar_prontuario(cpf, data, profissional, atividades, evolucao):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO prontuarios (cpf_cliente, data_atendimento, profissional, atividades, evolucao)
        VALUES (?, ?, ?, ?, ?)
    ''', (cpf, data, profissional, atividades, evolucao))
    conn.commit()

def carregar_prontuarios(cpf=""):
    if cpf:
        return pd.read_sql_query("SELECT * FROM prontuarios WHERE cpf_cliente = ?", conn, params=(cpf,))
    return pd.read_sql_query("SELECT * FROM prontuarios", conn)

# Título personalizado
st.title("🧘‍♀️ Stúdio de Pilates e Fisioterapia Ítalo e Letícia Sampaio")
st.subheader("Painel de Gestão Integrada: Financeiro, Agenda Visual, Clientes e Prontuários")

# Criação das Abas
aba_financeiro, aba_clientes, aba_mapa, aba_profissionais, aba_prontuario = st.tabs([
    "📊 Painel Financeiro", 
    "👥 Agendamento & Clientes", 
    "🧩 Mapa de Ocupação",
    "👩‍⚕️ Profissionais", 
    "📝 Prontuário Eletrônico"
])

# ==============================================================================
# ABA 1: PAINEL FINANCEIRO
# ==============================================================================
with aba_financeiro:
    st.markdown("Ajuste os parâmetros na barra lateral para simular faturamento, custos com professores e margens de lucro.")

    st.sidebar.header("⚙️ Parâmetros do Estúdio")

    st.sidebar.subheader("1. Estrutura e Capacidade")
    vagas_por_turma = st.sidebar.number_input("Alunos/Vagas por Turma", min_value=1, max_value=10, value=2, key="vagas_sidebar")
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

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Capacidade Máxima", f"{capacidade_slots_semanais} vagas/sem")
    m2.metric("Custo Professores", f"R$ {custo_professores_mes:,.2f}")
    m3.metric("Faturamento Máximo", f"R$ {df.iloc[-1]['Faturamento Bruto']:,.2f}")
    m4.metric("Lucro Líquido Máximo", f"R$ {df.iloc[-1]['Lucro Líquido']:,.2f}", delta=f"{df.iloc[-1]['Margem Líquida (%)']}% Margem")

    st.divider()
    st.subheader("💰 Faturamento Real (Baseado nos Clientes Cadastrados)")
    df_cadastrados_fin = carregar_clientes()
    
    if not df_cadastrados_fin.empty:
        contagem_planos = df_cadastrados_fin['plano'].value_counts()
        q_1x = contagem_planos.get("Plano 1x por semana", 0)
        q_2x = contagem_planos.get("Plano 2x por semana", 0)
        q_3x = contagem_planos.get("Plano 3x por semana", 0)
        q_ilimitado = contagem_planos.get("Plano Ilimitado", 0)
        total_cadastrados = len(df_cadastrados_fin)
        
        faturamento_real = (q_1x * preco_1x) + (q_2x * preco_2x) + (q_3x * preco_3x) + (q_ilimitado * preco_ilimitado)
        impostos_reais = faturamento_real * imposto_pct
        lucro_real = faturamento_real - (custos_fixos + impostos_reais + custo_professores_mes)

        r1, r2, r3, r4 = st.columns(4)
        r1.metric("Total de Alunos", f"{total_cadastrados} alunos")
        r2.metric("Faturamento Bruto Real", f"R$ {faturamento_real:,.2f}")
        r3.metric("Impostos Reais", f"R$ {impostos_reais:,.2f}")
        r4.metric("Lucro Líquido Real", f"R$ {lucro_real:,.2f}")
    else:
        st.info("Nenhum cliente cadastrado no momento.")

# ==============================================================================
# ESTRUTURA GLOBAL DE HORÁRIOS
# ==============================================================================
horarios_base = []
inicio_manha = datetime.combine(datetime.today(), time(8, 0))
fim_manha = datetime.combine(datetime.today(), time(12, 0))
atual = inicio_manha
while atual + timedelta(minutes=45) <= fim_manha:
    horarios_base.append(atual.strftime("%H:%M"))
    atual += timedelta(minutes=60)
    
inicio_tarde = datetime.combine(datetime.today(), time(14, 0))
fim_tarde = datetime.combine(datetime.today(), time(21, 0))
atual = inicio_tarde
while atual + timedelta(minutes=45) <= fim_tarde:
    horarios_base.append(atual.strftime("%H:%M"))
    atual += timedelta(minutes=60)

dias_semana_lista = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira", "Sexta-feira", "Sábado"]

def calcular_ocupacao_matriz(df_clientes, limite_vagas):
    ocupacao = {}
    for d in dias_semana_lista:
        for h in horarios_base:
            ocupacao[(d, h)] = 0
            
    if not df_clientes.empty:
        for _, row in df_clientes.iterrows():
            if pd.notna(row.get('dias_semana')) and pd.notna(row.get('horarios')):
                dias_cli = [x.strip() for x in row['dias_semana'].split(",")]
                hors_cli = [x.strip() for x in row['horarios'].split(",")]
                for d in dias_cli:
                    for h in hors_cli:
                        if (d, h) in ocupacao:
                            ocupacao[(d, h)] += 1
    return ocupacao

# ==============================================================================
# ABA 2: CADASTRO, EDIÇÃO, EXCLUSÃO DE CLIENTES & AGENDA
# ==============================================================================
with aba_clientes:
    st.header("📋 Agendamento e Gestão de Clientes")
    
    # Sub-abas para alternar entre Novo Cadastro e Gestão (Editar/Excluir)
    sub_aba_novo, sub_aba_gerenciar = st.tabs(["➕ Novo Cadastro", "✏️ Editar / Excluir Clientes"])

    with sub_aba_novo:
        if "limpar_campos" not in st.session_state:
            st.session_state.limpar_campos = False

        if st.session_state.limpar_campos:
            st.session_state.input_cpf = ""
            st.session_state.input_nome = ""
            st.session_state.input_email = ""
            st.session_state.input_nasc_texto = ""
            st.session_state.input_end = ""
            st.session_state.input_tel = ""
            st.session_state.input_emergencia = ""
            st.session_state.input_obj = ""
            st.session_state.input_dias = []
            st.session_state.limpar_campos = False

        df_atual_clientes = carregar_clientes()
        vagas_limite = vagas_por_turma
        ocupacao_matriz = calcular_ocupacao_matriz(df_atual_clientes, vagas_limite)

        col_form, col_lista = st.columns([1, 2])
        
        with col_form:
            st.subheader("Novo Cadastro & Agendamento")
            
            cpf = st.text_input("CPF (ID do Paciente)*", placeholder="000.000.000-00", key="input_cpf")
            nome = st.text_input("Nome Completo*", key="input_nome")
            email = st.text_input("E-mail", placeholder="exemplo@email.com", key="input_email")
            
            data_nasc = st.text_input("Data de Nascimento (DD/MM/AAAA)", placeholder="Ex: 15/08/1990", key="input_nasc_texto")
            
            idade_calculada = None
            if data_nasc.strip():
                try:
                    dt = datetime.strptime(data_nasc.strip(), "%d/%m/%Y").date()
                    hoje = date.today()
                    idade_calculada = hoje.year - dt.year - ((hoje.month, hoje.day) < (dt.month, dt.day))
                    st.info(f"🎂 **Idade calculada automaticamente:** {idade_calculada} anos")
                except ValueError:
                    st.caption("ℹ️ Digite a data no formato DD/MM/AAAA para calcular a idade automaticamente.")

            endereco = st.text_input("Endereço", key="input_end")
            
            col_tel1, col_tel2 = st.columns(2)
            with col_tel1:
                telefone = st.text_input("Telefone / WhatsApp", key="input_tel")
            with col_tel2:
                contato_emergencia = st.text_input("Contato de Emergência", placeholder="Nome e Telefone", key="input_emergencia")

            objetivo = st.text_area("Objetivo Clínico / Diagnóstico / Restrições", placeholder="Ex: Reabilitação lombar...", key="input_obj")
            plano = st.selectbox("Plano Contratado", ["Plano 1x por semana", "Plano 2x por semana", "Plano 3x por semana", "Plano Ilimitado"], key="input_plano")
            
            st.markdown("---")
            st.markdown(f"📅 **Agenda Individual por Dia (Limite por Turma: {vagas_limite} vagas)**")
            
            dias_escolhidos = st.multiselect("Selecione o(s) Dia(s) da Semana da Aula", dias_semana_lista, key="input_dias")
            
            horarios_por_dia_escolhido = []
            tem_algum_dia_sem_vaga = False
            
            if dias_escolhidos:
                st.markdown("🕒 **Defina o horário disponível para cada dia selecionado:**")
                for dia in dias_escolhidos:
                    opcoes_dia = []
                    mapa_rotulos = {}
                    
                    for h in horarios_base:
                        ocupados_neste_dia = ocupacao_matriz.get((dia, h), 0)
                        vagas_restantes = vagas_limite - ocupados_neste_dia
                        
                        if vagas_restantes > 0:
                            rotulo = f"⏰ {h} — [{vagas_restantes}/{vagas_limite} vagas livres 🟢]"
                            opcoes_dia.append(rotulo)
                            mapa_rotulos[rotulo] = h
                    
                    if not opcoes_dia:
                        st.error(f"⚠️ Todas as turmas do dia **{dia}** estão esgotadas!")
                        tem_algum_dia_sem_vaga = True
                    else:
                        escolha_rotulo = st.selectbox(f"Horário para **{dia}**:", opcoes_dia, key=f"horario_{dia}")
                        horarios_por_dia_escolhido.append(mapa_rotulos[escolha_rotulo])
            else:
                st.info("👈 Selecione os dias da semana para configurar os horários disponíveis.")

            if st.button("💾 Salvar e Confirmar Agendamento", type="primary"):
                if not cpf.strip() or not nome.strip():
                    st.warning("Preencha o CPF e o Nome Completo.")
                elif not dias_escolhidos:
                    st.warning("Selecione pelo menos um dia da semana.")
                elif tem_algum_dia_sem_vaga:
                    st.error("⚠️ Não é possível salvar pois há dias selecionados sem vagas disponíveis.")
                elif len(horarios_por_dia_escolhido) != len(dias_escolhidos):
                    st.warning("Selecione um horário válido para cada dia escolhido.")
                else:
                    idade_final = idade_calculada if idade_calculada is not None else 0
                    sucesso, msg = adicionar_cliente(cpf, nome, email, data_nasc, idade_final, endereco, telefone, contato_emergencia, objetivo, plano, dias_escolhidos, horarios_por_dia_escolhido)
                    if sucesso:
                        st.success(msg)
                        st.session_state.limpar_campos = True
                        st.rerun()
                    else:
                        st.error(msg)

        with col_lista:
            st.subheader("👥 Clientes Cadastrados")
            if not df_atual_clientes.empty:
                busca = st.text_input("🔍 Buscar cliente por nome ou CPF:", "", key="busca_cliente_tab")
                df_exibicao = df_atual_clientes.copy()
                if busca:
                    df_exibicao = df_exibicao[
                        df_exibicao['nome'].str.contains(busca, case=False, na=False) | 
                        df_exibicao['cpf'].str.contains(busca, case=False, na=False)
                    ]
                st.dataframe(df_exibicao, hide_index=True, width='stretch')
            else:
                st.info("Nenhum cliente cadastrado.")

    with sub_aba_gerenciar:
        st.subheader("✏️ Editar ou Excluir Cadastro de Clientes")
        df_cli_gerir = carregar_clientes()
        
        if not df_cli_gerir.empty:
            lista_clientes_editar = [f"{row['nome']} (CPF: {row['cpf']})" for _, row in df_cli_gerir.iterrows()]
            escolha_cli = st.selectbox("Selecione o cliente para gerenciar:", lista_clientes_editar, key="select_cli_edit")
            
            cpf_selecionado = escolha_cli.split("CPF: ")[1].split(")")[0]
            cliente_dados = df_cli_gerir[df_cli_gerir['cpf'] == cpf_selecionado].iloc[0]
            
            with st.form("form_edicao_cliente"):
                st.markdown(f"**Editando cadastro de:** {cliente_dados['nome']} (CPF: {cliente_dados['cpf']})")
                
                novo_nome = st.text_input("Nome Completo", value=cliente_dados.get('nome', ''))
                novo_email = st.text_input("E-mail", value=cliente_dados.get('email', '') if pd.notna(cliente_dados.get('email')) else '')
                
                col_e1, col_e2 = st.columns(2)
                with col_e1:
                    nova_data_nasc = st.text_input("Data de Nascimento (DD/MM/AAAA)", value=cliente_dados.get('data_nascimento', '') if pd.notna(cliente_dados.get('data_nascimento')) else '')
                with col_e2:
                    nova_idade = st.number_input("Idade", min_value=1, max_value=120, value=int(cliente_dados.get('idade', 30)) if pd.notna(cliente_dados.get('idade')) else 30)

                novo_endereco = st.text_input("Endereço", value=cliente_dados.get('endereco', '') if pd.notna(cliente_dados.get('endereco')) else '')
                
                col_e3, col_e4 = st.columns(2)
                with col_e3:
                    novo_tel = st.text_input("Telefone / WhatsApp", value=cliente_dados.get('telefone', '') if pd.notna(cliente_dados.get('telefone')) else '')
                with col_e4:
                    novo_emerg = st.text_input("Contato de Emergência", value=cliente_dados.get('contato_emergencia', '') if pd.notna(cliente_dados.get('contato_emergencia')) else '')

                novo_obj = st.text_area("Objetivo Clínico / Restrições", value=cliente_dados.get('objetivo', '') if pd.notna(cliente_dados.get('objetivo')) else '')
                
                planos_disp = ["Plano 1x por semana", "Plano 2x por semana", "Plano 3x por semana", "Plano Ilimitado"]
                plano_atual = cliente_dados.get('plano', 'Plano 1x por semana')
                idx_plano = planos_disp.index(plano_atual) if plano_atual in planos_disp else 0
                novo_plano = st.selectbox("Plano Contratado", planos_disp, index=idx_plano)
                
                # Dias da semana salvos
                dias_atuais_str = cliente_dados.get('dias_semana', '')
                dias_atuais_lista = [d.strip() for d in dias_atuais_str.split(",")] if pd.notna(dias_atuais_str) and dias_atuais_str else []
                novos_dias = st.multiselect("Dias da Semana da Aula", dias_semana_lista, default=[d for d in dias_atuais_lista if d in dias_semana_lista])
                
                horarios_atuais_str = cliente_dados.get('horarios', '')
                novos_horarios = [h.strip() for h in horarios_atuais_str.split(",")] if pd.notna(horarios_atuais_str) and horarios_atuais_str else ["08:00"]

                col_btn_salvar, col_btn_del = st.columns(2)
                with col_btn_salvar:
                    btn_atualizar = st.form_submit_button("💾 Salvar Alterações", type="primary")
                with col_btn_del:
                    btn_excluir = st.form_submit_button("🗑️ Excluir Cliente", type="secondary")

                if btn_atualizar:
                    atualizar_cliente(
                        cpf_antigo=cpf_selecionado,
                        nome=novo_nome,
                        email=novo_email,
                        data_nasc=nova_data_nasc,
                        idade=nova_idade,
                        endereco=novo_endereco,
                        telefone=novo_tel,
                        contato_emergencia=novo_emerg,
                        objetivo=novo_obj,
                        plano=novo_plano,
                        dias_semana=novos_dias,
                        horarios=novos_horarios
                    )
                    st.success("Cadastro do cliente atualizado com sucesso!")
                    st.rerun()

                if btn_excluir:
                    deletar_cliente(cpf_selecionado)
                    st.success("Cliente excluído com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum cliente cadastrado para gerenciar.")

# ==============================================================================
# ABA 3: MAPA VISUAL DE OCUPAÇÃO DAS TURMAS
# ==============================================================================
with aba_mapa:
    st.header("🧩 Mapa de Ocupação das Turmas")
    st.markdown("Visualização em tempo real das vagas e alunos agendados em cada horário.")
    
    df_mapa_clientes = carregar_clientes()
    limite_vagas_mapa = vagas_por_turma
    matriz = calcular_ocupacao_matriz(df_mapa_clientes, limite_vagas_mapa)
    
    col_leg1, col_leg2, col_leg3 = st.columns(3)
    col_leg1.markdown("🟢 **Vaga Disponível**")
    col_leg2.markdown("🧘‍♀️ **Aluno Agendado (Vaga Ocupada)**")
    col_leg3.markdown(f"⚙️ **Capacidade:** {limite_vagas_mapa} aluno(s) por turma")
    
    st.divider()
    
    for dia in dias_semana_lista:
        st.subheader(f"📅 {dia}")
        cols_horarios = st.columns(len(horarios_base))
        
        for idx, h in enumerate(horarios_base):
            qtd_ocupados = matriz.get((dia, h), 0)
            qtd_livres = max(0, limite_vagas_mapa - qtd_ocupados)
            
            with cols_horarios[idx]:
                assentos_html = ""
                for _ in range(qtd_ocupados):
                    assentos_html += "👤 "
                for _ in range(qtd_livres):
                    assentos_html += "🟢 "
                
                status_cor = "green" if qtd_livres > 0 else "red"
                st.markdown(f"**{h}**")
                st.markdown(assentos_html)
                st.caption(f":{status_cor}[{qtd_ocupados}/{limite_vagas_mapa} vagas]")
        st.markdown("---")

# ==============================================================================
# ABA 4: CADASTRO, EDIÇÃO E EXCLUSÃO DE PROFISSIONAIS
# ==============================================================================
with aba_profissionais:
    st.header("👩‍⚕️ Gestão de Fisioterapeutas e Profissionais")
    
    sub_aba_p_novo, sub_aba_p_gerir = st.tabs(["➕ Novo Profissional", "✏️ Editar / Excluir Profissionais"])
    
    with sub_aba_p_novo:
        col_p1, col_p2 = st.columns([1, 2])
        
        with col_p1:
            st.subheader("Novo Profissional")
            with st.form("form_prof", clear_on_submit=True):
                nome_prof = st.text_input("Nome do Profissional*")
                conselho = st.selectbox("Conselho", ["CREFITO", "CREF", "Outro"])
                registro = st.text_input("Número do Registro (Ex: 123456-F)*")
                
                btn_cad_prof = st.form_submit_button("💾 Salvar Profissional")
                if btn_cad_prof:
                    if nome_prof.strip() and registro.strip():
                        adicionar_profissional(nome_prof, conselho, registro)
                        st.success(f"Profissional **{nome_prof}** cadastrado com sucesso!")
                        st.rerun()
                    else:
                        st.warning("Preencha o nome e o registro profissional.")
                        
        with col_p2:
            st.subheader("Profissionais Cadastrados")
            df_profs = carregar_profissionais()
            if not df_profs.empty:
                st.dataframe(df_profs, hide_index=True, width='stretch')
            else:
                st.info("Nenhum profissional cadastrado.")

    with sub_aba_p_gerir:
        st.subheader("✏️ Editar ou Excluir Profissionais")
        df_profs_gerir = carregar_profissionais()
        
        if not df_profs_gerir.empty:
            lista_profs_edit = [f"{row['nome_prof']} ({row['conselho']}: {row['registro']}) [ID: {row['id']}]" for _, row in df_profs_gerir.iterrows()]
            escolha_prof = st.selectbox("Selecione o profissional para gerenciar:", lista_profs_edit, key="select_prof_edit")
            
            prof_id_sel = int(escolha_prof.split("[ID: ")[1].split("]")[0])
            prof_dados = df_profs_gerir[df_profs_gerir['id'] == prof_id_sel].iloc[0]
            
            with st.form("form_edicao_prof"):
                st.markdown(f"**Editando profissional ID {prof_id_sel}**")
                
                p_nome = st.text_input("Nome do Profissional", value=prof_dados['nome_prof'])
                
                conselhos_disp = ["CREFITO", "CREF", "Outro"]
                c_atual = prof_dados['conselho']
                idx_c = conselhos_disp.index(c_atual) if c_atual in conselhos_disp else 0
                p_conselho = st.selectbox("Conselho", conselhos_disp, index=idx_c)
                
                p_registro = st.text_input("Número do Registro", value=prof_dados['registro'])
                
                col_p_salvar, col_p_del = st.columns(2)
                with col_p_salvar:
                    btn_salvar_prof = st.form_submit_button("💾 Salvar Alterações", type="primary")
                with col_p_del:
                    btn_del_prof = st.form_submit_button("🗑️ Excluir Profissional", type="secondary")

                if btn_salvar_prof:
                    atualizar_profissional(prof_id_sel, p_nome, p_conselho, p_registro)
                    st.success("Profissional atualizado com sucesso!")
                    st.rerun()

                if btn_del_prof:
                    deletar_profissional(prof_id_sel)
                    st.success("Profissional excluído com sucesso!")
                    st.rerun()
        else:
            st.info("Nenhum profissional cadastrado para gerenciar.")

# ==============================================================================
# ABA 5: PRONTUÁRIO ELETRÔNICO
# ==============================================================================
with aba_prontuario:
    st.header("📝 Prontuário Eletrônico do Paciente")
    
    df_clientes_pront = carregar_clientes()
    df_profs_pront = carregar_profissionais()
    
    if df_clientes_pront.empty:
        st.warning("Cadastre pelo menos um cliente na aba de 'Agendamento & Clientes' para acessar os prontuários.")
    elif df_profs_pront.empty:
        st.warning("Cadastre pelo menos um profissional na aba de 'Profissionais' para assinar os atendimentos.")
    else:
        lista_pacientes = [f"{row['nome']} (CPF: {row['cpf']})" for _, row in df_clientes_pront.iterrows()]
        paciente_selecionado = st.selectbox("Selecione o Paciente", lista_pacientes)
        
        cpf_atual = paciente_selecionado.split("CPF: ")[1].split(")")[0]
        dados_paciente = df_clientes_pront[df_clientes_pront['cpf'] == cpf_atual].iloc[0]
        
        with st.expander("📌 Ver Dados Cadastrais e Plano do Paciente", expanded=False):
            c1, c2, c3 = st.columns(3)
            c1.write(f"**Nome:** {dados_paciente.get('nome', '-')}")
            c1.write(f"**E-mail:** {dados_paciente.get('email', '-')}")
            c1.write(f"**Idade / Nasc:** {dados_paciente.get('idade', '-')} anos ({dados_paciente.get('data_nascimento', '-')})")
            c2.write(f"**Telefone:** {dados_paciente.get('telefone', '-')}")
            c2.write(f"**Emergência:** {dados_paciente.get('contato_emergencia', '-')}")
            c2.write(f"**Plano:** {dados_paciente.get('plano', '-')}")
            c3.write(f"**Dias/Horários:** {dados_paciente.get('dias_semana', '-')} às {dados_paciente.get('horarios', '-')}")
            st.write(f"**Objetivo Clínico / Restrições:** {dados_paciente.get('objetivo', '-')}")

        st.divider()
        col_evolucao_form, col_evolucao_hist = st.columns([1, 1])
        
        with col_evolucao_form:
            st.subheader("➕ Registrar Nova Evolução / Consulta")
            with st.form("form_evolucao", clear_on_submit=True):
                data_atendimento = st.date_input("Data da Consulta", value=datetime.today(), format="DD/MM/YYYY")
                
                lista_nomes_profs = [f"{r['nome_prof']} ({r['conselho']}: {r['registro']})" for _, r in df_profs_pront.iterrows()]
                prof_responsavel = st.selectbox("Profissional Responsável", lista_nomes_profs)
                
                atividades = st.text_area("Atividades Realizadas / Exercícios Aplicados", placeholder="Ex: Aparelho Reformer...")
                evolucao = st.text_area("Evolução Clínica / Observações do Paciente", placeholder="Ex: Paciente relatou melhora...")
                
                btn_salvar_pront = st.form_submit_button("💾 Salvar Prontuário")
                
                if btn_salvar_pront:
                    if not atividades.strip() or not evolucao.strip():
                        st.warning("Preencha as atividades e a evolução clínica.")
                    else:
                        adicionar_prontuario(
                            cpf=cpf_atual,
                            data=data_atendimento.strftime("%d/%m/%Y"),
                            profissional=prof_responsavel,
                            atividades=atividades,
                            evolucao=evolucao
                        )
                        st.success("Evolução registrada com sucesso no prontuário!")
                        st.rerun()
                        
        with col_evolucao_hist:
            st.subheader("📖 Histórico de Atendimentos")
            df_historico = carregar_prontuarios(cpf_atual)
            
            if not df_historico.empty:
                for _, hist in df_historico.iterrows():
                    with st.container(border=True):
                        st.markdown(f"📅 **Data:** {hist['data_atendimento']} | 👩‍⚕️ **Profissional:** {hist['profissional']}")
                        st.markdown(f"🏋️ **Atividades:** {hist['atividades']}")
                        st.markdown(f"📝 **Evolução:** {hist['evolucao']}")
            else:
                st.info("Nenhum registro de atendimento encontrado para este paciente.")