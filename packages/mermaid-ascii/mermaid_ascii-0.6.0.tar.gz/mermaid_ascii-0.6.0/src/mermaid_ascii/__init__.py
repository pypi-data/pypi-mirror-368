import subprocess
import sys

from pathlib import Path
from typing import List


def run(args: List[str]):
    command = [f'{Path(__file__).parent}/mermaid-ascii'] + args[1:]
    result = subprocess.run(command, stdout=sys.stdout, stderr=sys.stderr)


def mermaid_ascii():
    run(sys.argv)


if __name__ == '__main__':
    mermaid_ascii()
