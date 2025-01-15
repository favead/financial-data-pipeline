import streamlit as st
import pandas as pd
import plotly.express as px

from financial_data.storages import initialize_storage


def load_metrics_to_dataframe():
    metrics_storage = initialize_storage("metric")
    metrics = metrics_storage.get_metrics_by_type("eda")
    df = pd.DataFrame(metrics)
    return df


def main():
    st.title("Document Analysis Dashboard")

    # Загружаем данные
    df = load_metrics_to_dataframe()

    # Боковая панель с фильтрами
    st.sidebar.header("Filters")

    # Фильтр по источникам
    sources = st.sidebar.multiselect(
        "Select Sources",
        options=df["source_name"].unique(),
        default=df["source_name"].unique(),
    )

    # Фильтр по датам
    min_date = df["timestamp"].min()
    max_date = df["timestamp"].max()
    date_range = st.sidebar.date_input(
        "Select Date Range",
        min_value=min_date,
        max_value=max_date,
        value=(min_date, max_date),
    )

    # Применяем фильтры
    mask = (
        df["source_name"].isin(sources)
        & (df["timestamp"].dt.date >= date_range[0])
        & (df["timestamp"].dt.date <= date_range[1])
    )
    filtered_df = df[mask]

    # Основные метрики
    st.header("Overview Statistics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Documents", len(filtered_df))
    with col2:
        st.metric("Average Tokens", int(filtered_df["tokens"].mean()))
    with col3:
        st.metric("Average Sentences", int(filtered_df["sentences"].mean()))

    # Графики
    st.header("Detailed Analysis")

    # График распределения токенов по источникам
    fig_tokens = px.box(
        filtered_df,
        x="source_name",
        y="tokens",
        title="Token Distribution by Source",
    )
    st.plotly_chart(fig_tokens)

    # График распределения предложений
    fig_sentences = px.histogram(
        filtered_df, x="sentences", title="Sentence Distribution", nbins=50
    )
    st.plotly_chart(fig_sentences)

    # Тепловая карта по времени
    daily_stats = (
        filtered_df.groupby(filtered_df["timestamp"].dt.date)["tokens"]
        .mean()
        .reset_index()
    )
    fig_heatmap = px.density_heatmap(
        daily_stats,
        x="timestamp",
        y="tokens",
        title="Average Tokens Over Time",
    )
    st.plotly_chart(fig_heatmap)

    # Таблица с наиболее частыми словами
    st.header("Most Common Words")
    if "most_common_words" in filtered_df.columns:
        words_df = pd.DataFrame(
            [
                word
                for words in filtered_df["most_common_words"]
                for word in words
            ],
            columns=["Word", "Count"],
        )
        words_summary = (
            words_df.groupby("Word")["Count"]
            .sum()
            .sort_values(ascending=False)
            .head(20)
        )
        fig_words = px.bar(words_summary, title="Top 20 Most Common Words")
        st.plotly_chart(fig_words)

    # Детальная таблица
    st.header("Detailed Data")
    st.dataframe(
        filtered_df.drop("most_common_words", axis=1, errors="ignore")
    )


if __name__ == "__main__":
    main()
