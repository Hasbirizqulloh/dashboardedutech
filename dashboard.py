import streamlit as st
import pandas as pd
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# ✅ Harus dipanggil paling atas sebelum elemen Streamlit lain
st.set_page_config(page_title="Student Performance Dashboard", layout="wide")

# Load dataset
@st.cache_data
def load_data():
    df = pd.read_csv("data.csv", delimiter=";")
    return df

df = load_data()


# Mapping kode Course ke nama lengkap
course_map = {
    33: "Biofuel Production Technologies",
    171: "Animation and Multimedia Design",
    8014: "Social Service (evening attendance)",
    9003: "Agronomy",
    9070: "Communication Design",
    9085: "Veterinary Nursing",
    9119: "Informatics Engineering",
    9130: "Equinculture",
    9147: "Management",
    9238: "Social Service",
    9254: "Tourism",
    9500: "Nursing",
    9556: "Oral Hygiene",
    9670: "Advertising and Marketing Management",
    9773: "Journalism and Communication",
    9853: "Basic Education",
    9991: "Management (evening attendance)"
}

# Balikkan mapping nama → kode
course_map_inverse = {v: k for k, v in course_map.items()}

# ---------------------
# Sidebar - Filters (pakai selectbox semua)
# ---------------------


st.sidebar.header("Filter Data:")

# Status
status_options = ["Semua"] + sorted(df["Status"].unique().tolist())
status_filter = st.sidebar.selectbox("Status Mahasiswa", options=status_options)

# Gender
gender_options = ["Semua", "Laki-laki", "Perempuan"]
gender_filter = st.sidebar.selectbox("Jenis Kelamin", options=gender_options)

# Pilihan course dalam bentuk nama
course_names = ["Semua"] + sorted(course_map_inverse.keys())
course_filter = st.sidebar.selectbox("Program Studi", options=course_names)

# ---------------------
# Filter data berdasarkan pilihan
# ---------------------
df_filtered = df.copy()

if status_filter != "Semua":
    df_filtered = df_filtered[df_filtered["Status"] == status_filter]

if gender_filter != "Semua":
    df_filtered = df_filtered[df_filtered["Gender"] == (1 if gender_filter == "Laki-laki" else 0)]

if course_filter != "Semua":
    selected_course_code = course_map_inverse[course_filter]
    df_filtered = df_filtered[df_filtered["Course"] == selected_course_code]


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
# Bar Chart: Status per Course (Top 10 program studi berdasarkan jumlah mahasiswa)
# ---------------------
st.subheader("🏫 Status Mahasiswa Berdasarkan Program Studi (Top 10)")

# Tambahkan nama lengkap course
df_filtered['Course_Name'] = df_filtered['Course'].map(course_map)

# Hitung total mahasiswa per course untuk urutan
course_totals = df_filtered.groupby('Course_Name').size().sort_values(ascending=False)
top_courses = course_totals.head(10).index.tolist()

# Filter hanya top 10
df_top_courses = df_filtered[df_filtered['Course_Name'].isin(top_courses)]

course_status = df_top_courses.groupby(["Course_Name", "Status"]).size().reset_index(name="Jumlah")

# Buat bar chart
fig_course = px.bar(
    course_status,
    x="Course_Name",
    y="Jumlah",
    color="Status",
    barmode="group",
    title="Jumlah Mahasiswa berdasarkan Status pada 10 Program Studi Terbesar",
    labels={"Course_Name": "Program Studi", "Jumlah": "Jumlah Mahasiswa"},
    category_orders={"Course_Name": top_courses}  # supaya urut sesuai jumlah total
)
fig_course.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig_course, use_container_width=True)


# ---------------------
# Line Chart: Rata-rata Nilai per Semester dengan garis total
# ---------------------
st.subheader("📈 Perbandingan Rata-rata Nilai Semester 1 dan Semester 2 berdasarkan Status")

# Data rata-rata nilai per Status
avg_grades = df_filtered.groupby("Status")[
    ["Curricular_units_1st_sem_grade", "Curricular_units_2nd_sem_grade"]
].mean().reset_index()

# Data rata-rata total (semua status)
total_avg = df_filtered[["Curricular_units_1st_sem_grade", "Curricular_units_2nd_sem_grade"]].mean().to_frame().T
total_avg["Status"] = "Total"

# Gabungkan untuk plot
avg_grades_all = pd.concat([avg_grades, total_avg], ignore_index=True)

# Melt agar format long untuk plotly line chart
avg_grades_melt = avg_grades_all.melt(id_vars="Status", var_name="Semester", value_name="Rata-rata Nilai")

# Ubah nama semester lebih user-friendly
semester_name_map = {
    "Curricular_units_1st_sem_grade": "Semester 1",
    "Curricular_units_2nd_sem_grade": "Semester 2"
}
avg_grades_melt["Semester"] = avg_grades_melt["Semester"].map(semester_name_map)

fig_grades = px.line(
    avg_grades_melt,
    x="Semester",
    y="Rata-rata Nilai",
    color="Status",
    markers=True,
    title="Rata-rata Nilai per Semester berdasarkan Status Mahasiswa",
    labels={"Rata-rata Nilai": "Rata-rata Nilai", "Semester": "Semester"},
)

fig_grades.update_layout(yaxis=dict(range=[0, 20]))  # sesuaikan skala nilai (misal 0-20)

st.plotly_chart(fig_grades, use_container_width=True)

# ---------------------
# Analisis Faktor Risiko
# ---------------------
st.subheader("⚠️ Analisis Faktor Risiko Dropout")

# Filter untuk memilih satu faktor risiko
risk_feature = st.selectbox(
    "Pilih Faktor Risiko yang Ingin Dianalisis:",
    options={
        "Scholarship_holder": "Penerima Beasiswa",
        "Debtor": "Status Hutang (Debtor)",
        "Tuition_fees_up_to_date": "Pembayaran UKT Tepat Waktu"
    },
    format_func=lambda x: {
        "Scholarship_holder": "Penerima Beasiswa",
        "Debtor": "Status Hutang (Debtor)",
        "Tuition_fees_up_to_date": "Pembayaran UKT Tepat Waktu"
    }[x]
)

# Tampilkan histogram hanya untuk fitur yang dipilih
fig_risk = px.histogram(
    df_filtered,
    x=risk_feature,
    color="Status",
    barmode="group",
    title=f"Distribusi Status Mahasiswa Berdasarkan '{risk_feature}'",
    labels={risk_feature: risk_feature.replace("_", " ").title(), "count": "Jumlah"}
)
st.plotly_chart(fig_risk, use_container_width=True)

# ---------------------
# Footer
# ---------------------
st.markdown("---")
st.markdown("📍 **Note**: Dashboard ini dibuat dengan Streamlit dan menggunakan dataset performa mahasiswa dari Jaya Jaya Institut.")
