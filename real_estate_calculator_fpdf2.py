import streamlit as st
import pandas as pd
from fpdf import FPDF
import os

st.set_page_config(page_title="Real Estate Calculator", layout="wide")

st.title("🏠 Real Estate Purchase Calculator")

if "records" not in st.session_state:
    st.session_state.records = []

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
                "Type": property_type,
                "Price": f"{price:,.2f}",
                "Down Pay": f"{down_payment:,.2f}",
                "Net Value": f"{net_value:,.2f}",
                "Rate%": interest_rate,
                "Years": years,
                "Interest": f"{total_interest:,.2f}",
                "Total": f"{total_with_interest:,.2f}",
                "Monthly": f"{monthly_payment:,.2f}",
                f"Rent({rental_percent}%)": f"{rent_value:,.2f}"
            })
            st.success("Property added successfully.")

st.markdown("### 📊 Properties Summary")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df.style.format(precision=2), use_container_width=True)

    if st.button("📄 Export to PDF"):
        class PDF(FPDF):
            def __init__(self):
                super().__init__(orientation='L', unit='mm', format='A4')
                self.set_auto_page_break(auto=True, margin=15)
                self.set_margins(10, 10, 10)
                
            def header(self):
                self.set_font("Helvetica", 'B', 12)
                self.cell(0, 10, "Real Estate Portfolio Summary", ln=True, align='C')
                self.ln(8)
                
            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", 'I', 8)
                self.cell(0, 10, f"Page {self.page_no()}", align='C')
                
            def create_table(self, data):
                self.set_font("Helvetica", '', 7)
                col_widths = [28, 30, 28, 28, 20, 20, 30, 30, 28, 28]  # Custom widths
                row_height = 8
                
                # Header
                self.set_fill_color(200, 230, 255)
                for i, col in enumerate(data.columns):
                    self.cell(col_widths[i], row_height, str(col), border=1, fill=True, align='C')
                self.ln(row_height)
                
                # Data
                for _, row in data.iterrows():
                    for i, item in enumerate(row):
                        self.cell(col_widths[i], row_height, str(item), border=1, align='C')
                    self.ln(row_height)

        # Prepare data
        df_pdf = df.copy()
        df_pdf.columns = [str(col)[:12] for col in df_pdf.columns]  # Shorten column names
        
        # Generate PDF
        pdf = PDF()
        pdf.add_page()
        pdf.create_table(df_pdf)
        
        output_path = "real_estate_report.pdf"
        pdf.output(output_path)
        
        with open(output_path, "rb") as f:
            st.download_button(
                "📥 Download PDF Report",
                data=f,
                file_name=output_path,
                mime="application/pdf"
            )
        os.remove(output_path)

    if st.button("🗑️ Clear All"):
        st.session_state.records.clear()
        st.success("All records cleared.")
else:
    st.info("No properties added yet.")
