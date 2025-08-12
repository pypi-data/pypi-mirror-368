
from s3_sdk import S3Client
# 创建 S3 客户端
s3 = S3Client(region='ap-northeast-1')

# 上传字节内容
s3.put_object('my-bucket', 'example.txt', b'Hello, S3!')

# 上传文件
s3.put_object_from_file('my-bucket', 'example.txt', '/path/to/example.txt')

# 下载文件
file_content = s3.download('my-bucket', 'example.txt')
with open('/path/to/downloaded_example.txt', 'wb') as f:
    f.write(file_content.read())

# 检查文件是否存在
exists = s3.exists('my-bucket', 'example.txt')
print(f"文件存在: {exists}")

# 生成临时下载链接
download_url = s3.generate_presigned_url('my-bucket', 'example.txt', 'get_object')
print(f"下载链接: {download_url}")