import boto3
import os
def handler(event,context):

    s3_client = boto3.client('s3')
    folder_name= os.environ.get('BUCKET_PREFIX')
    
    if event['RequestType'] == 'Create':
        return  s3_client.put_object(Bucket=os.environ.get('APPFLOW_BUCKET_NAME'), Key=(folder_name+'/'))
