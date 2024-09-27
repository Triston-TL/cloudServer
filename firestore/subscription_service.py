import asyncio  # Added to handle asynchronous tasks
from google.cloud.firestore import Client  # type: ignore
from typing import Callable

from .db_service import get_db


class SubscriptionService:
    def __init__(self) -> None:
        self.loop = asyncio.get_running_loop()
        self.db = get_db()
        self.create_handlers: dict[str, list[Callable]] = {}
        self.modify_handlers: dict[str, list[Callable]] = {}
        self.remove_handlers: dict[str, list[Callable]] = {}

    def on_create(self, collection_name: str):
        def decorator(func):
            if collection_name not in self.create_handlers:
                self.create_handlers[collection_name] = []
            self.create_handlers[collection_name].append(func)
            return func

        return decorator

    def on_modify(self, collection_name: str):
        def decorator(func):
            if collection_name not in self.modify_handlers:
                self.modify_handlers[collection_name] = []
            self.modify_handlers[collection_name].append(func)
            return func

        return decorator

    def on_remove(self, collection_name: str):
        def decorator(func):
            if collection_name not in self.remove_handlers:
                self.remove_handlers[collection_name] = []
            self.remove_handlers[collection_name].append(func)
            return func

        return decorator

    def subscribe_to_collection(self, collection_name: str):
        collection_ref = self.db.collection(collection_name)

        def on_snapshot(doc_snapshots, changes, read_time):
            for change in changes:
                if change.type.name == "ADDED":
                    for handler in self.create_handlers.get(collection_name, []):
                        asyncio.run_coroutine_threadsafe(handler(change.document), self.loop)  # Schedule async handler
                elif change.type.name == "MODIFIED":
                    for handler in self.modify_handlers.get(collection_name, []):
                        asyncio.run_coroutine_threadsafe(handler(change.document), self.loop)  # Schedule async handler
                elif change.type.name == "REMOVED":
                    for handler in self.remove_handlers.get(collection_name, []):
                        asyncio.run_coroutine_threadsafe(handler(change.document), self.loop)  # Schedule async handler

        return collection_ref.on_snapshot(on_snapshot)

    def subscribe_to_document(self, document_path: str):
        doc_ref = self.db.document(document_path)

        def on_snapshot(doc_snapshot, changes, read_time):
            if doc_snapshot.exists:
                print(f"Document data: {doc_snapshot.to_dict()}")
            else:
                print("Document does not exist!")

        return doc_ref.on_snapshot(on_snapshot)

    def unsubscribe(self):
        self.db.close()
