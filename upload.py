from RAG.zilliz_data_base import zilliz

CLUSTER_ENDPOINT = "YOUR CODE"
Token = "YOUR CODE"

Zilliz = zilliz(CLUSTER_ENDPOINT,Token)

Zilliz.insert('./DCstorage/titleVectors.json', 'YOUR COLLECTION', oringinal_len = 0)
Zilliz.insert('./DCstorage/summariseVectors.json', 'YOUR COLLECTION', oringinal_len = 0)