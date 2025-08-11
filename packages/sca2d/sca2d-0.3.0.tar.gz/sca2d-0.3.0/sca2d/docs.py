"""Create API documentation for OpenSCAD code."""

import os
import shutil
import posixpath

from lark.lexer import Token
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
from jinja2 import Environment, PackageLoader
from markdown import markdown

from sca2d import utilities
from sca2d import scadclasses
from sca2d.generate import ImageGenerator

API_DIR = "api"


class Documentation:
    """Generate HTML API documentation from OpenSCAD source files.

    This class handles parsing docstrings, formatting, and rendering SCAD source files
    into styled HTML documentation using Markdown, syntax highlighting, and
    Jinja2 templates.
    """

    def __init__(self, analyser, scad_files, args):
        """Initialise the documentation generator with project configuration.

        Sets up templating, syntax highlighting, and image generation tools
        needed to build a complete HTML documentation set.

        :param analyser: Analyser object used to extract scopes and definitions
        :param scad_files: List of SCAD file paths to process
        :param args: Argparse namespace with CLI configuration
        """
        self.analyser = analyser
        self.scad_files = scad_files
        self.project_title = args.project
        self._out_dir = "scad_docs"
        self._api_dir = os.path.join(self._out_dir, API_DIR)
        self._pygments_lexer = get_lexer_by_name("openscad")
        self._pygments_formatter = HtmlFormatter(cssclass="source")
        self._pygments_inline_formatter = HtmlFormatter(cssclass="source", nowrap=True)
        self._source_root = self._get_root()
        self._jinja_env = Environment(loader=PackageLoader("sca2d"))
        self._md_ext = [
            "markdown.extensions.attr_list",
            "markdown.extensions.fenced_code",
        ]
        self._img_gen = ImageGenerator(self._source_root, self._out_dir)
        self.images = []
        # Track the current state of doc processing. Eventually may want to change
        # To nested object.
        self._state = {"active_file": None, "active_definition": None}

    @property
    def image_generator(self):
        """The image generator object for the docs."""
        return self._img_gen

    def build(self):
        """Build the full HTML documentation set.

        This method prepares the output directories and generates all documentation
        pages from the given SCAD source files using templates and formatting tools.

        It does not generate the images. This should be done later. Using the
        `image_generator` property of this class.
        """
        self._prepare_dirs()
        self._create_docs()

    def _prepare_dirs(self):
        """Create and clean output directories for documentation files.

        Deletes any existing API output directory and recreates it to ensure
        a clean environment for generating fresh documentation.
        """
        if os.path.isdir(self._api_dir):
            shutil.rmtree(self._api_dir)
        os.makedirs(self._api_dir)

    def _create_docs(self):
        """Generate all documentation pages from SCAD source files.

        Renders the index page and individual documentation pages for each SCAD
        file using Jinja2 templates and data collected from the Analyser.
        """
        template = self._jinja_env.get_template("index.html.jinja")
        file_title = "API Index"
        html = template.render(
            project_title=self.project_title,
            page_title=file_title,
            breakable_page_title=to_breakable_html(file_title),
            rel_root=".",
            doc_paths=self._all_files_rel_to_root(),
            style=self._pygments_formatter.get_style_defs(),
        )
        index_path = os.path.join(self._out_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as html_file:
            html_file.write(html)
        for scad_file in self.scad_files:
            self._state["active_file"] = scad_file
            scope = self.analyser.get_scope_from_file(scad_file)
            self._write_file_docs(scope, scad_file)
        self._state["active_file"] = None

    def _write_file_docs(self, scope, scad_file):
        """Write the HTML documentation for a single SCAD file.

        Render the documentation page for the given scope and SCAD file using a
        Jinja2 template. Creates necessary directories if they don't exist, and
        save file to disk.

        :param scope: The analysed outerscope object for the scad file. This contains
            both the definitions and their associated docs
        :param scad_file: Path to the SCAD file being documented
        """
        out_path = self._get_scad_out_path(scad_file)
        file_title = self._get_rel_path(scad_file)
        template = self._jinja_env.get_template("apidocs_page.html.jinja")
        rel_root, doc_paths = self._all_paths_rel_to(scad_file)
        html = template.render(
            project_title=self.project_title,
            page_title=file_title,
            breakable_page_title=to_breakable_html(file_title),
            rel_root=rel_root,
            doc_paths=doc_paths,
            style=self._pygments_formatter.get_style_defs(),
            file_docs=self._format_docs(scope.docs, for_file=True),
            definitions=self._definition_data(scope),
        )
        dir_path = os.path.dirname(out_path)
        if not os.path.isdir(dir_path):
            os.makedirs(dir_path)
        with open(out_path, "w", encoding="utf-8") as html_file:
            html_file.write(html)

    def _definition_data(self, scope):
        """Collect formatted data for all definitions in the given scope.

        Process each definition to generate syntax-highlighted signatures,
        formatted documentation, and highlighted source code.

        Most of the "magic" happens in `_format_docs()` and `_highlighted_definition`

        :param scope: The analysed scope object containing definitions

        :returns: List of dictionaries with definition data for rendering
        """

        definition_data = []
        for definition in scope.definitions:
            self._state["active_definition"] = definition.name
            definition_data.append(
                {
                    "id": definition.name,
                    "breakable_id": to_breakable_html(definition.name),
                    "signature": self._highlighted_definition(definition, scope),
                    "docs": self._format_docs(definition.docs),
                    "source": self._highlighted_source(definition, scope),
                }
            )
        self._state["active_definition"] = None
        return definition_data

    def _format_docs(self, docs, for_file=False):
        """Format documentation strings into HTML using Markdown.

        Process:

        * Parameter definitions
        * Return statements
        * Assertions
        * SCAD code blocks

        for rich HTML rendering. Skip parameter, return, and assert replacements if
        formatting file-level docs.

        :param docs: Raw documentation string to format
        :param for_file: Flag indicating if formatting for the docstring at the top of
            a file. (default False)

        :returns: HTML string of formatted documentation
        """
        if docs is None:
            return ""
        if not for_file:
            docs = self._replace_param_defs(docs)
            docs = self._replace_returns(docs)
            docs = self._replace_asserts(docs)

        docs = self._replace_scad_blocks(docs)
        return markdown(docs, extensions=self._md_ext)

    def _replace_param_defs(self, docs):
        """Replace parameter definitions in docs with formatted HTML blocks.

        Find all parameter definitions using regex and convert them into
        markdown-rendered HTML with styled argument names.

        :param docs: Raw documentation string containing parameter definitions

        :returns: Documentation string with formatted parameter blocks
        """
        matches = utilities.PARAM_REGEX.findall(docs)
        for match in matches:
            # strip out trailing new lines
            initial_str = match[0].rstrip()
            arg = match[1]
            arg_info = remove_following_indentation(match[2])
            # Add variable back to the markdown in a named HTML span
            arg_md = f'<span class="arg-name">{arg}:</span>{arg_info}'
            arg_html = markdown(arg_md, extensions=self._md_ext)
            def_html = f'<div class="arg-definition">{arg_html}</div>'
            docs = docs.replace(initial_str, def_html)
        return docs

    def _replace_returns(self, docs):
        """Replace return statements in docs with formatted HTML blocks.

        Find all return statement blocks and convert them into markdown-rendered HTML
        with styled return headings.

        :param docs: Raw documentation string containing return statements

        :returns: Documentation string with formatted return information
        """
        matches = utilities.RETURN_REGEX.findall(docs)
        # There should only be one. SCA2D should warn if more, but will process all
        for match in matches:
            # strip out trailing new lines
            initial_str = match[0].rstrip()
            return_info = remove_following_indentation(match[1])
            # Add variable back to the markdown in a named HTML span
            arg_md = f'<span class="return-heading">Returns:</span>{return_info}'
            arg_html = markdown(arg_md, extensions=self._md_ext)
            def_html = f'<div class="return-info">{arg_html}</div>'
            docs = docs.replace(initial_str, def_html)
        return docs

    def _replace_asserts(self, docs):
        """Replace assert statements in docs with formatted HTML blocks.

        Find all assert blocks and convert them into markdown-rendered HTML with
        styled assertion headings and syntax highlighting.

        :param docs: Raw documentation string containing assert statements

        :returns: Documentation string with formatted assertion information
        """
        matches = utilities.ASSERT_REGEX.findall(docs)
        for match in matches:
            # strip out trailing new lines
            initial_str = match[0].rstrip()
            assertion = highlight(
                match[1], self._pygments_lexer, self._pygments_inline_formatter
            )
            return_info = remove_following_indentation(match[2])
            # Add variable back to the markdown in a named HTML span
            arg_md = f'<span class="assert-heading">assert <span class="source">({assertion})</span>:</span>{return_info}'
            arg_html = markdown(arg_md, extensions=self._md_ext)
            def_html = f'<div class="assert-info">{arg_html}</div>'
            docs = docs.replace(initial_str, def_html)
        return docs

    def _replace_scad_blocks(self, docs):
        """Replace SCAD code blocks in docs with highlighted HTML or examples.

        Find all SCAD code blocks and convert them into syntax-highlighted
        HTML.

        For example blocks, generate a SCAD source file that can be used to create
        an image and embed corresponding markdown. The SCAD is saved to disk in
        the `_examples` folder. The image identifier is appended to `self.images`.

        The image generator used to create images from these identifiers is
        accessible via the `image_generator` property.

        :param docs: Raw documentation string containing SCAD blocks

        :returns: Documentation string with formatted SCAD code and examples
        """
        matches = utilities.SCAD_BLOCK_REGEX.findall(docs)
        for i, match in enumerate(matches):
            html_scad = highlight(
                match[3], self._pygments_lexer, self._pygments_formatter
            )
            if match[1] == "example":
                img_md = self._generate_example(match, i)
                html_scad += f"\n\n{img_md}"
            docs = docs.replace(match[0], html_scad)
        return docs

    def _generate_example(self, match, example_index):
        """Create a SCAD file for an example and return markdown to embed its image.

        Generate a SCAD source file for the example snippet, cache its identifier
        in `self.images` for later image generation or retrieval, and return
        markdown that embeds the corresponding image.

        :param match: Regex match tuple containing example details
        :param example_index: Index of the example within the current definition

        :returns: Markdown string for embedding example image once generated
        """
        scad_file = self._state["active_file"]
        rel_source = self._get_rel_path(scad_file)
        example_ident = self._state["active_definition"] + f"--{example_index}"
        file_ident = self._img_gen.gen_image_scad_file(
            match[3],
            example_ident,
            rel_source,
        )
        customisers = match[2].strip().split()
        self.images.append((file_ident, customisers))
        # The dir of this html file
        html_dir = os.path.dirname(self._get_scad_out_path(scad_file))
        png_path = self._img_gen.ident_to_png_path(file_ident)
        png_rel_url = posixpath.normpath(posixpath.relpath(png_path, html_dir))
        return f"![{example_ident}]({png_rel_url})"

    def _highlighted_definition(self, definition, scope):
        """Format and syntax-highlight a definition signature.

        Generate a formatted string representation of the definition's signature
        and apply syntax highlighting for display in the documentation.

        :param definition: The function or module definition object
        :param scope: The outer scope containing the parse tree

        :returns: HTML string with syntax-highlighted definition signature
        """
        as_text = format_def(definition, scope.scad_code)
        return highlight(as_text, self._pygments_lexer, self._pygments_formatter)

    def _highlighted_source(self, definition, scope):
        """Extract and syntax-highlight the source code for a definition.

        Retrieve the source code corresponding to the definition's parse tree
        within the outer scope and apply syntax highlighting for documentation display.

        :param definition: The function or module definition object
        :param scope: The outer scope containing the parse tree and source code

        :returns: HTML string with syntax-highlighted source code of the definition
        """
        as_text = utilities.get_text_from_tree(scope.scad_code, definition.tree)
        return highlight(as_text, self._pygments_lexer, self._pygments_formatter)

    def _get_rel_path(self, input_path):
        """Return the path relative to the source root.

        Calculate the relative filesystem path from the source root directory
        to the given input path.

        :param input_path: The file path to be converted, either absolute or relative
            to the working directory.

        :returns: Path string relative to the source root
        """
        return os.path.relpath(input_path, self._source_root)

    def _get_scad_out_path(self, input_path, absolute=True):
        """Return the path to the output HTML file for a SCAD file.

        Compute the output HTML path corresponding to the given SCAD input file.
        If `absolute` is False, return a path relative to the output directory
        (not the API directory).

        :param input_path: Path to the source SCAD file
        :param absolute: Whether to return an absolute path (default True)

        :returns: Path string to the output HTML file for the SCAD file
        """
        # Relative path to the input file in the root source dir
        rel_path = os.path.relpath(input_path, self._source_root)
        # Same path with extension changed to html (this file won't exist)
        rel_path_html = os.path.splitext(rel_path)[0] + ".html"
        # Abs path to html in the API dir of the docs
        out_abs_path = os.path.join(self._api_dir, rel_path_html)
        if absolute:
            return out_abs_path
        return os.path.relpath(out_abs_path, self._out_dir)

    def _all_paths_rel_to(self, input_path):
        """Return posix-style paths for URLs relative to the given input page.

        Calculate relative URLs and identifiers for all SCAD files as seen
        from the directory containing `input_path`.

        :param input_path: The file path from which to calculate relative URLs

        :returns: Tuple containing the relative root path and a list of dictionaries
                  with file identifiers, breakable IDs, and URLs
        """
        dir_path = os.path.dirname(input_path)
        # Relative path to the api dir from this file.
        api_root = posixpath.normpath(os.path.relpath(self._source_root, dir_path))
        rel_root = posixpath.normpath(posixpath.join(api_root, ".."))
        files = []
        for scad_file in self.scad_files:
            html_file = os.path.splitext(scad_file)[0] + ".html"
            rel_html_file = os.path.relpath(html_file, dir_path)
            ident = self._get_rel_path(scad_file)
            files.append(
                {
                    "id": ident,
                    "breakable_id": to_breakable_html(ident),
                    "url": posixpath.normpath(rel_html_file),
                }
            )
        return rel_root, files

    def _all_files_rel_to_root(self):
        """Return posix-style paths for URLs relative to the root docs directory.

        Generate a list of dictionaries with file identifiers, breakable IDs,
        and URLs for all SCAD files relative to the root of the documentation output.

        :returns: List of dictionaries with file IDs, breakable IDs, and URLs
        """
        files = []
        for scad_file in self.scad_files:
            html_file = os.path.splitext(scad_file)[0] + ".html"
            rel_html_file = os.path.join(
                ".", API_DIR, os.path.relpath(html_file, self._source_root)
            )
            ident = self._get_rel_path(scad_file)
            files.append(
                {
                    "id": ident,
                    "breakable_id": to_breakable_html(ident),
                    "url": posixpath.normpath(rel_html_file),
                }
            )
        return files

    def _get_root(self):
        """Determine the common root directory for all SCAD source files.

        Identify the longest shared directory path prefix among all SCAD files,
        which serves as the root source directory.

        :returns: Path string of the common root directory
        """
        split_files = [fpath.split(os.sep) for fpath in self.scad_files]
        for i, directory in enumerate(split_files[0]):
            if all([split_file[i] == directory for split_file in split_files]):
                if i == 0:
                    root = directory
                else:
                    root = os.path.join(root, directory)
            else:
                break
        # If there is only one file in the dir, the above code will identify the full
        # file path.
        if os.path.isfile(root):
            return os.path.dirname(root)
        return root


def format_default(arg, scad):
    """Format the default value of a keyword argument into a string.

    Convert the default value of a keyword argument to its string representation,
    handling special SCAD built-in values appropriately.

    :param arg: The Variable object containing the default value
    :param scad: The source SCAD code

    :returns: String representation of the default value
    """
    scad_builtins = ["undef", "false", "undef"]
    var_type = arg.default.data
    if var_type in scad_builtins:
        return var_type
    tree = arg.default
    if len(tree.children) == 1 and isinstance(tree.children[0], Token):
        return tree.children[0].value
    return utilities.get_text_from_tree(scad, tree)


def format_args(args, scad):
    """Format a list of arguments into strings suitable for a definition signature.

    Convert each argument into a string, including default values for keyword
    arguments.

    :param args: List of Variable objects for each argument.
    :param scad: The source SCAD code

    :returns: List of formatted argument strings
    """
    arg_strings = []
    for arg in args:
        if arg.is_kwarg:
            arg_strings.append(f"{arg.name}={format_default(arg, scad)}")
        else:
            arg_strings.append(arg.name)
    return arg_strings


def format_def(definition, scad):
    """Format a function or module definition into a signature string.

    Generate a string representing the definition's signature, including its name
    and formatted argument list. Format with line breaks if the signature is long.

    :param definition: The function or module definition object
    :param scad: The source SCAD code

    :returns: Formatted signature string of the definition
    """
    args = format_args(definition.arguments, scad)
    if isinstance(definition, scadclasses.FunctionDef):
        start = f"function {definition.name}("
    elif isinstance(definition, scadclasses.ModuleDef):
        start = f"module {definition.name}("
    else:
        raise TypeError("Unknown definition type.")

    formatted = start + ", ".join(args) + ")"
    if len(formatted) > 99:
        formatted = start + "\n    " + ",\n    ".join(args) + "\n)"
    return formatted


def remove_following_indentation(md):
    """Remove indentation from lines after the first in a markdown string.

    For parameter docstrings, lines after the first are often indented by four spaces.
    This function removes those leading spaces to enable proper markdown parsing.

    :param md: The markdown string with possible indentation

    :returns: Markdown string with indentation removed
    """
    lines = md.split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            continue
        if line.startswith("    "):
            lines[i] = line[4:]
    return "\n".join(lines)


def to_breakable_html(string):
    """Insert `<wbr>` tags after underscores, hyphens, and slashes to allow word breaks.

    Modify the input string to include word break opportunities at common delimiters,
    improving text wrapping in HTML displays. This is needed for the sidebar navigation.

    :param string: The input string to modify

    :returns: The modified string with `<wbr>` tags inserted
    """
    return string.replace("_", "_<wbr>").replace("-", "-<wbr>").replace("/", "/<wbr>")
