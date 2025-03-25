import streamlit as st
import pandas as pd
from openai import OpenAI
import json
from datetime import datetime
import os

def format_argentine_number(x):
    """Format number in Argentine style (comma as decimal, period as thousands)"""
    try:
        num = float(x)
        # Format with 2 decimal places and thousands separator
        return f"{num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return x

def format_argentine_currency(x):
    """Format currency in Argentine style"""
    try:
        num = float(x)
        # Format with 2 decimal places and thousands separator
        return f"${num:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except:
        return x

def prepare_sample_data(df):
    """Prepare sample data for JSON serialization"""
    sample_df = df.head(5).copy()
    
    # Convert datetime columns to string format
    for col in sample_df.columns:
        if pd.api.types.is_datetime64_any_dtype(sample_df[col]):
            sample_df[col] = sample_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    
    return sample_df.to_dict(orient='records')

def calculate_statistics(df):
    """Calculate relevant statistics from the data"""
    stats = {}
    
    # Daily statistics
    daily_stats = df.groupby(df['Fecha'].dt.date).agg({
        'Importe': ['sum', 'count'],
        'Volumen': 'sum'
    }).reset_index()
    daily_stats.columns = ['Fecha', 'Importe_Total', 'Cantidad_Despachos', 'Volumen_Total']
    
    stats['daily'] = {
        'promedio_importe': float(daily_stats['Importe_Total'].mean()),
        'promedio_despachos': float(daily_stats['Cantidad_Despachos'].mean()),
        'promedio_volumen': float(daily_stats['Volumen_Total'].mean()),
        'max_importe': {
            'fecha': daily_stats.loc[daily_stats['Importe_Total'].idxmax(), 'Fecha'].strftime('%Y-%m-%d'),
            'valor': float(daily_stats['Importe_Total'].max())
        }
    }
    
    # Hourly statistics
    hourly_stats = df.groupby(df['Fecha'].dt.hour).agg({
        'Importe': ['sum', 'count'],
        'Volumen': 'sum'
    }).reset_index()
    hourly_stats.columns = ['Hora', 'Importe_Total', 'Cantidad_Despachos', 'Volumen_Total']
    
    stats['hourly'] = {
        'hora_mas_activa': {
            'hora': int(hourly_stats.loc[hourly_stats['Cantidad_Despachos'].idxmax(), 'Hora']),
            'cantidad': float(hourly_stats['Cantidad_Despachos'].max())
        },
        'hora_mayor_importe': {
            'hora': int(hourly_stats.loc[hourly_stats['Importe_Total'].idxmax(), 'Hora']),
            'importe': float(hourly_stats['Importe_Total'].max())
        }
    }
    
    # Surtidor statistics
    surtidor_stats = df.groupby('Surtidor').agg({
        'Importe': ['sum', 'count'],
        'Volumen': 'sum'
    }).reset_index()
    surtidor_stats.columns = ['Surtidor', 'Importe_Total', 'Cantidad_Despachos', 'Volumen_Total']
    
    stats['surtidor'] = {
        'mas_activo': {
            'surtidor': str(surtidor_stats.loc[surtidor_stats['Cantidad_Despachos'].idxmax(), 'Surtidor']),
            'cantidad': float(surtidor_stats['Cantidad_Despachos'].max())
        },
        'mayor_importe': {
            'surtidor': str(surtidor_stats.loc[surtidor_stats['Importe_Total'].idxmax(), 'Surtidor']),
            'importe': float(surtidor_stats['Importe_Total'].max())
        }
    }
    
    # General statistics
    stats['general'] = {
        'total_despachos': len(df),
        'total_importe': float(df['Importe'].sum()),
        'total_volumen': float(df['Volumen'].sum()),
        'promedio_importe_despacho': float(df['Importe'].mean()),
        'promedio_volumen_despacho': float(df['Volumen'].mean())
    }
    
    return stats

def analyze_data_with_ai(df, question):
    """Use OpenAI to analyze the data based on the user's question"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return "Error: No se encontró la clave API de OpenAI. Por favor, configure la variable de entorno OPENAI_API_KEY."
    
    client = OpenAI(api_key=api_key)
    
    # Calculate statistics
    stats = calculate_statistics(df)
    
    # Get dataframe info with serializable data
    df_info = {
        "columns": list(df.columns),
        "dtypes": {col: str(df[col].dtype) for col in df.columns},
        "sample_data": prepare_sample_data(df),
        "total_rows": len(df),
        "date_range": {
            "start": df['Fecha'].min().strftime('%Y-%m-%d'),
            "end": df['Fecha'].max().strftime('%Y-%m-%d')
        },
        "statistics": stats
    }
    
    # Create the system message with context about the data
    system_message = f"""You are a data analyst expert in analyzing GNC (compressed natural gas) dispatch data.
The data contains the following columns: {', '.join(df_info['columns'])}
Date range: from {df_info['date_range']['start']} to {df_info['date_range']['end']}

