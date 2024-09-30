from google.cloud.firestore_v1 import AsyncClient, Client, DocumentSnapshot
from google.cloud.firestore_v1.query_results import QueryResultsList
from google.oauth2.service_account import Credentials

CREDENTIAL_PATH = "private/gallix-qa-firebase-adminsdk-pxcoi-4ec503dca4.json"

cred = Credentials.from_service_account_file(CREDENTIAL_PATH)

db = Client(credentials=cred)
async_db = AsyncClient(credentials=cred)

def get_async_db() -> AsyncClient:
    return async_db

def get_db() -> Client:
    return db

class DBService:
    def __init__(self) -> None:
        self.async_db = get_async_db()
    
    async def get_document(self, document_path: str) -> DocumentSnapshot:
        return await self.async_db.document(document_path).get()
    
    async def get_collection(self, collection_path: str) -> QueryResultsList[DocumentSnapshot]:
        return await self.async_db.collection(collection_path).get()
