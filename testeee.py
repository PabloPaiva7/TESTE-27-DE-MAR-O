import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

# Inicialização das estruturas de dados
if "demandas" not in st.session_state:
    st.session_state.demandas = []
if "historico" not in st.session_state:
    st.session_state.historico = []

# Definição dos tipos de demanda
TIPOS_DEMANDA = [
    "Solicitação de Boleto",
    "Retorno de Análise",
    "Proposta",
    "Minuta",
    "Procuração",
    "Contato do Cliente"
]

# Simulação de usuários
usuarios = {
    "1": "Líder João",
    "2": "Colaborador Maria",
    "3": "Colaborador Pedro",
    "4": "Colaborador Ana",
    "5": "Colaborador Carlos"
}

# Função para registrar atividade no histórico
def registrar_atividade(demanda, acao, usuario):
    st.session_state.historico.append({
        "data_hora": datetime.now(),
        "demanda_id": demanda["id"],
        "titulo_demanda": demanda["titulo"],
        "tipo_demanda": demanda["tipo"],
        "acao": acao,
        "usuario": usuarios[usuario],
        "status": demanda["status"]
    })

# Configuração da página
st.set_page_config(
    page_title="Sistema de Gestão de Demandas",
    page_icon="📋",
    layout="wide"
)

# Sidebar para criar demanda
st.sidebar.header("🆕 Criar Nova Demanda")
with st.sidebar:
    titulo = st.text_input("Título da Demanda")
    descricao = st.text_area("Descrição")
    
    tipo_demanda = st.selectbox(
        "Tipo de Demanda",
        options=TIPOS_DEMANDA,
        help="Selecione o tipo da demanda"
    )
    
    colaborador_id = st.selectbox(
        "Atribuir a:",
        list(usuarios.keys()),
        format_func=lambda x: usuarios[x]
    )
    
    prioridade = st.select_slider(
        "Prioridade",
        options=["Baixa", "Média", "Alta"],
        value="Média"
    )
    
    data_limite = st.date_input("Data Limite")

    if st.button("📝 Criar Demanda"):
        nova_demanda = {
            "id": len(st.session_state.demandas) + 1,
            "titulo": titulo,
            "descricao": descricao,
            "tipo": tipo_demanda,
            "status": "pendente",
            "lider_id": "1",
            "colaborador_id": colaborador_id,
            "confirmacao_lider": False,
            "prioridade": prioridade,
            "data_criacao": datetime.now(),
            "data_limite": data_limite,
            "data_conclusao": None
        }
        st.session_state.demandas.append(nova_demanda)
        registrar_atividade(nova_demanda, "criação", "1")
        st.success("✅ Demanda criada com sucesso!")

# Corpo principal
st.title("📋 Sistema de Gestão de Demandas")

# Abas principais
aba = st.tabs(["📝 Minhas Demandas", "✅ Confirmar Conclusão", "📊 Histórico", "📈 Dashboard"])

# Aba 1: Minhas Demandas
with aba[0]:
    usuario_atual = st.selectbox(
        "👤 Selecione seu usuário:",
        list(usuarios.keys()),
        format_func=lambda x: usuarios[x]
    )
    
    demandas_usuario = [d for d in st.session_state.demandas if d["colaborador_id"] == usuario_atual]
    
    # Filtros
    col1, col2, col3 = st.columns(3)
    with col1:
        filtro_status = st.multiselect(
            "Status:",
            ["pendente", "concluído", "confirmado"],
            default=["pendente"]
        )
    with col2:
        filtro_prioridade = st.multiselect(
            "Prioridade:",
            ["Baixa", "Média", "Alta"],
            default=["Alta", "Média", "Baixa"]
        )
    with col3:
        filtro_tipo = st.multiselect(
            "Tipo de Demanda:",
            TIPOS_DEMANDA,
            default=TIPOS_DEMANDA
        )
    
    demandas_filtradas = [
        d for d in demandas_usuario
        if d["status"] in filtro_status
        and d["prioridade"] in filtro_prioridade
        and d["tipo"] in filtro_tipo
    ]
    
    for demanda in demandas_filtradas:
        with st.expander(f"📌 {demanda['titulo']} - {demanda['status'].upper()}"):
            st.write(f"📝 Descrição: {demanda['descricao']}")
            st.write(f"📋 Tipo: {demanda['tipo']}")
            st.write(f"⚡ Prioridade: {demanda['prioridade']}")
            st.write(f"📅 Data Limite: {demanda['data_limite'].strftime('%d/%m/%Y')}")
            
            if demanda["status"] == "pendente":
                if st.button("✅ Concluir", key=f"done_{demanda['id']}"):
                    demanda["status"] = "concluído"
                    demanda["data_conclusao"] = datetime.now()
                    registrar_atividade(demanda, "conclusão", usuario_atual)
                    st.success("Demanda concluída!")

