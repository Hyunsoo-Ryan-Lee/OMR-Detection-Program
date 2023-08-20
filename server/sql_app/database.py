from utils import mongoConnector

__all__ = ["db", "collection_user", "metadata", "answer", "result"]

client = mongoConnector.connect()
db = client["OMR"]
collection_user = db["users"]
metadata = db["metadata"]
answer = db["answer"]
result = db["result"]
