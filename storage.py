import os, re

class Storage:
    dir_path: str
    items: list[str]
    cache: dict
    
    def __init__(self, dir_path: str):
        self.dir_path = dir_path
        self.items = list()
        self.cache = dict()

        if not os.path.exists(self.dir_path):
            os.mkdir(self.dir_path)

        self.load_items()

    def load_items(self):
        self.items = [f[:-4] for f in os.listdir(self.dir_path) if f.endswith(".txt")]

    def is_valid_key(self, key:str) -> bool:
        if len(key) == 0: return False
        return bool(re.fullmatch(r'[a-z0-9\-_.]+', key, re.I))

    def get(self, key:str) -> str:
        key = key.strip()
        if not self.is_valid_key(key): return False
        if key in self.cache: return self.cache[key]

        contents = ""
        try:
            with open(os.path.join(self.dir_path, f"{key}.txt"), 'r') as f:
                contents = f.read()
        except:
            pass

        self.cache[key] = contents
        return contents

    def put(self, key:str, value:str) -> bool:
        key = key.strip()
        if not self.is_valid_key(key): return False

        try:
            with open(os.path.join(self.dir_path, f"{key}.txt"), 'w') as f:
                f.write(value)
        except:
            return False
        
        if key not in self.items:
            self.items.append(key)
        self.cache[key] = value
        return True

    def delete(self, key:str) -> bool:
        return False
