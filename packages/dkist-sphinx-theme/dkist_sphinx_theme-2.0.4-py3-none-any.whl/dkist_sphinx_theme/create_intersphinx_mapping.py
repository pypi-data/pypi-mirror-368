from dataclasses import dataclass
from importlib.metadata import distribution

from packaging.requirements import Requirement
from packaging.specifiers import Specifier


@dataclass
class MappingEntry:
    base_doc_url: str = None
    pri_inventory: str = None
    alt_inventory: str = None
    version_prefix: str = ""
    default_version: str = ""
    always_use_default: bool = False

    def doc_url_string(self, version: str):
        """
        Construct a base URL string for a documentation site given a version number.
        This is used to construct a cross-referencing map for sphinx (intersphinx_mapping).

        Parameters
        ----------
        version
            If this param is set, we are pinned to this version number.
            Pinning applies only to internal dkist repos for cross-referencing.
            For 3rd party libs we always use the default version

        Returns
        -------
        A string containing the doc URL for the selected version
        """
        if self.always_use_default or version == "":
            return self.base_doc_url + self.default_version
        else:
            return self.base_doc_url + self.version_prefix + version


# Cannot automate this part because the base_doc_url and version prefix may vary
mapping_dict = dict()

# DKIST repos/libraries
mapping_dict["dkist-processing-common"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/common/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-processing-core"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/core/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-processing-math"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/math/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-processing-pac"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/pac/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-processing-vbi"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/vbi/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-processing-visp"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/visp/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-header-validator"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/header-validator/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist-fits-specifications"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/data-products/en/",
    version_prefix="v",
    default_version="stable",
)
mapping_dict["dkist"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/python-tools/en/latest/",
    always_use_default=True,
)

# External libraries
mapping_dict["python"] = MappingEntry(
    base_doc_url="https://docs.python.org/3/",
    alt_inventory="http://www.astropy.org/astropy-data/intersphinx/python3.inv",
    always_use_default=True,
)
mapping_dict["numpy"] = MappingEntry(
    base_doc_url="https://numpy.org/doc/",
    alt_inventory="http://www.astropy.org/astropy-data/intersphinx/numpy.inv",
    default_version="stable",
    always_use_default=True,
)
mapping_dict["scipy"] = MappingEntry(
    base_doc_url="https://docs.scipy.org/doc/scipy/",
    alt_inventory="http://www.astropy.org/astropy-data/intersphinx/scipy.inv",
    always_use_default=True,
)
mapping_dict["matplotlib"] = MappingEntry(
    base_doc_url="https://matplotlib.org/",
    alt_inventory="http://www.astropy.org/astropy-data/intersphinx/matplotlib.inv",
    always_use_default=True,
)
mapping_dict["astropy"] = MappingEntry(
    base_doc_url="https://docs.astropy.org/en/stable",
    always_use_default=True,
)

# Rides the line b/t DKIST and external. Closer to DKIST in that we want to link to a versioned inventory
mapping_dict["solar-wavelength-calibration"] = MappingEntry(
    base_doc_url="https://docs.dkist.nso.edu/projects/solar-wavelength-calibration/en/",
    version_prefix="v",
    default_version="stable",
)


def create_intersphinx_mapping(pkg_name: str) -> dict:

    """
    For each library in the list:
        Determine the current version used in this deployment
        Create an intersphinx-mapping entry for the library
        If the version is pinned ('==') us that verrsion in the mapping
        Otherwise, use the default version for the mapping

    Parameters
    ----------
    pkg_name
        The name of the dkist-* repository we are processing

    Returns
    -------
    A dict of intersphinx-mapping entries

    """

    intersphinx_mapping = {}
    dist = distribution(pkg_name)
    req_strings = [item for item in dist.requires if "extra" not in item]
    for req_string in req_strings:
        req = Requirement(req_string)
        # Need to account for no version specified, meaning len(req.specifier) == 0
        req_spec = None
        req_op = None
        req_version = ""
        # Here a version is specified
        if len(req.specifier) > 0:
            # The version matters only if it is a pin, otherwise it is ignored
            for spec in req.specifier:
                req_spec = Specifier(str(spec))
                req_op = req_spec.operator
                # Are we pinned? If so, use the pinned version
                if req_op == "==":
                    req_version = req_spec.version
                    break  # probably not needed, as there should not be multiple reqs for ==
        # If this requirement is in the mapping_dict, then update
        # the intersphinx mapping dict for this requirement
        if req.name in mapping_dict:
            map_details = mapping_dict[req.name]
            inventory = mapping_dict[req.name].pri_inventory
            if map_details.alt_inventory is not None:
                inventory = (
                    mapping_dict[req.name].pri_inventory,
                    mapping_dict[req.name].alt_inventory,
                )
            intersphinx_mapping[req.name] = (
                mapping_dict[req.name].doc_url_string(req_version),
                inventory,
            )
    # Add python:
    name = "python"
    intersphinx_mapping[name] = (
        mapping_dict[name].base_doc_url,
        (
            mapping_dict[name].pri_inventory,
            mapping_dict[name].alt_inventory,
        ),
    )
    return intersphinx_mapping
