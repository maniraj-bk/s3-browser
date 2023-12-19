import logging
import boto3
from flask import Flask, make_response, redirect, render_template, request

logger = logging.getLogger()
logger.setLevel(logging.INFO)

app = Flask(__name__)

boto3.setup_default_session()
client = boto3.client("s3")
paginator = client.get_paginator("list_objects_v2")

def get_buckets():
    response = client.list_buckets()
    buckets = []
    for bucket in response['Buckets']:
        buckets.append(bucket['Name'])
    return buckets


def get_region(bucket):
    bucket_metadata = client.get_bucket_location(Bucket=bucket)
    if bucket_metadata.get('LocationConstraint') == None:
        bucket_metadata.pop('LocationConstraint')
    region = bucket_metadata.get('LocationConstraint', 'us-east-1')
    return region

@app.route("/", methods=["GET"])
def list_all_buckets():
    buckets = get_buckets()
    resp = {}
    for bucket in buckets:
        resp[bucket]=f'/bucket/{bucket}'
    return render_template("index.html", results=resp)

@app.route("/bucket/<string:bucket>/", methods=["GET"], defaults={"path": ""})
@app.route("/bucket/<string:bucket>/<path:path>", methods=["GET"])
def list(bucket ,path):
    path = path
    resp = list_s3_objects(bucket, path)
    for k,v in resp.items():
        resp[k] = f"/bucket/{bucket}/{v}"
    return render_template("index.html", results=resp)


@app.route("/bucket/<string:bucket>/redirect", methods=["GET"])
def redir(bucket):
    path = request.args.get("path")
    region = get_region(bucket)
    s3_client = boto3.client('s3', region_name=region)
    presigned_url = s3_client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket, 'Key': path},
            ExpiresIn=100
        )
    response = make_response(redirect(location=presigned_url))
    return response


@app.route("/health_check", methods=["GET"])
def health_check():
    return "success"


def list_s3_objects(bucket, path, delimiter="/"):
    l = {}
    response = paginator.paginate(Bucket=bucket, Delimiter=delimiter, Prefix=path)
    for items in response:
        for item in items.get("CommonPrefixes", []):
            prefix = item["Prefix"].split("/")[-2:-1][0]
            path = item["Prefix"]
            l[prefix] = path
        for item in items.get("Contents", []):
            key = item["Key"].split("/")[-1]
            l[key] = f"redirect?path={item['Key']}"
    l = dict(sorted(l.items(), key=lambda item: item[0], reverse=True))
    return l


if __name__ == "__main__":
    app.run(port=8000)
