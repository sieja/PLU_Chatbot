import time
import random

import streamlit as st

from utils.session import init_state_variable


class StreamedWrite(object):
    """
    Permet d'écrire du text en simulant un stream à partir d'un simple texte.
    La vitesse de défilement est configurable et une mémoire permet de ne par re-stream le text lorsque la page se
    rafraichie.
    Note : besoin d'appeler StreamedWrite.init() en début de page pour initialiser la mémoire
    Note : besoin d'appeler StreamWrite.reset_state_variables() pour réinitialiser la mémoire

    Exemple :
    >>> StreamedWrite.init()
    >>> ...
    >>> StreamedWrite("Ce message apparait lettre par lettre avec un délay de 0.1s entre chaque lettre", delay=0.1)
    >>> ...
    >>> if st.button("Réinitialiser ma session"):
    >>>     StreamedWrite.reset()
    """

    seed = random.Random(0)

    state_variable = 'custom_StreamedWrite_done'

    def __init__(self, text, delay=.01):
        """
        Construit l'objet

        :param text: texte à afficher
        :param delay: délai d'attente entre l'affichage de chaque lettre
        """
        self.uid = self.seed.random()
        self.text = text
        self.delay = delay

        init_state_variable(self.state_variable, [])

        if self.uid in st.session_state[self.state_variable]:
            st.write(self.text)
        else:
            st.write_stream(self.generator)
            st.session_state[self.state_variable].append(self.uid)

    def generator(self):
        for i in range(len(self.text)):
            yield self.text[i]
            time.sleep(self.delay)

    @classmethod
    def init(cls):
        """
        Initialise la class StreamedWrite pour la
        """
        cls.seed = random.Random(572948)

    @classmethod
    def reset(cls):
        """
        Reinitialise les états sauvegardés
        """
        st.session_state[cls.state_variable] = []
