import io
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Анализ CSV",
    page_icon="📊",
    layout="wide",
)

def _parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    '''Парсинг дат'''
    date_keywords = ["date", "time", "дата", "время", "timestamp", "dt", "год", "year", "month"]
    for col in df.columns:
        col_lower = col.lower()
        has_date_keyword = any(kw in col_lower for kw in date_keywords)
        if pd.api.types.is_string_dtype(df[col]) or df[col].dtype == object:
            threshold = 0.5 if has_date_keyword else 0.85
            try:
                parsed = pd.to_datetime(df[col], errors="coerce")
                if parsed.notna().mean() >= threshold:
                    df[col] = parsed
            except Exception:
                pass
    return df

@st.cache_data(show_spinner="Загружаем файл…")
def load_csv(file_bytes: bytes, filename: str) -> pd.DataFrame:
    '''Загружает файл CSV с учетом кодировки и разделителя'''
    encodings = ["utf-8", "cp1251"]
    separators = ["\t", ";", ",", "|"]

    for enc in encodings:
        for sep in separators:
            try:
                df = pd.read_csv(
                    io.BytesIO(file_bytes),
                    encoding=enc,
                    sep=sep,
                    engine="python",
                    on_bad_lines="warn",
                )
                if df.shape[0] > 0 and df.shape[1] >= 2:
                    df = _parse_dates(df)
                    return df
            except Exception as e:
                continue

    raise ValueError(f"Не удалось прочитать файл '{filename}'. Ошибка: {e}")

@st.cache_data(show_spinner=False)
def compute_statistics(series: pd.Series) -> dict:
    '''Статистический анализ столбца'''
    clean = series.dropna()
    return {
        "Среднее":         round(float(clean.mean()),   4),
        "Медиана":         round(float(clean.median()), 4),
        "Стд. отклонение": round(float(clean.std()),    4),
    }

def get_column_types(df: pd.DataFrame) -> dict:
    '''Определение типа столбца'''
    numeric_cols     = df.select_dtypes(include=[np.number]).columns.tolist()
    datetime_cols    = df.select_dtypes(include=["datetime", "datetimetz"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number, "datetime", "datetimetz"]).columns.tolist()
    return {"numeric": numeric_cols, "datetime": datetime_cols, "categorical": categorical_cols}


# Инициация сессии
for _key, _val in [("df", None), ("filename", None), ("last_fig", None)]:
    if _key not in st.session_state:
        st.session_state[_key] = _val

# Отображение страницы
st.markdown('<h1>Анализ CSV файла</h1>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Загрузить CSV-файл", type=["csv"])

if uploaded_file is None:
    if st.session_state["df"] is not None:
        st.session_state["df"] = None
        st.session_state["filename"] = None
        st.session_state["last_fig"] = None
        load_csv.clear()
        st.rerun()
else:
    if st.session_state["filename"] != uploaded_file.name:
        st.session_state["filename"] = uploaded_file.name
        st.session_state["df"] = None
        st.session_state["last_fig"] = None
        load_csv.clear()
    try:
        df_loaded = load_csv(uploaded_file.getvalue(), uploaded_file.name)
        st.session_state["df"] = df_loaded
        st.caption(f"Строк: {df_loaded.shape[0]:,} | Столбцов: {df_loaded.shape[1]}")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"Неожиданная ошибка: {e}")


df: pd.DataFrame | None = st.session_state.get("df")
if df is None: st.stop()

col_types = get_column_types(df)
numeric_cols = col_types["numeric"]
datetime_cols = col_types["datetime"]
categorical_cols = col_types["categorical"]
all_cols = df.columns.tolist()

tab_data, tab_charts = st.tabs(["📋 Данные", "📉 Графики"])

with tab_data:
    st.markdown('<h3>Статистический анализ</h3>', unsafe_allow_html=True)

    if not numeric_cols:
        st.warning("В загруженном файле не найдено числовых столбцов.")
    else:
        stat_col = st.selectbox("Выберите столбец", options=numeric_cols, key="stat_col")

        if stat_col:
            stats = compute_statistics(df[stat_col])

            c1, c2, c3 = st.columns(3)
            for col_ui, label, key in [
                (c1, "Среднее",         "Среднее"),
                (c2, "Медиана",         "Медиана"),
                (c3, "Стд. отклонение", "Стд. отклонение"),
            ]:
                with col_ui:
                    st.metric(label, stats[key])
    
    st.markdown('<h3>Таблица с данными</h3>', unsafe_allow_html=True)
    selected_cols = st.multiselect(
        "Выберите столбцы для отображения (по умолчанию — все)",
        options=all_cols, default=all_cols, key="table_cols",
    )
    if not selected_cols:
        st.warning("Выберите хотя бы один столбец.")
    else:
        st.dataframe(df[selected_cols], use_container_width=True, height=420)


