from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass
class AstLikeNode:
    kind: str
    name: str | None
    start_byte: int
    end_byte: int
    start_line: int
    start_col: int
    end_line: int
    end_col: int
    parent_idx: int | None
    meta: dict | None = None

# Minimal extractors. Extend per language.

def extract_ast_like(language: str, tree) -> list[AstLikeNode]:
    lang = language.lower()
    if lang in ("python",):
        return _extract_python(tree)
    if lang in ("js", "javascript", "jsx", "ts", "tsx"):
        return _extract_javascript(tree)
    if lang in ("css", "scss"):
        return _extract_css(tree)
    return []


def _walk(node, parent_idx, out):
    for child in node.children:
        yield child
        yield from _walk(child, parent_idx, out)


def _ts_range(node):
    (srow, scol) = node.start_point
    (erow, ecol) = node.end_point
    return node.start_byte, node.end_byte, srow, scol, erow, ecol


def _extract_python(tree):
    out: list[AstLikeNode] = []

    def visit(node, parent_idx=None):
        kind = node.type
        if kind in {"function_definition", "class_definition", "import_statement", "import_from_statement"}:
            name = None
            if kind in {"function_definition", "class_definition"}:
                name_node = node.child_by_field_name("name")
                if name_node:
                    name = name_node.text.decode("utf-8")
            start_byte, end_byte, srow, scol, erow, ecol = _ts_range(node)
            idx = len(out)
            out.append(AstLikeNode(kind=kind, name=name, start_byte=start_byte, end_byte=end_byte,
                                   start_line=srow, start_col=scol, end_line=erow, end_col=ecol,
                                   parent_idx=parent_idx))
            for child in node.children:
                visit(child, idx)
        else:
            for child in node.children:
                visit(child, parent_idx)

    visit(tree.root_node, None)
    return out


def _extract_javascript(tree):
    out: list[AstLikeNode] = []

    def visit(node, parent_idx=None):
        kind = node.type
        if kind in {"function_declaration", "class_declaration", "lexical_declaration", "import_statement"}:
            name = None
            name_node = node.child_by_field_name("name")
            if name_node:
                name = name_node.text.decode("utf-8")
            start_byte, end_byte, srow, scol, erow, ecol = _ts_range(node)
            idx = len(out)
            out.append(AstLikeNode(kind=kind, name=name, start_byte=start_byte, end_byte=end_byte,
                                   start_line=srow, start_col=scol, end_line=erow, end_col=ecol,
                                   parent_idx=parent_idx))
            for child in node.children:
                visit(child, idx)
        else:
            for child in node.children:
                visit(child, parent_idx)

    visit(tree.root_node, None)
    return out


def _extract_css(tree):
    out: list[AstLikeNode] = []

    def visit(node, parent_idx=None):
        kind = node.type
        if kind in {"rule_set", "at_rule"}:
            start_byte, end_byte, srow, scol, erow, ecol = _ts_range(node)
            idx = len(out)
            out.append(AstLikeNode(kind=kind, name=None, start_byte=start_byte, end_byte=end_byte,
                                   start_line=srow, start_col=scol, end_line=erow, end_col=ecol,
                                   parent_idx=parent_idx))
            for child in node.children:
                visit(child, idx)
        else:
            for child in node.children:
                visit(child, parent_idx)

    visit(tree.root_node, None)
    return out
