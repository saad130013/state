
import streamlit as st

st.set_page_config(page_title="حاسبة شراء العقار", layout="centered")

st.title("🏠 حاسبة شراء العقار")

# 1. نوع العقار
property_type = st.selectbox("نوع العقار", ["شقة", "بيت", "فيلا"])

# 2. السعر
price = st.number_input("سعر العقار", min_value=10000.0, step=1000.0)

# 3. الدفعة المقدمة
down_payment = st.number_input("الدفعة المقدمة", min_value=0.0, max_value=price, step=1000.0)

# 4. الفائدة السنوية
interest_rate = st.selectbox("نسبة الفائدة السنوية (%)", [round(i, 1) for i in [x * 0.1 for x in range(10, 71)]])

# 5. عدد السنوات
years = st.slider("مدة التمويل (عدد السنوات)", min_value=1, max_value=25, step=1)

# 6. حسابات تلقائية
original_property_value = price - down_payment
total_interest = original_property_value * (interest_rate / 100)
total_amount = original_property_value + total_interest
monthly_payment = total_amount / (years * 12)
rental_value = original_property_value * 0.05

# عرض النتائج
st.markdown("### النتائج")
st.write("🔹 **قيمة العقار الأصلي بعد الدفعة المقدمة:**", f"{original_property_value:,.2f} ريال")
st.write("🔹 **الفوائد:**", f"{total_interest:,.2f} ريال")
st.write("🔹 **الإجمالي مع الفوائد:**", f"{total_amount:,.2f} ريال")
st.write("🔹 **القسط الشهري:**", f"{monthly_payment:,.2f} ريال")
st.write("🔹 **قيمة الإيجار السنوي (5%):**", f"{rental_value:,.2f} ريال")
