"""
This module defines the OuterScope class. This is the main class needed by
sca2d to analyse the scad code.
"""

import os
from copy import copy
import re
from sca2d.scope import ScopeContents
from sca2d import utilities
from sca2d.scadclasses import (
    UseIncStatment,
    DummyTree,
    DummyToken,
    Variable,
    ModuleDef,
    FunctionDef,
)
from sca2d.messages import Message
from sca2d.definitions import SCAD_VARS, SCAD_MODS, SCAD_FUNCS, CustomArgDef
from sca2d.patterns import GLOBAL_PATTERN
from sca2d.utilities import SCAD_BLOCK_REGEX, VALID_EXAMPLE_CUSTOMISERS

DOCSTRING_REGEX = re.compile(r"^(\s*)\/\*(.*?)\*\/", re.DOTALL)


class OuterScope(ScopeContents):
    """
    This is a child class of ScopeContents but is the only class you should
    need to create. It will recursively create ScopeContents for each internal
    scope. Compared to all other ScopeContents classes it has some extra variables
    for storing used and included files as well as the filename of the file being
    analysed.

    To finish the SCAD2D analysis run OuterScope.analyse_tree this will create
    or find OuterScope objects for all included files and then run the final tests
    on all internal scopes.
    """

    def __init__(self, tree, scad_code, filename):
        self._filename = filename
        self._used_files = []
        self._included_files = []
        self._scad_code = scad_code
        self._docs = None
        # Find the position of each line ending
        self._locate_line_endings()
        # This will begin parsing the tree for this file and all sub trees
        # See ScopeContents._parse_scope
        super().__init__(tree, None, top_level=True)
        self._set_docstrings()
        # Disable warnings on unused methods, functions, or variables in outer scope run
        # after __init__ so it is not re-written
        self._this_scope_disabled_messages.append("W2007")
        self._this_scope_disabled_messages.append("W2008")
        self._this_scope_disabled_messages.append("W2009")
        if len(tree.children) == 0:
            # must use dummy tree as the meta element "start" has no line or column
            self._record_message("W1003", DummyTree(data="start", line=1, column=1))

    @property
    def filename(self):
        """
        Returns the name of the file this outer scope represents.
        """
        return self._filename

    @property
    def scad_code(self):
        """
        Returns the contents of the scad file.
        """
        return self._scad_code

    @property
    def used_files(self):
        """
        Returns a list of the files used as UseIncStatment objects.
        """
        return copy(self._used_files)

    @property
    def included_files(self):
        """
        Returns a list of the files included as UseIncStatment objects.
        """
        return copy(self._included_files)

    @property
    def definitions(self):
        """All module and function definitions."""
        defs = self._defined_modules + self._defined_functions
        defs.sort(key=lambda obj: obj.tree.line)
        return defs

    @property
    def docs(self):
        """The docs for this file."""
        return copy(self._docs)

    def get_line_and_column(self, char_index):
        """
        Return the line and column number for the python index of a given
        character
        """
        line = (
            next(
                (
                    i
                    for i, line_end in enumerate(self._line_endings)
                    if line_end > char_index
                ),
                len(self._line_endings),
            )
            + 1
        )
        if line == 1:
            line_start = 0
        else:
            line_start = self._line_endings[line - 2]
        column = char_index - line_start
        return line, column

    def _locate_line_endings(self):
        if self._scad_code is None:
            self._line_endings = []
        else:
            self._line_endings = [
                i for i, char in enumerate(self._scad_code) if char == "\n"
            ]

    def _set_docstrings(self):
        self._set_file_docstring()
        self._set_definition_docstrings()

    def _set_file_docstring(self):
        match = DOCSTRING_REGEX.search(self._scad_code)
        if not match:
            self._record_message("I4001", self.tree, [self.filename])
            return
        self._docs = match.group(2)
        self._check_doc_code_blocks(self._docs, self.tree)
        if match.group(1) != "":
            self._record_message("I0008", self.tree)

    def _set_definition_docstrings(self):
        for i, definition in enumerate(self.definitions):
            missing_code = "I4002" if isinstance(definition, ModuleDef) else "I4003"

            def_index = self.tree.children.index(definition.tree)
            if def_index == 0:
                end_of_last = None
            else:
                prev_tree = self.tree.children[def_index - 1]
                end_of_last = [prev_tree.end_line, prev_tree.end_column]

            code_before = utilities.get_text_range(
                self.scad_code,
                end_of_last,
                [definition.tree.line, definition.tree.column],
            )
            if not code_before:
                # No code before so no docstring.
                self._record_message(missing_code, definition.tree, [definition.name])
                # Continue as there is no need to perform a search.
                continue
            # Reverse the string and search backwards. This is much much faster than
            # a lazy forward search
            match = DOCSTRING_REGEX.search(code_before[::-1])
            if match:
                # Un-reverse it.
                docstring = match.group(2)[::-1]
                if i == 0 and docstring == self._docs:
                    # This definition is trying to use the module docstring!
                    self._record_message("I4007", definition.tree)
                    self._record_message(
                        missing_code, definition.tree, [definition.name]
                    )
                definition.docs = docstring
                self._check_doc_code_blocks(definition.docs, definition.tree)
                self._check_docstring(definition)
                if match.group(1) != "\n":
                    self._record_message("I0009", definition.tree)
            else:
                self._record_message(missing_code, definition.tree, [definition.name])

    def _check_docstring(self, definition):
        params = utilities.PARAM_REGEX.findall(definition.docs)
        doc_args = [param[1] for param in params]
        doc_args_set = set(doc_args)
        if len(doc_args) != len(doc_args_set):
            self._record_message("I4008", definition.tree)
        def_args = {arg.name for arg in definition.arguments}
        if doc_args_set != def_args:
            self._record_message("I4004", definition.tree, (doc_args, def_args))
        if isinstance(definition, FunctionDef):
            n_returns = len(utilities.RETURN_REGEX.findall(definition.docs))
            if n_returns == 0:
                self._record_message("I4005", definition.tree)
            if n_returns > 1:
                self._record_message("I4006", definition.tree, (n_returns,))

    def _check_doc_code_blocks(self, docstring, tree):
        """Check if `scad` code blocks have customisers only meant for `example` blocks."""
        matches = SCAD_BLOCK_REGEX.findall(docstring)
        for match in matches:
            if match[1] == "scad" and match[2] != "":
                self._record_message("I4009", tree)
                continue
            customisers = [i.strip() for i in match[2].split()]
            if len(customisers) != len(set(customisers)):
                self._record_message("I4011", tree)
            for customiser in customisers:
                if customiser not in VALID_EXAMPLE_CUSTOMISERS:
                    self._record_message("I4010", tree, (customiser,))

    def _check_whitespace(self):
        self._check_trailing_whitespace()
        self._check_definition_leading_whitespace()

    def _check_trailing_whitespace(self):
        # matches are either comments or trailing white spaces in code
        # The first group is the trailing whitespace. This is empty for comments
        matches = re.finditer(
            r"/\*(?:.|\n)*?\*/|//.*|( $)", self._scad_code, re.MULTILINE
        )
        # Get only whitespace matches
        matches = [match_obj for match_obj in matches if match_obj.group(1) is not None]
        for match_obj in matches:
            line, col = self.get_line_and_column(match_obj.start())
            self._record_message(
                "I0006", DummyTree(data="whitespace", line=line, column=col + 1)
            )

    def _check_definition_leading_whitespace(self):
        """Top level module and function definitions should start on column 1."""
        for definition in self._defined_modules + self._defined_functions:
            if definition.tree.column != 1:
                self._record_message("I0007", definition.tree)

    def _printed_var_lists(self, indent=2, this_indent=0):
        def print_list(plist):
            return "[" + ", ".join([str(item) for item in plist]) + "]"

        var_lists = [
            f"included_files: {print_list(self._included_files)}",
            f"used_files: {print_list(self._used_files)}",
        ]
        var_lists += super()._printed_var_lists(indent, this_indent)
        return var_lists

    def _parse_use_include(self, statement_tree):
        if statement_tree.data == "use_statement":
            self._used_files.append(UseIncStatment(statement_tree, self._filename))
        else:
            self._included_files.append(UseIncStatment(statement_tree, self._filename))

    def analyse_tree(self, analyser):
        """
        Perform analysis of the full tree and sub-scopes. The analyser is taken
        as an input to analyse included or used files. The entire tree as already been
        processed into scope objects on creation of this object. This function runs
        further analysis such as checking for valid syntax that does not meet the linters
        rules.

        The analyser object is needed to find new files which are included/used. This is
        so that SCA2D can check if what variables/modules are defined.
        """
        self._check_pointless_termination()
        self._check_pointless_scope()
        self._check_complexity()
        self._check_invalid_attributes()
        self._check_definitions(analyser)
        self._check_globals()
        self._check_whitespace()

    def _check_globals(self):
        global_definitions = [
            var for var in self._assigned_vars if not var.is_special()
        ]
        n_globals = len(global_definitions)
        if n_globals > 3:
            self._record_message("I1002", self.tree, [n_globals])
        for var in global_definitions:
            global_match = re.match(GLOBAL_PATTERN, var.name)
            if global_match is None:
                self._record_message("I3001", var.tree, [var.name])

    def _check_definitions(self, analyser):
        defs_and_msgs = BUILT_IN_SCOPE.get_external_definitions(analyser)
        all_def_var = copy(defs_and_msgs[0])
        all_def_mod = copy(defs_and_msgs[1])
        all_def_func = copy(defs_and_msgs[2])

        # To get the definitions from use and included files we run the same import
        # as any other file including this file with an include statement. We just
        # do not count the definitions from this file.
        defs_and_msgs = self.get_external_definitions(analyser, root_file=True)
        all_def_var += defs_and_msgs[0]
        all_def_mod += defs_and_msgs[1]
        all_def_func += defs_and_msgs[2]

        for message in defs_and_msgs[3]:
            self.messages.append(message)

        self._check_duplicate_external_defs(all_def_var, all_def_mod, all_def_func)
        all_uses = self.propagate_defs_and_use(all_def_var, all_def_mod, all_def_func)
        self._check_if_external_files_needed(analyser, defs_and_msgs[:3], all_uses)

    def _check_if_external_files_needed(self, analyser, all_defs, all_uses):
        for used_file in self._used_files:
            used_scope = analyser.get_scope_from_file(used_file)
            if not self._is_file_needed(
                used_scope, all_defs, all_uses, file_included=False
            ):
                self._record_message("W1001", used_file.tree, [used_file.filename])
        for included_file in self._included_files:
            included_scope = analyser.get_scope_from_file(included_file)
            if not self._is_file_needed(
                included_scope, all_defs, all_uses, file_included=True
            ):
                self._record_message(
                    "W1002", included_file.tree, [included_file.filename]
                )

    def _is_file_needed(self, file_scope, all_defs, all_uses, file_included):
        all_def_var, all_def_mod, all_def_func = all_defs
        all_var_use, all_mod_use, all_func_use = all_uses

        file_needed = False

        for mod in all_def_mod:
            if mod.included_by is file_scope:
                if mod in all_mod_use:
                    file_needed = True
                    continue
        if not file_needed:
            for func in all_def_func:
                if func.included_by is file_scope:
                    if func in all_func_use:
                        file_needed = True
                        continue
        if file_included and not file_needed:
            for var in all_def_var:
                if var.included_by is file_scope:
                    if var in all_var_use:
                        file_needed = True
                        continue
        return file_needed

    def get_external_definitions(
        self, analyser, breadcrumbs=None, root_file=False, inc_only=False
    ):
        """
        The definitions passed onto a file that when this file is included with and
        include statement. Count own should only be false when this is being called
        from itself.
        """
        breadcrumbs, message = self._check_and_append_breadcrumbs(breadcrumbs)
        if message is not None:
            return [], [], [], [message]

        all_def_var = []
        all_def_mod = []
        all_def_func = []
        # The message raised when getting external definitions
        all_msgs = []
        if not root_file:
            all_def_var += self._assigned_vars
            all_def_mod += self._defined_modules
            all_def_func += self._defined_functions

        if not inc_only:
            defs = _loop_over_external_files(
                self._used_files, analyser, breadcrumbs, inc_only=True
            )
            all_def_mod += defs[1]
            all_def_func += defs[2]
            all_msgs += defs[3]

        defs = _loop_over_external_files(
            self._included_files, analyser, breadcrumbs, inc_only=inc_only
        )
        all_def_var += defs[0]
        all_def_mod += defs[1]
        all_def_func += defs[2]
        all_msgs += defs[3]

        if not root_file:
            for item in all_def_mod + all_def_func + all_def_var:
                item.included_by = self

        return all_def_var, all_def_mod, all_def_func, all_msgs

    def _check_and_append_breadcrumbs(self, breadcrumbs):
        if breadcrumbs is None:
            breadcrumbs = []
        else:
            breadcrumbs = copy(breadcrumbs)
        if self._filename in breadcrumbs:
            crumb_str = " > ".join(breadcrumbs)
            breadcrumbs.append(self._filename)
            message = Message(
                self.filename, "E3003", self._tree, [self.filename, crumb_str]
            )
        else:
            breadcrumbs.append(self._filename)
            message = None
        return breadcrumbs, message

    def get_use_definitions(self):
        """
        The definitions passed onto a file that when this file is used with a
        `use` statement.
        """
        return self._defined_modules, self._defined_functions

    def _check_pointless_termination(self):
        subtrees = utilities.get_all_matching_subtrees(
            self._tree, "pointless_termination"
        )
        for tree in subtrees:
            self._record_message("I0001", tree)

    def _check_pointless_scope(self):
        subtrees = utilities.get_all_matching_subtrees(
            self._tree, "pointless_scoped_block"
        )
        for tree in subtrees:
            self._record_message("I0002", tree)

    def _check_complexity(self):
        self._check_complicated_argument()
        self._check_complicated_assignment()

    def _check_complicated_argument(self):
        # only check modules as functions are checked by _check_complicated_assignment
        mod_head_trees = utilities.get_all_matching_subtrees(
            self._tree, "module_header"
        )
        for mod_head_tree in mod_head_trees:
            arg_trees = utilities.get_all_matching_subtrees(mod_head_tree, "arg")
            for arg_tree in arg_trees:
                complexity = utilities.estimate_complexity(arg_tree)
                if complexity >= 8:
                    self._record_message("I1001", arg_tree, [complexity])

    def _check_complicated_assignment(self):
        var_assign_trees = utilities.get_all_matching_subtrees(
            self._tree, "variable_assignment", include_nested=False
        )
        var_assign_trees += utilities.get_all_matching_subtrees(
            self._tree, "control_assignment", include_nested=False
        )
        func_scope_trees = utilities.get_all_matching_subtrees(
            self._tree, "function_scope", include_nested=False
        )
        expr_trees = [tree.children[1] for tree in var_assign_trees]
        expr_trees += [tree.children[0] for tree in func_scope_trees]
        for tree in expr_trees:
            complexity = utilities.estimate_complexity(tree)
            if complexity >= 10:
                self._record_message("I1002", tree, [complexity])

    def _check_invalid_attributes(self):
        attrs = utilities.get_all_matching_tokens(self._tree, "ATTRIBUTE")
        for attr in attrs:
            if attr.value not in ["x", "y", "z"]:
                self._record_message("E2004", attr)

    def _check_duplicate_external_defs(self, all_def_var, all_def_mod, all_def_func):
        warnings = ["W2010", "W2011", "W2012"]
        def_lists = [all_def_var, all_def_mod, all_def_func]
        for def_list, warning in zip(def_lists, warnings):
            warned = []
            for i, definition in enumerate(def_list):
                if definition not in warned and definition in def_list[i + 1 :]:
                    index = def_list[i + 1 :].index(definition)
                    second_def = def_list[i + 1 :][index]
                    if definition.tree is not second_def.tree:
                        warned.append(definition)
                        self._record_message(warning, DummyTree(), [definition.name])


