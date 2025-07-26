import pandas as pd
from fpdf import FPDF
import io

def export_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

def export_df_to_pdf(df, title="Expense Report"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, title, ln=True, align='C')

    pdf.set_font("Arial", size=10)
    line_height = pdf.font_size * 2.5
    
    # Fix for 'epw' attribute error - calculate page width manually
    page_width = pdf.w - 2 * pdf.l_margin  # Total width minus left and right margins
    col_width = page_width / len(df.columns) if len(df.columns) > 0 else page_width

    # Header
    for col_name in df.columns:
        pdf.cell(col_width, line_height, str(col_name), border=1)
    pdf.ln(line_height)

    # Rows
    for row in df.itertuples(index=False):
        for datum in row:
            text = str(datum)[:20]  # Truncate long text to fit in cells
            pdf.cell(col_width, line_height, text, border=1)
        pdf.ln(line_height)

    # Return PDF as bytes
    return pdf.output(dest='S').encode('latin1')

def show_confirmation_dialog(action_type, details=""):
    """Show a confirmation dialog for destructive actions"""
    import streamlit as st
    
    if action_type == "reset_month":
        st.warning(f"⚠️ **Reset Current Month Data**\n\nThis will permanently delete all expenses and income for the current month.\n\n{details}")
    elif action_type == "delete_all":
        st.error(f"🚨 **Delete All Data**\n\nThis will permanently delete ALL your financial data. This action cannot be undone!\n\n{details}")
    elif action_type == "delete_month":
        st.warning(f"⚠️ **Delete Month Data**\n\nThis will permanently delete all data for the selected month.\n\n{details}")