# Aba 2: Confirmar Conclusão
with aba[1]:
    if usuario_atual == "1":  # Apenas líder
        demandas_concluidas = [
            d for d in st.session_state.demandas
            if d["status"] == "concluído" and not d["confirmacao_lider"]
        ]
        
        for demanda in demandas_concluidas:
            with st.expander(f"✅ {demanda['titulo']} - Aguardando Confirmação"):
                st.write(f"📝 Descrição: {demanda['descricao']}")
                st.write(f"📋 Tipo: {demanda['tipo']}")
                st.write(f"👤 Responsável: {usuarios[demanda['colaborador_id']]}")
                st.write(f"📅 Concluído em: {demanda['data_conclusao'].strftime('%d/%m/%Y %H:%M')}")
                
                if st.button("✔️ Confirmar", key=f"confirm_{demanda['id']}"):
                    demanda["confirmacao_lider"] = True
                    registrar_atividade(demanda, "confirmação", "1")
                    st.success("Confirmado com sucesso!")
    else:
        st.warning("⚠️ Acesso restrito ao líder")

# Aba 3: Histórico
with aba[2]:
    st.subheader("📊 Histórico de Atividades")
    
    # Filtros do histórico
    col_hist1, col_hist2 = st.columns(2)
    with col_hist1:
        filtro_usuario_hist = st.multiselect(
            "Filtrar por Usuário:",
            options=["Todos"] + list(usuarios.values()),
            default="Todos"
        )
    
    with col_hist2:
        filtro_tipo_hist = st.multiselect(
            "Filtrar por Tipo:",
            options=["Todos"] + TIPOS_DEMANDA,
            default="Todos"
        )
    
    historico_filtrado = st.session_state.historico.copy()
    
    if "Todos" not in filtro_usuario_hist:
        historico_filtrado = [
            h for h in historico_filtrado
            if h["usuario"] in filtro_usuario_hist
        ]
    
    if "Todos" not in filtro_tipo_hist:
        historico_filtrado = [
            h for h in historico_filtrado
            if h["tipo_demanda"] in filtro_tipo_hist
        ]
    
    historico_ordenado = sorted(
        historico_filtrado,
        key=lambda x: x["data_hora"],
        reverse=True
    )
    
    for registro in historico_ordenado:
        with st.expander(
            f"🕒 {registro['data_hora'].strftime('%d/%m/%Y %H:%M')} - {registro['titulo_demanda']}"
        ):
            st.write(f"👤 Usuário: {registro['usuario']}")
            st.write(f"📋 Tipo: {registro['tipo_demanda']}")
            st.write(f"🔄 Ação: {registro['acao']}")
            st.write(f"📌 Status: {registro['status']}")

