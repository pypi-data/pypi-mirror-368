from pathlib import Path

from psi_toml.parser import TomlParser


toml = TomlParser()

path = '/home/jeff/projects/phoenix/programs/attendance_rebates/pyproject.toml'

with open(path, 'r') as f_toml:
    result = toml.load(f_toml)
    print(result['dependency-groups'])
