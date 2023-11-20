from bs4 import BeautifulSoup


def scale(num, d, n):
    return num*n/d


def parse_html(html_file, page_no, img_shape):
    """
    This function takes html_file, page_no and img_shape as input and returns a list of dictionaries containing the
    information of the page 'page_no' where each dictionary contains the information about each word in the form
    {x: , y: , content: }, where x is the distance, in pixels, of the center of the box containing the word, along the
    X-axis, y is the distance, in pixels, of the center of the box containing the word, along the Y-axis and content is
    the actual word.

    Input: html_file --> the path to the html to be read
           page_no --> the page number to be read
           image_shape --> the shape of the image in the form (x, y) to scale x and y in each dictionary of the list to
                           be returned
    Output: a list of dictionaries containing information about each word
    """
    with open(html_file, 'r') as html:
        contents = html.read()
        soup = BeautifulSoup(contents, 'html.parser')
    page = list(soup.find_all('page'))[page_no-1]
    height = int(float(page['height']))
    width = int(float(page['width']))
    words = page.find_all('word')
    page_info = []
    for word in words:
        page_info.append({'x': scale(int(float(word['xmax'])) + int(float(word['xmin'])), width, img_shape[0])/2,
                          'y': scale(int(float(word['ymax'])) + int(float(word['ymin'])), height, img_shape[1])/2,
                          'content': word.text})

    return page_info
