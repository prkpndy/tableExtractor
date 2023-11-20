import subprocess as sp
from os import listdir
from os.path import isfile, join
import numpy as np
from skew_correct import skew_correct
from multi_level_table import get_page_data, read_html
import json
import argparse


def get_tables(file_path, debug, method):

    """
    This function takes the PDF file_path as input and does the following:
        converts the PDF file pages to images and save them to the directory data_<PDF file name>/photo
        generates the HTML of the PDF and save it to the directory data_<PDF file name>/photo
        calls the multi_level_table.get_page_data() for all the pages to get the tables data in that page
        data for all the pages is stored in a dictionary which is saved in JSON format

    Input : file_path --> PDF file path
            debug --> True/False indicating whether to save the intermediate images for debugging or not
            method --> google_vision/tesseract indicating which method to use for OCR
    Output : dictionary format of page[col1:[values]....]
    """
    name = file_path.split('/')[-1].split('.')[0]
    sp.run(['mkdir', 'pdf/data_' + name])
    sp.run(['mkdir', 'pdf/data_' + name + '/photo'])
    sp.run(['mkdir', 'pdf/data_' + name + '/html'])

    if debug:
        sp.run(['rm', '-r', 'pdf/test'])
        sp.run(['mkdir', 'pdf/test'])

    image_path = 'pdf/data_' + name + '/photo/'
    html_path = 'pdf/data_' + name + '/html/'
    sp.run(['pdftoppm', '-jpeg', '-r', str(250), file_path, image_path + 'photo'])
    sp.run(['pdftotext', '-bbox-layout', file_path, html_path + 'html.html'])

    image_files = [f for f in listdir(image_path) if isfile(join(image_path, f))]

    num = range(1, len(image_files) + 1)
    l = int(np.floor(np.log10(len(num)))) + 1
    image_files = []
    for n in num:
        image_files.append('photo-' + '0' * (l - len(str(n))) + str(n) + '.jpg')

    print(image_files)

    for page_no, im_f in enumerate(image_files, 1):
        if len(read_html.parse_html(html_path+'html.html', page_no, (0, 0))) < 5:
            skew_correct.correct_skew(im_f, image_path)

    data_frame = []

    for page_no, file in enumerate(image_files, 1):
        data_frame.append(get_page_data.get_data(name, image_path + file, html_path + 'html.html',
                                                 page_no, method, debug))

    data = {}

    for page_no, df in enumerate(data_frame):
        page_dict = {}

        if not df:
            data['page_' + str(page_no)] = page_dict
            continue

        for table in df:
            table_dict = {}
            cols = list(table['content'].columns)
            tab = {}
            for col in cols:
                tab[col] = list(table['content'][col])
            table_dict['content'] = tab
            table_dict['bbox'] = table['bbox']
            page_dict['table_'+str(table['table_no'])] = table_dict

        data['page_'+str(page_no)] = page_dict

    with open("pdf/data_" + name + "/ans.json", "w") as f:
        json.dump(data, f)

    return data


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='debug')
    parser.add_argument("--debug", default=0, type=int, help="debug")
    args = parser.parse_args()
    debug = args.debug
    df = get_tables('data/Districtwise_Hospital_IsoBeds.pdf', debug, method="google_vision")
