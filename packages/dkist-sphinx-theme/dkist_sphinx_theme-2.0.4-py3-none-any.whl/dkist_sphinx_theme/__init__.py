""" DKIST Sphinx Theme """
from pathlib import Path
from sphinx.application import Sphinx

from pydata_sphinx_theme import utils

__all__ = ["get_html_theme_path"]


def get_html_theme_path():
    """
    Return list of HTML theme paths.
    """
    parent = Path(__file__).parent.resolve()
    return parent / "theme" / "dkist"


def default_navbar():
    return [
        ("Python Tools", "https://docs.dkist.nso.edu/projects/python-tools/", 3),
        ("Data Products", "https://docs.dkist.nso.edu/projects/data-products/", 3),
        ("Calibration", [
            ("Home", "https://docs.dkist.nso.edu/en/latest/calibration.html", 3),
            ("Core", "https://docs.dkist.nso.edu/projects/core", 3),
            ("Common", "https://docs.dkist.nso.edu/projects/common", 3),
            ("VBI", "https://docs.dkist.nso.edu/projects/vbi", 3),
            ("ViSP", "https://docs.dkist.nso.edu/projects/visp", 3),
            ("Cryo-NIRSP", "https://docs.dkist.nso.edu/projects/cryo-nirsp", 3),
            ("DL-NIRSP", "https://docs.dkist.nso.edu/projects/dl-nirsp", 3),
            ("Polarization, Analysis and Calibration", "https://docs.dkist.nso.edu/projects/pac", 3),
            ("Math", "https://docs.dkist.nso.edu/projects/math", 3),
            ("Wavelength Calibration", "https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/", 3),
        ]),
    ]


def update_config(app):
    """
    Update config with new default values and handle deprecated keys.
    """
    # By the time `builder-inited` happens, `app.builder.theme_options` already exists.
    # At this point, modifying app.config.html_theme_options will NOT update the
    # page's HTML context (e.g. in jinja, `theme_keyword`).
    # To do this, you must manually modify `app.builder.theme_options`.
    theme_options = utils.get_theme_options_dict(app)

    if not theme_options.get("sst_logo"):
        theme_options["sst_logo"] = "img/nso_logo.png"

    if not theme_options.get("navbar_links"):
        theme_options["navbar_links"] = default_navbar()

    if not theme_options.get("footer_links"):
        theme_options["footer_links"] = [
            ("DKIST Home Page", "https://nso.edu/telescopes/dki-solar-telescope/", 3),
            ("Help Desk", "https://nso.atlassian.net/servicedesk/customer/portals", 3),
            ("Chat", "https://app.element.io/#/room/#dki-solar-telescope:openastronomy.org", 3),
        ]

    if not theme_options.get("external_links"):
        theme_options["external_links"] = [
            {"name": "Data Portal", "url": "https://dkist.data.nso.edu"},
            {"name": "Help Desk", "url": "https://nso.atlassian.net/servicedesk/customer/portals"},
        ]

def update_html_context(app: Sphinx, pagename: str, templatename: str, context, doctree) -> None:
    """
    Update the jinja context before rendering the pages.
    """
    # This is a deep hack to default the main theme logo to the light and dark images.
    # We set this function to have a higher priority and then we set our default
    # if someone hasn't set `html_theme_options['logo']`.

    if not context.get("theme_logo", {}).get("image_light"):
        pathto = context.get("pathto")
        context["theme_logo"] = {
            "image_light": "img/dkist-logo-v5-blue-text.png",
            "image_dark": "img/dkist-logo-v5-white-text.png",
            "image_relative": {
                "light": pathto("_static/img/dkist-logo-v5-blue-text.png", resource=True),
                "dark": pathto("_static/img/dkist-logo-v5-white-text.png", resource=True),
            }
        }

    if context.get("favicon_url", "_static/img/sunpy_icon.svg") == "_static/img/sunpy_icon.svg":
        context["favicon_url"] = "_static/img/favico.ico"


def setup(app: Sphinx):
    # Register theme
    theme_dir = get_html_theme_path()
    app.add_html_theme("dkist", theme_dir)
    app.add_css_file("css/dkist.css", priority=650)

    app.connect("builder-inited", update_config, priority=100)
    app.connect("html-page-context", update_html_context, priority=600)

    return {
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
