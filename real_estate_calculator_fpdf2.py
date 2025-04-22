import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

st.set_page_config(page_title="Real Estate Calculator", layout="wide")

st.title("🏠 Real Estate Purchase Calculator")

# تهيئة جلسة العمل لتخزين البيانات
if "records" not in st.session_state:
    st.session_state.records = []

# نموذج إدخال بيانات العقار
with st.form("add_property_form"):
    st.subheader("📋 Enter Property Details")
    
    property_type = st.selectbox("Property Type", ["Apartment", "House", "Villa"])
    price = st.number_input("Property Price", min_value=10000.0, step=1000.0)
    down_payment = st.number_input("Down Payment", min_value=0.0, step=1000.0)
    interest_rate = st.selectbox("Annual Interest Rate (%)", [round(i, 1) for i in [x * 0.1 for x in range(10, 71)]])
    years = st.slider("Loan Duration (Years)", min_value=1, max_value=25, step=1)
    rental_percent = st.number_input("Annual Rent Percentage (%)", min_value=0.0, max_value=100.0, value=5.0, step=0.1)
    
    submitted = st.form_submit_button("➕ Add Property")
    
    if submitted:
        if down_payment > price:
            st.error("Down payment cannot exceed property price.")
        else:
            net_value = price - down_payment
            total_interest = net_value * (interest_rate / 100) * years
            total_with_interest = net_value + total_interest
            monthly_payment = total_with_interest / (years * 12)
            rent_value = net_value * (rental_percent / 100)
            
            st.session_state.records.append({
                "Property Type": property_type,
                "Price": price,
                "Down Payment": down_payment,
                "Net Value": net_value,
                "Interest Rate (%)": interest_rate,
                "Years": years,
                "Total Interest": total_interest,
                "Total w/ Interest": total_with_interest,
                "Monthly Payment": monthly_payment,
                f"Annual Rent ({rental_percent}%)": rent_value
            })
            st.success("Property added successfully.")

# عرض الجدول
st.markdown("### 📊 Properties Summary")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df.style.format(precision=2), use_container_width=True)
    
    # زر تصدير الجدول إلى PDF
    if st.button("📄 Export to PDF"):
        class PDF(FPDF):
            def __init__(self):
                # استخدام الوضع Landscape (بالعرض) وحجم الورقة A4
                super().__init__(orientation='L', unit='mm', format='A4')
            
            def header(self):
                self.set_font("Helvetica", 'B', 10)
                self.cell(0, 10, "Real Estate Summary", ln=True, align='C')
                self.ln(3)
            
            def table(self, dataframe):
                # تقليل حجم الخط إلى 7
                self.set_font("Helvetica", '', 7)
                # حساب عرض العمود ديناميكيًا بحيث يعبئ العرض الكامل للورقة
                col_width = self.w / (len(dataframe.columns) + 1)
                row_height = 5  # ارتفاع الصف
                self.set_fill_color(200, 230, 255)
                
                # رسم رؤوس الجدول
                for col in dataframe.columns:
                    self.cell(col_width, row_height, str(col), border=1, fill=True)
                self.ln(row_height)
                
                # رسم بيانات الجدول
                for _, row in dataframe.iterrows():
                    for item in row:
                        text = f"{item:,.2f}" if isinstance(item, (int, float)) else str(item)
                        self.cell(col_width, row_height, text, border=1)
                    self.ln(row_height)
        
        pdf = PDF()
        pdf.add_page()
        pdf.table(df)
        
        file_path = "real_estate_summary_landscape.pdf"
        pdf.output(file_path)
        
        with open(file_path, "rb") as f:
            st.download_button("📥 Download PDF", f, file_name="real_estate_summary.pdf", mime="application/pdf")
        os.remove(file_path)
    
    if st.button("🗑️ Clear All"):
        st.session_state.records.clear()
        st.success("All records cleared.")
else:
    st.info("No properties added yet.")
