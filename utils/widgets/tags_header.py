import streamlit as st


def tags_header(tags: list):
    """
    Widget barre de tags
    """
    associated_css = """<style>
        div:has(> div > div > div > button:disabled[kind="pills"]) {
            gap: 0em;
        }
        
        div:has(> button:disabled[kind="pills"]) {
            column-gap: 0.6em;
        }
        
        button:disabled[kind="pills"] {
            background-color: var(--red7);
            border-radius: 99px;
            height: 2em;
            font-size: 1.5em;
            color: white;
            border-color: var(--red5);
            cursor: inherit;
            padding-left: 0.9rem;
            padding-right: 0.9rem;
            padding-top: 2px;
            padding-bottom: 2px;
            height: fit-content;
        }
        
        button:disabled[kind="pills"]:hover {
            cursor: inherit;
            color: white;
            border-color: var(--red5);
        }
        
        button:disabled[kind="pills"] > span {
            width: 2rem;
            font-size: inherit;
        }
        
        button:disabled[kind="pills"] > span > span {
            font-size: inherit;
        }
        
        button:disabled[kind="pills"] > div {
            font-size: inherit;
        }
    </style>"""

    with st.container():
        st.markdown(associated_css, unsafe_allow_html=True)

        st.pills("tags associés", tags, label_visibility='collapsed', disabled=True)
