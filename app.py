import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
import io
from PIL import Image as PILImage
import plotly.io as pio

# Cores da Paleta Living Spa
VERDE_SALVIA = "#98A869"
VERDE_MUSGO = "#6D7649"
BEGE_NEUTRO = "#E6D6CC"
CREME_SUAVE = "#FAFFE7"
MARROM_TERRA = "#A39384"
BRANCO_PURO = "#FFFFFF"
VERDE_OLIVA_ESCURO = "#3B3418"

# Cores para o gráfico (vibrantes e destacadas)
COR_SEM_PROMO = "#E74C3C"  # Vermelho vibrante
COR_COM_PROMO = "#27AE60"  # Verde vibrante

# Configuração da página
st.set_page_config(
    page_title="Living Spa - Análise Sazonal e Precificação",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Detecta o tema do Streamlit
def get_theme_mode():
    """Detecta se o tema é dark ou light"""
    try:
        if st.get_option("theme.base") == "dark":
            return "dark"
    except:
        pass
    return "light"

# Carrega os dados sazonais
def load_seasonal_data():
    """Carrega os dados sazonais do arquivo CSV"""
    df = pd.read_csv('dados_sazonais.csv')
    return df

# Função para gerar gráfico de comparação
def create_comparison_chart(demand, original_price, promotional_price, commission_percentage, service_cost, required_quantity):
    """Cria um gráfico comparativo de receita e lucro"""
    
    # Cálculos
    commission_decimal = commission_percentage / 100
    
    # Sem promoção
    revenue_without = original_price * demand
    commission_without = revenue_without * commission_decimal
    cost_without = service_cost * demand
    profit_without = revenue_without - commission_without - cost_without
    
    # Com promoção (usando quantidade necessária)
    revenue_with = promotional_price * required_quantity
    commission_with = revenue_with * commission_decimal
    cost_with = service_cost * required_quantity
    profit_with = revenue_with - commission_with - cost_with
    
    categories = ['Receita', 'Comissão', 'Custo', 'Lucro']
    sem_promo = [revenue_without, commission_without, cost_without, profit_without]
    com_promo = [revenue_with, commission_with, cost_with, profit_with]
    
    fig = go.Figure(data=[
        go.Bar(name='Sem Promoção', x=categories, y=sem_promo, marker_color=COR_SEM_PROMO),
        go.Bar(name='Com Promoção', x=categories, y=com_promo, marker_color=COR_COM_PROMO)
    ])
    
    fig.update_layout(
        title="Comparação: Sem Promoção vs Com Promoção",
        barmode='group',
        template='plotly_dark',
        height=400,
        showlegend=True,
        yaxis_title="Valor (R$)",
        hovermode='x unified',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color=BRANCO_PURO)
    )
    
    return fig

# Função para gerar gráfico para PDF com cores e texto preto
def create_comparison_chart_for_pdf(demand, original_price, promotional_price, commission_percentage, service_cost, required_quantity):
    """Cria um gráfico comparativo para PDF com texto preto"""
    
    # Cálculos
    commission_decimal = commission_percentage / 100
    
    # Sem promoção
    revenue_without = original_price * demand
    commission_without = revenue_without * commission_decimal
    cost_without = service_cost * demand
    profit_without = revenue_without - commission_without - cost_without
    
    # Com promoção (usando quantidade necessária)
    revenue_with = promotional_price * required_quantity
    commission_with = revenue_with * commission_decimal
    cost_with = service_cost * required_quantity
    profit_with = revenue_with - commission_with - cost_with
    
    categories = ['Receita', 'Comissão', 'Custo', 'Lucro']
    sem_promo = [revenue_without, commission_without, cost_without, profit_without]
    com_promo = [revenue_with, commission_with, cost_with, profit_with]
    
    fig = go.Figure(data=[
        go.Bar(name='Sem Promoção', x=categories, y=sem_promo, marker_color=COR_SEM_PROMO),
        go.Bar(name='Com Promoção', x=categories, y=com_promo, marker_color=COR_COM_PROMO)
    ])
    
    fig.update_layout(
        title="Comparação: Sem Promoção vs Com Promoção",
        barmode='group',
        template='plotly_white',  # Fundo branco para PDF
        height=400,
        showlegend=True,
        yaxis_title="Valor (R$)",
        hovermode='x unified',
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(255,255,255,1)',
        font=dict(color='#000000')  # Texto preto
    )
    
    return fig

