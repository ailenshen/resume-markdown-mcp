#!/usr/bin/env python3
import argparse
import logging
import os
from importlib.resources import files

from resume_markdown.converter import (
    get_bundled_css,
    guess_chrome_path,
    make_html,
    write_pdf,
)


def init_resume(directory: str = ".") -> None:
    """
    Write template resume.md and resume.css files to the specified directory.
    """
    package_files = files("resume_markdown")

    for filename in ["resume.md", "resume.css"]:
        dest_path = os.path.join(directory, filename)
        if os.path.exists(dest_path):
            logging.warning(f"{dest_path} already exists, skipping")
            continue

        template_content = (package_files / filename).read_text(encoding="utf-8")
        with open(dest_path, "w", encoding="utf-8") as f:
            f.write(template_content)
        logging.info(f"Wrote {dest_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Markdown resumes to HTML and PDF"
    )
    parser.add_argument("-q", "--quiet", action="store_true")
    parser.add_argument("--debug", action="store_true")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # init command
    subparsers.add_parser(
        "init",
        help="Create resume.md and resume.css template files"
    )

    # build command
    build_parser = subparsers.add_parser(
        "build",
        help="Build HTML and PDF from Markdown resume"
    )
    build_parser.add_argument(
        "file",
        help="markdown input file [resume.md]",
        default="resume.md",
        nargs="?",
    )
    build_parser.add_argument(
        "--no-html",
        help="Do not write html output",
        action="store_true",
    )
    build_parser.add_argument(
        "--no-pdf",
        help="Do not write pdf output",
        action="store_true",
    )
    build_parser.add_argument(
        "--chrome-path",
        help="Path to Chrome or Chromium executable",
    )

    args = parser.parse_args()

    if args.quiet:
        logging.basicConfig(level=logging.WARN, format="%(message)s")
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG, format="%(message)s")
    else:
        logging.basicConfig(level=logging.INFO, format="%(message)s")

    if args.command == "init":
        init_resume()
    elif args.command == "build":
        prefix, _ = os.path.splitext(os.path.abspath(args.file))

        with open(args.file, encoding="utf-8") as mdfp:
            md = mdfp.read()

        # Use same-named .css file if it exists alongside the input file,
        # otherwise fall back to the bundled default CSS.
        css_path = prefix + ".css"
        if os.path.exists(css_path):
            with open(css_path, encoding="utf-8") as cssfp:
                css = cssfp.read()
        else:
            css = get_bundled_css()

        html = make_html(md, css)

        if not args.no_html:
            with open(prefix + ".html", "w", encoding="utf-8") as htmlfp:
                htmlfp.write(html)
                logging.info(f"Wrote {htmlfp.name}")

        if not args.no_pdf:
            write_pdf(html, prefix + ".pdf", chrome=args.chrome_path or "")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
