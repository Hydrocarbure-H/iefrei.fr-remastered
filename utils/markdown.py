import os
import subprocess
from datetime import datetime
from typing import List, Dict, Any

PUBLIC_FOLDER_PATH: str = os.getenv('PUBLIC_FOLDER_PATH')
AUTHOR: str = os.getenv('AUTHOR')
HTTP_ADDR = os.getenv('HTTP_ADDR')
MD_FOLDER_LOCATION = os.getenv('MD_FOLDER_LOCATION')
MD_FOLDER = os.getenv('MD_FOLDER')


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
                    "date": os.path.getmtime(file),
                    "semester": os.getenv('SEMESTER')
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
    Convert a Markdown file to HTML and replace image paths with URLs.

    This function reads a Markdown file, replaces the relative paths of images with
    absolute URLs based on the environment variable HTTP_ADDR, and then uses Pandoc
    to convert the Markdown file into an HTML file.

    :param course: A dictionary containing course details such as title, semester, and paths.
    :return: None
    """
    # Read the content of the Markdown file
    with open(course['path'], 'r', encoding='utf-8') as f:
        content: str = f.read()

    # Replace relative image paths with full URLs
    content = content.replace(
        "./assets/",
        f"{HTTP_ADDR}/assets/{os.getenv('SEMESTER')}/{course['title']}/assets/"
    )

    # Convert the modification time from timestamp to datetime object
    course['date'] = datetime.fromtimestamp(course['date'])

    # Write the modified content back to the Markdown file
    with open(course['path'], 'w', encoding='utf-8') as f:
        f.write(content)

    # Build the Pandoc command to convert Markdown to HTML
    command: str = (
        f'pandoc -s --highlight-style pygments --verbose --katex --toc '
        f'-V toc-title:"Sommaire" --css {PUBLIC_FOLDER_PATH}css/fluent-light.css '
        f'--metadata title="{course["title"]}" "{course["path"]}" '
        f'-o "{course["html_path"]}"'
    )

    print(command)

    # Execute the Pandoc command using subprocess
    subprocess.run(command, shell=True, check=True)


def process_md_to_pdf(course: Dict[str, Any]) -> None:
    """
    Convert a Markdown file to PDF.

    This function uses Pandoc to convert a Markdown file into a PDF file.
    The PDF will include a table of contents, syntax highlighting, and use LaTeX
    for rendering mathematics (if any).

    :param course: A dictionary containing course details such as title, semester, and paths.
    :return: None
    """
    # Build the Pandoc command to convert Markdown to PDF
    command: str = (
        f'pandoc -s --highlight-style pygments --verbose --katex --toc '
        f'-V toc-title:"Sommaire" --css {PUBLIC_FOLDER_PATH}css/fluent-light.css '
        f'--metadata title="{course["title"]}" "{course["path"]}" '
        f'-o "{course["pdf_path"]}" '
        f'--pdf-engine=xelatex --variable mainfont="Roboto"'
    )

    print(command)

    # Execute the Pandoc command using subprocess
    subprocess.run(command, shell=True, check=True)
