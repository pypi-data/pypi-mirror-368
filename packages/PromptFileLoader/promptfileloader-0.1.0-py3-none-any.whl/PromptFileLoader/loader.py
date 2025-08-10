import os
import yaml
from typing import Union

class PromptLoader:
    def __init__(self, prompts_dir: str = None):
        self.prompts_dir = prompts_dir
        self.cache = {}

    def load(self, file_name: str) -> Union[str, dict]:
        if file_name in self.cache:
            return self.cache[file_name]

        if self.prompts_dir:
            file_path = os.path.join(self.prompts_dir, file_name)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(base_dir, '..', 'prompts', file_name)

        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Prompt file not found: {file_path}")

        ext = os.path.splitext(file_name)[1].lower()

        if ext in ['.yaml', '.yml']:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
        elif ext == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            raise ValueError(f"Unsupported prompt file extension: {ext}")

        self.cache[file_name] = content
        return content
