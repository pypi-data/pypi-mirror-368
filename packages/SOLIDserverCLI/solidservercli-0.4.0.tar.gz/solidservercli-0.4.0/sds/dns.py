import typer

import sds.config as config

app = typer.Typer()


@app.command()
def rr():
    config.err_console.log('dns rr not yet implemented')


if __name__ == "__main__":
    app()
