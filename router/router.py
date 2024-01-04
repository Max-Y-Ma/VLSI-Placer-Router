import argparse

class Router:
    """
    """

if __name__ == "__main__":
    # Input and Output file arguments
    parser = argparse.ArgumentParser(description="Program to demonstrate maze router")
    parser.add_argument("gridfile", type=str, help="Path to the input grid file")
    parser.add_argument("netfile", type=str, help="Path to the input net file")
    parser.add_argument("outfile", type=str, help="Path to the output file")
    args = parser.parse_args()

    print(args.gridfile)
    print(args.netfile)
    print(args.outfile)
