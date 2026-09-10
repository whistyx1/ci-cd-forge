from cli.app import run_cli


def main() -> int:
    try:
        return run_cli()
    except (EOFError, KeyboardInterrupt):
        print('Operation canceled by user.')
        return 130


if __name__ == '__main__':
    raise SystemExit(main())
