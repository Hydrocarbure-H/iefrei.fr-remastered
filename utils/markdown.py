import os
from typing import List, Dict, Any
import subprocess

PUBLIC_FOLDER_PATH:str = os.getenv('PUBLIC_FOLDER_PATH')
AUTHOR:str = os.getenv('AUTHOR')

def get_dir_contents(dir_path: str) -> List[str]:
    results: List[str] = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            results.append(os.path.join(root, file))
    return results

def process_markdown_files(dir_path: str) -> List[Dict[str, Any]]:
    files: List[str] = get_dir_contents(dir_path)
    md_files: List[Dict[str, Any]] = []
    for file in files:
        if file.endswith(".md"):
            md_files.append({
                "path": file,
                "html_path": file.replace(".md", ".html"),
                "pdf_path": file.replace(".md", ".pdf"),
                "title": os.path.basename(os.path.dirname(file)),
                "author": AUTHOR,
                "size": os.path.getsize(file),
                "date": os.path.getmtime(file)
            })
            process_md_to_html(md_files[-1])
    return md_files

def process_md_to_html(course: Dict[str, Any]) -> None:
    with open(course['path'], 'r', encoding='utf-8') as f:
        content: str = f.read()
    content = content.replace("./assets/", f"https://iefrei.fr/courses/md_sync_s7/Cours/{course['title']}/assets/")
    with open(course['path'], 'w', encoding='utf-8') as f:
        f.write(content)
    command: str = f'pandoc -s --highlight-style pygments --verbose --katex --toc -V toc-title:"Sommaire" --css {PUBLIC_FOLDER_PATH}css/fluent-light.css --metadata title="{course["title"]}" "{course["path"]}" -o "{course["html_path"]}" --self-contained -F mermaid-filter'
    subprocess.run(command, shell=True, check=True)
