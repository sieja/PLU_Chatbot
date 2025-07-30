import streamlit as st


class StyleAnchor(object):
    """
    Permet d'injecter du css puis de l'appliquer à différents containers de la page.
    1. créer l'object en tant que contexte avec 'with'
    2. '.add_style()' parametrer le style souhaité, applicable au container parent ou aux descendants
    3. relacher le contexte génère le css et l'injecte à la page
    3. '.spawn()' pour ajouter une ancre localement, permettant de cibler le container parent et y appliquer tous les styles associés
    
    Exemple:
    >>> with StyleAnchor("smaller-vertical-gap") as anchor_background_red:
    >>>     anchor_background_red.add_style('background: blue;', children_path='> div')
    >>>     anchor_background_red.add_style('color: red;', children_path='> div button')
    >>> # contexte relâché, css injecté
    >>> ...
    >>> with st.container():
    >>>     anchor_background_red.spawn()  # créer l'ancre de ciblage
    >>>     st.write("Texte dans un container au fond bleu")
    >>>     st.button('Bouton avec texte rouge')
    """

    def __init__(self, name, element_type="div", id_str=None, class_str=None, depth=7):
        """
        Construit l'objet permettant de construire le style et ajouter les ancres

        :param name: nom identifiant utilisé pour identifier l'élément css
        :param element_type: type de balise cible, généralement div
        :param id_str: id css à utiliser pour l'ancre
        :param class_str: class css à utiliser pour l'ancre
        :param depth: profondeur à laquelle se situe l'ancre par rapport au parent ciblé, inspecter la page générée lorsque la valeur par défaut ne fonctionne pas pour trouver la bonne valeur 
        """
        self.name = name
        self.element_type = element_type
        self.id_str = id_str
        self.class_str = class_str
        self.depth = depth

        self.style_rules = ''

    def get_css_selector(self, modifier=None, children_path=None):
        selector = self.element_type + ':has('
        if isinstance(self.depth, int):
            selector += '> div' * self.depth
        elif isinstance(self.depth, str):
            selector += self.depth
        if self.id_str is not None:
            selector += '#' + self.id_str
        if self.class_str is not None:
            selector += '.' + self.class_str
        selector += f'[custom-anchor="{self.name}"]'
        if modifier is not None:
            selector += ':' + modifier
        selector += ')'
        if children_path is not None:
            selector += children_path
        return selector

    def spawn(self):
        """
        Ajoute une ancre à la page. L'antre est utilisable pour cibler ses différents éléments parents et leurs enfants
        """
        with st.container():
            st.markdown(f'<div custom-anchor="hidden-container"></div>', unsafe_allow_html=True)

            div_id = "" if self.id_str is None else f'id="{self.id_str}"'
            div_class = "" if self.class_str is None else f'class="{self.class_str}"'
            st.markdown(f'<div {div_id} {div_class} custom-anchor="{self.name}"></div>', unsafe_allow_html=True)

    def add_style(self, content, modifier=None, children_path=None):
        """
        Ajouter des styles ciblant le container parent ou tout autre element enfant
        :param content: style css
        :param modifier: modifier css (e.g. 'hover' ou 'not(:hover)')
        :param children_path: chemin relatif pour cibler un element enfant, trouver le chemin souhaité avec l'inspection de la page web
        """
        selector = self.get_css_selector(modifier=modifier, children_path=children_path)
        style = '\n' + selector + '{' + content + '}'
        self.style_rules += style

    def add_rules(self, content):
        """
        Ajouter tout un style css aux règles à injecter. Le contenu doit être un css bien formaté, ciblant les directement l'ancre, ses parents et les enfants associés
        :param content: css bien correctement formaté
        """
        self.style_rules += content

    def apply_style(self):
        """
        Injecte le style css à la page web
        """
        with st.container():
            st.markdown(f'<div custom-anchor="hidden-container"></div>', unsafe_allow_html=True)
            st.markdown(f'<style>{self.style_rules}</style>', unsafe_allow_html=True)

    def __enter__(self):
        """
        Ouvre un contexte permettant d'automatiquement injecter le css résultant à sa cloture
        :return: 
        """
        return self

    def __exit__(self, *args, **kwargs):
        """
        Injecte le css résultant à la page
        """
        self.apply_style()
