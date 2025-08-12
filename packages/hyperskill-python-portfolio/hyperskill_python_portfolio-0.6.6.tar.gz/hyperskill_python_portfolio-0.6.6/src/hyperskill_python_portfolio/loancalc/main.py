"""Main entry point for the Loan Calculator application."""

from __future__ import annotations

from .cli import build_parser


def main() -> None:
    """Parses command-line arguments and runs the appropriate handler."""
    parser = build_parser()
    args = parser.parse_args()

    # The 'func' attribute is set by set_defaults in the CLI module
    output_message = args.func(args)
    if output_message:
        print(output_message)


if __name__ == "__main__":
    main()
