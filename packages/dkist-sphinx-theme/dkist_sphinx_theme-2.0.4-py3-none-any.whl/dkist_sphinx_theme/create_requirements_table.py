from importlib.metadata import distribution
from importlib.metadata import version

from docutils import nodes
from docutils.parsers.rst import Directive
from packaging.requirements import Requirement


class RequirementsTable(Directive):

    required_arguments = 1
    optional_arguments = 0
    has_content = False

    def run(self):
        pkg_name = self.arguments[0]

        # Start with the main package:
        record = "# Main package:\n"
        record += f"{pkg_name} == {version(pkg_name)}\n\n"

        # Now the dependencies
        record += "# Dependencies:\n"
        # Get the dependencies for the main package
        dep_reqs = self.get_requirements(pkg_name)
        # Get the set of dkist* dependencies
        dkist_deps = set([name for name in dep_reqs if name.startswith("dkist")])
        # Find any additional dependencies for the dkist packages
        for name in dkist_deps:
            dep_reqs.update(self.get_requirements(name))
        # Remove the dkist dependencies from the general set of pkg reqs
        dep_reqs.difference_update(dkist_deps)
        for name in sorted(dkist_deps):
            # Add this package to the output record
            record += f"{name} == {version(name)}\n"
        # Add the package dependencies to the output record
        for name in sorted(dep_reqs):
            record += f"{name} == {version(name)}\n"

        literal = nodes.literal_block(record, record)
        literal["language"] = "none"
        return [literal]

    @staticmethod
    def get_requirements(pkg_name: str) -> set:
        req_names = []
        req_strings = distribution(pkg_name).requires
        for req_string in req_strings:
            if "extra" not in req_string:
                req_names.append(Requirement(req_string).name)
        return set(req_names)


def setup(app):
    app.add_directive("requirements_table", RequirementsTable)

    return {"parallel_read_safe": True, "parallel_write_safe": True}
