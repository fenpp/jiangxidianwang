from pymilvus import MilvusClient, DataType
from RAG.utils import Read_json
import pymilvus.bulk_writer
import json
import sys
# 数据库及检索
class zilliz:
    def __init__(self,CLUSTER_ENDPOINT,TOKEN):
        self.uri = CLUSTER_ENDPOINT,
        self.token = TOKEN
        self.client = MilvusClient(
            uri=CLUSTER_ENDPOINT,
            token=TOKEN)

    def create_collection(self,collection_name,demension):
        self.client.create_collection(
            collection_name=collection_name,
            dimension=demension)

    def get_vector_bulk_writer(self,read_path,storage_path):
        # '../storage/vectorsnomic.json'
        data_from_json = Read_json(read_path).get_content()

        # 确定需要导入数据的目标 Collection 的 Schema
        schema = MilvusClient.create_schema(
            auto_id=False,
            enable_dynamic_field=True
        )

        schema.add_field(field_name="id", datatype=DataType.INT64, is_primary=True)
        schema.add_field(field_name="vector", datatype=DataType.FLOAT_VECTOR, dim=len(data_from_json[0]))
        # schema.add_field(field_name="scalar_1", datatype=DataType.VARCHAR, max_length=1024)
        # schema.add_field(field_name="scalar_2", datatype=DataType.INT64)

        schema.verify()

        # 将原始数据按行添加到缓存中，然后将缓存中的数据存入一个指定格式的本地文件中
        writer = pymilvus.bulk_writer.LocalBulkWriter(
            schema=schema,
            # local_path=r'D:\desktop\研究生\江西省电力项目\TinyRAG-master\storage_bulk_writer',
            local_path=storage_path,
            segment_size=512 * 1024 * 1024, # default value
            file_type=pymilvus.bulk_writer.BulkFileType.JSON
        )

        for i in range(0,len(data_from_json)):
            vector_chunk = data_from_json[i]  # 二维列表中第i行
            # print(vector_chunk[0])

            for j in (0,len(vector_chunk)-1):
                vector_f=[]
                vector_f.append(float(vector_chunk[j]))  # 转换为浮点数

            writer.append_row({
                "id": i,
                "vector": vector_chunk

            })

        writer.commit()


    def get_search(self,collection_name,query_vector,limit_num):
        # Single_vector_search方法
        answer=self.client.search(
            collection_name=collection_name,  # target collection
            data=query_vector,  # query vectors
            limit=limit_num)
        return answer

    def insert(self,read_path,collection_name,oringinal_len):
        spinner = ['|', '/', '-', '\\']
        try:
            with open(read_path, 'r') as file:
                data_from_json = json.load(file)
        except json.JSONDecodeError:
            data_from_json = []
            print("----Zilliz未发现向量新增项----")

        for i in range(len(data_from_json)):
            sys.stdout.write(f'\r{spinner[i % 4]} 正在上传{round(i / len(data_from_json) * 100, 2):.2f}%...')  # \r 会将光标移到行首，覆盖上一行
            sys.stdout.flush()
            data = {
                "primary_key": i + oringinal_len,
                "vector": data_from_json[i]
            }

            res = self.client.upsert(
                collection_name=collection_name,
                data=data
            )
            #print(res)
        sys.stdout.write('\r--上传成功!--\n')  # \r 会将光标移到行首，覆盖上一行
        sys.stdout.flush()

