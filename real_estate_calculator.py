
import streamlit as st
import pandas as pd

st.set_page_config(page_title="حاسبة شراء العقار", layout="centered")

st.title("🏠 حاسبة شراء العقار")

# جدول لتخزين البيانات في الجلسة
if "records" not in st.session_state:
    st.session_state.records = []

# إدخال بيانات العقار
with st.form("add_property_form"):
    st.subheader("🔢 إدخال بيانات العقار")

    property_type = st.selectbox("نوع العقار", ["شقة", "بيت", "فيلا"])
    price = st.number_input("سعر العقار", min_value=10000.0, step=1000.0)
    down_payment = st.number_input("الدفعة المقدمة", min_value=0.0, max_value=price, step=1000.0)
    interest_rate = st.selectbox("نسبة الفائدة السنوية (%)", [round(i, 1) for i in [x * 0.1 for x in range(10, 71)]])
    years = st.slider("مدة التمويل (عدد السنوات)", min_value=1, max_value=25, step=1)
    rental_percent = st.number_input("نسبة الإيجار السنوية (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

    submitted = st.form_submit_button("➕ إضافة العقار إلى الجدول")

    if submitted:
        original_value = price - down_payment
        total_interest = original_value * (interest_rate / 100) * years
        total_amount = original_value + total_interest
        monthly_payment = total_amount / (years * 12)
        rental_value = original_value * (rental_percent / 100)

        # تخزين في الجلسة
        st.session_state.records.append({
            "نوع العقار": property_type,
            "سعر العقار": price,
            "الدفعة المقدمة": down_payment,
            "قيمة العقار الأصلي": original_value,
            "نسبة الفائدة السنوية": interest_rate,
            "عدد السنوات": years,
            "إجمالي الفوائد": total_interest,
            "الإجمالي مع الفوائد": total_amount,
            "القسط الشهري": monthly_payment,
            f"قيمة الإيجار ({rental_percent}%)": rental_value
        })
        st.success("✅ تم إضافة العقار إلى الجدول.")

# عرض الجدول
st.markdown("### 📋 جدول العقارات")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df.style.format(precision=2), use_container_width=True)
else:
    st.info("لم يتم إضافة أي عقار بعد.")

# زر لمسح الجدول
if st.session_state.records:
    if st.button("🗑️ مسح جميع العقارات"):
        st.session_state.records.clear()
        st.success("✅ تم مسح الجدول.")
