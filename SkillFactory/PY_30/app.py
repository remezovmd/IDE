import streamlit as st
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

def calculate(sum: int, rate: float, loan_term: int, type: str, date: datetime) -> list:
    """
    Расчет графика платежей
    
    Параметры:
    sum - сумма кредита
    rate - годовая процентная ставка (в процентах, например 12)
    loan_term - срок кредита в месяцах
    type - тип платежей (аннуитетный или дифференциальный)
    date - дата первого платежа (datetime или None)
    
    Возвращает список [Ежемесячный платеж, Общая сумму займа, DataFrame с графиком платежей]
    """
    payment_schedule = []
    p = rate / 12 / 100
    balance = sum
    if type == 'аннуитетный':
        payment = round(sum * (p + (p / ((1 + p) ** loan_term - 1))))
    if type == 'дифференциальный':
        debt_portion = sum / loan_term
        
    for month in range(loan_term):
        if type == 'аннуитетный':
            interest_portion = balance * p
            debt_portion = payment - interest_portion
        if type == 'дифференциальный':
            interest_portion = balance * p
            payment = debt_portion + interest_portion
            
        payment_schedule_str = {}
        payment_schedule_str["Дата платежа"] = date + relativedelta(months=month) 
        payment_schedule_str["Остаток долга"] = round(balance, 2)
        payment_schedule_str["Платеж"] = round(payment, 2)
        payment_schedule_str["Процентная часть"] = round(interest_portion, 2)
        payment_schedule_str["Долговая часть"] = round(debt_portion, 2)
        balance -= debt_portion 
        payment_schedule_str["Долг на конец месяца"] = max(0, round(balance, 2))
        payment_schedule.append(payment_schedule_str)

    payment_schedule[-1]['Долговая часть'] = round(payment_schedule[-1]['Долговая часть'] + payment_schedule[-1]['Долг на конец месяца'], 2)
    payment_schedule[-1]['Платеж'] = round(payment_schedule[-1]['Долговая часть'] + payment_schedule[-1]['Процентная часть'], 2)
    payment_schedule[-1]['Долг на конец месяца'] = 0

    payment_schedule_table = pd.DataFrame(payment_schedule)
    all_sum = payment_schedule_table["Платеж"].sum()
    
    return [payment, all_sum, payment_schedule_table]

st.title('Кредитный калькулятор')
col1, col2 = st.columns(2, gap="medium")
col3 = st.container()
with col1:
    sum = st.number_input('Сумма кредита', min_value=10000, max_value=100000000, step=1000, value=10000)
    rate = st.number_input('Ставка', min_value=0.0, max_value=50.0, step=1.0, value=20.0)
    loan_term = st.select_slider('Срок кредита', list(map(lambda x: str(x) + ' месяц', range(1, 12))) + list(map(lambda x: str(x) + ' лет', range(1, 31))))
    # Вычисляем срок кредита в месяцах
    loan_term_month = loan_term.split(' ')
    loan_term_month = int(loan_term_month[0]) if loan_term_month[1] == 'месяц' else int(loan_term_month[0]) * 12
    
    type = st.radio('Тип платежа', ['аннуитетный', 'дифференциальный'], horizontal=True)
    date = st.date_input("Дата первого платежа", format = "DD.MM.YYYY", value = datetime.date.today(), min_value = datetime.date.today())
    run = st.button('Рассчитать', type='primary')

if run:
    result = calculate(sum, rate, loan_term_month, type, date)
    with col2:
        st.subheader('Результаты расчета')
        col2_1, col2_2 = st.columns([0.7, 0.3])
        with col2_1:
            if type == 'аннуитетный': st.text('Ежемесячный платеж')
            st.text('Cумма кредита')
            st.text('Общая сумма займа')
            st.text('Переплата')
        with col2_2:
            if type == 'аннуитетный': st.html(f'<b>{result[0]:,.2f}</b>'.replace(',', ' '))
            st.text(f'{sum:,.2f}'.replace(',', ' '))
            st.text(f'{result[1]:,.2f}'.replace(',', ' '))
            st.text(f'{result[1] - sum:,.2f}'.replace(',', ' '))
    with st.expander("Показать график платежей"):        
        st.dataframe(result[2], hide_index=True)