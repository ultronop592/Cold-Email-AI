import pdfplumber

def parse_resume(file):
    
    text = ""
    
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            
    return text