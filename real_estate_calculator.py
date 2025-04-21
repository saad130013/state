
import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

st.set_page_config(page_title="حاسبة شراء العقار", layout="wide")

st.markdown(""" 
    <style>
        .stDataFrameContainer {
            direction: rtl;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏠 حاسبة شراء العقار")

# جدول لتخزين البيانات في الجلسة
if "records" not in st.session_state:
    st.session_state.records = []

# إدخال بيانات العقار
with st.form("add_property_form"):
    st.subheader("🔢 إدخال بيانات العقار")

    property_type = st.selectbox("نوع العقار", ["شقة", "بيت", "فيلا"])
    price = st.number_input("سعر العقار", min_value=10000.0, step=1000.0)

    down_payment = st.number_input("الدفعة المقدمة", min_value=0.0, step=1000.0)
    interest_rate = st.selectbox("نسبة الفائدة السنوية (%)", [round(i, 1) for i in [x * 0.1 for x in range(10, 71)]])
    years = st.slider("مدة التمويل (عدد السنوات)", min_value=1, max_value=25, step=1)
    rental_percent = st.number_input("نسبة الإيجار السنوية (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)

    submitted = st.form_submit_button("➕ إضافة العقار إلى الجدول")

    if submitted:
        if down_payment > price:
            st.error("🚫 الدفعة المقدمة لا يمكن أن تتجاوز سعر العقار.")
        else:
            original_value = price - down_payment
            total_interest = original_value * (interest_rate / 100) * years
            total_amount = original_value + total_interest
            monthly_payment = total_amount / (years * 12)
            rental_value = original_value * (rental_percent / 100)

            st.session_state.records.append({
                "Property Type": property_type,
                "Price": price,
                "Down Payment": down_payment,
                "Net Property Value": original_value,
                "Annual Interest Rate (%)": interest_rate,
                "Years": years,
                "Total Interest": total_interest,
                "Total With Interest": total_amount,
                "Monthly Payment": monthly_payment,
                f"Annual Rent ({rental_percent}%)": rental_value
            })
            st.success("✅ تم إضافة العقار إلى الجدول.")

# عرض الجدول
st.markdown("### 📋 جدول العقارات")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df.style.format(precision=2), use_container_width=True, height=500)

    # زر تصدير إلى PDF
    if st.button("📄 تصدير إلى PDF"):
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", 'B', 14)
                self.cell(0, 10, "Real Estate Purchase Summary", ln=True, align='C')
                self.ln(5)

            def table(self, dataframe):
                self.set_font("Arial", '', 9)
                col_width = self.w / (len(dataframe.columns) + 1)
                row_height = 6

                # Header
                self.set_fill_color(230, 230, 250)
                for col in dataframe.columns:
                    self.cell(col_width, row_height, str(col), border=1, fill=True)
                self.ln(row_height)

                # Rows
                for _, row in dataframe.iterrows():
                    for item in row:
                        self.cell(col_width, row_height, str(round(item, 2)) if isinstance(item, (int, float)) else str(item), border=1)
                    self.ln(row_height)

        pdf = PDF()
        pdf.add_page()
        pdf.table(df)

        output_path = "real_estate_report.pdf"
        pdf.output(output_path)
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 تحميل ملف PDF",
                data=file,
                file_name="real_estate_report.pdf",
                mime="application/pdf"
            )
        os.remove(output_path)
else:
    st.info("لم يتم إضافة أي عقار بعد.")

# زر لمسح الجدول
if st.session_state.records:
    if st.button("🗑️ مسح جميع العقارات"):
        st.session_state.records.clear()
        st.success("✅ تم مسح الجدول.")
