"""
Command-line interface for dotpptx PowerPoint extraction and repackaging tool.

This module provides the CLI commands for working with PowerPoint (.pptx) files.
Users can extract presentations into XML components for inspection and editing,
then repackage them back into working .pptx files.

Commands:
    unpptx: Extract PowerPoint files into their component XML/media files
    dopptx: Repackage extracted directories back into .pptx files

The CLI supports both single-file operations and batch processing of multiple
files in a directory.
"""

import shutil
from pathlib import Path

import click

from dotpptx.dotpptx import dopptx_folder, unpptx_file


@click.group()
def cli() -> None:
    """
    Dotpptx - PowerPoint file extraction and repackaging tool.

    A command-line utility for working with PowerPoint (.pptx) files at the XML level.
    This tool allows you to extract PowerPoint presentations into their component
    XML files for inspection and editing, then repackage them back into working
    .pptx files.

    Common workflows:
    1. Extract a presentation: unpptx presentation.pptx
    2. Edit the XML files as needed
    3. Repackage: dopptx presentation_pptx/

    This is particularly useful for:
    - Programmatic manipulation of presentations
    - Version control of presentation content
    - Debugging presentation issues
    - Bulk modifications across slides
    """


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--pretty", is_flag=True, default=False)
def unpptx(path: Path, pretty: bool) -> None:  # noqa: FBT001
    """
    Extract PowerPoint (.pptx) files into their component parts.

    This command decompresses a PowerPoint presentation file into a directory structure
    that mirrors the internal organization of the .pptx file (which is essentially a
    ZIP archive). This allows you to examine and edit the underlying XML files that
    make up a PowerPoint presentation.

    The extracted folder will be named after the original file with a "_pptx" suffix.
    For example, "presentation.pptx" becomes "presentation_pptx/".

    Args:
        path: The path to a PowerPoint file (.pptx) to extract, or a directory
              containing multiple .pptx files to process in batch. Temporary files
              starting with "~$" are automatically skipped.
        pretty: If enabled, formats all XML files in the extracted content with
                proper indentation and line breaks for better readability. This
                makes the files easier to read and diff, but may increase file size.

    Examples:
        Extract a single PowerPoint file:
            python -m dotpptx unpptx presentation.pptx

        Extract all PowerPoint files in a directory with pretty formatting:
            python -m dotpptx unpptx /path/to/presentations --pretty

    Note:
        The extracted files maintain the exact same structure as the original .pptx
        internal format, including _rels directories, XML files, and media content.

    """
    if path.is_file():
        unpptx_file(path.parent, path, pretty=pretty)
    else:
        for pptx_file in path.glob("*.pptx"):
            if pptx_file.stem.startswith("~$"):
                continue

            unpptx_file(path, pptx_file, pretty=pretty)


@cli.command()
@click.argument("pptx-folder", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("--delete-original", is_flag=True, default=False)
def dopptx(pptx_folder: Path, delete_original: bool) -> None:  # noqa: FBT001
    """
    Repackage extracted PowerPoint directories back into .pptx files.

    This command takes directories that were previously extracted using the unpptx
    command and recompresses them back into functional PowerPoint (.pptx) files.
    This is useful after you've made modifications to the underlying XML structure
    of a presentation.

    The command can process either a single extracted directory (ending with "_pptx")
    or a parent directory containing multiple extracted directories.

    Args:
        pptx_folder: Path to either:
                    - A single extracted PowerPoint directory (ending with "_pptx")
                    - A parent directory containing multiple "*_pptx" directories
        delete_original: If enabled, removes the source directory after successfully
                        creating the .pptx file. Use with caution as this permanently
                        deletes the extracted files.

    Examples:
        Repackage a single extracted directory:
            python -m dotpptx dopptx presentation_pptx/

        Repackage all extracted directories in a folder:
            python -m dotpptx dopptx /path/to/extracted_presentations/

        Repackage and clean up source directories:
            python -m dotpptx dopptx presentation_pptx/ --delete-original

    Note:
        The resulting .pptx file will be created in the parent directory of the
        extracted folder, with the same base name as the original file.
        For example, "presentation_pptx/" becomes "presentation.pptx".

    """
    if pptx_folder.name.endswith("_pptx"):
        dopptx_folder(pptx_folder.parent, pptx_folder)

        if delete_original:
            shutil.rmtree(pptx_folder)

    else:
        for pptx_exploded_folder in pptx_folder.glob("*_pptx"):
            dopptx_folder(pptx_folder, pptx_exploded_folder)

            if delete_original:
                shutil.rmtree(pptx_exploded_folder)


if __name__ == "__main__":
    cli()
