import os
import re
import subprocess
from datetime import datetime
from typing import List, Dict, Any

PUBLIC_FOLDER_PATH: str = os.getenv("PUBLIC_FOLDER_PATH")
AUTHOR: str = os.getenv("AUTHOR")
HTTP_ADDR = os.getenv("HTTP_ADDR")
MD_FOLDER_LOCATION = os.getenv("MD_FOLDER_LOCATION")
MD_FOLDER = os.getenv("MD_FOLDER")


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
                md_files.append(
                    {
                        "path": file,
                        "html_path": file.replace(".md", ".html"),
                        "pdf_path": file.replace(".md", ".pdf"),
                        "title": os.path.basename(os.path.dirname(file)),
                        "author": AUTHOR,
                        "size": os.path.getsize(file),
                        "date": os.path.getmtime(file),
                        "semester": os.getenv("SEMESTER"),
                    }
                )
                process_md_to_html(md_files[-1])
                process_md_to_pdf(md_files[-1])

        except subprocess.SubprocessError as e:
            print(f"\033[91mError while executing a subprocess: {e}\033[0m")
            raise Exception("Error while refreshing courses. Please try again later.")
        except ValueError as e:
            print(f"\033[91mError: Invalid Picture Path: {e}\033[0m")
            raise ValueError(f"Invalid Picture Path. Please check the markdown file for theses "
                             f"paths: {e}")
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
    with open(course["path"], "r", encoding="utf-8") as f:
        content: str = f.read()

    # Idempotency
    # Invert replacements to the original state if the script is run multiple times
    content = content.replace(
        f"{HTTP_ADDR}/assets/{os.getenv('SEMESTER')}/{course['title']}/assets/",
        "./assets/",
    )
    content = content.replace(
        f"{HTTP_ADDR}/assets/{os.getenv('SEMESTER')}/{course['title']}/imgs/",
        "./imgs/",
    )

    # Check if every image path format starts with "./imgs/" or ./assets/
    invalid_paths = re.findall(r'(?<!\./)(imgs/|assets/)(?![^\s]*http)', content)

    if invalid_paths:
        raise ValueError(f"{len(invalid_paths)} invalid pictures paths found :"
                         f" {list(set(invalid_paths))}, in"
                         f" {course['title']}")

    # Replace relative image paths with full URLs
    content = content.replace(
        "./assets/",
        f"{HTTP_ADDR}/assets/{os.getenv('SEMESTER')}/{course['title']}/assets/",
    )

    # Replace relative image paths with full URLs
    content = content.replace(
        "./imgs/",
        f"{HTTP_ADDR}/assets/{os.getenv('SEMESTER')}/{course['title']}/imgs/",
    )

    # Convert the modification time from timestamp to datetime object
    course["date"] = datetime.fromtimestamp(course["date"])

    # Write the modified content back to the Markdown file
    with open(course["path"], "w", encoding="utf-8") as f:
        f.write(content)

    # Build the Pandoc command to convert Markdown to HTML
    command: str = (
        f"pandoc -s --highlight-style pygments --verbose --katex --toc "
        f'-V toc-title:"Sommaire" --css {PUBLIC_FOLDER_PATH}css/fluent-light.css '
        f'--metadata title="{course["title"]}" "{course["path"]}" '
        f'-o "{course["html_path"]}"'
    )

    # print(command)

    # Execute the Pandoc command using subprocess
    subprocess.run(command, shell=True, check=True)

    # Update references to /usr/share/javascript/katex
    with open(course["html_path"], "r", encoding="utf-8") as file:
        html_content = file.read()

    # Replace references to /usr/share/javascript/katex with the correct URL
    html_content = html_content.replace(
        "/usr/share/javascript/katex",
        f"{HTTP_ADDR}/static/katex"
    )
    
    # Save the file
    with open(course["html_path"], "w", encoding="utf-8") as file:
        file.write(html_content)


def process_md_to_pdf(course: Dict[str, Any]) -> None:
    """
    Convert a markdown file to PDF using wkhtmltopdf.
    :param course: the course dictionary
    :return: None
    """
    # Read the content of the HTML file
    with open(course["html_path"], "r", encoding="utf-8") as file:
        html_content = file.read()

    # Inject CSS and JavaScript into the HTML content
    injected_content = html_content.replace(
        "</head>",
        """
        <!-- Lien vers Google Fonts -->
        <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@300;400&display=swap" rel="stylesheet">
        <style>
            body {
                font-family: 'Roboto', sans-serif;
                  font-weight: 300;
                  font-style: normal;
            }
        </style>
        <!-- MathJax pour le rendu LaTeX -->
        <script src="https://cdn.jsdelivr.net/npm/promise-polyfill@8/dist/polyfill.min.js"></script>
        <script type="text/javascript" id="MathJax-script" async
            src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
        </script>
        </head>
        """,
    )

    # Save the file
    with open(course["html_path"], "w", encoding="utf-8") as file:
        file.write(injected_content)

    # Build the command to convert HTML to PDF using wkhtmltopdf
    command = f'prince "{course["html_path"]}" -o "{course["pdf_path"]}"'

    # Execute the command using subprocess
    subprocess.run(command, shell=True, check=True)

    # Remove the HTML added content
    with open(course["html_path"], "w", encoding="utf-8") as file:
        file.write(html_content)
