from table_detect import detect_table, table_detect_breakpoints
from . import read_html, read_table_ocr, read_table_html
import cv2 as cv


def get_data(pdf_name, image_file, html_file, page_no, method, debug):
    """
    This function takes image file as argument and find the tables in that image and calls the method to extract the
    content of that table based on whether the table is readable or image (scanned).

    Input : image_file --> path for image file
            html_file --> path for the html of the PDF file
            page_no --> page no of the PDF to which the image corresponds
            method --> google_vision/tesseract, method to use for OCR in image
            debug --> True/False indicating whether to save the intermediate images for debugging or not
    Output : df --> data of the tables in the page
    """
    tables = detect_table.detect_table(image_file)

    if not tables:
        return []

    image_orig = cv.imread(image_file, 0)
    shape_html = [image_orig.shape[1], image_orig.shape[0]]

    all_tables = []

    for table in tables:
        tx, ty, tw, th = table
        small_tables = table_detect_breakpoints.detect_table(image_orig[ty:(ty+th), tx:(tx+tw)])
        if not small_tables:
            all_tables.append(table)
            continue

        for st in small_tables:
            t_x, t_y, t_w, t_h = st
            t_x += tx
            t_y += ty
            all_tables.append([t_x, t_y, t_w, t_h])

    tables = all_tables
    print("="*100)
    print("tables -->", tables)


    page_info = read_html.parse_html(html_file, page_no, shape_html)
    table_ocr = []
    table_html = []

    for table in tables:
        flag = False
        tx, ty, tw, th = table
        for info in page_info:
            x = info['x']
            y = info['y']
            if (x > tx) and (x < (tx + tw)) and (y > ty) and (y < (ty + th)):
                table_html.append(table)
                flag = True
                break
        if not flag:
            table_ocr.append(table)

    print("OCR tables -->", table_ocr)
    print("HTML tables -->", table_html)

    df_ocr = []
    df_html = []

    if table_ocr:
        df_ocr = read_table_ocr.image_to_df(image_file, tables, method, debug)

    if table_html:
        df_html = read_table_html.image_to_df(image_file, table_html, page_info, len(table_ocr), debug)

    df = df_ocr + df_html

    return df
