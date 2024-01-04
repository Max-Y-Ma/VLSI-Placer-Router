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
        self.x = np.zeros((self.num_gates, 2))
        self.x[:,0] = np.array([n for n in range(self.num_gates)])
        self.y = np.zeros((self.num_gates, 2))
        self.y[:,0] = np.array([n for n in range(self.num_gates)])

    def output(self, outfile):
        """Output the quadratic placement coordinates"""
        with open(outfile, 'w') as file:
            for i in range(self.left_num_gates):
                index = int(self.left_x[i,0] + 1)
                x = '{:.8f}'.format(self.left_x[i,1])
                y = '{:.8f}'.format(self.left_y[i,1])
                file.write(f"{index} {x} {y}\n")

            for i in range(self.right_num_gates):
                index = int(self.right_x[i,0] + 1)
                x = '{:.8f}'.format(self.right_x[i,1])
                y = '{:.8f}'.format(self.right_y[i,1])
                file.write(f"{index} {x} {y}\n")

    # Helper Functions
    def init_placement(self):
        """ Construct the initial placement of gates. 
        This constitutes the first stage of the algorithm. """

        # Construct C matrix
        c_matrix = np.zeros((self.num_gates, self.num_gates))
        for gate_list in self.netlist.values():
            # Add gate connections to C matrix
            for row in gate_list:
                for column in gate_list:
                    if (row == column):
                        continue
                    else:
                        c_matrix[row, column] = 1

        # Construct A matrix
        a_matrix = np.where(c_matrix != 0, -c_matrix, 0)
        for i in range(self.num_gates):
            # Check pads and update diagonal
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
        self.x[:,1] = la.solve(a_matrix, bx)
        self.y[:,1] = la.solve(a_matrix, by)

    def vert_assignment(self):
        """Complete vertical gate assignment, sorting 
        X coordinates then Y coordinates"""

        # Calculate absolute (100000 * x + y) sort vector for x,y coordinates
        abs_vector = np.zeros((self.num_gates, 2))
        abs_vector[:,0] = np.array([n for n in range(self.num_gates)])
        abs_vector[:,1] = 100000 * self.x[:,1] + self.y[:,1]
        sorted_vector = abs_vector[abs_vector[:,1].argsort()]

        # Divide gates to compute assignment
        midpoint = sorted_vector.shape[0] // 2
        self.left_gates = list(sorted_vector[:midpoint][:,0])
        self.left_num_gates = len(self.left_gates)
        self.right_gates = list(sorted_vector[midpoint:][:,0])
        self.right_num_gates = len(self.right_gates)

    def vert_contain_left(self):
        """Complete containment problem on left assigned gates
        and solve quadratice placer"""

        # Determine all possible nets
        self.left_nets = np.array([])
        for gate in self.left_gates:
            self.left_nets = np.union1d(self.left_nets, self.gatelist[gate])
        self.left_nets = list(self.left_nets)

        # Construct C matrix
        c_matrix = np.zeros((self.left_num_gates, self.left_num_gates))
        for net in self.left_nets:
            gate_list = self.netlist[net]
            for row in gate_list:
                for column in gate_list:
                    if row not in self.left_gates:
                        break
                    elif row == column or column not in self.left_gates:
                        continue
                    else:
                        c_matrix[self.left_gates.index(row), self.left_gates.index(column)] = 1

        # Determine new padlist
        self.left_padlist = {}
        for net in self.left_nets:
            if net in self.padlist and net not in self.left_padlist:
                self.left_padlist[net] = self.padlist[net]
                if self.left_padlist[net][0] > 50:
                    self.left_padlist[net][0] = 50

        # Construct A matrix
        a_matrix = np.where(c_matrix != 0, -c_matrix, 0)
        for gate in self.left_gates:
            # Check pads
            pad_flag = 0
            net_list = self.gatelist[gate]
            for net in net_list:
                if net in self.left_padlist:
                    pad_flag = 1

            i = self.left_gates.index(gate)
            a_matrix[i, i] = sum(c_matrix[i]) + pad_flag

        # Construct bx and by vectors
        bx = np.zeros(self.left_num_gates)
        by = np.zeros(self.left_num_gates)
        for gate in self.left_gates:
            i = self.left_gates.index(gate)
            net_list = self.gatelist[gate]
            for net in net_list:
                if net in self.left_padlist:
                    bx[i] = self.left_padlist[net][0]
                    by[i] = self.left_padlist[net][1]
                    break

        # Compute x and y placement coordinates
        self.left_x = np.zeros((self.left_num_gates, 2))
        self.left_x[:,0] = self.left_gates
        self.left_x[:,1] = la.solve(a_matrix, bx)
        self.left_y = np.zeros((self.left_num_gates, 2))
        self.left_y[:,0] = self.left_gates
        self.left_y[:,1] = la.solve(a_matrix, by)

    def vert_contain_right(self):
        """Complete containment problem on left assigned gates
        and solve quadratice placer"""

        # Determine all possible nets
        self.right_nets = np.array([])
        for gate in self.right_gates:
            self.right_nets = np.union1d(self.right_nets, self.gatelist[gate])
        self.right_nets = list(self.right_nets)

        # Construct C matrix
        c_matrix = np.zeros((self.right_num_gates, self.right_num_gates))
        for net in self.right_nets:
            gate_list = self.netlist[net]
            for row in gate_list:
                for column in gate_list:
                    if row not in self.right_gates:
                        break
                    elif row == column or column not in self.right_gates:
                        continue
                    else:
                        c_matrix[self.right_gates.index(row), self.right_gates.index(column)] = 1

        # Determine new padlist
        self.right_padlist = {}
        for net in self.right_nets:
            if net in self.padlist and net not in self.right_padlist:
                self.right_padlist[net] = self.padlist[net]
                if self.right_padlist[net][0] < 50:
                    self.right_padlist[net][0] = 50

        # Construct A matrix
        a_matrix = np.where(c_matrix != 0, -c_matrix, 0)
        for gate in self.right_gates:
            # Check pads
            pad_flag = 0
            net_list = self.gatelist[gate]
            for net in net_list:
                if net in self.right_padlist:
                    pad_flag = 1

            i = self.right_gates.index(gate)
            a_matrix[i, i] = sum(c_matrix[i]) + pad_flag

        # Construct bx and by vectors
        bx = np.zeros(self.right_num_gates)
        by = np.zeros(self.right_num_gates)
        for gate in self.right_gates:
            i = self.right_gates.index(gate)
            net_list = self.gatelist[gate]
            for net in net_list:
                if net in self.right_padlist:
                    bx[i] = self.right_padlist[net][0]
                    by[i] = self.right_padlist[net][1]
                    break

        # Compute x and y placement coordinates
        self.right_x = np.zeros((self.right_num_gates, 2))
        self.right_x[:,0] = self.right_gates
        self.right_x[:,1] = la.solve(a_matrix, bx)
        self.right_y = np.zeros((self.right_num_gates, 2))
        self.right_y[:,0] = self.right_gates
        self.right_y[:,1] = la.solve(a_matrix, by)

    def run(self):
        """Run Quadratic Placement Algorithm"""
        print("Running Quadratic Placer...")
        self.init_placement()
        self.vert_assignment()
        self.vert_contain_left()
        self.vert_contain_right()

if __name__ == "__main__":
    # Input and Output file arguments
    parser = argparse.ArgumentParser(description="Program to demonstrate quadratic placer")
    parser.add_argument("infile", type=str, help="Path to the input file")
    parser.add_argument("outfile", type=str, help="Path to the output file")
    args = parser.parse_args()

    placer = QuadraticPlacer(args.infile)
    placer.run()
    placer.output(args.outfile)
