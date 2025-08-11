import os
import sys
import pathlib

from django.core.management import execute_from_command_line, call_command

cd = pathlib.Path(__file__).parents[0]

def init(argv):
    settings = argv[1]

    if len(argv) > 2:
        actions = argv[2]
    else:
        actions = "magcp"

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings)

    execute_from_command_line([
        "__irie__",
        "migrate"
    ])

    if "m" in actions:
        call_command("makemigrations")
        call_command("migrate")

    if "a" in actions:
        call_command("init_assets")

    if "g" in actions:
        call_command("init_cesmd")

    if "c" in actions:
        call_command("init_corridors")

    if "p" in actions:
        call_command("init_predictors")

if __name__ == "__main__":
    init(sys.argv)

