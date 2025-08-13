def test_import():
    """
    Given: the dkist_sphinx_theme package
    When: importing the features that are used by repos to build docs
    Then: the import doesn't fail
    """
    from dkist_sphinx_theme import conf
    from dkist_sphinx_theme.create_intersphinx_mapping import create_intersphinx_mapping
    assert True