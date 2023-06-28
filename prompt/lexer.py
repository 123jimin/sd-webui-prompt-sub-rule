import re
from dataclasses import dataclass

class TokenKind:
    TEXT = 1
    COLON = 2
    PIPE = 3
    COMMA = 4
    OPEN_PAREN = 10
    CLOSE_PAREN = 11
    OPEN_BRACKET = 12
    CLOSE_BRACKET = 13
    OPEN_CURLY = 14
    CLOSE_CURLY = 15
    OPEN_ANGLE = 16
    CLOSE_ANGLE = 17

    @staticmethod
    def is_opening(kind:int) -> bool:
        return kind in (TokenKind.OPEN_PAREN, TokenKind.OPEN_BRACKET, TokenKind.OPEN_CURLY, TokenKind.OPEN_ANGLE)

    @staticmethod
    def is_closing(kind:int) -> bool:
        return kind in (TokenKind.CLOSE_PAREN, TokenKind.CLOSE_BRACKET, TokenKind.CLOSE_CURLY, TokenKind.CLOSE_ANGLE)

    @staticmethod
    def add_space(prev:int, curr:int) -> bool:
        if curr == TokenKind.TEXT or TokenKind.is_opening(curr):
            return prev == TokenKind.COMMA or TokenKind.is_closing(prev)
        return False

CHAR_TOKENS = {
    ':': TokenKind.COLON,
    '|': TokenKind.PIPE,
    ',': TokenKind.COMMA,
    '(': TokenKind.OPEN_PAREN,
    ')': TokenKind.CLOSE_PAREN,
    '[': TokenKind.OPEN_BRACKET,
    ']': TokenKind.CLOSE_BRACKET,
    '{': TokenKind.OPEN_CURLY,
    '}': TokenKind.CLOSE_CURLY,
    '<': TokenKind.OPEN_ANGLE,
    '>': TokenKind.CLOSE_ANGLE
}

RE_REMOVE_BACKSLASH = re.compile(r'\\(.)')

@dataclass(frozen=True, slots=True)
class Token:
    kind: int
    text: str
    
    def __str__(self):
        return RE_REMOVE_BACKSLASH.sub(r'\1', self.text)

    @staticmethod
    def make_text(s: str):
        s = s.strip()
        if len(s): return Token(TokenKind.TEXT, s)
        else: return None

    @staticmethod
    def make_char(s: str):
        if s in CHAR_TOKENS: return Token(CHAR_TOKENS[s], s)
        else: return None

    def make_list(l: list[str]):
        return list(map(lambda s: (Token(CHAR_TOKENS[s], s) if s in CHAR_TOKENS else Token(TokenKind.TEXT, s)), l))

def tokenize(s: str) -> list[str]:
    tokens = []
    i = 0
    while i < len(s):
        if token := Token.make_char(s[i]):
            tokens.append(token)
            i += 1
        else:
            start = i
            while i < len(s):
                c = s[i]
                if c == '\\': i = min(len(s), i+2)
                elif c not in CHAR_TOKENS: i += 1
                else: break
            if token := Token.make_text(s[start:i]):
                tokens.append(token)
    return tokens

import unittest

class TestLexer(unittest.TestCase):
    def test_blank(self):
        test_data = ["", " ", "  "]
        for s in test_data:
            self.assertEqual(tokenize(s), [], f"empty result for {repr(s)}")

    def test_single(self):
        test_data = ["\\", "1girl", "looking at viewer", "a b c", "a\\", "a\\, b", "a\\(b c \\)", "hello-world"]
        for s in test_data:
            self.assertEqual(tokenize(s), [Token.make_text(s)], f"correct result for {repr(s)}")

    def test_simple(self):
        test_data = [
            ("a, b, c", ['a', ',', 'b', ',', 'c']),
            ("a (((farm))), daytime", ['a', '(', '(', '(', 'farm', ')', ')', ')', ',', 'daytime']),
            ("a [fantasy:cyberpunk:16] landscape", ['a', '[', 'fantasy', ':', 'cyberpunk', ':', '16', ']', 'landscape']),
        ]

        for (s, t) in test_data:
            self.assertEqual(tokenize(s), Token.make_list(t), f"correct result for {repr(s)}")

if __name__ == '__main__':
    unittest.main()
