import os
import json
import numpy as np
import pandas as pd
import streamlit as st

from langchain.vectorstores import Chroma
from langchain_google_vertexai import VertexAIEmbeddings

from langchain_google_vertexai import ChatVertexAI
from langchain.chains import RetrievalQA
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

from utils.session import init_multiple_state_variables, clear_state_variable
from utils.widgets import ChatContainer, StreamedWrite, StyledContainer, StyleAnchor
ChatContainer.init()
StreamedWrite.init()

from utils.google_vertex import connect_llm

st.set_page_config(layout='wide')

COLLECTION_NAME = "CONVENTIONS_COLLECTIVES"
persist_path_directory="./chroma_db"

ROOT_pdf_path = os.path.join(os.getcwd(), 'utils', 'data')
pdf_path = os.path.join(ROOT_pdf_path, 'PLU-de-PORNIC_Reglement.pdf')
pdf_path_cleaned = os.path.join(ROOT_pdf_path, 'PLU-de-PORNIC_Reglement_processed.json')


with StyleAnchor("smaller-vertical-gap") as anchor_smaller_vertical_gap:
    anchor_smaller_vertical_gap.add_style('gap: 0.1em;', children_path='> div')
with StyleAnchor("white-padding") as anchor_white_padding:
    anchor_white_padding.add_style('padding: 5px; background-color: white;')
with StyleAnchor("datasets-listing") as anchor_datasets_listing:
    anchor_datasets_listing.add_style('background-color: rgba(255,255,255,0.35); justify-content: left;', children_path='> div button')
    anchor_datasets_listing.add_style('border-color: var(--yellow5); color: black; background-color: rgb(from var(--yellow5) r g b / 0.4);', children_path='> div button:hover')
    anchor_datasets_listing.add_style('border-color: var(--yellow5); color: black; background-color: rgb(from var(--yellow5) r g b / 0.3);', children_path='> div button:focus:not(:active)')
    anchor_datasets_listing.add_style('background-color: var(--yellow5); color: black;', children_path='> div button:active')
    anchor_datasets_listing.add_style('color: inherit;', children_path='> div button:disabled')
    anchor_datasets_listing.add_style('color: inherit;', children_path='> div button:disabled:hover')
    anchor_datasets_listing.add_style('align-content: center;', children_path='> div > div:has(button) > div:nth-child(2)')
with StyleAnchor("sticky-bottom-corner-container") as anchor_sticky_bottom_left:
    anchor_sticky_bottom_left.add_style('position: fixed; bottom: 0.6em; margin-left: -4.5em;')
    anchor_sticky_bottom_left.add_style('gap: 0.4em;', children_path='> div')
    anchor_sticky_bottom_left.add_style('font-size: 28px;', children_path='> div > div > div:last-child div:last-child button > div > p')
    anchor_sticky_bottom_left.add_style('background-color: var(--red6); color: white', children_path='> div > div > div:last-child div:last-child button:disabled')
with StyleAnchor("sticky-bottom-container") as anchor_sticky_bottom_container:
    anchor_sticky_bottom_container.add_style("""position: fixed; bottom: 0px; background-color: var(--green1); 
        color: black; display: flex; flex-direction: column; -moz-box-align: center; align-items: center; 
        border-radius: 10px; padding: 10px; margin-right: 5em; z-index: 100;
        width: -moz-available;/* Mozilla */ width: -webkit-fill-available;/* Chrome */ width: stretch;"""
    )
    anchor_sticky_bottom_container.add_style('font-size: 24px;', children_path='> div > div > div:last-child div:last-child button > div > p')
    anchor_sticky_bottom_container.add_style('background-color: rgba(255,255,255,0.3); justify-content: left; padding-left: 1em;', children_path='> div > div:nth-child(2) > details > div > div > div button')
    anchor_sticky_bottom_container.add_style('background-color: rgba(255,255,255,0.5); border-color: var(--blue1); color: black', children_path='> div > div:nth-child(2) > details > div > div > div button:hover')
    anchor_sticky_bottom_container.add_style('background-color: rgba(0,0,0,0.2); border-color: var(--blue1); color: black', children_path='> div > div:nth-child(2) > details > div > div > div button:active')
    anchor_sticky_bottom_container.add_style('border-color: var(--blue2);', children_path=' details')
    anchor_sticky_bottom_container.add_style('border-color: var(--blue2);', children_path=' details:hover')
    anchor_sticky_bottom_container.add_style('color: black;', children_path=' details > summary')
    anchor_sticky_bottom_container.add_style('color: black;', children_path=' details > summary:hover')
    anchor_sticky_bottom_container.add_style('fill: black;', children_path=' details > summary > svg')
