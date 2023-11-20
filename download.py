import boto3
from config import ACCESS_KEY, SECRET_KEY
import os

s3 = boto3.client('s3',aws_access_key_id = ACCESS_KEY,aws_secret_access_key = SECRET_KEY)

s3.download_file('jaano2','Content Engine/models/image/table/model_final.pth',os.path.abspath('.')+'/model_table_detection/model_final.pth')
