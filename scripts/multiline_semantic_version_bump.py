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

alpha_var = "VERSION_ALPHA"
build_var = "VERSION_BUILD"
minor_var = "VERSION_MINOR"
major_var = "VERSION_MAJOR"


def bump_version(version_file: str, version_spec: str):
    alpha = 0
    build = 0
    minor = 0
    major = 0

    with open(version_file, "r", encoding="utf-8") as v:
        for line in v.readlines():
            if line.startswith(alpha_var):
                alpha = int(line.split('=')[1])
            elif line.startswith(build_var):
                build = int(line.split('=')[1])
            elif line.startswith(minor_var):
                minor = int(line.split('=')[1])
            elif line.startswith(major_var):
                major = int(line.split('=')[1])

    # Alpha Release
    if version_spec == "alpha":
        if alpha == 0:
            build += 1
        alpha += 1
        was_alpha = False  # Just for editor warnings, this won't be referenced
    else:
        was_alpha = alpha != 0
        alpha = 0

    # Stable Release
    if version_spec == "build":
        if not was_alpha:
            build += 1
    elif version_spec == "minor":
        build = 0
        minor += 1
    elif version_spec == "major":
        build = 0
        minor = 0
        major += 1

    # Write version change
    for line in fileinput.input(version_file, inplace=True):
        if line.startswith(alpha_var):
            print(f"{alpha_var} = {alpha}")
        elif line.startswith(build_var):
            print(f"{build_var} = {build}")
        elif line.startswith(minor_var):
            print(f"{minor_var} = {minor}")
        elif line.startswith(major_var):
            print(f"{major_var} = {major}")
        else:
            print(line.rstrip('\n'))


if __name__ == "__main__":
    file = argv[1]
    version_spec = argv[2]
    if len(argv) > 2:
        version_spec = argv[2]
    else:
        version_spec = "alpha"
    if len(argv) > 5:
        alpha_var = argv[3]
        build_var = argv[4]
        minor_var = argv[5]
        major_var = argv[6]

    bump_version(file, version_spec)
