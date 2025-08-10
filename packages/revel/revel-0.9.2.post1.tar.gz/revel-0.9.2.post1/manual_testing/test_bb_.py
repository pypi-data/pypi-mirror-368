import revel

raw = """
This is [bold]BBCode[/bold] text. It [red italic]works[/]! How about [blue underlined]two at once[/blue underlined]?
URLs are highlighted: https://example.com
As are emails: foo@bar.com
And numbers: Ha 123,456.789,123e2.7,4 Ho
""".strip()

# raw = revel.input("Markup source")

revel.select_short("Continue?", {"y": True, "n": False})

print(raw)
print()
print(revel.unescape(raw))
print()
revel.print(raw)
print()
revel.print(revel.escape(raw))
