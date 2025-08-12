import asyncio

from huibiao_framework.client import MinIOClient
from huibiao_framework.config import MinioConfig


# 进入智查的容器，有包huibiao_framework
# 智能容器名huibiao-general-pdf-bid-check-infer-integration-service
# 容器id要查：sudo docker ps |grep huibiao-general-pdf-bid-check-infer-integration-service
# 进入容器，sudo docker exec -it {容器id} /bin/bash
# 新建脚本test.py，也即是本脚本,修改下面的对象名和文件名
# python test.py
async def run():
    client = MinIOClient(secure=False)
    await client.init()
    print(await client.list_buckets())

    await client.download_file(
        bucket_name=MinioConfig.BUCKET_NAME,
        object_name="904d174a-2dd9-4b50-8a2c-43945c52a46c-1754014033.json",  # 对象名
        file_path="/logger/904d174a-2dd9-4b50-8a2c-43945c52a46c-1754014033.json",
    )
    # 容器/logger目录一般挂在到宿主机了，例如上海环境的/logger目录对应/data/deploy/dmx_deploy/logs/
    # 进入宿主机目录后，sz -by 904d174a-2dd9-4b50-8a2c-43945c52a46c-1754014033.json，即可下载到自己机器
    await client.close()


asyncio.run(run())
