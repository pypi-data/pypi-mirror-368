import importlib

import graphviz
from docutils import nodes
from docutils.parsers.rst import directives
from sphinx.ext.graphviz import figure_wrapper
from sphinx.ext.graphviz import graphviz as graphviz_node
from sphinx.ext.graphviz import latex_visit_graphviz
from sphinx.ext.graphviz import man_visit_graphviz
from sphinx.ext.graphviz import render_dot_html
from sphinx.ext.graphviz import texinfo_visit_graphviz
from sphinx.ext.graphviz import text_visit_graphviz
from sphinx.util.docutils import SphinxDirective


def _refine_color(color):
    """
    Converts color in #RGB (12 bits) format to #RRGGBB (32 bits), if it possible.

    Parameters
    ----------
    color
        Text representation of color
    Returns
    -------
    Refined representation of color

    Converts color in #RGB (12 bits) format to #RRGGBB (32 bits), if it possible.
    Otherwise, it returns the original value. Graphviz does not support colors in #RGB format.

    """
    if len(color) == 4 and color[0] == "#":
        color_r = color[1]
        color_g = color[2]
        color_b = color[3]
        return "#" + color_r + color_r + color_g + color_g + color_b + color_b
    return color


def get_workflow(fqn):
    index = fqn.rfind(".")
    module = importlib.import_module(fqn[:index])
    return getattr(module, fqn[index + 1 :])


def render_workflow(workflow, urls=None) -> graphviz.Digraph:
    """
    Renders the workflow object to the DOT object.

    Parameters
    ----------
    workflow
        The workflow to be rendered
        NB: Adding a typehint requires importing dkist-processing-core.
        Do we want that dependency?

    Returns
    -------
    Graphviz object
    """
    urls = urls or {}

    dot = graphviz.Digraph(
        workflow.workflow_name,
        graph_attr={
            "rankdir": "TB",
            "labelloc": "t",
            "ratio": "auto",
            "fontname": "Sans",
            "size": '"8.0, 10.0"',
        },
    )
    for node in workflow.nodes:
        full_task_name = node.task.__module__ + "." + node.task.__name__
        url_attributes = {}
        if full_task_name in urls:
            url_attributes = {"URL": urls[full_task_name], "target": '"_top"'}

        dot.node(
            node.task.__name__,
            _attributes={
                "shape": "rectangle",
                "style": "filled,rounded",
                "color": _refine_color("#000"),
                "fillcolor": _refine_color("#FFF"),
                "fontname": "Sans",
                "size": "7",
                "tooltip": full_task_name,
                **url_attributes,
            },
        )
        for upstream in node.upstreams:
            dot.edge(upstream.__name__, node.task.__name__)
    return dot


class workflow_graph(graphviz_node):
    pass


class WorkflowGraph(SphinxDirective):
    required_arguments = 1
    optional_arguments = 0
    final_argument_whitespace = True
    option_spec = {
        "caption": directives.unchanged,
    }

    def generate_refnodes(self, workflow):
        """
        This generates a list of nodes which will be converted to URLs at a
        later stage in the sphinx build process.
        """
        refnodes = []
        for node in workflow.nodes:
            full_task_name = node.task.__module__ + "." + node.task.__name__
            class_role = self.env.get_domain("py").role("class")
            ref, _ = class_role(
                "class", f":class:`{full_task_name}`", full_task_name, 0, self.state
            )
            refnodes += ref
        return refnodes

    def run(self):
        # There are two rendering paths for this graphviz object:

        # The first one for everything that isn't a HTML output is to render
        # the full dot source code here and then set that as node['code'] the
        # graphviz extension then handles the rendering of that for us.

        # The second is for HTML where while we generate the dot source (we
        # don't know what the renderer is here), but it isn't used, instead the
        # node['workflow'] object and the refnodes are used to delay rendering
        # the dot source code until the point in the sphinx build pipeline
        # where we know the HTML URLs for the tasks (which is
        # html_visit_workflow_graph below) before we pass it off to the
        # graphviz extension.

        workflow_obj = get_workflow(self.arguments[0])
        dot = render_workflow(workflow_obj)
        node = workflow_graph()
        # Add the refnodes as child nodes of the graph, they are never
        # rendered, but they are processed by sphinx to convert them into
        # actual URLs
        node.extend(self.generate_refnodes(workflow_obj))
        node["code"] = dot.source
        node["workflow"] = workflow_obj
        node["options"] = {"docname": self.env.docname}

        if "caption" not in self.options:
            self.add_name(node)
            return [node]
        else:
            figure = figure_wrapper(self, node, self.options["caption"])
            self.add_name(figure)
            return [figure]


def html_visit_workflow_graph(self, node: workflow_graph) -> None:
    """
    Output the graph for HTML.  This will insert a PNG with clickable
    image map.
    """
    # Create a mapping from fully-qualified class names to URLs.
    graphviz_output_format = self.builder.env.config.graphviz_output_format.upper()
    current_filename = self.builder.current_docname + self.builder.out_suffix
    urls = {}
    for child in node:
        if child.get('refuri') is not None:
            # Construct the name from the URI if the reference is external via intersphinx
            if not child.get('internal', True):
                refname = child['refuri'].rsplit('#', 1)[-1]
            else:
                refname = child['reftitle']

            urls[refname] = child.get('refuri')
        elif child.get('refid') is not None:
            if graphviz_output_format == 'SVG':
                urls[child['reftitle']] = current_filename + '#' + child.get('refid')
            else:
                urls[child['reftitle']] = '#' + child.get('refid')

    dotcode = render_workflow(node["workflow"], urls=urls).source
    render_dot_html(self, node, dotcode, node["options"], filename=node.get("filename"))
    raise nodes.SkipNode


def setup(app):
    app.setup_extension("sphinx.ext.graphviz")
    app.add_node(
        workflow_graph,
        html=(html_visit_workflow_graph, None),
        latex=(latex_visit_graphviz, None),
        texinfo=(texinfo_visit_graphviz, None),
        text=(text_visit_graphviz, None),
        man=(man_visit_graphviz, None),
    )
    app.add_directive("workflow_diagram", WorkflowGraph)
