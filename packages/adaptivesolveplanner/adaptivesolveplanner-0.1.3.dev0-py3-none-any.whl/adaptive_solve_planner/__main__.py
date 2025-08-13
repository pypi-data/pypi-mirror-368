def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(prog="adaptivesolveplanner", description="Adaptive Solve Planner CLI")
    parser.add_argument("--version", action="store_true", help="Show package version")
    args = parser.parse_args(argv)
    if args.version:
        from . import __version__
        print(__version__)
    else:
        print("Run with --version")

if __name__ == "__main__":
    main()
