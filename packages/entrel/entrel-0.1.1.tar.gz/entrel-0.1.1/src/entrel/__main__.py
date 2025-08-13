if __name__ == "__main__":
    import argparse
    import entrel

    parser = argparse.ArgumentParser(
        description="Generate ER diagram from a TOML definition file."
    )
    parser.add_argument("definition_file", help="Path to the TOML definition file.")
    parser.add_argument(
        "output_file", help="Path where the generated LaTeX file will be saved."
    )
    args = parser.parse_args()
    entrel.generate(args.definition_file, args.output_file)