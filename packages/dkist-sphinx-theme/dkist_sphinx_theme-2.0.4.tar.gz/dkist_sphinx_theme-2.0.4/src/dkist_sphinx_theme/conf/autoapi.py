from pathlib import Path

import dkist_sphinx_theme

autoapi_template_dir = Path(dkist_sphinx_theme.__file__).parent / "autoapi_templates"
autoapi_ignore = ["*tests*"]
autodoc_typehints = "description"
# WE must include the defaults if we customize otherwise the defaults get clobbered
autoapi_default_options = [
    "members",
    "undoc-members",
    "show-inheritance",
    "show-module-summary",
    "special-members",
    "imported-members",
]
# Customizations we want
autoapi_custom_options = [
    "show-inheritance-diagram",
]
autoapi_options = autoapi_default_options + autoapi_custom_options
