import io
import threading
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

secret_id = 'AKIDcq7HVrj0nlAWUYvPoslyMKKI2GNJ478z'
secret_key = '70xZrtGAwmf6WdXGhcch3gRt7hV4SJGx'
region = 'ap-chengdu'
config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
# 2. 获取客户端对象
client = CosS3Client(config)

bucket = 'yuekao-1254016670'


def upload_file(key: str, filedata: io.BytesIO):
    try:
        response = client.put_object(
            Bucket=bucket,
            Body=filedata,
            # Key=filename_md5,
            Key=key,
            StorageClass='STANDARD',
            EnableMD5=False
        )
        print(response)
        return True
    except Exception as e:
        print('ERROR:', e)
        return False


def upload_file_threaded(key: str, filedata: io.BytesIO, join=False):
    t = threading.Thread(target=upload_file, args=(key, filedata))
    t.setDaemon(True)
    t.start()
    if join:
        t.join()
