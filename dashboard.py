import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv")
    return df

df = load_data()

st.set_page_config(page_title="Student Performance Dashboard", layout="wide")

# ---------------------
# Sidebar - Filters
# ---------------------
st.sidebar.header("Filter Data:")
status_filter = st.sidebar.multiselect(
    "Status Mahasiswa", options=df["Status"].unique(), default=df["Status"].unique()
)
gender_filter = st.sidebar.selectbox(
    "Jenis Kelamin", options=["Semua", "Laki-laki", "Perempuan"]
)
course_filter = st.sidebar.multiselect(
    "Program Studi", options=df["Course"].unique(), default=df["Course"].unique()
)

# Filter data
df_filtered = df[df["Status"].isin(status_filter)]
if gender_filter != "Semua":
    df_filtered = df_filtered[df_filtered["Gender"] == (1 if gender_filter == "Laki-laki" else 0)]
df_filtered = df_filtered[df_filtered["Course"].isin(course_filter)]

# ---------------------
# Main Title
# ---------------------
st.title("🎓 Dashboard Monitoring Performa Mahasiswa")
st.markdown("Analisis visual untuk memantau status, performa akademik, dan faktor sosial mahasiswa.")

# ---------------------
# Metrics
# ---------------------
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Mahasiswa", len(df_filtered))
col2.metric("Rata-rata Nilai Sem 1", f"{df_filtered['Curricular_units_1st_sem_grade'].mean():.2f}")
col3.metric("Rata-rata Nilai Sem 2", f"{df_filtered['Curricular_units_2nd_sem_grade'].mean():.2f}")
col4.metric("Rata-rata Usia Masuk", f"{df_filtered['Age_at_enrollment'].mean():.1f} th")

# ---------------------
# Distribusi Status Mahasiswa
# ---------------------
st.subheader("📊 Distribusi Status Mahasiswa")
fig_status = px.pie(df_filtered, names='Status', title='Distribusi Status', hole=0.4)
st.plotly_chart(fig_status, use_container_width=True)

# ---------------------
# Bar Chart: Status per Course
# ---------------------
st.subheader("🏫 Status Mahasiswa Berdasarkan Program Studi")
course_status = df_filtered.groupby(["Course", "Status"]).size().reset_index(name="Jumlah")
fig_course = px.bar(course_status, x="Course", y="Jumlah", color="Status", barmode="group")
st.plotly_chart(fig_course, use_container_width=True)

# ---------------------
# Line Chart: Rata-rata Nilai per Semester
# ---------------------
st.subheader("📈 Perbandingan Nilai Semester 1 dan Semester 2")
avg_grades = df_filtered.groupby("Status")[
    ["Curricular_units_1st_sem_grade", "Curricular_units_2nd_sem_grade"]
].mean().reset_index()
fig_grades = px.line(
    avg_grades.melt(id_vars="Status", var_name="Semester", value_name="Rata-rata Nilai"),
    x="Semester", y="Rata-rata Nilai", color="Status", markers=True
)
st.plotly_chart(fig_grades, use_container_width=True)

# ---------------------
# Korelasi antara variabel
# ---------------------
st.subheader("📌 Korelasi Variabel Akademik")
corr_cols = [
    "Admission_grade",
    "Curricular_units_1st_sem_grade",
    "Curricular_units_2nd_sem_grade",
    "Curricular_units_1st_sem_approved",
    "Curricular_units_2nd_sem_approved"
]
fig_corr, ax = plt.subplots()
sns.heatmap(df_filtered[corr_cols].corr(), annot=True, cmap="coolwarm", ax=ax)
st.pyplot(fig_corr)

# ---------------------
# Analisis Faktor Risiko
# ---------------------
st.subheader("⚠️ Analisis Faktor Risiko Dropout")
risk_cols = ["Scholarship_holder", "Debtor", "Tuition_fees_up_to_date"]
for col in risk_cols:
    fig_risk = px.histogram(df_filtered, x=col, color="Status", barmode="group",
                            title=f"Distribusi Status berdasarkan {col}")
    st.plotly_chart(fig_risk, use_container_width=True)

# ---------------------
# Footer
# ---------------------
st.markdown("---")
st.markdown("📍 **Note**: Dashboard ini dibuat dengan Streamlit dan menggunakan dataset performa mahasiswa dari Jaya Jaya Institut.")
