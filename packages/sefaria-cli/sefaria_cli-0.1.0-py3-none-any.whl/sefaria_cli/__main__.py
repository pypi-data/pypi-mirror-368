def app():
    try:
        from . import cli
        if hasattr(cli, "main") and callable(cli.main):
            return cli.main()
    except Exception:
        pass
    import runpy
    runpy.run_module("sefaria_cli.cli", run_name="__main__")

if __name__ == "__main__":
    app()
