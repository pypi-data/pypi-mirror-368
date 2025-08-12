from __future__ import annotations

import argparse
from typing import List, Optional

from .use_cases.hello.say_hello import say_hello


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="FullTrader Data CLI")
    parser.add_argument("-n", "--name", default="FullTrader", help="Nome para o cumprimento")
    args = parser.parse_args(argv)

    print(say_hello(args.name))
    return 0


