from __future__ import annotations


def tokenize_html(node):
    tokens = []

    def _tokenize(node):
        if node.name and node.name != '[document]':
            tokens.append(f"<{node.name}>")
            for child in node.children:
                _tokenize(child)
            tokens.append(f"</{node.name}>")
        elif node.string and node.string.strip():
            tokens.append(node.string.strip())

    for child in node.children:
        _tokenize(child)

    return tokens