def _loop_over_external_files(file_list, analyser, breadcrumbs, inc_only):
    all_defs_and_msgs = [[], [], [], []]
    for file_ref in file_list:
        file_scope = analyser.get_scope_from_file(file_ref)
        if isinstance(file_scope, Message):
            err_breadcrumbs = copy(breadcrumbs)
            err_breadcrumbs.append(file_ref.filename)
            message = file_scope
            # Overwrite the dummy message tree with the tree of calling statement
            if message.code == "F0001":
                args = [file_ref.filename, message.args[0], " > ".join(err_breadcrumbs)]
                message = Message(file_scope.filename, "E3001", file_ref.tree, args)
            if message.code == "F0002":
                args = [file_ref.filename, " > ".join(err_breadcrumbs)]
                message = Message(file_scope.filename, "E3002", file_ref.tree, args)
            all_defs_and_msgs[3].append(message)
            continue
        defs_and_msgs = file_scope.get_external_definitions(
            analyser, breadcrumbs, inc_only=inc_only
        )
        for message in defs_and_msgs[3]:
            # Also overwrite tree with calling statement for any messages raise before.
            message.tree = file_ref.tree
            message.filename = file_scope.filename
        # Concatenate the variable, module and function definition lists
        all_defs_and_msgs = [i + j for i, j in zip(all_defs_and_msgs, defs_and_msgs)]
    return all_defs_and_msgs


