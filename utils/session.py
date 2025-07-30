import streamlit as st


def init_state_variable(name: str, default):
    """
    Simplifie la création d'une variable du session_state
    """
    if name not in st.session_state:
        st.session_state[name] = default


def init_multiple_state_variables(dict_name_to_default: dict):
    """
    Simplifie la création de plusieurs variables du session_state
    """
    for name, default in dict_name_to_default.items():
        init_state_variable(name, default)

def clear_state_variable(dict_name_to_default: dict):
    """
    Reinitialise les variables du session_state
    """
    for name, default in dict_name_to_default.items():
        st.session_state[name] = default

