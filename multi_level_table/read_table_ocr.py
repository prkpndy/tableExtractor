import cv2 as cv
import pytesseract
from PIL import Image
from . import read_image_gocr, functions
from . import hough_lines


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
        x = (text['x1']+text['x2'])/2
        y = (text['y1']+text['y2'])/2
        if (x > (contour[0] - tx)) and (x < (contour[0] + contour[2] + tx)) and (y > (contour[1] - ty)) and (y < (contour[1] + contour[3] + ty)):
            ret = ret + " " + text['content']
    return ret.strip()


def image_to_df(image_file, tables, method='google_vision', debug=0):
    """
    This function takes an image file and the method to be used to extract the table from that image and returns the
    table in the form of a list of dictionaries, which is extracted using the specified method, where each dictionary
    contains information about a particular table in page in the form {bbox: , table_no: , content: }
    Input: image_file --> the path to the image file
           method --> the method to be used to extract the table content
    Output: a list of dictionaries containing information of each table
    """
    df_list = []

    image_orig = cv.imread(image_file, 0)
    shape = image_orig.shape

    # Detecting all the contours in the page
    img_vh = functions.get_contours(image_orig)

    if debug:
        cv.imwrite('pdf/test/' + 'table_structure_verHorLines_' + image_file.split('/')[-1].split('.')[0] + '.jpg', img_vh)

    # Getting the information in the page if method == google_vision
    if method == 'google_vision':
        page_info = read_image_gocr.parse_image(image_file)

    # Looping through all the tables
    for table_no, table in enumerate(tables):
        t_x, t_y, t_w, t_h = table
        cells_rect = []

        img_table_struct = hough_lines.hough_lines(img_vh[(t_y-10):(t_y+t_h+10), (t_x-10):(t_x+t_w+10)])

        if debug:
            image = cv.imread(image_file)
            cv.rectangle(image, (t_x-10, t_y-10), (t_x+t_w+10, t_y+t_h+10), (0, 255, 0), 2)
            cv.imwrite('pdf/test/' + 'table_' + image_file.split('/')[-1].split('.')[0] + 'table_' + str(table_no) + '.jpg', image)
            cv.imwrite('pdf/test/' + 'table_hough_lines' + image_file.split('/')[-1].split('.')[0] + 'table_' + str(table_no) + '.jpg', img_table_struct)

        contours, hierarchy = cv.findContours(~img_table_struct, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

        # Continuing with the loop if the table has no contours
        if not contours:
            continue

        # Collecting only those contours which are cells of the current table, in the list cells
        # for c, h in zip(contours, hierarchy[0]):
        #     if h[2] == -1:
        #         x, y, wd, ht = cv.boundingRect(c)
        #         if x > (t_x - 10) and y > (t_y - 10) and (x + wd) < (t_x + t_w + 10) and (y + ht) < (t_y + t_h + 10):
        #             cells.append(c)

        for c, h in zip(contours, hierarchy[0]):
            if h[2] == -1:
                x, y, wd, ht = cv.boundingRect(c)
                cells_rect.append([x, y, wd, ht])

        # cells_rect = [list(cv.boundingRect(c)) for c in contours]
        for i in range(len(cells_rect)):
            cells_rect[i][0] += t_x-10
            cells_rect[i][1] += t_y-10

        if debug:
            image = cv.imread(image_file)
            for b in cells_rect:
                cv.rectangle(image, (b[0], b[1]), (b[0]+b[2], b[1]+b[3]), (0, 255, 0), 2)
            cv.imwrite('pdf/test/'+'contours_'+image_file.split('/')[-1].split('.')[0] + 'table_' + str(table_no) + '.jpg', image)

        # Getting the row and the column bounds to detect which cell belongs to which row and column
        rows, cols = functions.get_bounds(cells_rect, shape, 50, 100)

        row_count = len(rows)
        col_count = len(cols)
        print("nrow -->", row_count)
        print("ncol -->", col_count)

        list_row_col = []

        # Checking if the specified method is google_vision
        if method == 'google_vision':
            # TODO: add functionality for pi radians of rotation
                    # Getting the orientation of the table: 1 & 3 corresponds to pi/2 & 3pi/2 rotation resp. in clockwise direction
            orientation = functions.get_orientation(page_info, table)
            print('Orientation of table ', table, ' is ', orientation)

            for col_n in range(col_count - 1):
                x1 = int(cols[col_n] + shape[1] // 100)
                x2 = int(cols[col_n + 1] - shape[1] // 100)
                for row_n in range(row_count - 1):
                    y1 = int(rows[row_n] + shape[0] // 100)
                    y2 = int(rows[row_n + 1] - shape[0] // 100)
                    for contour in cells_rect:
                        if functions.inside(contour, (x1, y1, x2, y2)):
                            data_cell = {'row': row_n, 'col': col_n,
                                          'content': tell_content(page_info, contour, image_orig.shape)}
                            if orientation == 1:
                                data_cell['row'] = col_count - 2 - col_n
                                data_cell['col'] = row_n
                            elif orientation == 2:
                                data_cell['row'] = row_count - 2 - row_n
                                data_cell['col'] = col_count - 2 - col_n
                            elif orientation == 3:
                                data_cell['row'] = col_n
                                data_cell['col'] = row_count - 2 - row_n
                            list_row_col.append(data_cell)
                            break

        # Else checking if the specified method is tesseract
        elif method == 'tesseract':
            contents = []

            for bound in cells_rect:
                x, y, w, h = bound
                contents.append(pytesseract.image_to_string(Image.fromarray(image_orig[y:(y + h), x:(x + w)])))

            for col_n in range(col_count - 1):
                x1 = int(cols[col_n] + shape[1] // 100)
                x2 = int(cols[col_n + 1] - shape[1] // 100)
                for row_n in range(row_count - 1):
                    y1 = int(rows[row_n] + shape[0] // 100)
                    y2 = int(rows[row_n + 1] - shape[0] // 100)
                    for contour, content in zip(cells_rect, contents):
                        if functions.inside(contour, (x1, y1, x2, y2)):
                            list_row_col.append({'row': row_n, 'col': col_n, 'content': content})
                            break

        df_list.append(functions.data_to_dataframe(list_row_col, col_count - 1, table_no, table))

    return df_list
