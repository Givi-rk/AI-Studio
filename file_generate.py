import pandas as pd
from xhtml2pdf import pisa
from docx import Document
import os
import io

def generate_file(html_content, extension):
    """
    Converts HTML content into the requested file format.
    Uses xhtml2pdf for pure Python PDF generation.
    """
    output_dir = "generated_files"
    os.makedirs(output_dir, exist_ok=True)
    filename = f"document.{extension}"
    filepath = os.path.join(output_dir, filename)

    if extension == 'pdf':
        # Create a file object to write the PDF
        with open(filepath, "wb") as f:
            # pisa.CreatePDF directly writes HTML to the PDF file
            pisa_status = pisa.CreatePDF(html_content, dest=f)
            
        if pisa_status.err:
            raise ValueError(f"Could not generate PDF: {pisa_status.err}")
    
    elif extension == 'csv':
        try:
            dfs = pd.read_html(html_content)
            dfs[0].to_csv(filepath, index=False)
        except Exception as e:
            raise ValueError(f"Could not parse HTML table for CSV: {e}")
            
    elif extension == 'docx':
        # Simple DOCX generation
        doc = Document()
        doc.add_paragraph(html_content) 
        doc.save(filepath)
        
    return filepath
