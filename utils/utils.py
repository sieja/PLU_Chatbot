import re
import streamlit as st

import os
import json
import chromadb

from chromadb.utils import embedding_functions
from pydantic import BaseModel
from chromadb import Documents, EmbeddingFunction, Embeddings

from utils.google_vertex import init_embedding_model, embed_multiple_text

def get_corpus(filepath) -> list:
    docs: List = json.load(open(filepath))
    return docs

def extract_answer_for_user(response):
    return response.candidates[0].content.parts[0].text

def extract_json_answer(raw_string):
    cleaned = re.sub(r"```json|```", "", raw_string).strip()
    tmp = json.loads(cleaned)
    return tmp['is_answer'], tmp['text']


def from_chunks_to_chroma(json_path, persist_directory):
    # Charger le corpus
    with open(json_path, "r") as f:
        doc_list = json.load(f)
    texts = []
    metadatas = []
    ids = []
    for doc in doc_list:
        # Adapte selon la structure de ton JSON
        text = doc.get("text", doc.get("id", ""))
        texts.append(text)
        metadatas.append(doc)
        ids.append(doc.get("id", str(len(ids))))
    # Embedding
    embeddings = init_embedding_model(texts)
    
    # ChromaDB custom
    client = chromadb.PersistentClient(path=persist_directory)
    collection = client.get_or_create_collection("CONVENTIONS_COLLECTIVES")
    # Stocker dans Chroma
    collection.add(
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
        ids=ids
    )
    return collection


def retrieve_from_chroma(query_emb, collection, project_id="si-valeuriad-recette", model_name="text-embedding-004", k=3):

    # Recherche dans Chroma
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k
    )
    return results

# Chargement des informations de base des différents datasets existants
@st.cache_data
def get_dict_datasets(data_path):
    
    list_prepared_sets = os.listdir(data_path)
    list_prepared_sets = [o for o in list_prepared_sets if os.path.isdir(os.path.join(data_path, o))]
    dict_datasets = {
        folder: {
            "logo": os.path.join(data_path, folder, 'logo.webp'),
            "title": open(os.path.join(data_path, folder, 'title.txt')).read()
        }
        for folder in list_prepared_sets
    }
    return dict_datasets

def load_clean_convention(filepath) -> json:

    if os.path.isfile(filepath):
        doc_list:List = json.load(open(filepath))
        return doc_list

    else:
        st.write(f"Fichier introuvable, vérifier le chemin d'accès: {filepath}")


class MyEmbeddingFunction(EmbeddingFunction):
    def __call__(self, input: Documents) -> Embeddings:
        # embed the documents somehow
        embedding_model = init_embedding_model()
        st.write(f"len input : {len(input)}")
        max_length = 250 
        embeddings = []
        input_splitted = [input[i:i+max_length] for i in range(0, len(input), max_length)]
        
        for docs in input_splitted:
            embeddings.extend(embedding_model.get_embeddings(docs))

        return embeddings

@st.cache_resource
def init_chroma_client(persist_path_directory):
    return chromadb.PersistentClient(path=persist_path_directory)

def save_into_db(_corpus, persist_path_directory):
    collection = chromadb_collection_exist(persist_path_directory)
    if collection.count()==0:
        documents = _corpus.get_texts()
        embeddings = embed_multiple_text(
                documents,
                task= "RETRIEVAL_DOCUMENT"
            )
        collection.add(
            documents=documents,
            ids=_corpus.get_ids(),
            metadatas=_corpus.get_metadatas(),
            embeddings=embeddings
        )

def chromadb_collection_exist(persist_path_directory):
    client = init_chroma_client(persist_path_directory)
    collection = client.get_or_create_collection(
        st.session_state.convention_name,
        metadata={"hnsw:space": "cosine"}
    )
    return collection



