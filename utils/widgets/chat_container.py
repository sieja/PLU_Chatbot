from typing import Literal

import streamlit as st

from utils.widgets import StyleAnchor


BASE_CHAT_CONTAINER_STYLE = """
div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"]){
  background-color: var(--yellow1);
  border-radius: 10px;
  width: 80%;
  max-width: 80%;
  padding-right: 16px;
  gap: 0px;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"]) div.stChatMessage > div:first-child {
  background-color: var(--yellow5);
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"]:not(.unrestrained)){
  width: fit-content;
}
div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"].fullwidth){
  width: 100%;
  max-width: 100%;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"]) h3 {
  padding-top: 0px;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"]) img {
  border-radius: 0px;
  width: 100%;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-assistant"]) > div > div > div > div > div > div > div > div > div > div > button {
  width: 100%;
  justify-content: left;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-user"]) {
  background-color: var(--green1);
  border-radius: 10px;
  max-width: 80%;
  margin-left: auto;
  gap: 0px;
  width: fit-content;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-user"]) div.stChatMessage {
  background-color: var(--green1);
  padding-right: 16px;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-user"]) div.stChatMessage > div:first-child {
  background-color: var(--blue2);
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-user"]:not(.unrestrained)){
  width: fit-content;
}
div:has(> div > div > div > div > div > div[custom-anchor="chat-container-user"].fullwidth){
  width: 100%;
  max-width: 100%;
}

div:has(> div > div > div > div > div > div[custom-anchor="chat-container-user"]) div.stChatMessage div.stMarkdown {
  color: black;
}
"""


class ChatContainer(object):
    """
    Container basé sur st.chat_message() avec une injection de style
    Note : besoin d'appeler ChatContainer.init() en début de page pour préparer l'injection du style (lazy)

    Exemple:
    >>> ChatContainer.init()
    >>> ...
    >>> with ChatContainer('assistant'):
    >>>     st.write("Je suis un assistant")
    >>> with ChatContainer('user', width="full"):
    >>>     st.write("Bonjour assistant")
    """

    STYLE_INITIALIZED = False

    def __init__(self, name: Literal["user", "assistant"], width: Literal["fit", "chat", "full"] = "fit"):
        """
        Construit d'objet chat et inject le css au besoin

        :param name: émetteur de la bulle de chat 'user' ou 'assistant'
        :param width: largeur de la bulle
            - "fit" la bulle se limite à la taille du contenu jusqu'à occuper 80% de la largeur du container parent au maximum
            - "chat" la bulle occupe 80% de la largeur du container parent
            - "full" la bulle occupe 100% de la largeur de container parent
        """
        self.name = name

        self.container_list = []

        element_name = f'chat-container-{self.name}'
        class_name = None
        if width == "chat":
            class_name = "unrestrained"
        if width == "full":
            class_name = "fullwidth"
        self.anchor = StyleAnchor(element_name, class_str=class_name)

        if not self.STYLE_INITIALIZED:
            with self.anchor:
                self.anchor.add_rules(BASE_CHAT_CONTAINER_STYLE)
            self.STYLE_INITIALIZED = True

    def __enter__(self):
        self.container_list.append(st.container())
        self.container_list[-1].__enter__()
        self.anchor.spawn()
        self.container_list.append(st.chat_message(self.name))
        self.container_list[-1].__enter__()

    def __exit__(self, *args, **kwargs):
        for i in range(len(self.container_list)):
            self.container_list[-i].__exit__(*args, **kwargs)

    @classmethod
    def init(cls):
        cls.STYLE_INITIALIZED = False
