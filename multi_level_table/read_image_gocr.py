import io

from google.cloud import vision
# from google.cloud.vision import types


def parse_image(image_file):
    """
    This function take the image_file as input and returns a list of dictionaries where each dictionary contains the
    information about each word in the form {x: , y: , content: }, where x is the distance, in pixels, of the center of
    the box containing the word, along the X-axis, y is the distance, in pixels, of the center of the box containing the
    word, along the Y-axis and content is the actual word.

    Input: image_file --> the path to the image to be read
    Output: a list of dictionaries containing information about each word
    """

    client = vision.ImageAnnotatorClient()

    with io.open(image_file, 'rb') as image_file:
        content = image_file.read()

    image = vision.Image(content=content)

    response = client.document_text_detection(image=image)
    document = response.full_text_annotation
    list_content = []
    for page in document.pages:
        for block in page.blocks:
            for paragraph in block.paragraphs:
                for word in paragraph.words:
                    w = ''
                    for symbol in word.symbols:
                        w += symbol.text
                    list_content.append({'x1': word.bounding_box.vertices[0].x,
                                         'y1': word.bounding_box.vertices[0].y,
                                         'x2': word.bounding_box.vertices[2].x,
                                         'y2': word.bounding_box.vertices[2].y,
                                         'content': w})
    return list_content


if __name__ == '__main__':
    import pickle
    page_info_90 = parse_image('photo_90.jpg')
    page_info_270 = parse_image('photo_270.jpg')
    with open('page_info90.pk', 'wb') as pkfile:
        pickle.dump(page_info_90, pkfile)
    with open('page_info270.pk', 'wb') as pkfile:
        pickle.dump(page_info_270, pkfile)