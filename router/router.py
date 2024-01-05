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

class WaveFront:
    """Wrapper around heapq data structure"""
    def __init__(self):
        self.heap = []

    def push(self, wavecell):
        heapq.heappush(self.heap, wavecell)

    def pop(self):
        return heapq.heappop(self.heap)

    def empty(self):
        return len(self.heap) == 0

    def clear(self):
        self.heap.clear()

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

class NetCell:
    """
    Single Cell in Netlist (64-bit + 8-bit):
    -------------------------------------------------------------------------
    XCoord2 (16-bit) | YCoord2 (16-bit) | XCoord1 (16-bit) | YCoord1 (16-bit)
    -------------------------------------------------------------------------
    NetID (6-bit) | Layer2 (1-bit) | Layer1 (1-bit)
    -------------------------------------------------------------------------
    """
    def __init__(self, coord=0, data=0, instring=None):
        self.coord = coord
        self.data = data

        # Parse stringified netlist
        if instring is not None:
            self.list = instring.split()
            self.set_id(int(self.list[0]))
            self.set_layer1(int(self.list[1]) - 1)  # Convert to 0-indexed
            self.set_x1(int(self.list[2]))
            self.set_y1(int(self.list[3]))
            self.set_layer2(int(self.list[4]) - 1)  # Convert to 0-indexed
            self.set_x2(int(self.list[5]))
            self.set_y2(int(self.list[6]))

    # Getters and Setters
    def get_x1(self):
        return (self.coord & 0x00000000FFFF0000) >> 16

    def get_x2(self):
        return (self.coord & 0xFFFF000000000000) >> 48
    
    def get_y1(self):
        return self.coord & 0x000000000000FFFF
    
    def get_y2(self):
        return (self.coord & 0x0000FFFF00000000) >> 32
    
    def get_id(self):
        return (self.data & 0xFC) >> 2

    def get_layer1(self):
        return (self.data & 0x02) >> 1

    def get_layer2(self):
        return self.data & 0x01

    def set_x1(self, x):
        self.coord = ((x << 16) & 0x00000000FFFF0000) | (self.coord & 0xFFFFFFFF0000FFFF)

    def set_x2(self, x):
        self.coord = ((x << 48) & 0xFFFF000000000000) | (self.coord & 0x0000FFFFFFFFFFFF)

    def set_y1(self, y):
        self.coord = (y & 0x000000000000FFFF) | (self.coord & 0xFFFFFFFFFFFF0000)

    def set_y2(self, y):
        self.coord = ((y << 32) & 0x0000FFFF00000000) | (self.coord & 0xFFFF0000FFFFFFFF)

    def set_id(self, id):
        self.data = ((id << 2) & 0xFC) | (self.data & 0x03)

    def set_layer1(self, layer):
        self.data = ((layer << 1) & 0x02) | (self.data & 0xFD)

    def set_layer2(self, layer):
        self.data = (layer & 0x01) | (self.data & 0xFE)

