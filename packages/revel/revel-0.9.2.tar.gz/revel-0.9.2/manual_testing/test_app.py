import revel

revel.GLOBAL_STYLES.add_alias("primary", ["magenta"])
revel.GLOBAL_STYLES.add_alias("bg-primary", ["bg-magenta"])

app = revel.App(
    nicename="Test App",
    command_name="test_app",
    summary="This is a summary",
    details="""
This is a detailed description of the app.

It can be multiple lines long.
With newlines too.
""",
    version="1.2.3",
)


@app.command()
def hello_world():
    revel.print("Hello world!")


@app.command(
    # name="FOOOO",
    aliases=["foo", "bar"],
    summary="Does foo",
    details="""
This is a detailed description of what foo does
""",
    parameters=[
        revel.Parameter(
            "text_to_echo",
            summary="The text to print",
            prompt="What text do you want to print?",
        )
    ],
)
def echo(text_to_echo: str, *, color: bool = False):
    if color:
        text_to_echo = f"[green]{text_to_echo}[/]"

    revel.print(
        text_to_echo,
    )


app.run()
