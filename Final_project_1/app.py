'''
Web приложение на streamlit с использованием sqlite, pandas и plotly.express
которое позволяет анализировать и визуализировать исторические метеорологические данные.

Возможности:
- выбор одного ил более городов для анализа
- выбор диапазона дат
- выбор типа графиков

Отображает:
- таблицу с данными
- диаграммы распределения погодных показателей
- графики для сравнения природных показателей
- графики для прогнозирования
'''

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px

# Загрузка данных
DB_PATH = 'data/weather.db'
st.set_page_config(page_title='WeatherInsight', layout='wide')

@st.cache_data
def load_data():
	conn = sqlite3.connect(DB_PATH)
	df = pd.read_sql('SELECT * FROM weather ORDER BY date', conn)
	conn.close()
	return df

try:
    df = load_data()
except Exception as e:
    st.error(f'❌ Не удалось загрузить данные. Убедитесь, что база данных существует и доступна.')
    st.stop()

# Предобработка данных
def comfort_rating(row) -> int:
	'''
    Функция для расчета комфортности погоды    
    Параметры:
    row - строка датафрейма   
    Возвращает целое число (от 1 до 5)
    '''
	rating = 1
	if 22 < float(row['avg_temp']) < 26: rating += 2
	if 18 < float(row['avg_temp']) < 22 or 26 < float(row['avg_temp']) < 30: rating += 1
	if float(row['total_precip']) == 0: rating += 1
	if float(row['avg_wind']) < 6: rating += 1
	return rating

extended_data = df.copy()
extended_data['date'] = pd.to_datetime(extended_data['date']).dt.date
extended_data['temp_category'] = extended_data.apply(
    lambda row: 'холодно' if float(row['avg_temp']) <= 10 else ('умеренно' if 10 < float(row['avg_temp']) < 20 else 'тепло'), 
    axis=1
    )
extended_data['precipitation'] = extended_data.apply(
    lambda row: 'без осадков' if float(row['total_precip']) == 0 else ('небольшие' if 0 < float(row['total_precip']) < 20 else 'сильные'), 
    axis=1
    )
extended_data['comfort'] = extended_data.apply(comfort_rating, axis=1)

col1, col2, = st.columns(2)
with col1:
	st.title('WeatherInsight: Погодные тренды')
	st.subheader('📊 Общая статистика')
	total_records = len(df)
	unique_cities = df['city'].nunique()
	st.write(f'Всего записей: {total_records}')
	st.write(f'Уникальных городов: {unique_cities}')
 
	# Выбор города
	cities = sorted(list(extended_data['city'].unique()))
	checkbox_values = []
	for city in cities:
		checkbox_key = f'checkbox_{city}'
		checkbox_value = st.checkbox(city, value=True)
		checkbox_values.append(checkbox_value)
	selected_city = [elem for elem, flag in zip(cities, checkbox_values) if flag]
	filtered_data = extended_data[extended_data['city'].isin(selected_city)]

	# Выбор диапазона дат
	start_date = extended_data['date'].min()
	end_date = extended_data['date'].max()

	selected_date = st.date_input(
	    'Выберите диапазон дат',
	    min_value=start_date,
	    max_value=end_date,
	    value=(start_date, end_date),
	    format='MM.DD.YYYY'
	)
	if len(selected_date) == 2: filtered_data = filtered_data[filtered_data['date'].between(*selected_date)]

	# Выбор типа графика
	graph_type = ['Диаграммы распределения', 'Сравнение погодных показателей', 'Временные ряды и прогнозирование']
	selected_graph = st.selectbox('Выберите тип графиков', graph_type)

	# Отображение данных
	page = st.session_state.setdefault('page', 1)
	per_page = 10
	total_pages = (len(filtered_data) + per_page - 1) // per_page
	if page > total_pages or (page == 0 and total_pages > 0): 
		setattr(st.session_state, 'page', 1)
		page = 1
	col1_1, col1_2, col1_3 = st.columns(3)
	col1_1.container(horizontal_alignment='center').button('←', on_click=lambda: setattr(st.session_state, 'page', max(1, page-1)))
	col1_2.container(horizontal_alignment='center').text(f'{page}/{total_pages}')
	col1_3.container(horizontal_alignment='center').button('→', on_click=lambda: setattr(st.session_state, 'page', min(total_pages, page+1)))
	start = (st.session_state.page - 1) * per_page
	st.dataframe(filtered_data.iloc[start:start+per_page], column_config={'comfort': st.column_config.ProgressColumn(min_value=1, max_value=5, format='')})


with col2:
    # Отображение графиков
	if selected_graph == 'Диаграммы распределения':
		fig = px.box(data_frame=filtered_data, 
               		x='avg_temp', 
                 	color='city', 
                  	title='Коробчатая диаграмма распределения температур по городам')
		st.plotly_chart(fig)
		fig = px.box(data_frame=filtered_data, 
               		x='total_precip', 
                 	color='city', 
                  	title='Коробчатая диаграмма распределения количества осадков по городам')
		st.plotly_chart(fig)
		fig = px.box(data_frame=filtered_data, 
               		x='avg_wind', 
                 	color='city', 
                  	title='Коробчатая диаграмма распределения силы ветра по городам')
		st.plotly_chart(fig)
	if selected_graph == 'Сравнение погодных показателей':
		fig = px.line(data_frame=filtered_data, 
                	x='date', y='avg_temp', 
                 	color='city',
                    title='Cравнение изменения температуры')
		st.plotly_chart(fig)
		fig = px.line(data_frame=filtered_data, 
                	x='date', y='total_precip', 
                 	color='city',
                    title='Cравнение изменения количества осадков')
		st.plotly_chart(fig)
		fig = px.line(data_frame=filtered_data, 
                	x='date', y='avg_wind', 
                 	color='city',
                    title='Cравнение изменения скорости ветра')
		st.plotly_chart(fig)
	if selected_graph == 'Временные ряды и прогнозирование':
		fig = px.scatter(data_frame=filtered_data, 
                	y='avg_temp',
					color='city',
					trendline='rolling', trendline_options=dict(window=7),
                    title='Прогноз температуры')
		st.plotly_chart(fig)
		fig = px.scatter(data_frame=filtered_data, 
                	y='total_precip',
					color='city',
					trendline='rolling', trendline_options=dict(window=7),
                    title='Прогноз количества осадков')
		st.plotly_chart(fig)
		fig = px.scatter(data_frame=filtered_data, 
                	y='avg_wind',
					color='city',
					trendline='rolling', trendline_options=dict(window=7),
                    title='Прогноз скорости ветра')
		st.plotly_chart(fig)