class WaveCell:
    """
    Single Cell in Wavefront (64-bit):
    -------------------------------------------------------------------------------------------
    XCoord (16-bit) | YCoord (16-bit) | Pathcost (28-bit) | Predecessor (3-bit) | Layer (1-bit)
    -------------------------------------------------------------------------------------------
    """
    def __init__(self, data=0):
        self.data = data

    def __lt__(self, other):
        return self.get_pathcost() < other.get_pathcost()
    
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
    def parse_grid(self, gridfile):
        """Parse gridfile and initialize grid data structure"""
        with open(gridfile, 'r') as file:
            grid_header = file.readline().split()
            self.grid_x = int(grid_header[0])
            self.grid_y = int(grid_header[1])
            self.bend_penalty = int(grid_header[2])
            self.via_penalty = int(grid_header[3])

            # Initialize grid with layers
            self.grid = np.array([[[GridCell() for _ in range(self.grid_x)] for _ in range(self.grid_y)] for _ in range(self.grid_layers)])

            # Initialize first layer of grid
            for y in range(self.grid_y):
                grid_row = file.readline().split()
                for x in range(self.grid_x):
                    self.grid[0][y][x].set_cost(int(grid_row[x]))

            # Initialize second layer of grid
            for y in range(self.grid_y):
                grid_row = file.readline().split()
                for x in range(self.grid_x):
                    self.grid[1][y][x].set_cost(int(grid_row[x]))
            
    def parse_net(self, netfile):
        """Parse netfile and initialize net data structure"""
        with open(netfile, 'r') as file:
            net_header = file.readline().split()
            self.num_nets = int(net_header[0])

            # Initialize netlist
            self.nets = np.array([NetCell() for _ in range(self.num_nets)])

            for i in range(self.num_nets):
                self.nets[i] = NetCell(instring=file.readline())

    def __init__(self, gridfile, netfile):
        # Routing grid data structure variables
        self.grid_x = 0
        self.grid_y = 0
        self.grid_layers = 2
        self.bend_penalty = 0
        self.via_penalty = 0
        self.grid = np.array([[[]]])
        self.routes = []

        self.num_nets = 0
        self.nets = np.array([])
        
        # Wavefront (heap/priority queue) data structure variables
        self.wavefront = WaveFront()

        # Parse gridfile and netfile
        self.parse_grid(gridfile)
        self.parse_net(netfile)

    def cleanup(self):
        """Cleanup grid after routing a net"""
        for y in range(self.grid_y):
            for x in range(self.grid_x):
                self.grid[0][y][x].set_reached(0)
                self.grid[1][y][x].set_reached(0)
                self.grid[0][y][x].set_pred(0)
                self.grid[1][y][x].set_pred(0)

    def get_cell_neighbors(self, x, y, layer):
        """Get unreached neighbors of cell"""
        unreached_neighbors = []
        
        # Check left neighbor
        if x > 0 and self.grid[layer][y][x-1].get_reached() == 0 and self.grid[layer][y][x-1].get_cost() != 4095:
            unreached_neighbors.append([self.grid[layer][y][x-1], (layer, y, x-1), PredTag.E.value])
        
        # Check right neighbor
        if x < self.grid_x - 1 and self.grid[layer][y][x+1].get_reached() == 0 and self.grid[layer][y][x+1].get_cost() != 4095:
            unreached_neighbors.append([self.grid[layer][y][x+1], (layer, y, x+1), PredTag.W.value])

        # Check top neighbor
        if y > 0 and self.grid[layer][y-1][x].get_reached() == 0 and self.grid[layer][y-1][x].get_cost() != 4095:
            unreached_neighbors.append([self.grid[layer][y-1][x], (layer, y-1, x), PredTag.S.value])

        # Check bottom neighbor
        if y < self.grid_y - 1 and self.grid[layer][y+1][x].get_reached() == 0 and self.grid[layer][y+1][x].get_cost() != 4095:
            unreached_neighbors.append([self.grid[layer][y+1][x], (layer, y+1, x), PredTag.N.value])

        # # Check above neighbor
        # if layer == 0 and self.grid[1][y][x].get_reached() == 0:
        #     unreached_neighbors.append((x, y, 1))

        # # Check below neighbor
        # if layer == 1 and self.grid[0][y][x].get_reached() == 0:
        #     unreached_neighbors.append((x, y, 0))
        return unreached_neighbors

    def backtrace_route(self, source, cell_x, cell_y, cell_layer):
        """Backtrace route from target to source"""

        # Initialize current cell to target
        current_cell = GridCell()
        current_cell.set_pred(self.grid[cell_layer, cell_y, cell_x].get_pred())

        path = []
        while(True):
            # Add cell to path
            path.append((cell_layer, cell_x, cell_y))

            # Check for source, append source
            if (cell_x == source.get_x() and cell_y == source.get_y() and cell_layer == source.get_layer()):
                break

            # Get predecessor direction
            pred = current_cell.get_pred()

            # Get predecessor cell
            if pred == PredTag.N.value:
                current_cell = self.grid[cell_layer][cell_y-1][cell_x]
                cell_y -= 1
            elif pred == PredTag.S.value:
                current_cell = self.grid[cell_layer][cell_y+1][cell_x]
                cell_y += 1
            elif pred == PredTag.E.value:
                current_cell = self.grid[cell_layer][cell_y][cell_x+1]
                cell_x += 1
            elif pred == PredTag.W.value:
                current_cell = self.grid[cell_layer][cell_y][cell_x-1]
                cell_x -= 1
            # elif pred == PredTag.U.value:
            #     current_cell = self.grid[0][current_cell.get_y()][current_cell.get_x()]
            # elif pred == PredTag.D.value:
            #     current_cell = self.grid[1][current_cell.get_y()][current_cell.get_x()]
            else:
                break

        return path

    def route(self, net):
        """
        Routes given net and returns the backtraced path as a list of WaveCells. 
        If no path exists, an empty list is returned.
        """

        # Create source and target cells
        source = WaveCell()
        source.set_x(net.get_x1())
        source.set_y(net.get_y1())
        source.set_layer(net.get_layer1())

        target = WaveCell()
        target.set_x(net.get_x2())
        target.set_y(net.get_y2())
        target.set_layer(net.get_layer2())
        
        # Initialize wavefront to source cell
        self.wavefront.clear()
        self.wavefront.push(source)
        self.grid[source.get_layer(), source.get_y(), source.get_x()].set_reached(1)

        # Maze routing algorithm
        path = []
        while(True):
            # No path was found, target could not be reached
            if self.wavefront.empty():
                break

            # Grab lowest cost cell from wavefront
            current_cell = self.wavefront.pop()
            cell_x = current_cell.get_x()
            cell_y = current_cell.get_y()
            cell_layer = current_cell.get_layer()

            # Check for target
            if (cell_x == target.get_x() and cell_y == target.get_y() and cell_layer == target.get_layer()):
                # Target reached, backtrace path
                path = self.backtrace_route(source, cell_x, cell_y, cell_layer)

                # Cleanup
                self.cleanup()
                break

            # Complete expansion, checking neighbor cells
            unreached_neighbors = self.get_cell_neighbors(cell_x, cell_y, cell_layer)
            for neighbor in unreached_neighbors:
                neighbor_cell = neighbor[0]
                location = neighbor[1]
                predecessor = neighbor[2]
                
                # Mark cell as reached
                neighbor_cell.set_reached(1)

                # Compute new pathcost
                pathcost = current_cell.get_pathcost() + neighbor_cell.get_cost()

                # Mark predecessor direction
                neighbor_cell.set_pred(predecessor)

                # Add neighbor to wavefront
                next_layer = location[0]
                next_y = location[1]
                next_x = location[2]

                next_cell = WaveCell()
                next_cell.set_x(next_x)
                next_cell.set_y(next_y)
                next_cell.set_pathcost(pathcost)
                next_cell.set_pred(predecessor)
                next_cell.set_layer(next_layer)

                self.wavefront.push(next_cell)

        return path

    def run(self):
        """Complete maze routing for each netlist"""
        # Route each net in netlist
        for net in self.nets:
            maze_route = self.route(net)
            self.routes.append(maze_route)

    def output(self, outfile):
        """Output final maze routing"""
        with open(outfile, 'w') as file:
            # Output total number of nets
            file.write(f"{self.num_nets}\n")

            net_number = 1
            for route in self.routes:
                # Output net number
                file.write(f"{net_number}\n")

                # Output routed path
                if len(route) != 0:
                    for cell in route[::-1]:
                        file.write(f"{cell[0] + 1} {cell[1]} {cell[2]}\n")  # Convert layer to 1-indexed

                # Output end number
                file.write("0\n")
                net_number += 1

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
