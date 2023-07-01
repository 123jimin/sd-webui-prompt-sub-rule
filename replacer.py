from prompt import Prompt, Token, TokenKind
import re

class Entry:
    name: str
    out: Prompt
    tags: set[str]
    keywords: list[str]
    tag_regexs: list[re.Pattern]

    def __init__(self, name: str):
        self.name = name
        self.out = None
        self.tags = set()
        self.tag_regexs = []

    def add_extra_networks(self, prompt: Prompt):
        for extra in self.out.extra_networks:
            prompt.add_extra_network(extra)

    def process(self, prompt: Prompt):
        for i in range(len(prompt.tokens)):
            token = prompt.tokens[i]
            if token.kind != TokenKind.TEXT: continue

            token_text = str(token)
            
            if token_text.lower() in self.tags:
                prompt.tokens = prompt.tokens[:i] + self.out.tokens + prompt.tokens[i+1:]
                self.add_extra_networks(prompt)
                return
        
            for tag_regex in self.tag_regexs:
                if tag_regex.search(token_text):
                    self.add_extra_networks(prompt)
                    return

class Replacer:
    entries: list[Entry]

    def __init__(self):
        self.entries = []

    def add_rule(self, text: str):
        if not text: return

        curr_entry = None

        for line in text.split("\n"):
            line = line.strip()
            if not line: continue
            if line.startswith('#'): continue

            if line.startswith("rule:"):
                curr_entry = Entry(line[5:].lstrip())
                self.entries.append(curr_entry)
                continue

            if curr_entry is None: continue

            if line.startswith("for:"):
                curr_entry.out = Prompt(line[4:].lstrip())

            if line.startswith("tag:"):
                for token in Prompt(line[4:].lstrip()).tokens:
                    if token.kind == TokenKind.TEXT:
                        curr_entry.tags.add(str(token).lower())
            
            if line.startswith("re:"):
                curr_entry.tag_regexs.append(re.compile(line[3:].lstrip(), re.I))
            
            if line.startswith("keyword:"):
                keyword_regex = "|".join(keyword.strip() for keyword in line[8:].split(","))
                curr_entry.tag_regexs.append(re.compile(keyword_regex, re.I))

    def replace(self, prompt_txt: str):
        if not len(self.entries): return prompt_txt
        prompt = Prompt(prompt_txt)
        for entry in self.entries:
            entry.process(prompt)
        return str(prompt)

