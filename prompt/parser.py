from dataclasses import dataclass
from .lexer import TokenKind, Token, tokenize

class ExtraNetwork:
    __slots__ = ['net_type', 'net_name', 'weight']

    net_type: str
    net_name: str
    weight: float

    def __init__(self, tokens: list[Token]):
        self.net_type = self.net_name = ''
        self.weight = 1.0
        
        parts = ['']

        for token in tokens:
            if token.kind == TokenKind.COLON:
                parts.append('')
            elif token.kind not in (TokenKind.OPEN_ANGLE, TokenKind.CLOSE_ANGLE):
                parts[-1] += str(token)

        if len(parts) == 1:
            self.net_name = parts[0]
        elif len(parts) == 2:
            self.net_type = parts[0]
            self.net_name = parts[1]
        else:
            self.net_type = parts[0]
            self.net_name = ":".join(parts[1:-1])
            self.weight = float(parts[-1])

    def __str__(self):
        return f"<{self.net_type}:{self.net_name}:{self.weight:.3f}>"

    def __repr__(self):
        return f"ExtraNetwork()"

# It turns out that I don't need to implement a parser...
class Prompt:
    orig_tokens: list[Token]
    tokens: list[Token]
    extra_networks: dict[str, ExtraNetwork]

    def __init__(self, s: str):
        self.orig_tokens = tokenize(s)
        self.tokens = []
        self.extra_networks = dict()

        extra_network_tokens = []
        for token in self.orig_tokens:
            if len(extra_network_tokens):
                extra_network_tokens.append(token)
                if token.kind == TokenKind.CLOSE_ANGLE:
                    self.add_extra_network(ExtraNetwork(extra_network_tokens))
                    extra_network_tokens = []
            elif token.kind == TokenKind.OPEN_ANGLE:
                extra_network_tokens.append(token)
            else:
                self.tokens.append(token)

        if len(extra_network_tokens):
            self.tokens.extend(extra_network_tokens)

    def __str__(self):
        fragments = [str(en) for en in self.extra_networks.values()]
        
        prev_token = None
        for token in self.tokens:
            if prev_token and TokenKind.add_space(prev_token.kind, token.kind):
                fragments.append(' ')
            fragments.append(token.text)
            prev_token = token

        return "".join(fragments)

    def add_extra_network(self, extra_network: ExtraNetwork):
        key = f"${extra_network.net_type}:${extra_network.net_name}"
        prev_network = self.extra_networks[key]
        if not prev_network:
            self.extra_networks[key] = extra_network
            return
        
        prev_network.weight = max(prev_network.weight, extra_network.weight)

import unittest

class TestParser(unittest.TestCase):
    def test_blank(self):
        test_data = ["", " ", "  "]
        for s in test_data:
            prompt = Prompt(s)
            self.assertEqual(prompt.orig_tokens, [], f"empty orig_token for {repr(s)}")
            self.assertEqual(prompt.tokens, [], f"empty tokens for {repr(s)}")
            self.assertEqual(prompt.extra_networks, [], f"empty extra_networks for {repr(s)}")
    def test_complex(self):
        test_in = "1girl, ((looking at viewer)) <lora:foo:1.0>"
        print(Prompt(test_in))

if __name__ == '__main__':
    unittest.main()
