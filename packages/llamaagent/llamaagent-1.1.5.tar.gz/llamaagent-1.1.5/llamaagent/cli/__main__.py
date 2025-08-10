"""Allow `python -m llamaagent.cli …` and `python -m llamaagent …`."""

from llamaagent.cli.main import main

if __name__ == "__main__":  # pragma: no cover
    main()
