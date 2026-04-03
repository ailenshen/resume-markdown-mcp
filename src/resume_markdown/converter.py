#!/usr/bin/env python3
import base64
import itertools
import logging
import os
import re
import select
import shutil
import subprocess
import sys
import tempfile
import time
from importlib.resources import files

import markdown

preamble = """\
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{title}</title>
<style>
{css}
</style>
</head>
<body>
<div id="resume">
"""

postamble = """\
</div>
</body>
</html>
"""

CHROME_GUESSES_MACOS = (
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Google Chrome Canary.app/Contents/MacOS/Google Chrome Canary",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
)

# https://stackoverflow.com/a/40674915/409879
CHROME_GUESSES_WINDOWS = (
    # Windows 10
    os.path.expandvars(r"%ProgramFiles(x86)%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%ProgramFiles%\Google\Chrome\Application\chrome.exe"),
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\Application\chrome.exe"),
    # Windows 7
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    # Vista
    r"C:\Users\UserName\AppDataLocal\Google\Chrome",
    # XP
    r"C:\Documents and Settings\UserName\Local Settings\Application Data\Google\Chrome",
)

# https://unix.stackexchange.com/a/439956/20079
CHROME_GUESSES_LINUX = [
    "/".join((path, executable))
    for path, executable in itertools.product(
        (
            "/usr/local/sbin",
            "/usr/local/bin",
            "/usr/sbin",
            "/usr/bin",
            "/sbin",
            "/bin",
            "/opt/google/chrome",
        ),
        ("google-chrome", "chrome", "chromium", "chromium-browser"),
    )
]


def get_bundled_css() -> str:
    return (files("resume_markdown") / "resume.css").read_text(encoding="utf-8")


def get_template_md() -> str:
    return (files("resume_markdown") / "resume.md").read_text(encoding="utf-8")


def guess_chrome_path() -> str:
    if sys.platform == "darwin":
        guesses = CHROME_GUESSES_MACOS
    elif sys.platform == "win32":
        guesses = CHROME_GUESSES_WINDOWS
    else:
        guesses = CHROME_GUESSES_LINUX
    for guess in guesses:
        if os.path.exists(guess):
            logging.info("Found Chrome or Chromium at " + guess)
            return guess
    raise ValueError("Could not find Chrome. Please set --chrome-path.")


def title(md: str) -> str:
    for line in md.splitlines():
        if re.match("^#[^#]", line):
            return line.lstrip("#").strip()
    raise ValueError(
        "Cannot find any lines that look like markdown h1 headings to use as the title"
    )


def make_html(md: str, css: str) -> str:
    return "".join(
        (
            preamble.format(title=title(md), css=css),
            markdown.markdown(md, extensions=["smarty", "abbr"]),
            postamble,
        )
    )


def write_pdf(
    html: str, output_path: str, chrome: str = "", timeout: int = 30
) -> str:
    chrome = chrome or guess_chrome_path()
    output_path = os.path.abspath(os.path.expanduser(output_path))
    output_dir = os.path.dirname(output_path)
    if not os.path.isdir(output_dir):
        raise ValueError(f"Output directory does not exist: {output_dir}")
    html64 = base64.b64encode(html.encode("utf-8"))
    options = [
        "--no-sandbox",
        "--headless",
        "--print-to-pdf-no-header",
        "--no-pdf-header-footer",
        "--enable-logging=stderr",
        "--log-level=2",
        "--in-process-gpu",
        "--disable-gpu",
    ]

    tmpdir = tempfile.mkdtemp(prefix="resume.md_")
    options.append(f"--crash-dumps-dir={tmpdir}")
    options.append(f"--user-data-dir={tmpdir}")

    proc = subprocess.Popen(
        [
            chrome,
            *options,
            f"--print-to-pdf={output_path}",
            "data:text/html;base64," + html64.decode("utf-8"),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,  # merge stderr into stdout so we read one stream
    )

    try:
        pdf_written = False
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            # Use select so we don't block forever if Chrome stops producing output
            ready, _, _ = select.select([proc.stdout], [], [], 1.0)
            if not ready:
                # No output this second — check if Chrome already exited
                if proc.poll() is not None:
                    break
                continue

            line = proc.stdout.readline()
            if not line:
                break  # EOF: Chrome closed its end of the pipe

            text = line.decode("utf-8", errors="replace").strip()
            logging.debug(f"Chrome: {text}")

            if "written to file" in text:
                logging.info(f"Wrote {output_path}")
                pdf_written = True
                break

        if not pdf_written:
            if os.path.isfile(output_path):
                logging.info(f"Wrote {output_path} (detected on disk)")
                pdf_written = True
            else:
                raise RuntimeError(
                    f"Chrome did not produce {output_path} within {timeout}s"
                )
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait()
        shutil.rmtree(tmpdir, ignore_errors=True)
        if os.path.isdir(tmpdir):
            logging.debug(f"Could not delete {tmpdir}")

    return output_path
