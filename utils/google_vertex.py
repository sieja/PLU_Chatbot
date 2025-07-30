import os
import streamlit as st
import vertexai

from typing import List, Optional
from vertexai.language_models import TextEmbeddingModel, TextEmbeddingInput
from langchain_google_vertexai import VertexAI
from vertexai.generative_models import GenerativeModel
#from utils.env import GOOGLE_PROJECT_ID, GOOGLE_LOCATION, GOOGLE_LLM_MODEL

GOOGLE_PROJECT_ID = "gen-lang-client-0452200199"
GOOGLE_LOCATION = "europe-west4"
GOOGLE_LLM_MODEL = "gemini-1.5-flash"


@st.cache_resource
def connect_llm():
    llm = VertexAI(
        model_name=GOOGLE_LLM_MODEL,
        project=GOOGLE_PROJECT_ID,
        temperature=1.5
    )
    return llm

@st.cache_resource
def connect_vertex_gen_model(system_instruction=None):
    vertexai.init(project=GOOGLE_PROJECT_ID)
    return vertexai.generative_models.GenerativeModel(GOOGLE_LLM_MODEL, system_instruction=system_instruction)

@st.cache_resource
def init_embedding_model():
    vertexai.init(project=GOOGLE_PROJECT_ID, location=GOOGLE_LOCATION)  # ou europe-west4 selon ta région
    model = TextEmbeddingModel.from_pretrained("textembedding-gecko-multilingual@001")
    return model

def embed_multiple_text(
    texts: list = None,
    task: str = "RETRIEVAL_DOCUMENT"
) -> List[List[float]]:
    """Embeds texts with a pre-trained, foundational model.
    Args:
        texts (List[str]): A list of texts to be embedded.
        task (str): The task type for embedding. Check the available tasks in the model's documentation.
        dimensionality (Optional[int]): The dimensionality of the output embeddings.
    Returns:
        List[List[float]]: A list of lists containing the embedding vectors for each input text
    """
    model = init_embedding_model()
    # inputs = [TextEmbeddingInput(text, task) for text in texts]
    max_document = 10 
    embeddings = []
    input_splitted = [texts[i:i+max_document] for i in range(0, len(texts), max_document)]

    for docs in input_splitted:
        input = [TextEmbeddingInput(doc, task) for doc in docs]
        embeddings.extend(model.get_embeddings(input))

    return [emb.values for emb in embeddings]


def embed_single_text(
        text: str,
        task: str = "RETRIEVAL_DOCUMENT"
    ) -> List[List[float]]:
    
    model = init_embedding_model()
    input = [TextEmbeddingInput([text], task)]
    embeddings = model.get_embeddings(input)

    return embeddings[0].values