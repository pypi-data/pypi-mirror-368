from abc import ABC, abstractmethod
from typing import List

from fastapi import FastAPI, UploadFile


class BaseRAG:
    def __init__(
        self,
        vector_store,
    ):
        pass

    def ingest(self):
        pass

    def query(self):
        pass

    def start_api(self, port, host) -> FastAPI:
        app = FastAPI()

        @app.post("/ingest")
        async def ingest_endpoint(file: UploadFile):
            self.ingest(file)
            return {"status": "success"}

        @app.get("/query")
        async def query_endpoint(q: str):
            return self.query(q)

        @app.get("/logs")
        def logs_endpoint():
            return self.logger.get_logs()

        return app


class BaseChunker(ABC):
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    @abstractmethod
    def chunk(self, text: str) -> List[str]:
        """
        Split input text into chunks.
        Must be implemented by subclasses.
        """
        pass
