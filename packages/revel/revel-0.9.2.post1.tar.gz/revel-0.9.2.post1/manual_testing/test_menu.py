from typing import *  # type: ignore

import revel
from revel import *


if __name__ == "__main__":
    print_chapter("Chapter!")
    print("Yes, totally inside of a chapter")

    # result = revel.select_multiple(
    result = revel.menu.select(
        {
            "First": "first",
            "Second": "second",
            "Third": "third",
        },
        prompt="Select an option:",
    )

    print(f"You've chosen: {result!r}")
