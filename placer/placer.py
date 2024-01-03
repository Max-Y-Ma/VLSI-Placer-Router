import argparse
import numpy as np
import scipy.linalg as la

class QuadraticPlacer:
    """
    Implements a simple gate quadratic placement algorithm.
    Algorithm computes 3 stages:
        - Placement of initial gates
        - Assignment of gates to left and right halves
        - Containment of gates to solve left and right placements
    Usage:
        - Declare object and initialize with input text file
        - Run the algorithm on the given input file
        - Output the resulting gate coordinates with output text file
            - `placer = QuadraticPlacer("input.txt")`
            - `placer.run()`
            - `placer.output("output.txt")`
    """
    def __init__(self, infile):
        """Parse input netlist file"""
        print(infile)
    
    def output(self, outfile):
        """Output the quadratic placement coordinates"""
        print(outfile)

    # Helper Functions

    def run(self):
        """Run Quadratic Placement Algorithm"""
        print("Running Quadratic Placer...")

if __name__ == "__main__":
    # Input and Output file arguments
    parser = argparse.ArgumentParser(description="Program to demonstrate quadratic placer")
    parser.add_argument("infile", type=str, help="Path to the input file")
    parser.add_argument("outfile", type=str, help="Path to the output file")
    args = parser.parse_args()

    placer = QuadraticPlacer(args.infile)
    placer.run()
    placer.output(args.outfile)


    
