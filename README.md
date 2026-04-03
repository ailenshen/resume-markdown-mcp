# resume-markdown-mcp

Write your resume in Markdown, export to PDF — powered by AI via MCP.

![Resume preview](https://raw.githubusercontent.com/ailenshen/resume-markdown-mcp/main/example/resume.png)

Let Claude write, edit, and format your resume. The MCP server handles Markdown-to-PDF conversion with a built-in stylesheet — no CSS knowledge required.

Requires: Python ≥ 3.12, Google Chrome or Chromium (for PDF export)

## Setup

### Claude Code

```bash
claude mcp add resume-markdown -- uvx resume-markdown-mcp
```

### Claude Desktop

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "resume-markdown": {
      "command": "uvx",
      "args": ["resume-markdown-mcp"]
    }
  }
}
```

## What Can It Do?

| Type | Name | Description |
|------|------|-------------|
| Tool | `export_resume_pdf` | Convert a Markdown resume to PDF. Accepts a file path or raw Markdown text. CSS is applied automatically. |
| Resource | `resume://template` | The built-in Markdown resume template. AI reads this to understand the required format. |
| Resource | `resume://style` | The built-in CSS stylesheet. AI reads this when you want to customise the appearance. |

## Example Prompts

- "Help me write a resume for a software engineer role and export it as a PDF to my Desktop"
- "Here's my resume at ~/resume.md — export it to PDF"
- "My resume.md doesn't follow the right format, fix it and export to /tmp/resume.pdf"
- "Make the font size smaller and re-export my resume"

## Resume Markdown Format

The PDF renderer depends on these Markdown conventions:

```markdown
# Full Name

- email@example.com
- Phone number
- City, Country

One-line summary (optional)

## Experience

### <span>Job Title, Company</span> <span>2022 – 2025</span>

- Achievement one
- Achievement two

## Education

### <span>Degree, University</span> <span>2018 – 2022</span>

## Skills

- Skill category: item, item, item
```

The `<span>` tags inside `###` headings are required — they enable the left/right flexbox layout for title and date. AI handles this automatically when writing from scratch; if your existing file lacks them, ask Claude to reformat it before exporting.

## How It Works

1. AI calls `export_resume_pdf` with Markdown content or a file path
2. The server converts Markdown to HTML using [python-markdown](https://python-markdown.github.io/), with the built-in CSS inlined
3. Headless Chrome renders the HTML and prints it to PDF
4. Chrome exits as soon as the PDF is written; the tool returns the output path

## CLI Usage

The package also ships a standalone CLI:

```bash
# Create template files in the current directory
uvx resume-markdown-mcp init

# Build HTML and PDF from resume.md
uvx resume-markdown-mcp build

# Options
uvx resume-markdown-mcp build --no-pdf          # HTML only
uvx resume-markdown-mcp build --no-html         # PDF only
uvx resume-markdown-mcp build myresume.md       # Custom input file
uvx resume-markdown-mcp build --chrome-path=... # Specify Chrome path
```

The CLI picks up a `resume.css` file alongside the input if present; otherwise the built-in stylesheet is used.

## License

MIT
