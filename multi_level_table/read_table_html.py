import cv2 as cv
from . import functions


def tell_content(page_info, contour, shape):
    """
    This function will map the contour to the written content of the table.

    Input: page_info --> the information of the page in the form {x: , y: , content: }
           contour --> the contour of which the content needs to be extracted (in the form [x, y, width, height])
           shape --> the shape of the image (to estimate the buffer)
    Output: string which is the content inside the given contour
    """
    tx = shape[1]//200
    ty = shape[0]//200
    ret = ""
    for text in page_info:
        x = text['x']
        y = text['y']
        if (x > (contour[0] - tx)) and (x < (contour[0] + contour[2])) and (y > (contour[1] - ty)) and (y < (contour[1] + contour[3])):
            if 'content' in text.keys():
                ret = ret + " " + text['content']
    return ret.strip()


def image_to_df(image_file, tables, page_info, start, debug=0):

    """
    This function takes the image file as input and return the data-frame contained in that image.

    Input: image_file --> the path of the image file
           html_file --> the path of the HTML file of the PDF
           page_no --> the page no of the PDF which needs to be scraped
    Output: returns a list of dictionaries containing information about all the table in the page of the form
            [ {bbox: , table_no: , content: } ] where content is the data frame of that table
    """

    # df_list will contain all the data-frames in the current page
    df_list = []

    image_orig = cv.imread(image_file, 0)
    shape = image_orig.shape

    img_vh = functions.get_contours(image_orig, 1, 1, 1, 1, 3, 3, 3, 3)

    if debug:
        cv.imwrite('pdf/test/' + 'table_structure_verHorLines_' + image_file.split('/')[-1].split('.')[0] + '.jpg', img_vh)

    # Detecting all the contours in the page
    contours, hierarchy = cv.findContours(~img_vh, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    if not contours:
        return df_list

    # Looping through all the tables
    for table_no, table in enumerate(tables, start):
        t_x, t_y, t_w, t_h = table
        cells_rect = []

        if debug:
            image = cv.imread(image_file)
            cv.rectangle(image, (t_x-10, t_y-10), (t_x+t_w+10, t_y+t_h+10), (0, 255, 0), 2)
            cv.imwrite('pdf/test/' + 'table_' + image_file.split('/')[-1].split('.')[0] + 'table_' + str(table_no) + '.jpg', image)

        # Collecting only those contours which are cells of the current table, in the list cells_rect
        for c, h in zip(contours, hierarchy[0]):
            if h[2] == -1:
                x, y, wd, ht = cv.boundingRect(c)
                if x > (t_x - 10) and y > (t_y - 10) and (x + wd) < (t_x + t_w + 10) and (y + ht) < (t_y + t_h + 10):
                    cells_rect.append([x, y, wd, ht])

        # continuing with the loop if the table has no contours
        if not cells_rect:
            continue

        if debug:
            image = cv.imread(image_file)
            for b in cells_rect:
                cv.rectangle(image, (b[0], b[1]), (b[0]+b[2], b[1]+b[3]), (0, 255, 0), 2)
            cv.imwrite('pdf/test/'+'contours_'+image_file.split('/')[-1].split('.')[0]+'table_'+str(table_no)+'.jpg', image)

        # Getting the row and the column bounds to detect which cell belongs to which row and column
        rows, cols = functions.get_bounds(cells_rect, image_orig.shape, 100, 300)
        row_count = len(rows)
        col_count = len(cols)
        print("nrow -->", row_count)
        print("ncol -->", col_count)

        list_row_col = []
        for col_n in range(col_count - 1):
            x1 = int(cols[col_n] + shape[1]//200)
            x2 = int(cols[col_n + 1] - shape[1]//200)
            for row_n in range(row_count - 1):
                y1 = int(rows[row_n] + shape[0]//200)
                y2 = int(rows[row_n + 1] - shape[0]//200)
                for contour in cells_rect:
                    if functions.inside(contour, (x1, y1, x2, y2)):
                        list_row_col.append({'row': row_n, 'col': col_n,
                                             'content': tell_content(page_info, contour, image_orig.shape)})
                        break

        df_list.append(functions.data_to_dataframe(list_row_col, col_count - 1, table_no, table))

    return df_list
