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

st.markdown("### 📊 Properties Summary")
if st.session_state.records:
    df = pd.DataFrame(st.session_state.records)
    st.dataframe(df.style.format(precision=2), use_container_width=True)

    if st.button("📄 Export to PDF"):
        class CustomPDF(FPDF):
            def __init__(self):
                super().__init__(orientation='L', unit='mm', format='A4')
                
            def header(self):
                self.set_font("Helvetica", 'B', 14)
                self.cell(0, 10, "Real Estate Portfolio Summary", ln=True, align='C')
                self.ln(12)
                
            def footer(self):
                self.set_y(-15)
                self.set_font("Helvetica", 'I', 8)
                self.cell(0, 10, f"Page {self.page_no()}", align='C')
                
            def create_table(self, dataframe):
                self.set_font("Helvetica", '', 8)
                col_width = self.w / len(dataframe.columns)
                row_height = 8
                
                # Table Header
                self.set_fill_color(200, 230, 255)
                for col in dataframe.columns:
                    self.cell(col_width, row_height, str(col), border=1, fill=True, align='C')
                self.ln(row_height)
                
                # Table Data
                for _, row in dataframe.iterrows():
                    for item in row:
                        text = f"{item:,.2f}" if isinstance(item, float) else str(item)
                        self.cell(col_width, row_height, text, border=1, align='C')
                    self.ln(row_height)
                self.ln(10)

        # Prepare data
        numeric_cols = ['Price', 'Down Payment', 'Net Value', 'Total Interest',
                       'Total w/ Interest', 'Monthly Payment', 
                       df.columns[df.columns.str.contains('Annual Rent')][0]]
        
        df[numeric_cols] = df[numeric_cols].applymap(lambda x: f"{x:,.2f}")

        # Generate PDF
        pdf = CustomPDF()
        pdf.add_page()
        pdf.create_table(df)
        
        output_file = "real_estate_portfolio.pdf"
        pdf.output(output_file)
        
        with open(output_file, "rb") as f:
            st.download_button(
                "📥 Download Full Report",
                data=f,
                file_name=output_file,
                mime="application/pdf"
            )
        os.remove(output_file)

    if st.button("🗑️ Clear All"):
        st.session_state.records.clear()
        st.success("All records cleared.")
else:
    st.info("No properties added yet.")
