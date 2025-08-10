import argparse
import sys

from . import editor

def main():
    parser = argparse.ArgumentParser(
        prog='pelyx',
        description='Pelyx is a toy terminal text editor.',
    )
    parser.add_argument(
        'path', nargs='*', help='the file to open')
    args = parser.parse_args()

    app = editor.Editor(args.path)
    app.run()

    sys.exit(app.return_code or 0)