Key Statistics:
- Total despachos: {stats['general']['total_despachos']:,}
- Total importe: ${stats['general']['total_importe']:,.2f}
- Total volumen: {stats['general']['total_volumen']:,.2f}
- Promedio importe por despacho: ${stats['general']['promedio_importe_despacho']:,.2f}
- Hora más activa: {stats['hourly']['hora_mas_activa']['hora']:02d}:00 ({stats['hourly']['hora_mas_activa']['cantidad']:,.0f} despachos)
- Surtidor más activo: {stats['surtidor']['mas_activo']['surtidor']} ({stats['surtidor']['mas_activo']['cantidad']:,.0f} despachos)

Sample data: {json.dumps(df_info['sample_data'], indent=2, ensure_ascii=False)}

Detailed statistics: {json.dumps(stats, indent=2, ensure_ascii=False)}

Provide clear, concise answers in Spanish with an Argentine style.
If calculations are needed, use the provided statistics.
If relevant, include total amounts in Argentine Peso format ($ with comma for decimals and period for thousands).
"""

    # Create the conversation
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": question}
    ]

    # Get the response from OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=messages,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error al analizar los datos: {str(e)}"

def render():   
    try:
        # Read the CSV file
        df = pd.read_csv('gnc.csv')
        
        # Convert Fecha to datetime with dayfirst=True for DD/MM/YYYY format
        df['Fecha'] = pd.to_datetime(df['Fecha'], dayfirst=True)
        
        # Convert Importe to numeric, removing currency symbols and thousands separators
        df['Importe'] = pd.to_numeric(df['Importe'].str.replace('[\$,]', '', regex=True), errors='coerce')
        
        # Add filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Date range filter
            min_date = df['Fecha'].min()
            max_date = df['Fecha'].max()
            date_range = st.date_input(
                "Período",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
        with col2:
            # Surtidor filter
            surtidores = sorted(df['Surtidor'].unique())
            surtidor_selected = st.multiselect(
                "Bomba",
                options=surtidores,
                default=surtidores
            )
        
        # Apply filters
        if len(date_range) == 2:
            mask = (df['Fecha'].dt.date >= date_range[0]) & (df['Fecha'].dt.date <= date_range[1])
            df = df[mask]
        
        if surtidor_selected:
            df = df[df['Surtidor'].isin(surtidor_selected)]

        # Add AI Analysis section
        st.write("### Análisis de Datos")
        st.write("Hacé preguntas sobre los datos y obtené respuestas detalladas:")
        
        # Add example questions
        st.caption("Ejemplos de preguntas:")
        st.caption("- ¿Cuál es el promedio de ventas por día?")
        st.caption("- ¿Cuál es la bomba que más despachos realizó?")
        st.caption("- ¿Cuál es el horario con mayor actividad?")
        st.caption("- ¿Cuál fue el día con mayor facturación?")
        st.caption("- ¿Cuál es el volumen promedio por despacho?")
        
        # Add text input for questions
        user_question = st.text_input("Tu pregunta:", placeholder="Escribí tu pregunta aquí...")
        
        if user_question:
            with st.spinner('Analizando los datos...'):
                answer = analyze_data_with_ai(df, user_question)
                st.write("#### Respuesta:")
                st.write(answer)
                st.divider()

        # Create a copy of the DataFrame for display
        display_df = df.copy()
        
        # Select columns to display (excluding 'Cliente' and 'Producto')
        columns_to_display = [col for col in display_df.columns if col not in ['Cliente', 'Producto']]
        display_df = display_df[columns_to_display]
        
        # Format the Fecha column to show only the date
        if 'Fecha' in display_df.columns:
            display_df['Fecha'] = display_df['Fecha'].dt.strftime('%d/%m/%Y')
        
        # Format numeric columns
        if 'Volumen' in display_df.columns:
            display_df['Volumen'] = display_df['Volumen'].apply(format_argentine_number)
        
        if 'Importe' in display_df.columns:
            display_df['Importe'] = display_df['Importe'].apply(format_argentine_currency)
        
        if 'PPU' in display_df.columns:
            display_df['PPU'] = display_df['PPU'].apply(format_argentine_number)
        
        # Display total records
        st.write(f"Cantidad de registros: {len(df)}")
        
        # Add pagination controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            page_size = st.selectbox(
                "Registros por página",
                options=[10, 25, 50, 100],
                index=1  # Default to 25
            )
        
        # Calculate pagination
        total_pages = (len(display_df) + page_size - 1) // page_size
        current_page = st.session_state.get('current_page', 1)
        
        with col2:
            st.write(f"Página {current_page} de {total_pages}")
        
        with col3:
            if current_page > 1:
                if st.button("← Anterior"):
                    st.session_state.current_page = current_page - 1
            if current_page < total_pages:
                if st.button("Siguiente →"):
                    st.session_state.current_page = current_page + 1
        
        # Slice the dataframe for the current page
        start_idx = (current_page - 1) * page_size
        end_idx = start_idx + page_size
        page_df = display_df.iloc[start_idx:end_idx]
        
        # Display the paginated dataframe
        st.dataframe(
            page_df,
            use_container_width=True,
            hide_index=True
        )
        
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}") 