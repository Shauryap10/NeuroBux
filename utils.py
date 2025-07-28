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
    
    # Calculate page width manually to avoid 'epw' attribute error
    page_width = pdf.w - 2 * pdf.l_margin
    col_width = page_width / len(df.columns) if len(df.columns) > 0 else page_width

    # Header row
    for col_name in df.columns:
        pdf.cell(col_width, line_height, str(col_name), border=1)
    pdf.ln(line_height)

    # Data rows
    for row in df.itertuples(index=False):
        for datum in row:
            text = str(datum)[:20]  # Truncate long text to fit
            pdf.cell(col_width, line_height, text, border=1)
        pdf.ln(line_height)

    # Fixed: Handle both string and bytes output properly
    try:
        pdf_output = pdf.output(dest='S')
        
        # Check if output is already bytes or needs encoding
        if isinstance(pdf_output, bytes):
            return pdf_output
        elif isinstance(pdf_output, str):
            return pdf_output.encode('latin1')
        else:
            # Handle bytearray case
            return bytes(pdf_output)
            
    except Exception as e:
        # Fallback method using BytesIO
        pdf_buffer = io.BytesIO()
        pdf_string = pdf.output(dest='S')
        
        if isinstance(pdf_string, (bytes, bytearray)):
            pdf_buffer.write(bytes(pdf_string))
        else:
            pdf_buffer.write(pdf_string.encode('latin1'))
        
        return pdf_buffer.getvalue()

def show_confirmation_dialog(action_type, details=""):
    """Show a confirmation dialog for destructive actions"""
    import streamlit as st
    
    if action_type == "reset_month":
        st.warning(f"⚠️ **Reset Current Month Data**\n\nThis will permanently delete all expenses and income for the current month.\n\n{details}")
    elif action_type == "delete_all":
        st.error(f"🚨 **Delete All Data**\n\nThis will permanently delete ALL your financial data. This action cannot be undone!\n\n{details}")
    elif action_type == "delete_month":
        st.warning(f"⚠️ **Delete Month Data**\n\nThis will permanently delete all data for the selected month.\n\n{details}")
