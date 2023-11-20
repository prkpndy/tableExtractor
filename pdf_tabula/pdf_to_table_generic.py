import tabula
import pandas as pd

from PyPDF2 import PdfFileReader


# print(type(pdf_length))
def get_table_tabula(file_path):

    '''
    To be used for tables without lines
    input: pdf path
    output: json with tables from all pages
    
    '''
    
    pdfs = tabula.read_pdf(file_path, stream=True, multiple_tables=True, pages = 'all')

    pages = {}
    for i,j in enumerate(reversed(pdfs)):
        
        cols = list(j.columns)
        page = {}
        for col in cols:
            rows_j = list(j[col])
            page[col]=rows_j
        pages[i]=page
    return pages
    