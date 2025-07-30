from enum import Enum, StrEnum
import json
from typing import Optional, List, TypedDict

from pydantic import BaseModel, ValidationError
from chromadb import Embeddings, Metadata, IDs, Include
import streamlit as st


class Document(BaseModel):
    id: str
    text: str
    metadata: dict


class Corpus(BaseModel):
    documents: List[Document]

    @classmethod
    def from_json(cls, filepath):
        try:
            with open(filepath, 'r') as f:
                contents = json.load(f)

            if not isinstance(contents, list):
                raise ValueError("Le fichier JSON doit contenir une liste de documents.")
            
            documents = [Document(**c) for c in contents]

            return cls(documents=documents)
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            raise RuntimeError(f"Erreur lors du chargement du corpus : {e}")


    def get_ids(self):
        return[doc.id for doc in self.documents]

    def get_texts(self):
        return[doc.text for doc in self.documents]
    
    def get_metadatas(self):
        return[doc.metadata for doc in self.documents]


def embed(corpus, max_words=10000, overlap=100):
    corpus_chunked = []

    for document in corpus:

        if len(document.text.split()) < max_words:
            corpus_chunked.extend(
                Document(
                    id=document.id,
                    text=document.text,
                    metadata=document.metadata
                )
            )
        else:

            i = 0 
            for separator in range(0, corpus.text.split(), overlap):          
                corpus_chunked.extend(
                    Document(
                        id=document.id+f"{i}",
                        text=document.text[separator:separator+overlap],
                        metadata=document.metadata
                    )
                )
    return corpus_chunked

class QueryResult(TypedDict):
    ids: List[IDs]
    embeddings: Optional[List[Embeddings]]
    documents: Optional[List[List[Document]]]
    metadatas: Optional[List[List[Metadata]]]
    distances: Optional[List[List[float]]]
    included: Include


class GetResult(TypedDict):
    ids: List[str]
    embeddings: Optional[Embeddings]
    documents: Optional[List[Document]]
    metadatas: Optional[List[Metadata]]
    included: Include