with StyleAnchor("sticky-bottom-corner-container") as anchor_sticky_bottom_left:
    anchor_sticky_bottom_left.add_style('position: fixed; bottom: 0.6em; margin-left: -4.5em;')
    anchor_sticky_bottom_left.add_style('gap: 0.4em;', children_path='> div')
    anchor_sticky_bottom_left.add_style('font-size: 28px;', children_path='> div > div > div:last-child div:last-child button > div > p')
    anchor_sticky_bottom_left.add_style('background-color: var(--red6); color: white', children_path='> div > div > div:last-child div:last-child button:disabled')

colormap_notes = {
    1: '#ba0000',
    2: '#ff2f00',
    3: '#ff6900',
    4: '#ffb400',
    5: '#f0e600',
}

session_states = {
    "messages": [],
    "count": 0
}
init_multiple_state_variables(session_states)


def reset_session_state():
    st.session_state = None
    # st.session_state.reviews_list = None
    # st.session_state.selected_shop_name = None
    # st.session_state.selected_shop = None
    # st.session_state.summary = None
    # st.session_state.dict_clusters = {}

def display_history():
    for message in st.session_state.messages:
        if message["role"] == "user":
            with ChatContainer("user"):
                st.markdown(message['content'])
        elif message["role"] == "assistant":
            with ChatContainer("assistant"):
                st.markdown(message['content'])
            with st.expander(" > Sources utilisées"):
                st.write(message["source"])

st.markdown("""
Bienvenue ! Cet assistant est conçu pour répondre **uniquement** aux questions concernant la **convention collective Syntec**.

Posez vos questions dans le champ ci-dessous.
            TEST : Combien de congé par an ? 
""")

def init_embedding_model():
    return VertexAIEmbeddings(model="text-embedding-004", 
                            project="si-valeuriad-recette")

def chroma_exists(persist_directory):
    return os.path.exists(os.path.join(persist_directory, "index"))  # index/ is key folder

# Chargement et vectorisation des documents 
@st.cache_resource
def load_vectorstore():
    # Charge le document
    doc_list:List = json.load(open(pdf_path_cleaned))['pages']

    ## format Documents
    corpus = [Document(page_content=doc['content'], id=doc['page_number']) for doc in doc_list]


    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(corpus)

    embedding_model = init_embedding_model()

    # Créer chromaDB 
    vectordb = Chroma.from_documents(docs, embedding_model, persist_directory=persist_path_directory, collection_name=COLLECTION_NAME)
    vectordb.persist()

    return vectordb



# tester si la db existe deja ou non 
if not chroma_exists(persist_path_directory) :
    vectordb = load_vectorstore()
    vectordb.persist() 
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
else : 
    vectordb = Chroma(persist_directory=persist_path_directory, embedding_function=init_embedding_model())
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
 

# RAG avec Vertex AI
llm_chat=ChatVertexAI(model_name="gemini-1.5-flash-002", temperature=0.1, project="si-valeuriad-recette")

qa_chain = RetrievalQA.from_chain_type(
    llm=llm_chat,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)

with st.container():
    anchor_sticky_bottom_container.spawn()
    query = st.chat_input("Votre question:")
    st.session_state.count += 1

st.write("page", st.session_state.count)

with st.container():
    anchor_sticky_bottom_left.spawn()
    st.button(":material/delete_history:", type="primary", help="Supprimer l'historique de conversation", on_click=clear_state_variable, args=[session_states],disabled=len(st.session_state.messages) == 0)

if query:
    st.session_state.messages.append({"role":"user", "content": query})
    with st.spinner("Recherche en cours..."):
        result = qa_chain({"query": query})
        st.session_state.messages.append({"role":"assistant", "content": result['result'], "source": result['source_documents']})
        display_history()






