# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2022 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import fileinput
from sys import argv


def bump_version(version_file: str, version_spec: str):
    with open(version_file, "r", encoding="utf-8") as v:
        for line in v.readlines():
            if line.startswith("__version__"):
                if '"' in line:
                    version = line.split('"')[1]
                else:
                    version = line.split("'")[1]

    # Parse version from string
    parts = version.split('.')
    if 'a' in parts[2]:
        major = parts[0]
        minor = parts[1]
        patch, alpha = parts[2].split('a', 1)
        was_alpha = True
    else:
        major, minor, patch = parts
        alpha = None
        was_alpha = False

    # Alpha Release
    if version_spec == "alpha":
        if not alpha:
            alpha = 0
            patch = int(patch) + 1
        alpha = int(alpha) + 1
    else:
        alpha = None

    # Stable Release
    if version_spec == "patch":
        if not was_alpha:
            patch = int(patch) + 1
    elif version_spec == "minor":
        patch = 0
        minor = int(minor) + 1
    elif version_spec == "major":
        patch = 0
        minor = 0
        major = int(major) + 1

    # Build version string
    if alpha:
        version = f"{major}.{minor}.{patch}a{alpha}"
    else:
        version = f"{major}.{minor}.{patch}"

    for line in fileinput.input(version_file, inplace=True):
        if line.startswith("__version__"):
            print(f"__version__ = \"{version}\"")
        else:
            print(line.rstrip('\n'))


if __name__ == "__main__":
    file = argv[1]
    if len(argv) > 2:
        version_spec = argv[2]
    else:
        version_spec = "alpha"
    bump_version(file, version_spec)