# Função para gerar PDF
def generate_pdf_report(service, month, demand, std_dev, original_price, service_cost, 
                        commission_percentage, desired_profit_increase, promotional_price,
                        revenue_without_promo, commission_without_promo, total_service_cost_without_promo,
                        spa_revenue_without_promo, desired_spa_revenue, required_quantity,
                        total_promo_revenue, final_commission, total_service_cost_with_promo,
                        spa_revenue_with_promo, comparison_chart, is_custom=False):
    """Gera um relatório em PDF com todas as informações da estratégia de promoção"""
    
    # Define o nome do serviço em singular
    if is_custom:
        service_singular = "do serviço"
        service_name_display = "Outros"
    else:
        service_singular = "drenagem" if "Drenagem" in service else "massagem"
        service_name_display = service
    
    # Cria buffer para o PDF
    pdf_buffer = io.BytesIO()
    
    # Cria o documento PDF
    doc = SimpleDocTemplate(pdf_buffer, pagesize=A4,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Lista de elementos do PDF
    elements = []
    
    # Estilos
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor(VERDE_SALVIA),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor(VERDE_MUSGO),
        spaceAfter=12,
        spaceBefore=12,
        fontName='Helvetica-Bold'
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor(VERDE_OLIVA_ESCURO),
        spaceAfter=6,
        leading=14
    )
    
    # Título
    elements.append(Paragraph("🌿 RELATÓRIO DE ESTRATÉGIA DE PROMOÇÃO", title_style))
    elements.append(Paragraph(f"Living Spa - {datetime.now().strftime('%d/%m/%Y às %H:%M')}", 
                             ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=10, 
                                          textColor=colors.HexColor(MARROM_TERRA), alignment=TA_CENTER)))
    elements.append(Spacer(1, 0.3*inch))
    
    # Seção 1: Informações Gerais
    elements.append(Paragraph("1. INFORMAÇÕES GERAIS", heading_style))
    
    if is_custom:
        info_text = f"""
        <b>Serviço:</b> {service_name_display}<br/>
        <b>Demanda Esperada:</b> {int(demand)} atendimentos<br/>
        <b>Data do Relatório:</b> {datetime.now().strftime('%d/%m/%Y')}
        """
    else:
        info_text = f"""
        <b>Serviço:</b> {service_name_display}<br/>
        <b>Mês da Promoção:</b> {month}<br/>
        <b>Data do Relatório:</b> {datetime.now().strftime('%d/%m/%Y')}
        """
    elements.append(Paragraph(info_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Seção 2: Análise de Demanda (apenas se não for custom)
    if not is_custom:
        elements.append(Paragraph("2. ANÁLISE DE DEMANDA", heading_style))
        
        demand_text = f"""
        <b>Demanda Esperada:</b> {int(demand)} atendimentos<br/>
        <b>Desvio Padrão:</b> ±{std_dev:.2f}
        """
        elements.append(Paragraph(demand_text, normal_style))
        elements.append(Spacer(1, 0.2*inch))
        
        section_number = 3
    else:
        section_number = 2
    
    # Seção de Parâmetros de Precificação
    elements.append(Paragraph(f"{section_number}. PARÂMETROS DE PRECIFICAÇÃO", heading_style))
    
    pricing_text = f"""
    <b>Preço Original:</b> R$ {original_price:.2f}<br/>
    <b>Preço Promocional:</b> R$ {promotional_price:.2f}<br/>
    <b>Desconto:</b> {((1 - promotional_price/original_price) * 100):.1f}%<br/>
    <b>Custo por Serviço:</b> R$ {service_cost:.2f}<br/>
    <b>Comissão Massagista:</b> {commission_percentage:.1f}%<br/>
    <b>Lucro Adicional Desejado:</b> {desired_profit_increase:.1f}%
    """
    elements.append(Paragraph(pricing_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Seção de Cenário Sem Promoção
    section_number += 1
    elements.append(Paragraph(f"{section_number}. CENÁRIO SEM PROMOÇÃO (BASELINE)", heading_style))
    
    without_text = f"""
    <b>Receita Total:</b> R$ {revenue_without_promo:,.2f}<br/>
    <b>Comissão Massagista:</b> R$ {commission_without_promo:,.2f}<br/>
    <b>Custo Total:</b> R$ {total_service_cost_without_promo:,.2f}<br/>
    <b>Lucro Real sem Estratégia:</b> R$ {spa_revenue_without_promo:,.2f}
    """
    elements.append(Paragraph(without_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Seção de Cenário Com Promoção
    section_number += 1
    elements.append(Paragraph(f"{section_number}. CENÁRIO COM PROMOÇÃO (META)", heading_style))
    
    if is_custom:
        service_text = "do serviço"
    else:
        service_text = "drenagens" if "Drenagem" in service else "massagens"
    
    with_text = f"""
    <b>Quantidade Necessária:</b> {required_quantity} {service_text}<br/>
    <b>Receita Total:</b> R$ {total_promo_revenue:,.2f}<br/>
    <b>Comissão Massagista:</b> R$ {final_commission:,.2f}<br/>
    <b>Custo Total:</b> R$ {total_service_cost_with_promo:,.2f}<br/>
    <b>Lucro Real da Estratégia:</b> R$ {spa_revenue_with_promo:,.2f}
    """
    elements.append(Paragraph(with_text, normal_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Seção de Resumo Executivo
    section_number += 1
    elements.append(Paragraph(f"{section_number}. RESUMO EXECUTIVO", heading_style))
    
    lucro_diff = spa_revenue_with_promo - spa_revenue_without_promo
    lucro_diff_pct = ((spa_revenue_with_promo / spa_revenue_without_promo - 1) * 100) if spa_revenue_without_promo > 0 else 0
    
    summary_text = f"""
    <b>Estratégia:</b> Reduzir o preço de R$ {original_price:.2f} para R$ {promotional_price:.2f} (desconto de {((1 - promotional_price/original_price) * 100):.1f}%)<br/><br/>
    
    <b>Objetivo:</b> Aumentar o lucro em {desired_profit_increase:.1f}% em relação ao cenário atual<br/><br/>
    
    <b>Meta de Vendas:</b> {required_quantity} {service_text} ao preço promocional<br/><br/>
    
    <b>Impacto no Lucro:</b> Aumento de R$ {lucro_diff:,.2f} ({lucro_diff_pct:+.1f}%)<br/><br/>
    
    <b>Lucro Esperado:</b> R$ {spa_revenue_with_promo:,.2f} (vs R$ {spa_revenue_without_promo:,.2f} sem promoção)
    """
    
    elements.append(Paragraph(summary_text, normal_style))
    elements.append(Spacer(1, 0.3*inch))
    
    # Seção de Gráfico Comparativo
    section_number += 1
    elements.append(Paragraph(f"{section_number}. GRÁFICO COMPARATIVO", heading_style))
    
    # Salva o gráfico como imagem com fundo branco e texto preto
    try:
        img_buffer = io.BytesIO()
        pio.write_image(comparison_chart, img_buffer, format='png', width=600, height=400)
        img_buffer.seek(0)
        img = Image(img_buffer, width=6*inch, height=4*inch)
        elements.append(img)
    except:
        elements.append(Paragraph("Gráfico não disponível nesta versão", normal_style))
    
    elements.append(Spacer(1, 0.2*inch))
    
    # Rodapé
    elements.append(Spacer(1, 0.1*inch))
    footer_text = f"<i>Relatório gerado automaticamente pelo Living Spa Dashboard em {datetime.now().strftime('%d/%m/%Y às %H:%M:%S')}</i>"
    elements.append(Paragraph(footer_text, ParagraphStyle('footer', parent=styles['Normal'], 
                                                         fontSize=8, textColor=colors.HexColor(MARROM_TERRA), 
                                                         alignment=TA_CENTER)))
    
    # Constrói o PDF
    doc.build(elements)
    pdf_buffer.seek(0)
    
    return pdf_buffer

# CSS personalizado com paleta Living Spa
st.markdown(f"""
    <style>
    /* Configurações gerais */
    :root {{
        --verde-salvia: {VERDE_SALVIA};
        --verde-musgo: {VERDE_MUSGO};
        --bege-neutro: {BEGE_NEUTRO};
        --creme-suave: {CREME_SUAVE};
        --marrom-terra: {MARROM_TERRA};
        --branco-puro: {BRANCO_PURO};
        --verde-oliva-escuro: {VERDE_OLIVA_ESCURO};
    }}
    
    /* Cards de Métrica */
    .metric-card {{
        background: linear-gradient(135deg, {VERDE_SALVIA} 0%, {VERDE_MUSGO} 100%);
        padding: 20px;
        border-radius: 12px;
        margin: 10px 0;
        border: 2px solid {MARROM_TERRA};
        color: {BRANCO_PURO};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .metric-card p {{
        color: {BRANCO_PURO} !important;
        margin: 5px 0;
    }}
    .metric-card strong {{
        color: {BRANCO_PURO} !important;
    }}
    .metric-card h4 {{
        color: {CREME_SUAVE} !important;
        margin-top: 0;
    }}
    
    /* Cards de Sucesso */
    .success-card {{
        background: linear-gradient(135deg, {VERDE_SALVIA} 0%, {VERDE_MUSGO} 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid {MARROM_TERRA};
        margin: 10px 0;
        color: {BRANCO_PURO};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .success-card h4 {{
        color: {CREME_SUAVE} !important;
        margin-top: 0;
    }}
    .success-card p {{
        color: {BRANCO_PURO} !important;
        margin: 5px 0;
    }}
    .success-card strong {{
        color: {BRANCO_PURO} !important;
    }}
    
    /* Cards de Aviso */
    .warning-card {{
        background: linear-gradient(135deg, {BEGE_NEUTRO} 0%, {CREME_SUAVE} 100%);
        padding: 20px;
        border-radius: 12px;
        border-left: 5px solid {VERDE_SALVIA};
        margin: 10px 0;
        color: {VERDE_OLIVA_ESCURO};
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }}
    .warning-card h4 {{
        color: {VERDE_MUSGO} !important;
        margin-top: 0;
    }}
    .warning-card p {{
        color: {VERDE_OLIVA_ESCURO} !important;
        margin: 5px 0;
    }}
    .warning-card strong {{
        color: {VERDE_MUSGO} !important;
    }}
    
    /* Título */
    h1 {{
        color: {VERDE_SALVIA} !important;
        font-weight: 600;
    }}
    
    h2 {{
        color: {VERDE_MUSGO} !important;
    }}
    
    /* Texto */
    body {{
        color: {VERDE_OLIVA_ESCURO} !important;
    }}
    </style>
""", unsafe_allow_html=True)

# Detecta o tema e carrega a logo apropriada
theme_mode = get_theme_mode()
if theme_mode == "dark":
    logo_path = "Logo-Living-SPA-BRANCO.png"
else:
    logo_path = "Logo-Living-SPA-PRETO.png"

# Título principal com logo
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image(logo_path, width=100)
    except:
        st.write("🌿")

with col_title:
    st.title("Living Spa - Dashboard de Precificação")
    st.markdown("*Análise Sazonal e Estratégia de Promoção Inteligente*")

st.markdown("---")

# Carrega dados
seasonal_data = load_seasonal_data()

# Sidebar com navegação
st.sidebar.title("🌿 Menu")
page = st.sidebar.radio(
    "Selecione uma página:",
    ["📊 Análise Sazonal", "💰 Precificação Inteligente"]
)

# Meses para referência
months = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

# ============================================================================
# PÁGINA 1: ANÁLISE SAZONAL
# ============================================================================
if page == "📊 Análise Sazonal":
    st.header("📊 Análise Sazonal de Demanda")
    st.markdown("Visualize a demanda média mensal e o desvio padrão dos serviços")
    st.markdown("---")
    
    # Separa dados por serviço
    drainage_data = seasonal_data[seasonal_data['Servico'] == 'Drenagem Linfática corporal (50 min)'].sort_values('Mes')
    massage_data = seasonal_data[seasonal_data['Servico'] == 'Massagem Relaxante (50 min)'].sort_values('Mes')
    
    # Cria abas
    tab1, tab2 = st.tabs(["🌿 Drenagem Linfática", "🧘 Massagem Relaxante"])
    
    # ========== TAB 1: DRENAGEM LINFÁTICA ==========
    with tab1:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Demanda Mensal")
            
            # Gráfico de linha para demanda
            fig_demand = go.Figure()
            fig_demand.add_trace(go.Scatter(
                x=[months[m] for m in drainage_data['Mes']],
                y=drainage_data['Media'],
                mode='lines+markers',
                name='Demanda Média',
                line=dict(color=VERDE_SALVIA, width=3),
                marker=dict(size=8, color=VERDE_MUSGO)
            ))
            
            fig_demand.update_layout(
                title="Demanda Média de Drenagens por Mês",
                xaxis_title="Mês",
                yaxis_title="Quantidade de Atendimentos",
                hovermode='x unified',
                template='plotly_dark',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=BRANCO_PURO)
            )
            
            st.plotly_chart(fig_demand, use_container_width=True)
        
        with col2:
            st.subheader("📊 Desvio Padrão")
            
            # Gráfico de barras para desvio padrão
            fig_std = go.Figure()
            fig_std.add_trace(go.Bar(
                x=[months[m] for m in drainage_data['Mes']],
                y=drainage_data['Desvio_padrao'],
                name='Desvio Padrão',
                marker=dict(color=VERDE_SALVIA)
            ))
            
            fig_std.update_layout(
                title="Variação da Demanda (Desvio Padrão)",
                xaxis_title="Mês",
                yaxis_title="Desvio Padrão",
                hovermode='x unified',
                template='plotly_dark',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=BRANCO_PURO)
            )
            
            st.plotly_chart(fig_std, use_container_width=True)
        
        # Tabela com dados
        st.subheader("Dados Detalhados")
        display_data = drainage_data.copy()
        display_data['Mes'] = display_data['Mes'].map(months)
        display_data = display_data[['Mes', 'Media', 'Desvio_padrao']].rename(
            columns={'Mes': 'Mês', 'Media': 'Demanda Média', 'Desvio_padrao': 'Desvio Padrão'}
        )
        st.dataframe(display_data, use_container_width=True, hide_index=True)
    
    # ========== TAB 2: MASSAGEM RELAXANTE ==========
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 Demanda Mensal")
            
            # Gráfico de linha para demanda
            fig_demand = go.Figure()
            fig_demand.add_trace(go.Scatter(
                x=[months[m] for m in massage_data['Mes']],
                y=massage_data['Media'],
                mode='lines+markers',
                name='Demanda Média',
                line=dict(color=VERDE_MUSGO, width=3),
                marker=dict(size=8, color=VERDE_SALVIA)
            ))
            
            fig_demand.update_layout(
                title="Demanda Média de Massagens por Mês",
                xaxis_title="Mês",
                yaxis_title="Quantidade de Atendimentos",
                hovermode='x unified',
                template='plotly_dark',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=BRANCO_PURO)
            )
            
            st.plotly_chart(fig_demand, use_container_width=True)
        
        with col2:
            st.subheader("📊 Desvio Padrão")
            
            # Gráfico de barras para desvio padrão - CORRIGIDO PARA VERDE
            fig_std = go.Figure()
            fig_std.add_trace(go.Bar(
                x=[months[m] for m in massage_data['Mes']],
                y=massage_data['Desvio_padrao'],
                name='Desvio Padrão',
                marker=dict(color=VERDE_SALVIA)  # Mudado para VERDE_SALVIA
            ))
            
            fig_std.update_layout(
                title="Variação da Demanda (Desvio Padrão)",
                xaxis_title="Mês",
                yaxis_title="Desvio Padrão",
                hovermode='x unified',
                template='plotly_dark',
                height=400,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color=BRANCO_PURO)
            )
            
            st.plotly_chart(fig_std, use_container_width=True)
        
        # Tabela com dados
        st.subheader("Dados Detalhados")
        display_data = massage_data.copy()
        display_data['Mes'] = display_data['Mes'].map(months)
        display_data = display_data[['Mes', 'Media', 'Desvio_padrao']].rename(
            columns={'Mes': 'Mês', 'Media': 'Demanda Média', 'Desvio_padrao': 'Desvio Padrão'}
        )
        st.dataframe(display_data, use_container_width=True, hide_index=True)

# ============================================================================
# PÁGINA 2: PRECIFICAÇÃO INTELIGENTE
# ============================================================================
elif page == "💰 Precificação Inteligente":
    st.header("💰 Precificação Inteligente")
    st.markdown("Calcule preços promocionais para atingir suas metas de lucro")
    st.markdown("---")
    
    col1, col2 = st.columns([1, 2])
    
    # ========== COLUNA 1: FORMULÁRIO ==========
    with col1:
        st.subheader("⚙️ Configuração")
        
        # Seleção de serviço
        service = st.selectbox(
            "Selecione o Serviço",
            ["Drenagem Linfática corporal (50 min)", "Massagem Relaxante (50 min)", "Outros"]
        )
        
        # Define o nome do serviço em singular para exibição
        is_custom_service = service == "Outros"
        
        if is_custom_service:
            service_name = "do serviço"
            service_name_plural = "do serviço"
            
            # Input customizado de demanda
            demand = st.number_input(
                "Demanda Esperada",
                min_value=1.0,
                value=20.0,
                step=1.0,
                format="%.1f",
                help="Quantidade de atendimentos esperados para este serviço"
            )
            std_dev = 0.0  # Sem desvio padrão para serviços customizados
            current_month = None
            
            st.markdown(f"""
            <div class="metric-card">
                <h4>📊 Dados Customizados</h4>
                <p><strong>Demanda Esperada:</strong> {demand:.1f} atendimentos</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            service_name = "drenagem" if "Drenagem" in service else "massagem"
            service_name_plural = "drenagens" if "Drenagem" in service else "massagens"
            
            # Seleção de mês
            current_month = st.selectbox(
                "Mês Atual",
                list(months.values()),
                index=datetime.now().month - 1
            )
            current_month_num = list(months.values()).index(current_month) + 1
            
            # Busca dados do mês selecionado
            month_data = seasonal_data[
                (seasonal_data['Servico'] == service) & 
                (seasonal_data['Mes'] == current_month_num)
            ]
            
            if not month_data.empty:
                demand = month_data['Media'].values[0]
                std_dev = month_data['Desvio_padrao'].values[0]
                
                st.markdown(f"""
                <div class="metric-card">
                    <h4>📊 Dados do Mês</h4>
                    <p><strong>Demanda Esperada:</strong> {int(demand)} {service_name_plural}</p>
                    <p><strong>Desvio Padrão:</strong> ±{std_dev:.2f}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                demand = 0
                std_dev = 0
        
        st.markdown("---")
        
        # Inputs do formulário
        original_price = st.number_input(
            "Preço Original (R$)",
            min_value=0.0,
            value=100.0,
            step=0.01,
            format="%.2f"
        )
        
        service_cost = st.number_input(
            "Custo por Serviço (R$)",
            min_value=0.0,
            value=20.0,
            step=0.01,
            format="%.2f",
            help="Custo do spa para realizar o serviço (materiais, energia, etc)"
        )
        
        commission_percentage = st.number_input(
            "Comissão Massagista (%)",
            min_value=0.0,
            max_value=130.0,
            value=30.0,
            step=0.5,
            format="%.1f"
        )
        
        desired_profit_increase = st.number_input(
            "Lucro Adicional Desejado (%)",
            min_value=0.0,
            value=5.0,
            step=0.5,
            format="%.1f"
        )
        
        promotional_price = st.number_input(
            "Preço Promocional (R$)",
            min_value=0.0,
            value=100.0,
            step=0.01,
            format="%.2f"
        )
        
        st.markdown("---")
        
        # Botão de cálculo
        calculate_button = st.button("🧮 Calcular", use_container_width=True, type="primary")
    
    # ========== COLUNA 2: RESULTADOS ==========
    with col2:
        if calculate_button and demand > 0:
            # Cálculos
            commission_decimal = commission_percentage / 100
            profit_increase_decimal = desired_profit_increase / 100
            
            # ===== CENÁRIO SEM PROMOÇÃO =====
            revenue_without_promo = original_price * demand
            total_costs_without_promo = (commission_percentage / 100 * revenue_without_promo) + (service_cost * demand)
            spa_revenue_without_promo = revenue_without_promo - total_costs_without_promo
            
            commission_without_promo = (commission_percentage / 100) * revenue_without_promo
            total_service_cost_without_promo = service_cost * demand
            
            # ===== META DE LUCRO =====
            desired_spa_revenue = spa_revenue_without_promo * (1 + profit_increase_decimal)
            
            # ===== CENÁRIO COM PROMOÇÃO =====
            profit_per_promo_service = promotional_price - (promotional_price * commission_decimal) - service_cost
            required_quantity = int(desired_spa_revenue / profit_per_promo_service) + 1
            
            # Comissão final
            total_promo_revenue = promotional_price * required_quantity
            final_commission = total_promo_revenue * commission_decimal
            total_service_cost_with_promo = service_cost * required_quantity
            spa_revenue_with_promo = total_promo_revenue - final_commission - total_service_cost_with_promo
            
            # Exibe resultados
            st.subheader("📈 Análise Sem Promoção")
            st.markdown(f"""
            <div class="success-card">
                <h4>Cenário Atual (Preço Normal)</h4>
                <p><strong>Demanda Esperada:</strong> {demand:.1f if is_custom_service else int(demand)} {service_name_plural}</p>
                <p><strong>Receita Total:</strong> R$ {revenue_without_promo:,.2f}</p>
                <p><strong>Comissão Massagista:</strong> R$ {commission_without_promo:,.2f}</p>
                <p><strong>Custo por Serviço:</strong> R$ {total_service_cost_without_promo:,.2f}</p>
                <p style="font-weight: bold; font-size: 16px; color: {CREME_SUAVE};"><strong>Lucro Real sem Estratégia:</strong> R$ {spa_revenue_without_promo:,.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.subheader("🎯 Meta de Lucro com Promoção")
            
            # Texto dinâmico baseado no serviço
            if is_custom_service:
                meta_text = f"Você precisa vender {required_quantity} do serviço"
            else:
                meta_text = f"Você precisa vender {required_quantity} {service_name_plural}"
            
            st.markdown(f"""
            <div class="warning-card">
                <h4>Cenário Promocional</h4>
                <p><strong>Lucro Necessário:</strong> R$ {desired_spa_revenue:,.2f}</p>
                <p style="font-size: 24px; font-weight: bold; color: {VERDE_MUSGO}; margin: 15px 0;">
                    {meta_text}
                </p>
                <p style="font-size: 14px; color: {VERDE_OLIVA_ESCURO};">ao preço promocional de R$ {promotional_price:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.metric("Receita Total", f"R$ {total_promo_revenue:,.2f}")
            with col_b:
                st.metric("Comissão", f"R$ {final_commission:,.2f}")
            with col_c:
                st.metric("Custo Serviço", f"R$ {total_service_cost_with_promo:,.2f}")
            
            st.metric("💰 Lucro Real da Estratégia", f"R$ {spa_revenue_with_promo:,.2f}", delta=f"{((spa_revenue_with_promo / spa_revenue_without_promo - 1) * 100):.1f}%" if spa_revenue_without_promo > 0 else "0%")
            
            # Gera gráfico comparativo
            comparison_chart = create_comparison_chart(demand, original_price, promotional_price, 
                                                      commission_percentage, service_cost, required_quantity)
            st.plotly_chart(comparison_chart, use_container_width=True)
            
            # Botão para baixar PDF
            st.markdown("---")
            
            # Cria gráfico para PDF com cores e texto preto
            comparison_chart_pdf = create_comparison_chart_for_pdf(demand, original_price, promotional_price, 
                                                                   commission_percentage, service_cost, required_quantity)
            
            pdf_buffer = generate_pdf_report(
                service, current_month if not is_custom_service else None, demand, std_dev, original_price, service_cost,
                commission_percentage, desired_profit_increase, promotional_price,
                revenue_without_promo, commission_without_promo, total_service_cost_without_promo,
                spa_revenue_without_promo, desired_spa_revenue, required_quantity,
                total_promo_revenue, final_commission, total_service_cost_with_promo,
                spa_revenue_with_promo, comparison_chart_pdf, is_custom=is_custom_service
            )
            
            st.download_button(
                label="📥 Baixar Relatório em PDF",
                data=pdf_buffer,
                file_name=f"Relatorio_Promocao_{current_month if current_month else 'Outros'}_{datetime.now().strftime('%d_%m_%Y')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )
        
        elif not is_custom_service and demand == 0:
            st.error("❌ Dados não encontrados para este mês e serviço")
        elif is_custom_service and demand > 0:
            st.info("👈 Preencha os dados e clique em 'Calcular' para ver os resultados")
        elif not is_custom_service:
            st.info("👈 Preencha os dados e clique em 'Calcular' para ver os resultados")

# Footer
st.markdown("---")
st.markdown(
    f"<p style='text-align: center; color: {MARROM_TERRA}; font-size: 12px;'>"
    "Living Spa © 2024 | Dashboard de Precificação Inteligente"
    "</p>",
    unsafe_allow_html=True
)
