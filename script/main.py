import boto3
import getopt
import json
import sys
import os

# Install aws credential
aws_keyid = os.getenv("AWS_KEYID")
aws_accesskey = os.getenv("AWS_ACCESSKEY")
aws_keypath = '/root/.aws/'
aws_file = 'credentials'
if not os.path.exists(aws_keypath):
    os.makedirs(aws_keypath)

f = open(os.path.join(aws_keypath, aws_file),'w')
f.write('[default]\n')
f.write(f'aws_access_key_id = {aws_keyid}\n')
f.write(f'aws_secret_access_key = {aws_accesskey}\n')
f.close()

# Get kaggle dataset name and s3 bucket
kaggle_dataname = ""
s3_bucket = ""
options, remainder = getopt.getopt(sys.argv[1:],'',['kaggle_dataname=','s3_bucket='])
for opt, arg in options:
    if opt == '--kaggle_dataname':
        kaggle_dataname = arg
    elif opt == '--s3_bucket':
        s3_bucket = arg
    
# Check if s3 bucket exists
s3 = boto3.resource('s3')
buckets = map(lambda s:s.name,s3.buckets.all())
if not s3_bucket in  buckets:
    print(f"{s3_bucket} does not exist in S3")
    exit(1)

# Download from kaggle
kaggle_downloadpath = '/kaggletmp'
if not os.path.exists(kaggle_downloadpath):
    os.makedirs(kaggle_downloadpath)
kaggle_downloadcmd = f'kaggle datasets download {kaggle_dataname} -p {kaggle_downloadpath}' 

status = os.system(kaggle_downloadcmd)
if status != 0:
    print(f"kaggle download failed! Please check the user/database:{kaggle_dataname} name is correct")
    exit(1)

status = os.system(f"unzip {kaggle_downloadpath}/*.zip -d {kaggle_downloadpath}")
if status != 0:
    print("kaggle file download or unzip failed!")
    exit(1)

os.system(f"rm {kaggle_downloadpath}/*.zip")

# Upload to s3 
for root, dirs, files in os.walk(kaggle_downloadpath):
    for name in files:
        data = open(os.path.join(kaggle_downloadpath,name), 'rb')
        s3.Bucket(s3_bucket).put_object(Key=name, Body=data)
        print(f"{name} is uploaded to S3")
        
os.system(f"rm -rf {kaggle_downloadpath}")    
