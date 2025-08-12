# The MIT License (MIT)
#
# Copyright (c) 2025 Almaz Ilaletdinov <a.ilaletdinov@yandex.ru>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.

"""Flake8 plugin entry point for checking variable names contain only one word."""

# flake8: noqa: WPS232, WPS226

import ast
import re
from collections.abc import Generator
from typing import final


@final
class Plugin:
    """Flake8 plugin for checking variable names contain only one word."""

    name = 'flake8-simple-var'
    version = '0.1.0'

    def __init__(self, tree: ast.AST) -> None:
        """Ctor."""
        self._tree = tree

    def run(self) -> Generator[tuple[int, int, str, type], None, None]:
        """Entry point for flake8 plugin."""
        visitor = VariableNameVisitor()
        visitor.visit(self._tree)
        yield from visitor.errors


@final
class VariableNameVisitor(ast.NodeVisitor):
    """AST visitor for checking variable names."""

    def __init__(self) -> None:
        """Initialize visitor."""
        self.errors: list[tuple[int, int, str, type]] = []
        self._in_function = False
        self._in_class = False

    def _check_variable_name(self, node: ast.AST, name: str, error_code: str) -> None:
        """Check if variable name contains only one word."""
        if not name or name.startswith('_'):
            return

        if re.search(r'[A-Z]', name) or '_' in name or re.search(r'[A-Z]{2,}', name):
            self.errors.append(
                (
                    node.lineno,  # type: ignore[attr-defined]
                    node.col_offset,  # type: ignore[attr-defined]
                    '\n'.join(['{} Variable name "{}" should contain only one word'.format(error_code, name)]),
                    type(self),
                ),
            )

    def visit_arg(self, node: ast.arg) -> None:
        """Visit function arguments."""
        self._check_variable_name(node, node.arg, 'SVN200')
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        """Visit annotated assignments."""
        if isinstance(node.target, ast.Name):
            # Check if this is a global variable (top-level assignment)
            if not self._in_function and not self._in_class:
                self._check_variable_name(node.target, node.target.id, 'SVN500')
            else:
                self._check_variable_name(node.target, node.target.id, 'SVN100')
        self.generic_visit(node)

    def visit_Assign(self, node: ast.Assign) -> None:
        """Visit assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                if not self._in_function and not self._in_class:
                    self._check_variable_name(target, target.id, 'SVN500')
                else:
                    self._check_variable_name(target, target.id, 'SVN100')
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        """Visit for loops."""
        if isinstance(node.target, ast.Name):
            self._check_variable_name(node.target, node.target.id, 'SVN200')
        self.generic_visit(node)

    def visit_comprehension(self, node: ast.comprehension) -> None:
        """Visit list/dict comprehensions."""
        if isinstance(node.target, ast.Name):
            self._check_variable_name(node.target, node.target.id, 'SVN200')
        self.generic_visit(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        """Visit exception handlers."""
        if node.name:
            self._check_variable_name(node, node.name, 'SVN300')
        self.generic_visit(node)

    def visit_withitem(self, node: ast.withitem) -> None:
        """Visit with statement items."""
        if node.optional_vars and isinstance(node.optional_vars, ast.Name):
            self._check_variable_name(node.optional_vars, node.optional_vars.id, 'SVN400')
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Visit function definitions."""
        old_in_function = self._in_function
        self._in_function = True
        self.generic_visit(node)
        self._in_function = old_in_function

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        """Visit async function definitions."""
        old_in_function = self._in_function
        self._in_function = True
        self.generic_visit(node)
        self._in_function = old_in_function

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        """Visit class definitions."""
        old_in_class = self._in_class
        self._in_class = True
        self.generic_visit(node)
        self._in_class = old_in_class