# Aba 4: Dashboard
with aba[3]:
    st.subheader("📈 Dashboard de Desempenho")
    
    # Filtros do Dashboard
    col_filtros1, col_filtros2, col_filtros3 = st.columns(3)
    
    with col_filtros1:
        filtro_colaborador = st.multiselect(
            "👥 Colaboradores:",
            options=["Todos"] + list(usuarios.values()),
            default="Todos"
        )
    
    with col_filtros2:
        filtro_tipo_dash = st.multiselect(
            "📋 Tipos de Demanda:",
            options=["Todos"] + TIPOS_DEMANDA,
            default="Todos"
        )
    
    with col_filtros3:
        filtro_periodo = st.date_input(
            "📅 Período:",
            value=(datetime.now().date(), datetime.now().date())
        )

    # Aplicar filtros
    demandas_filtradas_dash = st.session_state.demandas.copy()
    
    if "Todos" not in filtro_colaborador:
        demandas_filtradas_dash = [
            d for d in demandas_filtradas_dash
            if usuarios[d["colaborador_id"]] in filtro_colaborador
        ]
    
    if "Todos" not in filtro_tipo_dash:
        demandas_filtradas_dash = [
            d for d in demandas_filtradas_dash
            if d["tipo"] in filtro_tipo_dash
        ]
    
    if isinstance(filtro_periodo, tuple):
        inicio, fim = filtro_periodo
        demandas_filtradas_dash = [
            d for d in demandas_filtradas_dash
            if inicio <= d["data_criacao"].date() <= fim
        ]

    # Métricas Gerais
    st.subheader("📊 Métricas Gerais")
    col1, col2, col3 = st.columns(3)
    
    total_filtrado = len(demandas_filtradas_dash)
    concluidas_filtrado = len([d for d in demandas_filtradas_dash if d["status"] == "concluído"])
    taxa_conclusao = (concluidas_filtrado / total_filtrado * 100) if total_filtrado > 0 else 0
    
    with col1:
        st.metric("Total de Demandas", total_filtrado)
    with col2:
        st.metric("Concluídas", concluidas_filtrado)
    with col3:
        st.metric("Taxa de Conclusão", f"{taxa_conclusao:.1f}%")

    # Análise por Colaborador
    st.subheader("👥 Desempenho por Colaborador")
    
    dados_colaboradores = []
    for col_id, col_nome in usuarios.items():
        demandas_col = [d for d in demandas_filtradas_dash if d["colaborador_id"] == col_id]
        total_col = len(demandas_col)
        concluidas_col = len([d for d in demandas_col if d["status"] == "concluído"])
        taxa_col = (concluidas_col / total_col * 100) if total_col > 0 else 0
        
        dados_colaboradores.append({
            "Colaborador": col_nome,
            "Total": total_col,
            "Concluídas": concluidas_col,
            "Taxa de Conclusão": f"{taxa_col:.1f}%"
        })
    
    df_colaboradores = pd.DataFrame(dados_colaboradores)
    st.dataframe(df_colaboradores, use_container_width=True)

    # Gráficos
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        # Gráfico de Pizza - Tipos de Demanda
        demandas_por_tipo = {tipo: len([d for d in demandas_filtradas_dash if d["tipo"] == tipo])
                            for tipo in TIPOS_DEMANDA}
        
        fig_pizza = px.pie(
            values=list(demandas_por_tipo.values()),
            names=list(demandas_por_tipo.keys()),
            title="Distribuição por Tipo de Demanda"
        )
        st.plotly_chart(fig_pizza, use_container_width=True)
    
    with col_graf2:
        # Gráfico de Barras - Status por Colaborador
        status_por_colaborador = []
        for col_id, col_nome in usuarios.items():
            for status in ["pendente", "concluído", "confirmado"]:
                qtd = len([d for d in demandas_filtradas_dash 
                          if d["colaborador_id"] == col_id and d["status"] == status])
                status_por_colaborador.append({
                    "Colaborador": col_nome,
                    "Status": status.capitalize(),
                    "Quantidade": qtd
                })
        
        df_status = pd.DataFrame(status_por_colaborador)
        fig_barras = px.bar(
            df_status,
            x="Colaborador",
            y="Quantidade",
            color="Status",
            title="Status das Demandas por Colaborador"
        )
        st.plotly_chart(fig_barras, use_container_width=True)

    # Evolução Temporal
    st.subheader("📈 Evolução Temporal")
    demandas_por_dia = {}
    for demanda in demandas_filtradas_dash:
        data = demanda["data_criacao"].date()
        if data not in demandas_por_dia:
            demandas_por_dia[data] = 0
        demandas_por_dia[data] += 1
    
    df_temporal = pd.DataFrame({
        "Data": list(demandas_por_dia.keys()),
        "Quantidade": list(demandas_por_dia.values())
    })
    
    if not df_temporal.empty:
        fig_linha = px.line(
            df_temporal,
            x="Data",
            y="Quantidade",
            title="Evolução de Demandas ao Longo do Tempo"
        )
        st.plotly_chart(fig_linha, use_container_width=True)
    else:
        st.info("Não há dados para o período selecionado")