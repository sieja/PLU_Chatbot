from uuid import uuid4

import streamlit as st



class HiddenContainer(object):
    """
    Un simple container qui n'est pas affiché. Permet de cacher du contenu.
    S'utilise comme un contexte comme st.container

    Exemple:
    >>> with HiddenContainer():
    >>>     st.write('ne sera pas affiché')
    """

    def __init__(self):
        self.container_list = []

    def __enter__(self):
        self.container_list.append(st.container())
        self.container_list[-1].__enter__()

        st.markdown(f'<div custom-anchor="hidden-container"></div>', unsafe_allow_html=True)

    def __exit__(self, *args, **kwargs):
        for i in range(len(self.container_list)):
            self.container_list[-i].__exit__(*args, **kwargs)


class StyledContainer(object):
    """
    Permettant de simplement créer un container stylisé. Ajouter tout le style css souhaité lors de la création de l'objet.
    S'utilise comme un contexte comme st.container

    Exemple:
    >>> with StyledContainer(background_color='red', padding=42):
    >>>     st.write('hello world')
    """

    def __init__(self, **kwargs):
        """
        Toutes les cléfs-valeurs données seront converties en cléfs-valeurs du style css du container.
        Une simple conversion des cléfs est appliquée afin de convertir de python à css: les '_' seront convertis en '-'
        
        Note:
        - les cléfs seront converties de python vers css: '_' seront convertis en '-' (e.g. 'background_color' deviendra 'background-color').
        - les valeurs données en int deviendront des pixels.
        
        :param kwargs: ensemble de cléfs-valeurs pour le style, les valeurs données en int seront convertis en pixels
        """
        self.container_list = []

        self.dict_style = {}

        for k, v in kwargs.items():
            if v is not None:
                if isinstance(v, int):
                    v = f'{v}px'
            self.dict_style[k] = v

    def __enter__(self):
        self.container_list.append(st.container())
        self.container_list[-1].__enter__()

        uid = str(uuid4())
        with st.container():
            style = ''
            for k, v in self.dict_style.items():
                if v is None:
                    continue
                style += k.replace('_', '-') + ': ' + v + ';'
            st.markdown('<style>div:has(> div > div > div > div > div > div[custom-anchor="'+uid+'"]){'+style+'}</style>', unsafe_allow_html=True)
            st.markdown('<style>div:has(> div > div > div > div > div[custom-anchor="'+uid+'"]){display: none}</style>', unsafe_allow_html=True)
            st.markdown(f'<div custom-anchor="{uid}""></div>', unsafe_allow_html=True)

    def __exit__(self, *args, **kwargs):
        for i in range(len(self.container_list)):
            self.container_list[-i].__exit__(*args, **kwargs)
