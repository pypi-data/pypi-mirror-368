"""A helper script to run portfolio applications."""

from __future__ import annotations

import runpy
import sys


def main() -> None:
    """A helper script to run portfolio applications.

    This script acts as a dynamic entry point, using `runpy` to execute
    the main module of a specified application. It expects the application
    name as its first command-line argument, and forwards all subsequent
    arguments to that application.
    """
    if len(sys.argv) < 2:
        print("Error: No application name provided.", file=sys.stderr)
        print("Usage: poe run <app_name> [app_args...]", file=sys.stderr)
        sys.exit(1)

    app_name = sys.argv[1]
    # The rest of the arguments are for the application itself.
    app_args = sys.argv[2:]

    # We must reconstruct sys.argv for the target script. The first element
    # should be the script path, which runpy will interpret correctly.
    sys.argv = [f"{app_name}.py", *app_args]

    try:
        # Dynamically find and run the main module of the requested app.
        runpy.run_module(
            f"hyperskill_python_portfolio.{app_name}.main",
            run_name="__main__",
        )
    except ModuleNotFoundError:
        print(f"Error: Application '{app_name}' not found.", file=sys.stderr)
        sys.exit(1)
    except ImportError as e:
        print(f"Error importing application '{app_name}': {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
