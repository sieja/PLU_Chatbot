import streamlit as st
from streamlit_theme import st_theme

from utils.widgets import StyleAnchor, HiddenContainer, tags_header
from tabs.pages_config import PAGES_DICT



def init_color_theme():
    """
    Injecte un css global à la page.
    Utilisé pour injecter des couleurs paramétrées et des règles globales
    """
    with HiddenContainer():
        page_style = """<style>
        :root {    
            --yellow1: #f9d66b;
            --yellow2: #fae192;
            --yellow3: #fcebb7;
            --yellow4: #fdf5db;
    
            --yellow5: #e49d1c;
    
            --blue1: #232d4e;
            --blue2: #5d657c;
            --blue3: #959aa9;
            --blue4: #cacdd4;
    
            --pink1: #f4a396;
            --pink2: #f8bbb1;
            --pink3: #f8c5bd;
            --pink4: #fde8e5;
    
            --green1: #68bfbb;
            --green2: #92cfcd;
            --green3: #9ad1ce;
            --green4: #dcefee;
    
            --grey1: #dcefee;
            --grey2: #f3f5f7;
            --grey3: #fbfbfc;
            --grey4: #ffffff;
    
            --red1: #ff5b3f;
            --red2: #ff7a63;
            --red3: #e99182;
            --red4: #d9a59c;
    
            --red5: #e4452a;
            --red6: #e8b0b0;
            --red7: #ff4b4b;
        }
        
        /* Limite la page et ignore ce qui est afficher en dehors (ex. barre de titre) */
        section.stMain {max-width: 100%; overflow-x: hidden;}
        
        /* Style pour cacher tous le HiddenContainer */
        div:has(> div > div > div > div > div[custom-anchor="hidden-container"]){gap: 0px; max-height: 0px; display: none;}
        
        </style>"""
        st.markdown(page_style, unsafe_allow_html=True)


def _get_theme_assets():
    with HiddenContainer():
        theme = st_theme()

        dict_assets = {
            'dark': {
                'logo': './assets/Valeuriad_logo_haut_gris-v2.svg',
                'header': './assets/Logo-Long-Blanc-sans-baseline.svg'
            },
            'light': {
                'logo': './assets/Valeuriad_logo_haut_bleu-v2.svg',
                'header': './assets/Logo-Long-Bleu-sans-baseline.svg'
            },
        }


        theme_base = theme['base'] if theme is not None else "light"
        theme_assets = dict_assets.get(theme_base, dict_assets['light'])
        return theme_assets


def add_logo_to_sidebar():
    """
    Ajoute le logo Valeuriad dans la sidebar
    """
    with HiddenContainer():
        theme_assets = _get_theme_assets()

        st.logo(theme_assets['logo'], size='large', icon_image=theme_assets['logo'])
        st.markdown('''<style>
            section.stSidebar > div > div > img[data-testid="stLogo"] {
                height: 6.5rem;
                margin: 15% auto 5% 20%;
            }
            </style>
            ''', unsafe_allow_html=True)

    return theme_assets


def set_page_title(page_uri):
    """
    Affiche bare-titre
    """
    title = PAGES_DICT.get(page_uri, {}).get('title')

    if title is None:
        st.error('Titre non trouvé')

    with StyleAnchor("title-header") as anchor_title:
        anchor_title.add_style('gap: 0px;', children_path='> div')
        anchor_title.add_style('position: sticky; top: 3.75em; z-index: 100;')
        anchor_title.add_style('position: relative; left: -3em; background-color: var(--blue1); border-radius: 50px; color: white; width: 140%; max-width:200%', children_path='> div:last-child')
        anchor_title.add_style('padding-left: 2em;', children_path='> div:last-child > div')
        anchor_title.add_style('margin-bottom: 0rem;', children_path='> div:last-child > div > div > div')

    with st.container():
        anchor_title.spawn()
        st.title(title)


def set_page_tags(page_uri):
    """
    Affiche les tags
    """
    tags = PAGES_DICT.get(page_uri, {}).get('tags', None)

    if tags is None:
        st.error('Tags non trouvés')

    tags_header(tags)


def add_background():
    """
    Affiche le fond de page
    """
    storage = Storage('theme_assets')
    storage.check_project_resources(force=True)

    with StyleAnchor("test-image") as anchor_test_image:
        anchor_test_image.add_style('gap: 0px;', children_path='> div')
        anchor_test_image.add_style('position: absolute;')
        anchor_test_image.add_style('overflow: hidden;', children_path=' div.stImage')
        anchor_test_image.add_style('position: fixed; left: 5em; top: 12em; width: 110%; filter: opacity(60%); z-index: -1;', children_path="> div > div:last-child > div > div > div:last-child > div > img")

    with st.container():
        anchor_test_image.spawn()
        st.markdown("<style>div#root > div > div > div {background: none;}</style>", unsafe_allow_html=True)
        st.image(storage.get_resource_path('background/motif1.png'), use_container_width=True, width=2000)
