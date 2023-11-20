from pdf_tabula import pdf_to_table_generic
import pdb
def get_tables_without_lines(path):

    '''
    generic way to get tables without lines using tabula
    
    '''
    
    df = pdf_to_table_generic.get_table_tabula(path)

    return df


if __name__ == '__main__':
    df=get_tables_without_lines('data/Districtwise_Hospital_IsoBeds.pdf')
