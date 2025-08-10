import os
import yaml
from typing import Union


class PromptLoader:
    def __init__(self, prompts_dir: str = None):
        if prompts_dir:
            self.prompts_dir = prompts_dir
        else:
            # Start from the current file's directory
            base_dir = os.path.dirname(os.path.abspath(__file__))

            # Walk up directories to find project root (heuristic)
            # If inside '.venv', move up until out of it
            while os.path.basename(base_dir) in ('.venv', 'venv'):
                base_dir = os.path.dirname(base_dir)

            # Assume project root is now base_dir's parent or base_dir itself
            # Adjust this if your project layout differs
            project_root = os.path.abspath(os.path.join(base_dir, '..'))

            # Final prompts dir
            self.prompts_dir = os.path.join(project_root, 'prompts')

        self.cache = {}

    def load(self, file_name: str) -> Union[str, dict]:
        if file_name in self.cache:
            return self.cache[file_name]

        file_path = os.path.join(self.prompts_dir, file_name)
        print(f"[PromptLoader] Loading prompt file: {file_path}")  # Debug

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
