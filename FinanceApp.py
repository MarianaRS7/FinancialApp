import numpy as np
import pandas as pd
import requests
import time
import matplotlib.pyplot as plt
import streamlit as st
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from urllib.parse import quote
import plotly.express as px
from PIL import Image
from io import BytesIO
import datetime
import os


st.markdown("<h2 style='text-align: center; color: #4B8BBE;'>MY FINANCIAL APP📊</h2>", unsafe_allow_html=True)
# Crear las pestañas
tabs = st.tabs(["Información Empresa", "Dashboard","Noticias", "Simulador de Inversiones"])


# COMPANY OVERVIEW

with tabs[0]:
    
    st.markdown("# Company Overview :bar_chart:")

    st.markdown(
    """
    <div style="
        color: #003366;
        font-size: 16px;
        text-align: justify;
        margin-bottom: 20px;">
        En esta sección, puedes obtener información detallada sobre cualquier empresa que cotice en bolsa con solo ingresar su ticker. Verás una breve descripción de la empresa, datos financieros importantes y gráficos interactivos. Todo está pensado para ayudarte a tomar mejores decisiones de inversión de manera fácil y rápida.
    </div>
    """,
    unsafe_allow_html=True
    )


    # Campo de texto para que el usuario ingrese el ticker
    ticker = st.text_input(label="**Enter a stock ticker (for example, AAPL)**").strip()

    if ticker:
        try:
            company = yf.Ticker(ticker)
            info = company.info
            
            company_name = info.get('longName', 'Nombre no disponible')
            st.markdown(f"<h3 style='text-align: center; color: #FF6347;'>{company_name}</h3>", unsafe_allow_html=True)


            # Obtener el precio actual
            todays_data = company.history(period='1d')
            current_price = todays_data['Close'][0]
            open_price = todays_data['Open'][0]
            price_change = current_price - open_price
            percent_change = (price_change / open_price) * 100
            # Determinar el color y el signo del cambio
            if price_change >= 0:
                change_color = "green"
                sign = "+"
            else:
                change_color = "red"
                sign = ""

            st.markdown("<h3 style='text-align: center; color: #4B8BBE;'>INFORMACIÓN DE LA COMPAÑÍA</h3>", unsafe_allow_html=True)

            # Organizar la disposición en dos columnas
            col1, col2 = st.columns(2)

            # Columna 1: Información de la empresa
            with col1:
                st.markdown(f"<p style='font-size: 18px;'><b>Simbolo:</b> {ticker.upper()}</p>", unsafe_allow_html=True)

                # Mostrar una descripción más corta
                full_description = info.get('longBusinessSummary', 'Descripción no disponible')
                short_description = (full_description[:200] + '...') if len(full_description) > 200 else full_description
                st.markdown(f"<p style='font-size: 16px;'><b>Descripción breve:</b> {short_description}</p>", unsafe_allow_html=True)


            # Columna 2: Datos financieros calculados
            with col2:

                st.markdown(f"<p style='font-size: 16px;'><b>MarketCap:</b> ${'{:,.0f}'.format(info['marketCap']) if 'marketCap' in info and isinstance(info['marketCap'], (int, float)) else 'N/A'}</p>",unsafe_allow_html=True)

                st.markdown(f"<p style='font-size: 16px;'><b>Industry:</b> {info.get('industry', 'N/A')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 16px;'><b>Sector:</b> {info.get('sector', 'N/A')}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 16px;'><b>Beta:</b> {info['beta']:,}</p>" if 'beta' in info and isinstance(info['beta'], (int, float)) else "<p style='font-size: 16px;'><b>Beta:</b> N/A</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 16px;'><b>Recommendation:</b> {info.get('recommendationKey', 'N/A')}</p>", unsafe_allow_html=True)


                # Descargar datos históricos de 10 años
                historical_data = company.history(period="10y")
                historical_data['Return'] = historical_data['Close'].pct_change()
                annualized_return = ((1 + historical_data['Return'].mean()) ** 252 - 1) * 100
                average_risk = historical_data['Return'].std() * (252 ** 0.5) * 100

            st.markdown(f"#### Precio actual: ${current_price:.2f} <span style='color:{change_color}; font-size:0.9em;'>{sign}{price_change:.2f} ({sign}{percent_change:.2f})% </span>", unsafe_allow_html=True)
            # Título para la gráfica
            st.markdown("<h3 style='text-align: center; color: #4B8BBE;'>DESEMPEÑO HISTÓRICO</h3>", unsafe_allow_html=True)

            # Gráfica de desempeño histórico
            plt.figure(figsize=(12, 6))
            plt.plot(historical_data.index, historical_data['Close'], color='#1f77b4', linewidth=2)
            plt.title(f'Precio Histórico de {ticker.upper()} en los Últimos 10 Años', fontsize=16)
            plt.xlabel('Fecha', fontsize=14)
            plt.ylabel('Precio ($)', fontsize=14)
            plt.grid(visible=True, linestyle='--', alpha=0.5)
            st.pyplot(plt)

            st.markdown(f"<p style='font-size: 16px; text-align: center;'><b>Rendimiento Anualizado:</b> {annualized_return:.2f}%</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 16px; text-align: center;'><b>Riesgo Promedio (Volatilidad):</b> {average_risk:.2f}%</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-size: 16px; text-align: center;'><b>Ratio Riesgo/Rendimiento:</b> {(annualized_return / average_risk):.2f}</p>", unsafe_allow_html=True)

            # Agregar un botón para mostrar la gráfica
            if st.button("Mostrar Gráfica Comparativa"):
                # Crear la gráfica con Plotly
                fig = go.Figure()

                # Añadir datos a la gráfica
                fig.add_trace(go.Bar(
                    x=['Rendimiento Anualizado', 'Riesgo Promedio'],
                    y=[annualized_return, average_risk],
                    text=[f"{annualized_return:.2f}%", f"{average_risk:.2f}%"],
                    textposition='auto',
                    marker_color=['#A3C1E5', '#D6A4E0']  # Azul y Morado
                ))

                # Personalización de la gráfica
                fig.update_layout(
                    title='Comparativa: Rendimiento vs Riesgo',
                    xaxis_title='Métricas',
                    yaxis_title='Porcentaje (%)',
                    template='plotly_white'
                )

                # Mostrar la gráfica en Streamlit
                st.plotly_chart(fig)

            # Sección de gráficos adicionales
            st.markdown("---")
            st.markdown("<h3 style='text-align: center; color: #4B8BBE;'>GRÁFICAS ESTADOS FINANCIEROS</h3>", unsafe_allow_html=True)

            # Income Statement
            financials = company.financials
            if financials is not None and 'Total Revenue' in financials.index and 'Net Income' in financials.index:
                financial_data = financials.loc[['Total Revenue', 'Net Income']].tail(5)
                financial_data.columns = [str(year.year) for year in financial_data.columns]

                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=financial_data.columns,
                    y=financial_data.loc['Total Revenue'],
                    name='Total Revenue',
                    marker_color='rgba(70, 130, 180, 0.6)'  # Azul claro
                ))
                fig.add_trace(go.Bar(
                    x=financial_data.columns,
                    y=financial_data.loc['Net Income'],
                    name='Net Income',
                    marker_color='rgba(25, 25, 112, 0.6)'  # Azul marino
                ))

                fig.update_layout(
                    title='INGRESOS Y UTILIDAD NETA',
                    xaxis_tickmode='array',
                    xaxis_tickvals=financial_data.columns,
                    xaxis_ticktext=[str(year) for year in financial_data.columns],
                    yaxis=dict(
                        title='Amount ($)',
                        tickprefix='$',
                        ticks='outside',
                        tickformat=',.0f'
                    ),
                    barmode='group',
                    legend_title_text='Metric'
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write("Financial data for Total Revenue and/or Net Income is not available.")


            # Free Cash Flow
            cash_flow = company.cashflow
            if 'Free Cash Flow' in cash_flow.index:
                cash_flow_data = cash_flow.loc['Free Cash Flow'].tail(5)
                years = [str(year.year) for year in cash_flow.columns[-5:]]

                fig = go.Figure()

                fig.add_trace(go.Scatter(
                    x=years,
                    y=cash_flow_data,
                    fill='tozeroy',  # Rellena el área debajo de la línea
                    mode='lines+markers',
                    line=dict(color='rgba(0, 191, 255, 0.8)', width=3),  # Línea azul brillante
                    marker=dict(size=8, color='rgba(0, 191, 255, 0.8)'),
                    name='Free Cash Flow'
                ))

                fig.update_layout(
                    title='FLUJO DE EFECTIVO',
                    xaxis=dict(
                        title='',
                        tickmode='array',
                        tickvals=years,
                    ),
                    yaxis=dict(
                        title='Amount ($)',
                        tickprefix='$',
                        ticks='outside',
                        tickformat=',.0f'
                    ),
                    legend_title_text='Metric',
                    template='plotly_white'
                )

                st.plotly_chart(fig, use_container_width=True)
            else:
                st.write(f"Free Cash Flow data for {ticker} is not available.")


        except Exception as e:
            st.warning(f"Error al cargar los datos para {ticker}. Verifique el ticker e intente nuevamente. Detalles: {str(e)}")

                     
# SECTOR DASHBOARD
with tabs[1]:
    # Configuración inicial
    FinViz_Structure = {
        'Overview': '111',
        'Valuation': '121',
        'Financial': '161',
        'Ownership': '131',
        'Performance': '141',
        'Technical': '171'
    }

    sectores_disponibles = {
        'Any': '',
        'Basic Materials': 'sec_basicmaterials',
        'Communication Services': 'sec_communicationservices',
        'Consumer Cyclical': 'sec_consumercyclical',
        'Consumer Defensive': 'sec_consumerdefensive',
        'Energy': 'sec_energy',
        'Financial': 'sec_financial',
        'Healthcare': 'sec_healthcare',
        'Industrials': 'sec_industrials',
        'Real Estate': 'sec_realestate',
        'Technology': 'sec_technology',
        'Utilities': 'sec_utilities'
    }

    optionable = {
        'Any': '',
        'Optionable': 'sh_opt_option'
    }

    End_Point_1 = "https://elite.finviz.com/export.ashx?v="

    # Filtro del índice S&P 500
    index_filter = 'idx_sp500'


    st.markdown("# Sector Dashboard :earth_americas:")
    st.markdown(
    """
    <div style="
        color: #003366;
        font-size: 16px;
        text-align: justify;
        margin-bottom: 20px;">
        En esta sección, puedes explorar datos detallados de un sector específico seleccionando el sector, el estado de opciones y la categoría. La aplicación descargará automáticamente información desde Finviz, permitiéndote elegir una acción y analizar sus indicadores clave. Además, podrás visualizar un treemap interactivo que muestra el market cap del sector, ayudándote a comprender mejor su composición y desempeño. Todo está diseñado para facilitar tu análisis de mercado de manera clara y eficiente.
    </div>
    """,
    unsafe_allow_html=True
    )

    st.markdown("### Selecciona las siguientes categorías")
    
    # Selector de sector
    selected_sector = st.selectbox("Sector", list(sectores_disponibles.keys()))

    # Selector de opción entre "Optionable" o "Any"
    selected_optionable = st.selectbox("Optionable Status", list(optionable.keys()))

    # Selección de categoría y visualización de datos
    selected_category = st.selectbox("Category", list(FinViz_Structure.keys()))

    # Descarga de datos
    if st.button("Download Data"):
        st.write("Wait a moment...:clock3:")

        downloaded_successfully = True  # Inicializar la variable

        # Construir la URL con los filtros seleccionados
        value = FinViz_Structure[selected_category]
        sector_filter = sectores_disponibles[selected_sector] if selected_sector != 'Any' else ''
        optionable_filter = optionable[selected_optionable]

        filters = [index_filter]  # Incluir el filtro del índice S&P 500 por defecto
        if sector_filter:
            filters.append(sector_filter)
        if optionable_filter:
            filters.append(optionable_filter)

        filters_str = ','.join(filters) if filters else ''

        token1 = "fc4d1056-21d9-42b0-9dd9-4c947e694cfe"
        url = f"{End_Point_1}{value}&f={filters_str}&auth={token1}"

        response = requests.get(url)
        if response.status_code == 200:
            filename = f"{selected_category}.csv"
            with open(filename, "wb") as file:
                file.write(response.content)
            st.success(f"The data for the {selected_sector} sector (S&P 500) has been downloaded successfully")
        else:
            downloaded_successfully = False  # Marcar como falso si la descarga falla
            st.error("Failed to download data. Please try again.")

        time.sleep(2)  # Pausa para evitar limitaciones de la API

        if downloaded_successfully:
            st.session_state['last_downloaded_sector'] = selected_sector

    # Mostrar datos si el sector coincide, usamos st.session_state.get
    if selected_category and (selected_sector == st.session_state.get('last_downloaded_sector', '')):
        filename = f"{selected_category}.csv"
        
        if os.path.exists(filename):
            data = pd.read_csv(filename, index_col='No.')
        
            st.markdown("---")
    
        # Mostrar métricas según el ticker seleccionado
        selected_ticker = st.selectbox("Select Ticker", data['Ticker'].unique())
        selected_ticker_data = data[data['Ticker'] == selected_ticker]

        if selected_ticker_data.empty:
            st.warning("No data available for the selected ticker.")
        else:

            # Configurar la cuadrícula para el dashboard
            col1, col2, col3 = st.columns(3)
            # Mostrar las métricas específicas para cada categoría
            if selected_category == 'Overview':
                
                col1.metric("Market Cap", value=f"${selected_ticker_data['Market Cap'].iloc[0]:,.2f}")
                col2.metric("Price", value=f"${selected_ticker_data['Price'].iloc[0]:,.2f}")
                col3.metric("P/E Ratio", value=selected_ticker_data['P/E'].iloc[0])

                st.markdown("---")

            elif selected_category == 'Valuation':
                col1.metric("Market Cap", value=f"${selected_ticker_data['Market Cap'].iloc[0]:,.2f}")
                col2.metric("Price", value=f"${selected_ticker_data['Price'].iloc[0]:,.2f}")
                col3.metric("Volume", value=f"{selected_ticker_data['Volume'].iloc[0]:,.0f}")
                st.markdown("---")
                col1.metric("P/E Ratio", value=selected_ticker_data['P/E'].iloc[0])
                col2.metric("Forward P/E", value=selected_ticker_data['Forward P/E'].iloc[0])
                col3.metric("PEG", value=selected_ticker_data['PEG'].iloc[0])

            elif selected_category == 'Financial':
                col1.metric("Dividend Yield", value=selected_ticker_data['Dividend Yield'].iloc[0])
                col2.metric("Operating Margin", value=selected_ticker_data['Operating Margin'].iloc[0])
                col3.metric("Profit Margin", value=selected_ticker_data['Profit Margin'].iloc[0])
                st.markdown("---")
                col1.metric("ROA", value=selected_ticker_data['Return on Assets'].iloc[0])
                col2.metric("ROE", value=selected_ticker_data['Return on Equity'].iloc[0])
                col3.metric("ROI", value=selected_ticker_data['Return on Investment'].iloc[0])

            elif selected_category == 'Ownership':
                col1.metric("Float Short", value=selected_ticker_data['Short Float'].iloc[0])
                col2.metric("Insider Ownership", value=selected_ticker_data['Insider Ownership'].iloc[0])
                col3.metric("Inst Ownership", value=selected_ticker_data['Institutional Ownership'].iloc[0])
                st.markdown("---")

            elif selected_category == 'Performance':
                col1.metric("Performance (Week)", value=selected_ticker_data['Performance (Week)'].iloc[0])
                col2.metric("Performance (Month)", value=selected_ticker_data['Performance (Month)'].iloc[0])
                col3.metric("Performance (Quarter)", value=selected_ticker_data['Performance (Quarter)'].iloc[0])
                st.markdown("---")
                col1.metric("Performance (Year)", value=selected_ticker_data['Performance (Year)'].iloc[0])
                col2.metric("Performance (YTD)", value=selected_ticker_data['Performance (YTD)'].iloc[0])
                col3.metric("Volatility (M)", value=selected_ticker_data['Volatility (Month)'].iloc[0])


            elif selected_category == 'Technical':
                col1.metric("Beta", value=selected_ticker_data['Beta'].iloc[0])
                col2.metric("ATR", value=selected_ticker_data['Average True Range'].iloc[0])
                col3.metric("SMA200", value=selected_ticker_data['200-Day Simple Moving Average'].iloc[0])


        # TREEMAP MARKET CAP
        # Verifica si 'data' está en el espacio de nombres locales y tiene la columna 'Market Cap'
        if 'data' in locals() and 'Market Cap' in data.columns:
            # Condiciones para mostrar el treemap
            if selected_category in ['Overview', 'Valuation', 'Financial', 'Ownership']:
                st.markdown(f"""<h3 style='color: #003366;'>MARKET CAP: {selected_sector} sector</h3>""", unsafe_allow_html=True)

                
                # Crear el gráfico de treemap
                fig = px.treemap(data, path=[px.Constant(f"{selected_sector}"), 'Ticker'], values='Market Cap',
                                color='Market Cap', hover_data=['Ticker'],
                                color_continuous_scale='RdBu', title='')
                st.plotly_chart(fig, use_container_width=True)
        else:
            # Condiciones para no mostrar nada si las categorías son 'Performance' o 'Technical'
            if selected_category not in ['Performance', 'Technical']:
                st.write("")

# COMPANY NEWS
with tabs[2]:

    token2 = "16c994a439224ccaa2cf8b2753dced0f"

    st.markdown("# Financial News:newspaper:")

    st.markdown("""
    <div style="
            color: #003366;
            font-size: 16px;
            text-align: justify;
            margin-bottom: 20px;">
            En esta sección, puedes buscar las noticias más recientes relacionadas con cualquier empresa que cotice en bolsa. 
            Solo ingresa el ticker de la acción y obtendrás información actualizada para mantenerte al día sobre los eventos y 
            desarrollos clave que podrían impactar tus decisiones de inversión.
        </div>
        """,
        unsafe_allow_html=True
    )

    ticker = st.text_input("Enter a stock ticker (e.g., AAPL):", key='news_ticker')
    
    if ticker:
        # Asegurándose de que el query está codificado correctamente para URL
        search_query = quote(ticker)
        url = f'https://newsapi.org/v2/everything?q={search_query}&apiKey={token2}'

        response = requests.get(url)
        news = response.json()

        # Comprobar si la respuesta contiene artículos
        if response.status_code == 200 and 'articles' in news:
            articles = news['articles']
            if articles:
                st.subheader(f"Noticias recientes sobre {ticker}")
                for article in articles:
                    with st.container():
                        col1, col2 = st.columns([1, 4])  # Ajusta la proporción según sea necesario
                        with col1:
                            if article.get('urlToImage'):  # Verificar si hay una imagen disponible
                                st.image(article['urlToImage'], use_column_width=True)
                        with col2:
                            st.markdown(f"#### [{article['title']}]({article['url']})")
                            
                            # Formatting the date and time
                            published_at = article.get('publishedAt')
                            if published_at:
                                # Convert string to datetime
                                dt = datetime.datetime.fromisoformat(published_at[:-1])
                                # Determine the day suffix
                                day_suffix = "th" if 11 <= dt.day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(dt.day % 10, "th")
                                # Format date and time as "November 19th, 2024, 14:45"
                                formatted_date = dt.strftime(f"%B {dt.day}{day_suffix}, %Y, %H:%M")
                                st.write(formatted_date)
                            else:
                                st.write("Date not available.")
                            
                            st.write(article.get('description', 'Description not available.'))
            else:
                st.write("No news articles found for this ticker.")
        else:
            # Manejo de errores o problemas en la respuesta
            error_message = news.get('message', 'Failed to fetch news without a specific error message.')
            st.error(f"Error fetching news: {error_message}")

        url_sources = "https://newsapi.org/v2/sources?apiKey=" + token2
        response_sources = requests.get(url_sources)
        data_sources = response_sources.json()
        print(data_sources)

# SIMULADOR DE INVERSIONES
with tabs[3]:
    st.markdown("# Simulador de Inversiones 💰")

    st.markdown(
    """
    <div style="
        color: #003366;
        font-size: 16px;
        text-align: justify;
        margin-bottom: 20px;">
        En esta sección, puedes realizar un análisis de inversión ingresando el ticker de una acción, el monto a invertir y el plazo deseado. 
        Obtendrás datos analíticos clave, como el rendimiento esperado, el riesgo asociado y el valor futuro de tu inversión. 
        Todo está diseñado para brindarte información clara y útil que te ayude a tomar decisiones financieras informadas.
    </div>
    """,
    unsafe_allow_html=True
)


    # Entrada para el ticker
    ticker = st.text_input("Ingresa el ticker de la acción (por ejemplo, AAPL):", key='sim_ticker')

    # Entrada para la cantidad a invertir y plazo
    investment_amount = st.number_input("Monto a invertir ($):", min_value=100.0, step=100.0)
    investment_period = st.slider("Selecciona el plazo de inversión (en años):", min_value=1, max_value=10, value=5)

    # Tasa libre de riesgo (puedes ajustarla)
    risk_free_rate = 4.0  # Tasa libre de riesgo (en %)

    if ticker and investment_amount > 0:
        try:
            # Obtener datos históricos del activo
            company = yf.Ticker(ticker)
            historical_data = company.history(period="10y")
            historical_data['Return'] = historical_data['Close'].pct_change()

            # Filtrar los datos para los últimos años seleccionados
            days_to_consider = investment_period * 252  # Aproximadamente 252 días hábiles por año
            filtered_data = historical_data.tail(days_to_consider)

            if len(filtered_data) > 0:
                # Calcular el rendimiento promedio y el riesgo promedio para el período seleccionado
                period_return_avg = filtered_data['Return'].mean() * 252 * 100
                period_risk_avg = filtered_data['Return'].std() * (252 ** 0.5) * 100

                # Calcular el Sharpe Ratio
                sharpe_ratio = (period_return_avg - risk_free_rate) / period_risk_avg

                # Calcular el retorno y valor futuro
                annual_return_rate = period_return_avg / 100  # Convertir porcentaje a decimal
                future_value = investment_amount * ((1 + annual_return_rate) ** investment_period)

                # Mostrar resultados
                col1, col2, col3 = st.columns(3)

                col1.metric(label="Rendimiento Promedio", value=f"{period_return_avg:.2f}%", 
                            help=f"Promedio anualizado del rendimiento en los últimos {investment_period} años.")
                col2.metric(label="Volatilidad Promedio (Riesgo)", value=f"{period_risk_avg:.2f}%", 
                            help="Volatilidad anualizada basada en los datos históricos.")
                col3.metric(label="Ratio de Sharpe", value=f"{sharpe_ratio:.2f}", 
                            help="Medida ajustada por riesgo del rendimiento promedio.")

                # Mostrar el Valor Futuro como subtítulo centrado
                # Mostrar el Valor Futuro como un título destacado
                st.markdown(f"""
                    <h2 style='text-align: center; color: #FF5733; font-size: 28px; font-weight: bold;'>
                        Valor Futuro de la Inversión: ${future_value:,.2f}
                    </h2>
                """, unsafe_allow_html=True)


            else:
                st.error(f"No hay suficientes datos históricos para los últimos {investment_period} años.")
        except Exception as e:
            st.error(f"No se pudieron calcular los resultados para el ticker {ticker}. Error: {str(e)}")
