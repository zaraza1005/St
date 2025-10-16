import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Фінанси + Медіа + Репутація", layout="wide")

st.title("📊 Комплексний дашборд «Фінанси + Медіа + Репутація»")

st.markdown("""
Цей дашборд дозволяє:
- завантажити кілька CSV-файлів із даними про компанії (фінанси, медіа, публічний імідж);
- об’єднати їх у спільний DataFrame;
- розрахувати інтегральний рейтинг компаній;
- переглянути результати за вкладками.
""")

# === Завантаження файлів ===
st.sidebar.header("Завантаж CSV-файли")
fin_file = st.sidebar.file_uploader("Фінансові показники", type=["csv"])
med_file = st.sidebar.file_uploader("Медійні показники", type=["csv"])
rep_file = st.sidebar.file_uploader("Публічний імідж", type=["csv"])

# === Зчитування даних ===
def read_csv(file):
    if file is not None:
        return pd.read_csv(file)
    return pd.DataFrame()

fin_df = read_csv(fin_file)
med_df = read_csv(med_file)
rep_df = read_csv(rep_file)

if fin_df.empty and med_df.empty and rep_df.empty:
    st.info("⬆️ Завантаж хоча б один CSV-файл для початку роботи.")
    st.stop()

# === Об’єднання ===
dfs = [df for df in [fin_df, med_df, rep_df] if not df.empty]
df = dfs[0]
for next_df in dfs[1:]:
    df = pd.merge(df, next_df, on="company", how="outer")

st.subheader("Об’єднаний DataFrame")
st.dataframe(df)

# === Ваги показників ===
st.sidebar.header("Ваги для інтегрального рейтингу")
w_fin = st.sidebar.slider("Фінанси", 0.0, 1.0, 0.4)
w_med = st.sidebar.slider("Медіа", 0.0, 1.0, 0.3)
w_rep = st.sidebar.slider("Репутація", 0.0, 1.0, 0.3)

total = w_fin + w_med + w_rep
w_fin, w_med, w_rep = w_fin/total, w_med/total, w_rep/total

# === Розрахунок інтегрального рейтингу ===
df_calc = df.copy()

# допоміжна функція для нормалізації
def norm(series):
    if series.isna().all():
        return pd.Series(0.5, index=series.index)
    if series.max() == series.min():
        return pd.Series(0.5, index=series.index)
    return (series - series.min()) / (series.max() - series.min())

# нормалізація окремих груп
fin_cols = [c for c in df.columns if "revenue" in c or "profit" in c or "growth" in c]
med_cols = [c for c in df.columns if "mention" in c or "sentiment" in c or "positive" in c]
rep_cols = [c for c in df.columns if "survey" in c or "nps" in c or "controvers" in c]

df_calc["fin_score"] = norm(df[fin_cols].select_dtypes("number").mean(axis=1))
df_calc["med_score"] = norm(df[med_cols].select_dtypes("number").mean(axis=1))
df_calc["rep_score"] = norm(df[rep_cols].select_dtypes("number").mean(axis=1))

df_calc["integral"] = (
    df_calc["fin_score"] * w_fin +
    df_calc["med_score"] * w_med +
    df_calc["rep_score"] * w_rep
)
df_calc["integral_100"] = 100 * norm(df_calc["integral"])

df_final = df_calc[["company", "fin_score", "med_score", "rep_score", "integral_100"]]\
    .sort_values("integral_100", ascending=False)

st.subheader("🏆 Інтегральний рейтинг компаній")
st.dataframe(df_final)

# === Вкладки ===
tab1, tab2, tab3 = st.tabs(["Фінанси", "Медіа", "Публічний імідж"])

with tab1:
    st.subheader("Фінансові показники")
    if not fin_df.empty:
        st.dataframe(fin_df)
    else:
        st.warning("Не завантажено фінансовий CSV.")

with tab2:
    st.subheader("Медійні показники")
    if not med_df.empty:
        st.dataframe(med_df)
    else:
        st.warning("Не завантажено медійний CSV.")

with tab3:
    st.subheader("Показники публічного іміджу")
    if not rep_df.empty:
        st.dataframe(rep_df)
    else:
        st.warning("Не завантажено CSV публічного іміджу.")

st.success("✅ Дашборд готовий до використання!")
