import posixpath

import pytest
import requests
from requests import HTTPError
from sphinx.builders.html import INVENTORY_FILENAME

from dkist_sphinx_theme.create_intersphinx_mapping import mapping_dict, create_intersphinx_mapping


REQUEST_TIMEOUT_S = 10.

def check_inv_exists(inv_location: str) -> bool:
    try:
        with requests.get(inv_location, timeout=REQUEST_TIMEOUT_S) as r:
            r.raise_for_status()
    except HTTPError:
        return False

    return True

def convert_single_mapping_to_inv_locations(mapping: tuple[str, None | str | tuple[str | None, ...]]) -> list[str]:
    project_url, inv_locations = mapping

    final_inv_locations = []
    match inv_locations:
        case None:
            final_inv_locations.append(posixpath.join(project_url, INVENTORY_FILENAME))
        case str():
            final_inv_locations.append(inv_locations)
        case tuple():
            for alt_location in inv_locations:
                final_inv_locations += convert_single_mapping_to_inv_locations((project_url, alt_location))
        case _:
            raise ValueError(f"{inv_locations = } has a type I don't recognize. This is probably a test setup issue.")

    return final_inv_locations

def get_package_latest_pypi_version(package_name: str) -> str:
    # Taken from https://github.com/romanzdk/latest-pypi-version/blob/main/latest_pypi_version/cli.py
    url = f"https://pypi.org/pypi/{package_name}/json"
    response = requests.get(url, timeout=REQUEST_TIMEOUT_S)
    if response.status_code == 200:
        return response.json()["info"]["version"]
    else:
        raise RuntimeError(f"Could not find most recent version of {package_name}. Response code: {response.status_code}")


class DummyDefaultDistribution():
    def __init__(self, pkg_name: str):
        self.requires = list(mapping_dict.keys())

class DummyVersionedDistribution():
    def __init__(self, pkg_name: str):
        self.requires = [f"{k}=={get_package_latest_pypi_version(k)}" for k in mapping_dict.keys() if k != "python"]

@pytest.mark.parametrize("dummy_distribution",
                         [pytest.param(DummyDefaultDistribution, id="non_versioned"),
                          pytest.param(DummyVersionedDistribution, id="versioned")])
def test_defined_default_mappings(dummy_distribution, mocker):
    """
    Given: The set of custom mappings defined in `create_intersphinx_mapping.mapping_dict`
    When: Trying to get an inventory file from each mapping
    Then: All mappings have at least one reachable inventory file
    """
    mocker.patch("dkist_sphinx_theme.create_intersphinx_mapping.distribution", new=dummy_distribution)

    full_mapping = create_intersphinx_mapping("doesnt_matter_bc_of_mock")
    for package, single_mapping in full_mapping.items():
        locations = convert_single_mapping_to_inv_locations(single_mapping)
        assert any([check_inv_exists(l) for l in locations]), f"Could not find any inventory for {package}"
