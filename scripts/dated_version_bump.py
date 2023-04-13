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
from datetime import datetime
from sys import argv


def bump_version(version_file: str, do_alpha: bool):
    with open(version_file, "r", encoding="utf-8") as v:
        for line in v.readlines():
            if line.startswith("__version__"):
                if '"' in line:
                    version = line.split('"')[1]
                else:
                    version = line.split("'")[1]

    date = datetime.now()
    version = f"{str(date.year)[2:]}.{date.month}.{date.day}"

    if do_alpha:
        if 'a' in version and not version.endswith('a'):
            alpha_ver = int(version.split('a')[1]) + 1
        else:
            alpha_ver = 1

        version = f"{version}a{alpha_ver}"

    for line in fileinput.input(version_file, inplace=True):
        if line.startswith("__version__"):
            print(f"__version__ = \"{version}\"")
        else:
            print(line.rstrip('\n'))


if __name__ == "__main__":
    file = argv[1]
    if len(argv) > 2:
        print(f"do_alpha={argv[2]}")
        alpha = argv[2] == "true"
    else:
        alpha = True
    bump_version(file, alpha)
