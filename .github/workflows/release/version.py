#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Split branch name with different parts."""

import os
import re
from tabnanny import verbose

BRANCH_NAME = os.getenv('branch');
REGEX_VERSION = r'^([\w]+-[\w]+-[\w]+)' #r'^[0-9]\-[0-9]\-[0-9]$'

if __name__ == '__main__':
    lines = BRANCH_NAME.split('-', 1)
    changelog = lines[0]
    version_name = lines[len(lines) - 1]
    if (changelog == version_name) :
        version_name = 'new-release'
    name = version_name.replace(version_name + '-', '')
    version_name = version_name.replace('-', '.')

    print('branch_name={}'.format(name))
    print('version={}'.format(changelog))
