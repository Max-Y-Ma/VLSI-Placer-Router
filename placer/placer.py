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
        self.netlist = {}   # <Net Number, Gate List>
        self.gatelist = {}  # <Gate Number, Net List>
        self.padlist = {}   # <Net Number, Pad Coords (X,Y)>
        self.num_gates = 0
        self.num_nets = 0
        self.num_pads = 0

        with open(infile, 'r') as file:
            # Read gate header
            gate_header = file.readline().split()
            self.num_gates = int(gate_header[0])
            self.num_nets = int(gate_header[1])

            # Construct gatelist and netlist
            for n in range(self.num_gates):
                # Parse line arguments
                gate_line = file.readline().split()
                gate_number = int(gate_line[0]) - 1
                net_list = [int(gate_line[i]) - 1 for i in range(2, int(gate_line[1]) + 2)]

                # Create <Gate Number, Net List> pairs
                self.gatelist[gate_number] = net_list

                # Append to <Net Number, Gate List> pairs
                for net in net_list:
                    if net in self.netlist:
                        self.netlist[net].append(gate_number)
                    else:
                        self.netlist[net] = [gate_number]

            # Read Pad header
            pad_header = file.readline().split()
            self.num_pads = int(pad_header[0])

            # Construct padlist
            for n in range(self.num_pads):
                # Parse line arguments
                pad_line = file.readline().split()
                net_number = int(pad_line[1]) - 1
                x_coord = int(pad_line[2])
                y_coord = int(pad_line[3])

                # Create <Net Number, Pad Coords (X,Y)> pairs
                self.padlist[net_number] = [x_coord, y_coord]

        # Final coordinates
        self.x = np.zeros(self.num_gates)
        self.y = np.zeros(self.num_gates)

    def output(self, outfile):
        """Output the quadratic placement coordinates"""
        with open(outfile, 'w') as file:
            for i in range(self.num_gates):
                file.write(f"{i + 1} {self.x[i]} {self.y[i]}\n")

    # Helper Functions
    def init_placement(self):
        """ Construct the initial placement of gates. 
        This constitutes the first stage of the algorithm. """

        # Construct C matrix
        c_matrix = np.zeros((self.num_gates, self.num_gates))
        for gate_list in self.netlist.values():
            for row in gate_list:
                for column in gate_list:
                    if (row == column):
                        continue
                    else:
                        c_matrix[row, column] = 1

        # Construct A matrix
        a_matrix = np.where(c_matrix != 0, -c_matrix, 0)
        for i in range(self.num_gates):
            # Check pads
            pad_flag = 0
            net_list = self.gatelist[i]
            for net in net_list:
                if net in self.padlist:
                    pad_flag = 1

            a_matrix[i, i] = sum(c_matrix[i]) + pad_flag

        # Construct bx and by vectors
        bx = np.zeros(self.num_gates)
        by = np.zeros(self.num_gates)
        for i in range(self.num_gates):
            net_list = self.gatelist[i]
            for net in net_list:
                if net in self.padlist:
                    bx[i] = self.padlist[net][0]
                    by[i] = self.padlist[net][1]
                    break

        # Compute x and y placement coordinates
        self.x = la.solve(a_matrix, bx)
        self.y = la.solve(a_matrix, by)

    def run(self):
        """Run Quadratic Placement Algorithm"""
        print("Running Quadratic Placer...")
        self.init_placement()

if __name__ == "__main__":
    # Input and Output file arguments
    parser = argparse.ArgumentParser(description="Program to demonstrate quadratic placer")
    parser.add_argument("infile", type=str, help="Path to the input file")
    parser.add_argument("outfile", type=str, help="Path to the output file")
    args = parser.parse_args()

    placer = QuadraticPlacer(args.infile)
    placer.run()
    placer.output(args.outfile)


    
