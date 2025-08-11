"""Create Images API documentation for OpenSCAD code.

Unlike the rest of SCA2D this requires openscad to be installed and on the path.
"""

import os
import subprocess
import re
from typing import Optional

from sca2d.messages import Message
from sca2d.scadclasses import DummyTree


class ImageGenerator:
    """A class for handling image generation.

    This handles both creating SCAD files from source that can be generated into into
    images, and generating images.
    """

    def __init__(self, source_dir, docs_dir):
        """Initialise the ImageGenerator with source and documentation directories.

        * Set up environment variables and paths needed to generate images from OpenSCAD
        code.
        * Creates directories for example SCAD files and output assets.

        :param source_dir: Root directory of the OpenSCAD source files
        :param docs_dir: Output directory for generated documentation files
        """
        self._docs_dir = docs_dir
        self._examples_dir = os.path.join(self._docs_dir, "_examples")
        self._assets_dir = os.path.join(self._docs_dir, "assets")

        self._env = os.environ.copy()
        self._source_dir = os.path.abspath(source_dir)
        openscad_path = self._env.get("OPENSCADPATH", "")
        openscad_path = (
            self._source_dir + os.pathsep + openscad_path
            if openscad_path
            else self._source_dir
        )
        self._env["OPENSCADPATH"] = openscad_path
        self._setup_directories()

    @property
    def assets_dir(self):
        """The directory path where generated image assets are saved."""
        return self._assets_dir

    @property
    def examples_dir(self):
        """The directory where OpenSCAD example snippets are saved for processing."""
        return self._examples_dir

    def _setup_directories(self):
        """Create output directories if they do not exist."""
        if not os.path.isdir(self._examples_dir):
            os.makedirs(self._examples_dir)

        if not os.path.isdir(self._assets_dir):
            os.makedirs(self._assets_dir)

    def gen_image_scad_file(self, code, ident, scad_source):
        """Generate a SCAD source file from example code for image generation.

        Write the example SCAD code to a uniquely identified file referencing the
        original source.

        :param code: The SCAD code snippet extracted from documentation
        :param ident: Unique identifier for the example within its source file
        :param scad_source: Path to the original SCAD file defining the example

        :returns: Identifier string for the generated SCAD file
        """
        source_wo_ext = os.path.splitext(scad_source)[0]
        file_ident = re.sub(r"[^a-zA-Z0-9_]+", "--", source_wo_ext + "--" + ident)
        filepath = self.ident_to_scad_path(file_ident)
        with open(filepath, "w", encoding="utf-8") as file_obj:
            file_obj.write(f"use <{scad_source}>\n\n")
            file_obj.write(code)
        return file_ident

    def ident_to_png_path(self, file_ident):
        """Return the full path to the PNG image corresponding to a given identifier.

        :param file_ident: Identifier string for the example

        :returns: Path to the PNG image file
        """
        return os.path.join(self._assets_dir, file_ident + ".png")

    def ident_to_scad_path(self, file_ident):
        """Return the full path to the SCAD source file for a given identifier.

        :param file_ident: Identifier string for the example

        :returns: Path to the SCAD source file
        """
        return os.path.join(self._examples_dir, file_ident + ".scad")

    def create_image(
        self, file_ident: str, customisers: list[str]
    ) -> tuple[bool, Optional[str]]:
        """Invoke OpenSCAD to generate a PNG image from the SCAD source file.

        Run the OpenSCAD command line tool to render the SCAD file into a PNG image.

        :param file_ident: Identifier string for the example SCAD file to render

        :returns: A tuple of a boolean representing image generation success, and on
            failure a Message object for the failure (or None if generation was
            successful.
        """
        custom_args = args_from_customisers(customisers)
        scad_path = self.ident_to_scad_path(file_ident)
        png_path = self.ident_to_png_path(file_ident)
        cmd = ["openscad"] + custom_args + ["-o", png_path, scad_path]
        try:
            subprocess.run(cmd, env=self._env, check=True)
            return True, None
        except subprocess.CalledProcessError:
            return False, Message(scad_path, "E4001", DummyTree())


def args_from_customisers(customisers):
    """Return arguments based on customisers.

    No warnings are given for incorrect or duplicated customisers. These should already
    have been raised during parsing.
    """
    if "no-axes" in customisers:
        args = []
    else:
        args = ["--view", "axes"]
    if "render" in customisers:
        args.append("--render")
    return args
