"""
Dotpptx - PowerPoint file extraction and repackaging tool.

A Python library and command-line tool for working with PowerPoint (.pptx) files
at the XML level. This allows for programmatic manipulation of presentations by
extracting them into their component XML files, editing them, and repackaging
them back into working .pptx files.

Key Features:
- Extract .pptx files into directory structures with XML components
- Repackage modified directories back into functional .pptx files
- Optional XML prettification for improved readability
- Command-line interface for easy batch processing
- Support for programmatic manipulation of presentation content

Example Usage:
    >>> from dotpptx import unpptx_file, dopptx_folder
    >>> from pathlib import Path
    >>>
    >>> # Extract a PowerPoint file
    >>> unpptx_file(Path("."), Path("presentation.pptx"), pretty=True)
    >>>
    >>> # Repackage it back
    >>> dopptx_folder(Path("."), Path("presentation_pptx"))

Command Line Usage:
    $ python -m dotpptx unpptx presentation.pptx --pretty
    $ python -m dotpptx dopptx presentation_pptx/
"""

from .dotpptx import dopptx_folder, unpptx_file

__version__ = "0.1.2"
__all__ = ["unpptx_file", "dopptx_folder"]
