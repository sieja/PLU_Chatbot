import os
import json

import streamlit as st

import chromadb
import chromadb.utils.embedding_functions as embedding_functions

from tabs.nlp.faq_utils import (
    extract_answer_for_user,
    extract_json_answer,
    get_corpus,
    get_dict_datasets,
    load_clean_convention,
    save_into_db,
    chromadb_collection_exist
)
from tabs.nlp.faq_entities import Corpus, Document
from utils.storage import Storage
from utils.session import init_multiple_state_variables, clear_state_variable
from utils.theming import init_color_theme, add_logo_to_sidebar, add_background, set_page_title, set_page_tags
from utils.widgets import ChatContainer, StreamedWrite, StyledContainer, StyleAnchor

from utils.google_vertex import embed_single_text, embed_multiple_text, connect_vertex_gen_model

ChatContainer.init()
StreamedWrite.init()

st.set_page_config(layout='wide')
init_color_theme()
add_logo_to_sidebar()
add_background()
set_page_title(__file__[5:])
set_page_tags(__file__[5:])


storage = Storage(os.path.basename(__file__)[:-3])
storage.check_project_resources()

COLLECTION_NAME = "CONVENTIONS_COLLECTIVES"
persist_path_directory="./chromadb"
FILENAME_CLEAN = 'clean_convention.json'


import tabs.nlp.system_prompts as system_prompts
SYSTEM_PROMPT = system_prompts

llm = connect_vertex_gen_model()

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
    "convention_name": None,
    "selected_convention": None,
    "selected_prepared_folder": None,
    "loaded_convention": None,
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
                    if "source" in message:
                        anchor_smaller_vertical_gap.spawn()
                        st.write(message["source"])

st.markdown("""
Bienvenue ! Cet assistant est conçu pour répondre **uniquement** aux questions concernant la **convention collective Syntec**.
""")

N_TEST = 10

# ------------- Récupération doc ------------- 
# TODO : Ajout filename dynamique dans container
# Démarrage de la conversation
with ChatContainer("assistant"):
    StreamedWrite("Quelles conventions souhaitez vous interroger ?")
    dict_prepared_datasets = get_dict_datasets(
        storage.get_resource_directory('data')
    )
    with st.container():
        anchor_smaller_vertical_gap.spawn()
        anchor_datasets_listing.spawn()
        for name, d in dict_prepared_datasets.items():

            col_icon, col_button = st.columns([1.5, 10])
            with col_icon:
                st.image(d["logo"])

            with col_button:
                if st.button(d["title"], disabled=st.session_state.selected_convention is not None, use_container_width=True):
                    st.session_state.selected_convention = name
                    st.write(st.session_state.selected_convention)
                    st.rerun(scope='app')

    StreamedWrite("Souhaitez-vous importer votre propre convention ?")

    with st.container():
        anchor_smaller_vertical_gap.spawn()
        anchor_datasets_listing.spawn()

        col_icon, col_button = st.columns([1.5, 10])
        with col_icon:
            st.image('./assets/icons/page_document.png')

        with col_button:
            if st.button("Vos propres données", disabled=st.session_state.selected_convention is not None, use_container_width=True):
                st.session_state.selected_convention = "custom"
                st.rerun(scope='app')


if st.session_state.selected_convention is None:
    st.stop()

@st.fragment
def custom_convention_import():
    return []

if st.session_state.convention_name == "custom":
    with ChatContainer("user"):
        StreamedWrite("Je souhaite importez ma propre convention", delay=0.005)
    with ChatContainer("assistant", width="chat"):
        StreamedWrite("Très bien. Veuillez trouver ci-dessous le formulaire de chargement de données")
        # time.sleep(0.5)
        with st.expander('Import manuel de données'):
            st.session_state.convention_name = "custom"
            st.session_state.loaded_convention = custom_convention_import()
else:
    with ChatContainer("user"):
        d = get_dict_datasets(storage.get_resource_directory('data'))
        StreamedWrite(f"Charge moi les données *{d[st.session_state.selected_convention]['title']}*")
    with ChatContainer("assistant"):
        if st.session_state.convention_name != st.session_state.selected_convention:
            with st.spinner("Chargement des données en cours..."):
                st.session_state.dict_tables = {}

                prepared_folder = storage.get_resource_directory('data')
                st.session_state.selected_prepared_folder = str(os.path.join(prepared_folder, st.session_state.selected_convention))
                
                with open(os.path.join(st.session_state.selected_prepared_folder, 'info.json'), 'r') as info:
                    prepared_info = json.load(info)
                
                st.session_state.loaded_convention = load_clean_convention(
                                                                os.path.join(
                                                                    st.session_state.selected_prepared_folder, 
                                                                    FILENAME_CLEAN
                                                                    )
                                                                )

                st.session_state.convention_name = st.session_state.selected_convention

        StreamedWrite("Chargement complété.")
        st.markdown(open(os.path.join(st.session_state.selected_prepared_folder, 'description.md')).read())
        StreamedWrite("J'attends vos questions.")
    with st.container():
        anchor_smaller_vertical_gap.spawn()
        anchor_datasets_listing.spawn()
    anchor_datasets_listing.spawn()

    # docs = get_corpus(filepath)
    filepath=os.path.join(st.session_state.selected_prepared_folder, FILENAME_CLEAN)
    corpus = Corpus.from_json(filepath)
    # corpus.documents = corpus.documents
    save_into_db(corpus, persist_path_directory)


with st.container():
    anchor_sticky_bottom_container.spawn()
    query = st.chat_input("Votre question:")

    collection = chromadb_collection_exist(persist_path_directory)
    if query:

        result = llm.generate_content(SYSTEM_PROMPT.SYSTEM_PROMPT_EXTRACT_REQUEST.format(user_input=query))
        is_query, format_query = extract_json_answer(result.text)
        st.session_state.messages.append({"role":"user", "content": query})
        
        if is_query:

            
            query_embed = embed_multiple_text(
                                [format_query],
                                task= "RETRIEVAL_DOCUMENT"
                        )
            result = collection.query(
                query_embeddings=query_embed,
                n_results=5,
                include=["documents", "metadatas", "embeddings"]
            )
            user_input = f"\
                Question utilisateur: {format_query},\
                Liste de documents: {('/n').join(result["documents"][0])}\
                "
            with st.spinner("Recherche en cours..."):
                response = llm.generate_content(SYSTEM_PROMPT.SYSTEM_PROMPT_RI+user_input)
                
                st.session_state.messages.append({"role":"assistant", "content": response.text, "source":result["documents"][0]})
            
        else:
            st.session_state.messages.append({"role":"assistant", "content": format_query})
    
display_history()

with st.container():
    anchor_sticky_bottom_left.spawn()
    st.button(":material/delete_history:", type="primary", help="Supprimer l'historique de conversation", on_click=clear_state_variable, args=[session_states],disabled=len(st.session_state.messages) == 0)
    