from contracts.loader import loader
import boto3
import os




class LoaderS3(loader):
    @classmethod
    def load(cls, file_path: str, s3_key: str):
        try:
            s3 = boto3.client(
                "s3",
                aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
                aws_session_token=os.getenv("AWS_SESSION_TOKEN"),
                region_name=os.getenv("AWS_DEFAULT_REGION"),
            )
            bucket_name = os.getenv("AWS_BUCKET_SONG_NAME")
            s3.upload_file(file_path, bucket_name, s3_key)
            print(f"✅ Subido: {file_path} → s3://{bucket_name}/{s3_key}")
        except Exception as e:
            print("error {e}")
