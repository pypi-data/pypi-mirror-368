import argparse
from importlib.metadata import PackageNotFoundError, version

from definet import definet


def get_version():
    try:
        return version("definet")
    except PackageNotFoundError:
        return "unknown"


def main():
    parser = argparse.ArgumentParser(
        description="tool that searches for the definition of any word you provide"
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"definet {get_version()}",
        help="Show definet version",
    )
    parser.add_argument("word", nargs="?", type=str, help="word to define")
    args = parser.parse_args()

    word = args.word if args.word else ""

    definet(single=word)


if __name__ == "__main__":
    main()
