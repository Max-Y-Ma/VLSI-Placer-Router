import heapq
import argparse
import numpy as np
from enum import Enum

class PredTag(Enum):
    N = 1
    S = 2
    E = 3
    W = 4
    U = 5
    D = 6

class GridCell:
    """
    Single Cell in Routing Grid (16-bit):
    ----------------------------------------------------
    Cost (12-bit) | Predecessor (3-bit) | Reached (1-bit)
    ----------------------------------------------------
    """
    def __init__(self, data=0):
        self.data = data
    
    # Getters and Setters
    def get_cost(self):
        return (self.data & 0xFFF0) >> 4
    
    def get_pred(self):
        return (self.data & 0x000E) >> 1

    def get_reached(self):
        return self.data & 0x0001

    def set_cost(self, cost):
        self.data = ((cost << 4) & 0xFFF0) | (self.data & 0x000F)

    def set_pred(self, pred):
        self.data = ((pred << 1) & 0x000E) | (self.data & 0xFFF1)

    def set_reached(self, reached):
        self.data = (reached & 0x0001) | (self.data & 0xFFFE)

class WaveCell:
    """
    Single Cell in Wavefront (64-bit):
    -------------------------------------------------------------------------------------------
    XCoord (16-bit) | YCoord (16-bit) | Pathcost (28-bit) | Predecessor (3-bit) | Layer (1-bit)
    -------------------------------------------------------------------------------------------
    """
    def __init__(self, data=0):
        self.data = data
    
    # Getters and Setters
    def get_x(self):
        return (self.data & 0xFFFF000000000000) >> 48
    
    def get_y(self):
        return (self.data & 0x0000FFFF00000000) >> 32

    def get_pathcost(self):
        return (self.data & 0x00000000FFFFFFF0) >> 4

    def get_pred(self):
        return (self.data & 0x000000000000000E) >> 1

    def get_layer(self):
        return self.data & 0x0000000000000001

    def set_x(self, x):
        self.data = ((x << 48) & 0xFFFF000000000000) | (self.data & 0x0000FFFFFFFFFFFF)
        
    def set_y(self, y):
        self.data = ((y << 32) & 0x0000FFFF00000000) | (self.data & 0xFFFF0000FFFFFFFF)

    def set_pathcost(self, pathcost):
        self.data = ((pathcost << 4) & 0x00000000FFFFFFF0) | (self.data & 0xFFFFFFFF0000000F)

    def set_pred(self, pred):
        self.data = ((pred << 1) & 0x000000000000000E) | (self.data & 0xFFFFFFFFFFFFFFF1)

    def set_layer(self, layer):
        self.data = (layer & 0x0000000000000001) | (self.data & 0xFFFFFFFFFFFFFFFE)


class MazeRouter:
    """
    Implements a simple maze router that supports 2-point nets, non-unit cost, 
    bend pennalty, and 2-layers with vias.

    The fundamental algorithm comprises a wavefront-expansion search with backtracing
    to find the optimal path. A cost function is created from the given input grid and
    additional metrics such as bends and vias.

    The grid data structure is stored as an optimized 2D array with a predecessor direction.
    The wavefront, which contains the most recent explored cells, is a heap or priority queue.

    Usage:
        - Declare object and initialize with input text file
        - Run the algorithm on the given input file
        - Output the resulting gate coordinates with output text file
            - `router = MazeRouter("gridfile.txt", "netfile.txt")`
            - `router.run()`
            - `router.output("output.txt")`
    """
    def __init__(self, gridfile, netfile):
        self.grid = 0
        self.nets = 0
        self.wavefront = 0

    def run(self):
        """Complete maze routing for each netlist"""

    def output(self, outfile):
        """Output final maze routing"""

if __name__ == "__main__":
    # Input and Output file arguments
    parser = argparse.ArgumentParser(description="Program to demonstrate maze router")
    parser.add_argument("gridfile", type=str, help="Path to the input grid file")
    parser.add_argument("netfile", type=str, help="Path to the input net file")
    parser.add_argument("outfile", type=str, help="Path to the output file")
    args = parser.parse_args()

    router = MazeRouter(args.gridfile, args.netfile)
    router.run()
    router.output(args.outfile)