with tab_charts:
    st.markdown('<h3>Построение графика</h3>', unsafe_allow_html=True)

    if not numeric_cols:
        st.warning("Для построения графика необходим хотя бы один числовой столбец (ось Y).")
    else:
        col_left, col_right = st.columns([1, 3])

        with col_left:
            chart_type = st.radio(
                "Тип графика",
                options=["Линейный", "Диаграмма рассеяния"],
                key="chart_type",
            )

            x_col = st.selectbox("Ось X", options=all_cols, key="x_col")

            y_cols = st.multiselect(
                "Ось Y (только числовые)",
                options=numeric_cols,
                default=[numeric_cols[0]] if numeric_cols else [],
                key="y_cols",
            )

            color_col = st.selectbox(
                "Раскраска по столбцу (опционально)",
                options=["—"] + categorical_cols,
                key="color_col",
            )
            color_col = None if color_col == "—" else color_col

            build_btn = st.button("Построить график", type="primary", use_container_width=True)

        with col_right:
            if build_btn:
                if not y_cols:
                    st.warning("Выберите хотя бы один числовой столбец для оси Y.")
                else:
                    try:
                        # Собираем нужные столбцы, убираем NaN по X
                        plot_cols = list({x_col} | set(y_cols) | ({color_col} if color_col else set()))
                        plot_df   = df[plot_cols].dropna(subset=[x_col])

                        is_x_date    = pd.api.types.is_datetime64_any_dtype(df[x_col])
                        is_x_numeric = pd.api.types.is_numeric_dtype(df[x_col])
                        is_x_string  = (
                            pd.api.types.is_string_dtype(df[x_col])
                            or df[x_col].dtype == object
                        )

                        # Для линейного сортируем по числовому/датовому X
                        if chart_type == "Линейный" and (is_x_date or is_x_numeric):
                            plot_df = plot_df.sort_values(by=x_col)

                        def _melt(d: pd.DataFrame) -> pd.DataFrame:
                            """Переводим несколько Y в длинный формат для plotly."""
                            id_cols = [x_col] + ([color_col] if color_col else [])
                            return d.melt(id_vars=id_cols, value_vars=y_cols,
                                          var_name="Показатель", value_name="Значение")

                        if chart_type == "Линейный":
                            if len(y_cols) == 1:
                                fig = px.line(plot_df, x=x_col, y=y_cols[0], color=color_col,
                                              title=f"Линейный: {y_cols[0]} от {x_col}",
                                              labels={x_col: x_col, y_cols[0]: y_cols[0]},
                                              markers=True)
                            else:
                                fig = px.line(_melt(plot_df), x=x_col, y="Значение",
                                              color="Показатель",
                                              title=f"Линейный: {', '.join(y_cols)} от {x_col}",
                                              markers=True)
                        else:
                            if len(y_cols) == 1:
                                fig = px.scatter(
                                    plot_df, x=x_col, y=y_cols[0], color=color_col,
                                    title=f"Рассеяние: {y_cols[0]} от {x_col}",
                                    labels={x_col: x_col, y_cols[0]: y_cols[0]},
                                    opacity=0.7,
                                )
                            else:
                                fig = px.scatter(
                                    _melt(plot_df), x=x_col, y="Значение",
                                    color="Показатель",
                                    title=f"Рассеяние: {', '.join(y_cols)} от {x_col}",
                                    opacity=0.7,
                                )

                        fig.update_layout(
                            xaxis_title=x_col,
                            yaxis_title=", ".join(y_cols),
                            hovermode="x unified" if chart_type == "Линейный" else "closest",
                            legend_title_text="",
                            height=500,
                        )
                        if is_x_date:
                            fig.update_xaxes(tickformat="%Y-%m-%d", tickangle=30)
                        # Поворачиваем подписи если категорий много
                        if is_x_string and df[x_col].nunique() > 10:
                            fig.update_xaxes(tickangle=45)

                        st.session_state["last_fig"] = fig
                        st.plotly_chart(fig, use_container_width=True)

                    except Exception as e:
                        st.error(f"Ошибка при построении графика: {e}")

            elif st.session_state.get("last_fig") is not None:
                st.plotly_chart(st.session_state["last_fig"], use_container_width=True)
            else:
                st.info('Выберите столбцы и нажмите «Построить график».')

    st.markdown('<h3>График распределения</h3>', unsafe_allow_html=True)

    if not numeric_cols:
        st.warning("Нет числовых столбцов для анализа распределения.")
    else:
        dist_col = st.selectbox("Выберите столбец", options=numeric_cols, key="dist_col")
        if dist_col:
            bins = st.slider("Детализация гистограммы (bins)", 5, 100, 30, key="hist_bins")
            fig_dist = px.histogram(df, x=dist_col, nbins=bins,
                                    title=f"Гистограмма: {dist_col}",
                                    color_discrete_sequence=["#1f77b4"], marginal="rug")
            fig_dist.update_layout(xaxis_title=dist_col, yaxis_title="Частота")
            st.plotly_chart(fig_dist, use_container_width=True)