#!/usr/bin/env python3
"""
Resume Markdown MCP Server

Exposes one tool and two resources for AI-assisted resume creation and PDF export.
"""
import json
import os
from typing import Optional

from mcp.server.fastmcp import FastMCP

from resume_markdown.converter import (
    get_bundled_css,
    get_template_md,
    make_html,
    write_pdf,
)

mcp = FastMCP("resume-markdown")


@mcp.tool()
def export_resume_pdf(
    markdown_content: Optional[str] = None,
    file_path: Optional[str] = None,
    css_content: Optional[str] = None,
    css_path: Optional[str] = None,
    output_path: str = "~/resume.pdf",
) -> str:
    """Export a Markdown resume to PDF.

    ## Resume Markdown format

    The resume must use these conventions for the PDF to render correctly:

    - `# Full Name` — first h1 becomes the page title and name header
    - Unordered list immediately after h1 — becomes an inline contact bar (email, phone, URL, location)
    - Paragraph after the contact list — optional summary/objective
    - `## Section Name` — major section headings (Experience, Education, Skills, etc.)
    - `### <span>Job Title, Company</span> <span>Start – End</span>` — entry headings; the two
      `<span>` tags are required so the title and dates are laid out left/right via flexbox
    - Bullet lists under an entry — achievements and details

    ## When to use file_path vs markdown_content

    - If the user's Markdown file already follows the format above → pass `file_path` directly.
    - If the file doesn't follow the format (missing `<span>` tags, wrong structure, etc.) →
      read the file, rewrite it to match the format, and pass the result as `markdown_content`.
    - If you are generating a resume from scratch → write the Markdown and pass as `markdown_content`.
    - If you need a full example of the correct format → read the `resume://template` resource first.

    ## CSS / styling

    By default the built-in stylesheet is applied automatically — no CSS parameter needed.
    If the user wants to customise the style:
    - Pass `css_path` pointing to a CSS file, OR
    - Pass `css_content` with the raw CSS text.
    To see the default stylesheet, read the `resume://style` resource.

    ## Parameters

    - markdown_content: Raw Markdown text of the resume (mutually exclusive with file_path)
    - file_path: Path to a .md file (mutually exclusive with markdown_content)
    - css_content: Custom CSS text (mutually exclusive with css_path; optional)
    - css_path: Path to a custom CSS file (mutually exclusive with css_content; optional)
    - output_path: Where to write the PDF (default: ~/resume.pdf)

    ## Returns

    JSON string: {"pdf_path": "/absolute/path/to/resume.pdf", "success": true}
    """
    # Validate Markdown input
    if markdown_content is None and file_path is None:
        return json.dumps({"success": False, "error": "Provide either markdown_content or file_path."})
    if markdown_content is not None and file_path is not None:
        return json.dumps({"success": False, "error": "Provide only one of markdown_content or file_path, not both."})

    # Validate CSS input
    if css_content is not None and css_path is not None:
        return json.dumps({"success": False, "error": "Provide only one of css_content or css_path, not both."})

    # Read Markdown
    if file_path is not None:
        file_path = os.path.abspath(os.path.expanduser(file_path))
        if not os.path.isfile(file_path):
            return json.dumps({"success": False, "error": f"File not found: {file_path}"})
        with open(file_path, encoding="utf-8") as f:
            md = f.read()
    else:
        md = markdown_content

    # Resolve CSS
    if css_path is not None:
        css_path = os.path.abspath(os.path.expanduser(css_path))
        if not os.path.isfile(css_path):
            return json.dumps({"success": False, "error": f"CSS file not found: {css_path}"})
        with open(css_path, encoding="utf-8") as f:
            css = f.read()
    elif css_content is not None:
        css = css_content
    else:
        css = get_bundled_css()

    # Convert and export
    try:
        html = make_html(md, css)
        pdf_path = write_pdf(html, output_path)
        return json.dumps({"success": True, "pdf_path": pdf_path})
    except Exception as exc:
        return json.dumps({"success": False, "error": str(exc)})


@mcp.resource("resume://template")
def get_resume_template() -> str:
    """The built-in Markdown resume template.

    Read this resource to understand the exact format conventions required by
    export_resume_pdf, or to use as a starting point when writing a resume.
    """
    return get_template_md()


@mcp.resource("resume://style")
def get_resume_style() -> str:
    """The built-in default CSS stylesheet applied to all resumes.

    Read this resource when the user wants to customise the PDF appearance.
    Modify the CSS and pass the result via the css_content parameter of
    export_resume_pdf.
    """
    return get_bundled_css()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
