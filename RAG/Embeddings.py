import os
from typing import List
import numpy as np
import ollama

os.environ['CURL_CA_BUNDLE'] = ''
from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())

class BaseEmbeddings:
    """
    Base class for embeddings
    """
    def __init__(self, path: str, is_api: bool) -> None:
        self.path = path
        self.is_api = is_api

    def get_embedding(self, text: str, model: str) -> List[float]:
        raise NotImplementedError

    @classmethod
    def cosine_similarity(cls, vector1: List[float], vector2: List[float]) -> float:
        """
        calculate cosine similarity between two vectors（余弦相似度）
        """
        dot_product = np.dot(vector1, vector2)
        magnitude = np.linalg.norm(vector1) * np.linalg.norm(vector2)  # 计算vector1与vector2的模的乘积
        if not magnitude:
            return 0
        return dot_product / magnitude

class OllamaEmbedding:
    def __init__(self, model_name: str = "nomic-embed-text") -> None:
        self.model_name = model_name

    def get_embedding(self, text: str) -> List[float]:
        response = ollama.embeddings(model=self.model_name, prompt= text.strip())

        return response['embedding']