from collections import defaultdict
from importlib.metadata import distribution
from importlib.metadata import PackageNotFoundError
from importlib.metadata import requires
from importlib.metadata import version

from packaging.requirements import Requirement


def get_requirements(package):
    """
    This wraps `importlib.metadata.requires` to not be garbage.
    Parameters
    ----------
    package : str
        Package you want requirements for.
    Returns
    -------
    `dict`
        A dictionary of requirements with keys being the extra requirement group names.
    """
    requirements: list = requires(package)
    requires_dict = defaultdict(list)
    for requirement in requirements:
        req = Requirement(requirement)
        package_name, package_marker = req.name, req.marker
        if package_marker and "extra ==" in str(package_marker):
            group = str(package_marker).split("extra == ")[1].strip('"').strip("'").strip()
            requires_dict[group].append(package_name)
        else:
            requires_dict["required"].append(package_name)
    return requires_dict


def find_dependencies(package, extras=None):
    """
    List installed and missing dependencies.
    Given a package and, optionally, a tuple of extras, identify any packages
    which should be installed to match the requirements and return any which are
    missing.
    """
    requirements = get_requirements(package)
    installed_requirements = {}
    missing_requirements = {}
    extras = extras or ["required"]
    for group in requirements:
        if group not in extras:
            continue
        for package in requirements[group]:
            try:
                package_version = version(package)
                installed_requirements[package] = package_version
            except PackageNotFoundError:
                missing_requirements[package] = f"Missing {package}"
    return missing_requirements, installed_requirements


def missing_dependencies_by_extra(package, extras=None):
    """
    Get all the specified extras for a package and report any missing dependencies.
    This function will also return a "required" item in the dict which is the
    dependencies associated with no extras.
    """
    extras = extras or []
    requirements = get_requirements(package)
    missing_dependencies = {}
    for group in requirements.keys():
        if group in extras:
            missing_dependencies[group] = find_dependencies(package, [group])[0]
    return missing_dependencies
