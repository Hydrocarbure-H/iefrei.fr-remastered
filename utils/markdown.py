import os
from typing import List, Dict, Any
import subprocess

PUBLIC_FOLDER_PATH:str = os.getenv('PUBLIC_FOLDER_PATH')
AUTHOR:str = os.getenv('AUTHOR')

def get_dir_contents(dir_path: str) -> List[str]:
    """
    Get all files in a directory
    :param dir_path: the directory path
    :return: a list of files paths
    """
    results: List[str] = []
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            results.append(os.path.join(root, file))
    return results

def process_markdown_files(dir_path: str) -> List[Dict[str, Any]]:
    """
    Process all markdown files in a directory.
    This function will convert all markdown files to html and pdf.
    If an error occurs, it will raise an exception.
    :param dir_path: the directory path
    :return: a list of dictionaries containing the course data (without the content)
    """
    files: List[str] = get_dir_contents(dir_path)
    md_files: List[Dict[str, Any]] = []

    for file in files:
        try:
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
                process_md_to_pdf(md_files[-1])

        except subprocess.SubprocessError as e:
            print(f"\033[91mError while executing a subprocess: {e}\033[0m")
            raise Exception("Error while refreshing courses. Please try again later.")
        except Exception as e:
            print(f"\033[91mError: {e}\033[0m")
            raise Exception("Error while refreshing courses. Please try again later.")

    return md_files

def process_md_to_html(course: Dict[str, Any]) -> None:
    """
    Convert a markdown file to html
    :param course: the course dictionary
    :return: None
    """
    with open(course['path'], 'r', encoding='utf-8') as f:
        content: str = f.read()
    content = content.replace("./assets/", f"https://iefrei.fr/courses/md_sync_s7/Cours/{course['title']}/assets/")
    with open(course['path'], 'w', encoding='utf-8') as f:
        f.write(content)
    command: str = f'pandoc -s --highlight-style pygments --verbose --katex --toc -V toc-title:"Sommaire" --css {PUBLIC_FOLDER_PATH}css/fluent-light.css --metadata title="{course["title"]}" "{course["path"]}" -o "{course["html_path"]}" --self-contained -F mermaid-filter'
    subprocess.run(command, shell=True, check=True)

def process_md_to_pdf(course: Dict[str, Any]) -> None:
    """
    Convert a markdown file to pdf
    :param course: the course dictionary
    :return: None
    """
    command: str = f'pandoc -s --highlight-style pygments --verbose --katex --toc -V toc-title:"Sommaire" --css {PUBLIC_FOLDER_PATH}css/fluent-light.css --metadata title="{course["title"]}" "{course["path"]}" -o "{course["pdf_path"]}" --self-contained -F mermaid-filter'
    subprocess.run(command, shell=True, check=True)

