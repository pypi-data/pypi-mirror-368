# Revel

`revel` helps you create beautiful interfaces for your command line tools. Best
of all, it's extremely easy to use.

Simply replace the standard `print` function with revel's and just like that you
can now display colors!

```py
from revel import print

print('[green]Hello, World![/]')
```

## Styles

`revel` uses BBCode-style markup to style your text. A variety of styles
are available:

- Formatting:
  - bold
  - dim
  - italic
  - underlined
  - inverted
  - strikethrough

- Text Colors:
  - black
  - red
  - green
  - blue
  - magenta
  - cyan
  - white

- Background Colors:
  - bg-black
  - bg-red
  - bg-green
  - bg-blue
  - bg-magenta
  - bg-cyan
  - bg-white

Adding `weak` to a tag will only apply the styles of that tag, if no competing styles are already applied. For example:

```py
print("[red]Hello, [weak blue underlined]World![/][/]")
```

This will be displayed entirely in red (since the weak "blue" formatting is
overridden by "red"), but the "underlined" formatting will still be applied.

## Progressbars

Adding progressbars is easy as can be:

```py
from revel import print, ProgressBar
import time

with ProgressBar(max=10, unit="percent") as bar:
    for ii in range(10):
        bar.progress = ii
        time.sleep(1.0)
```

You can switch units between "count", "percent", "byte" and "time". The bar will
also automatically display how much time remains until completion, once it is
confident in its estimate.

## Edit text after it has already been printed

Docked widgets can be edited at will. For example, this example docks a text
line and updates it repeatedly:

```py
from revel import print
import time

line = print("Looking for files", dock=True)

for ii in range(1, 10):
    line.text = f"Found {ii} file(s)"
    time.sleep(1.0)
```

## Additional `print`-like methods

In addition to `print`, revel also provides `success`, `warning`, `error` and
`fatal`. These will be displayed in color, drawing attention to the message.

## TODO

- Implement the `verbatim` tag
- Jupyter Notebook support
- Test on bad terminals
- Actual docs
- Showcase features:
  - `print_chapter`
  - `select`
  - `select_multiple`
  - `select_short`
    - `select_yes_no`
  - `input_key`
  - `input`
    - general improvements, such as parsing, default
    - secret input
  - `escape`
  - `unescape`
