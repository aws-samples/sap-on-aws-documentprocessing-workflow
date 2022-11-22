import boto3
import io
import os
import json
import uuid


s3         = boto3.resource('s3')
s3client   = boto3.client('s3')

def handler(event,context):
    print(event)
    targetbucket = os.environ.get('APPFLOW_TARGET_BUCKET')
    prefix =  os.environ.get('APPFLOW_TARGET_BUCKET_PREFIX')
    jsonln = io.StringIO()

    # Create JSON lines from order items
    for item in event['orderitems']:
        json.dump(item.copy(),jsonln)
        jsonln.write('\n')
    
    # empty the bucket first 
    empty_bucket(bucketname=targetbucket)

    filename = ''.join([ prefix,
                            "/",
                            str(uuid.uuid4().hex[:6]),
                            ".jsonl"])

    object = s3.Object(targetbucket,filename)

    object.put(Body=jsonln.getvalue())

    print(jsonln.getvalue())

    return {
        "bucketname": targetbucket,
        "key": filename,
        "content": jsonln.getvalue()
    }

def empty_bucket(bucketname:str):
    bucket = s3.Bucket(bucketname)
    for object_summary in bucket.objects.filter():
        resp = s3client.delete_object(
            Bucket=bucket.name,
            Key=object_summary.key,
        )