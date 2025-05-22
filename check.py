import streamlit as st
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# Заголовок додатка
st.title("🩺 Штучний Інтелект для Діагностики Інфаркту")
st.markdown("""
Цей додаток допомагає оцінити ймовірність інфаркту на основі ваших симптомів.
**Увага**: Це не заміняє консультації лікаря!
""")

# 1. Генерація синтетичних даних (тепер з тиском і пульсом)
@st.cache_data
def load_data():
    data = {
        'age': [55, 60, 45, 70, 50, 65, 40, 75, 62, 48, 30, 85],
        'chest_pain': [1, 1, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
        'pain_arm': [1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
        'shortness_breath': [1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1],
        'sweating': [1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1],
        'nausea': [1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1, 1],
        'systolic_bp': [180, 120, 130, 200, 110, 160, 115, 190, 170, 125, 140, 210],  # Верхній тиск
        'diastolic_bp': [110, 80, 85, 120, 70, 90, 75, 100, 95, 80, 90, 130],      # Нижній тиск
        'pulse': [90, 72, 80, 110, 65, 95, 70, 105, 85, 75, 88, 115],              # Пульс
        'heart_attack': [1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 1, 1]
    }
    return pd.DataFrame(data)

df = load_data()

# 2. Навчання моделі
X = df.drop('heart_attack', axis=1)
y = df['heart_attack']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 3. Інтерфейс введення даних
st.sidebar.header("Введіть ваші симптоми:")

# Обов'язкові поля
age = st.sidebar.slider("Вік", 15, 105, 50)
chest_pain = st.sidebar.radio("Біль у грудях", ["Немає", "Так"], index=0)
pain_arm = st.sidebar.radio("Біль віддає в ліву руку/щелепу", ["Немає", "Так"], index=0)
breath = st.sidebar.radio("Задишка", ["Немає", "Так"], index=0)
sweating = st.sidebar.radio("Пітливість/холодний піт", ["Немає", "Так"], index=0)
nausea = st.sidebar.radio("Нудота/блювання", ["Немає", "Так"], index=0)

# Опціональні поля (з можливістю пропуску)
st.sidebar.markdown("---")
st.sidebar.subheader("Додаткові параметри (необов'язково)")

bp_col1, bp_col2 = st.sidebar.columns(2)
with bp_col1:
    systolic = st.number_input("Верхній тиск (мм рт.ст.)", min_value=50, max_value=250, value=120, step=1)
with bp_col2:
    diastolic = st.number_input("Нижній тиск (мм рт.ст.)", min_value=30, max_value=150, value=80, step=1)

pulse = st.sidebar.number_input("Пульс (уд/хв)", min_value=30, max_value=200, value=72, step=1)

use_bp_pulse = st.sidebar.checkbox("Враховувати тиск і пульс у аналізі", value=False)

# 4. Підготовка даних для передбачення
input_data = {
    'age': age,
    'chest_pain': 1 if chest_pain == "Так" else 0,
    'pain_arm': 1 if pain_arm == "Так" else 0,
    'shortness_breath': 1 if breath == "Так" else 0,
    'sweating': 1 if sweating == "Так" else 0,
    'nausea': 1 if nausea == "Так" else 0,
    'systolic_bp': systolic if use_bp_pulse else df['systolic_bp'].median(),
    'diastolic_bp': diastolic if use_bp_pulse else df['diastolic_bp'].median(),
    'pulse': pulse if use_bp_pulse else df['pulse'].median()
}

input_df = pd.DataFrame([input_data])

# 5. Передбачення
probability = model.predict_proba(input_df)[0][1] * 100

# 6. Вивід результату
st.subheader("Результат оцінки:")
if probability >= 50:
    st.error(f"🔴 **Високий ризик інфаркту!** Ймовірність: {probability:.1f}%")
    st.markdown("""
    **Рекомендації:**  
    • Негайно викличте швидку (103 або 112)  
    • Прийміть 250-325 мг аспірину (розжувати)  
    • Ляжте, уникайте рухів  
    """)
    
    if use_bp_pulse:
        if systolic > 140 or diastolic > 90:
            st.warning("⚠ Ваш тиск підвищений! Спробуйте заспокоїтися.")
        if pulse > 100:
            st.warning("⚠ Ваш пульс прискорений! Дихайте повільно та глибоко.")
else:
    st.success(f"🟢 **Низький ризик інфаркту.** Ймовірність: {probability:.1f}%")
    st.markdown("""
    **Рекомендації:**  
    • Продовжуйте спостерігати за станом  
    • Якщо симптоми зберігаються >20 хв – зверніться до лікаря  
    """)

# 7. Додаткова інформація
st.markdown("---")
st.subheader("📊 Інтерпретація показників")
col1, col2 = st.columns(2)
with col1:
    st.markdown("**Тиск:**")
    st.write("- Норма: <120/80 мм рт.ст.")
    st.write("- Гіпертонія: ≥140/90 мм рт.ст.")
with col2:
    st.markdown("**Пульс:**")
    st.write("- Норма: 60-100 уд/хв")
    st.write("- Тахікардія: >100 уд/хв")

st.markdown("---")
st.subheader("ℹ Важливо знати")
st.write("""
• 30% інфарктів проходять без класичного болю в грудях  
• Жінки частіше відчувають нудоту/біль у спині замість грудного болю  
• При діабеті симптоми можуть бути менш вираженими  
""")