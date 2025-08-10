from revel import (
    print,
    success,
    warning,
    error,
    input,
    select_yes_no,
    print_chapter,
    debug,
)
import revel
import time
import sys

revel.select_yes_no("foo?", default_value=True)
# revel.input("[bold]Foo[/]")
