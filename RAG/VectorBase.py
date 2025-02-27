import os
from typing import List
import json
from RAG.Embeddings import BaseEmbeddings,OllamaEmbedding
import numpy as np
from tqdm import tqdm


class VectorStore:
    def __init__(self, document: List[str] = ['']) -> None:
        self.document = document

    def get_vector(self, EmbeddingModel: OllamaEmbedding) -> List[List[float]]:
        
        self.vectors = []
        for doc in tqdm(self.document, desc="Calculating embeddings"):
        # tqdm库对文档进行迭代，每个文档 doc 都会被逐个处理，并且进度条会在终端上显示“Calculating embeddings”作为描述
            self.vectors.append(EmbeddingModel.get_embedding(doc))
        return self.vectors

    def persistTexts(self, path: str = 'storage', name: str = "default"):
        if not os.path.exists(path):
            os.makedirs(path)
        with open(f"{path}/{name}.json", 'w', encoding='utf-8') as f:
            json.dump(self.document, f, ensure_ascii=False)

    def persistVectors(self, path: str = 'storage', name: str = "default"):
        if self.vectors:
            with open(f"{path}/{name}.json", 'w', encoding='utf-8') as f:
                # 打开一个名为 vectorsnomic.json 的文件进行写入，路径同样为之前指定的 path
                json.dump(self.vectors, f, ensure_ascii=False)
                # 将 self.vectors 数据以 JSON 格式写入该文件

    def persistZillizVectors(self, path: str = 'storage', name: str = "default"):
        if self.vectors:
            data = {"rows": []}
            for i, vector in enumerate(self.vectors):
                row = {
                    "primary_key": i,  # 使用 i 作为主键
                    "vector": vector  # 向量
                }
                data["rows"].append(row)
            with open(f"{path}/{name}.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False)

    def load_vector(self, path: str = 'storage', name : str = "default"):
        with open(f"{path}/{name}.json", 'r', encoding='utf-8') as f:
            self.vectors = json.load(f)
            # return self.vectors

    def load_text(self, path: str = 'storage', name : str = "default"):
        with open(f"{path}/{name}.json", 'r', encoding='utf-8') as f:
            self.document = json.load(f)
            # return self.document

    def get_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        return BaseEmbeddings.cosine_similarity(vector1, vector2)

    def query(self, query: str, EmbeddingModel: OllamaEmbedding, k: int = 1) -> List[str]:
        # 表示该函数的返回值类型是一个字符串列表
        query_vector = EmbeddingModel.get_embedding(query)  # 问题向量化
        result = np.array([self.get_similarity(query_vector, vector)
                          for vector in self.vectors])  # 计算问题与vectors的相似度
        return np.array(self.document)[result.argsort()[-k:][::-1]].tolist()
        # result.argsort()表示 result 数组中元素的索引，按升序排序。
        # [-k:]: 获取最后 k 个索引（即相似度最高的 k 个文档的索引）。
        # [::-1]: 将这些索引反转，以得到从高到低的顺序。
        # np.array(self.document): 将 self.document 转换为 NumPy 数组
        # tolist(): 将 NumPy 数组转换为 Python 列表

    def get_order(self, query: str, EmbeddingModel: OllamaEmbedding):
        query_vector = EmbeddingModel.get_embedding(query)  # 问题向量化
        result = np.array([self.get_similarity(query_vector, vector)
                    for vector in self.vectors])  # 计算问题与vectors的相似度
        #print(sorted(result, reverse=True)[:10])
        return result.argsort()

    def get_text(self, order, k: int = 1) -> List[str]:
        return np.array(self.document)[order[-k:][::-1]].tolist()