class NonFileOuterScope(OuterScope):
    """
    This is a child class of OuterScope. It is used so that a code block rather
    than a file can be analysed. Include and Use statements will look in the working
    directory.
    """

    def __init__(self, tree, scad_code):
        filename = os.path.join(os.getcwd(), "INPUT_CODE")
        super().__init__(tree, scad_code, filename)


class BuiltInScope(OuterScope):
    """
    A dummy scope for built in definitions
    """

    def __init__(self):
        super().__init__(DummyTree(), "", "BUILT_IN")
        self._set_built_in_vars()
        self._set_built_in_mods()
        self._set_built_in_funcs()

    def _parse_scope(self, overload_tree=None):
        pass

    def _set_built_in_vars(self):
        for scad_var in SCAD_VARS:
            token = DummyToken("VARIABLE", scad_var)
            self._assigned_vars.append(Variable(token))

    def _set_built_in_mods(self):
        for scad_mod in SCAD_MODS:
            tree = DummyTree()
            module = ModuleDef(
                name=scad_mod[0],
                arg_definition=UndefinedArgDef(),
                tree=tree,
                scope=self,
            )
            self._defined_modules.append(module)

    def _set_built_in_funcs(self):
        for scad_func in SCAD_FUNCS:
            tree = DummyTree()
            function = FunctionDef(
                name=scad_func[0],
                arg_definition=UndefinedArgDef(),
                tree=tree,
                scope=self,
            )
            self._defined_functions.append(function)


class UndefinedArgDef(CustomArgDef):
    """
    Custom argument defitionion for use when behaviour is undefined
    so no warnings can be raised. Not checks are performed
    """

    def check_call(self, call):
        return []


BUILT_IN_SCOPE = BuiltInScope()
