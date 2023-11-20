from flask import Flask, jsonify, request
import inference_pdf
import inference_tabula
from async_pdf import save_pdf
import os
from shutil import rmtree
import logging
import pdb
logging.basicConfig(filename='./app.log', filemode='a', format='%(name)s - %(levelname)s - %(message)s')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def getJsonHandlerHealth():
    return jsonify({
        'response': 200
    })


@app.route('/get_pdf_tables', methods=['POST'])
def PostJsonHandlerLineTable():
    content = request.get_json()
    print(content)

    try:
        pdf_links = content['pdf_links']
        if not isinstance(pdf_links, list):
            return jsonify({
                'code': 404,
                'message': 'pdf in list not found ; try with ["xyz.pdf","abc.pdf"]'
            })
        else:
            if len(pdf_links) > 10 or len(pdf_links) == 0:
                return jsonify({
                    'code': 404,
                    'message': 'pdf list is empty or greater than 10'
                })
            else:
                os.mkdir(os.path.abspath('.') + '/pdf')
                pdf_paths = save_pdf(pdf_links)
    except:
        return jsonify({
            'code': 404,
            'message': 'No pdf found'
        })

    try:
        lines = content['lines']
    except:
        lines = 0

    method = 'google_vision'
    # method = 'tesseract'
    debug = 0
    try:
        if lines == 1:
            final_df = {}
            for i in pdf_paths:
                pdf_path = os.path.join(os.path.abspath('.'), 'pdf', i.split('/')[-1].split('.')[0] + '.pdf')
                df = inference_pdf.get_tables(pdf_path,debug,method)
                final_df[i] = df

            rmtree(os.path.abspath('.') + '/pdf')
            return jsonify({
                'code': 200,
                'data': final_df
            })

        elif lines == 0:
            final_df = {}
            for i in pdf_paths:
                pdf_path = os.path.join(os.path.abspath('.'), 'pdf', i.split('/')[-1].split('.')[0] + '.pdf')
                df = inference_tabula.get_tables_without_lines(pdf_path)
                final_df[i] = df

            rmtree(os.path.abspath('.') + '/pdf')
            return jsonify({
                'code': 200,
                'data': final_df
            })

        else:
            rmtree(os.path.abspath('.') + '/pdf')
            return jsonify({
                'code': 200,
                'data': {},
                'message': 'Not supported for tables without ocr and lines'
            })

    except Exception as e:
        logging.exception("Exception occurred")
        rmtree(os.path.abspath('.') + '/pdf')
        return jsonify({
            'code': 404,
            'message': 'Error!'
        })


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='3002')
