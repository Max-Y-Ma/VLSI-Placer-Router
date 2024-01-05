from router import GridCell, WaveCell, NetCell
import unittest
import random

num_basic_test = 1000

class RouterTestModule(unittest.TestCase):
    def test_cell_getter_setter(self):
        # Test Getter and Setter for GridCell
        gridcell = GridCell()
        self.assertEqual(gridcell.get_cost(), 0)
        self.assertEqual(gridcell.get_pred(), 0)
        self.assertEqual(gridcell.get_reached(), 0)

        for i in range(num_basic_test):
            gc_data = [random.randint(0, 2**12 - 1), random.randint(1, 6), random.randint(0, 1)]
            gridcell.set_cost(gc_data[0])
            gridcell.set_pred(gc_data[1])
            gridcell.set_reached(gc_data[2])

            self.assertEqual(gridcell.get_cost(), gc_data[0])
            self.assertEqual(gridcell.get_pred(), gc_data[1])
            self.assertEqual(gridcell.get_reached(), gc_data[2])

        # Test Getter and Setter for WaveCell
        wavecell = WaveCell()
        self.assertEqual(wavecell.get_x(), 0)
        self.assertEqual(wavecell.get_y(), 0)
        self.assertEqual(wavecell.get_pathcost(), 0)
        self.assertEqual(wavecell.get_pred(), 0)
        self.assertEqual(wavecell.get_layer(), 0)

        for i in range(num_basic_test):
            wc_data = [random.randint(0, 2**16 - 1), random.randint(0, 2**16 - 1), 
                             random.randint(0, 2**28 - 1), random.randint(1, 6), random.randint(0, 1)]
            wavecell.set_x(wc_data[0])
            wavecell.set_y(wc_data[1])
            wavecell.set_pathcost(wc_data[2])
            wavecell.set_pred(wc_data[3])
            wavecell.set_layer(wc_data[4])

            self.assertEqual(wavecell.get_x(), wc_data[0])
            self.assertEqual(wavecell.get_y(), wc_data[1])
            self.assertEqual(wavecell.get_pathcost(), wc_data[2])
            self.assertEqual(wavecell.get_pred(), wc_data[3])
            self.assertEqual(wavecell.get_layer(), wc_data[4])

        # Test Getter and Setter for NetCell
        netcell = NetCell()
        self.assertEqual(netcell.get_x1(), 0)
        self.assertEqual(netcell.get_y1(), 0)
        self.assertEqual(netcell.get_x2(), 0)
        self.assertEqual(netcell.get_y2(), 0)
        self.assertEqual(netcell.get_id(), 0)
        self.assertEqual(netcell.get_layer1(), 0)
        self.assertEqual(netcell.get_layer2(), 0)

        for i in range(num_basic_test):
            nc_coord = [random.randint(0, 2**16 - 1), random.randint(0, 2**16 - 1), 
                                  random.randint(0, 2**16 - 1), random.randint(0, 2**16 - 1)]
            nc_data = [random.randint(0, 2**6 - 1), random.randint(0, 1), random.randint(0, 1)]

            netcell.set_x2(nc_coord[0])
            netcell.set_y2(nc_coord[1])
            netcell.set_x1(nc_coord[2])
            netcell.set_y1(nc_coord[3])
            netcell.set_id(nc_data[0])
            netcell.set_layer2(nc_data[1])
            netcell.set_layer1(nc_data[2])

            self.assertEqual(netcell.get_x2(), nc_coord[0])
            self.assertEqual(netcell.get_y2(), nc_coord[1])
            self.assertEqual(netcell.get_x1(), nc_coord[2])
            self.assertEqual(netcell.get_y1(), nc_coord[3])
            self.assertEqual(netcell.get_id(), nc_data[0])
            self.assertEqual(netcell.get_layer2(), nc_data[1])
            self.assertEqual(netcell.get_layer1(), nc_data[2])

        for i in range(num_basic_test):
            nc2_coord = [random.randint(0, 2**16 - 1), random.randint(0, 2**16 - 1),
                         random.randint(0, 2**16 - 1), random.randint(0, 2**16 - 1)]
            nc2_data = [random.randint(0, 2**6 - 1), random.randint(1, 2), random.randint(1, 2)]
            netcell2 = NetCell(instring=f" {nc2_data[0]}   {nc2_data[2]}  {nc2_coord[2]} {nc2_coord[3]}   {nc2_data[1]}  {nc2_coord[0]} {nc2_coord[1]}")
            self.assertEqual(netcell2.get_x2(), nc2_coord[0])
            self.assertEqual(netcell2.get_y2(), nc2_coord[1])
            self.assertEqual(netcell2.get_x1(), nc2_coord[2])
            self.assertEqual(netcell2.get_y1(), nc2_coord[3])
            self.assertEqual(netcell2.get_id(), nc2_data[0])
            self.assertEqual(netcell2.get_layer2(), nc2_data[1] - 1)
            self.assertEqual(netcell2.get_layer1(), nc2_data[2] - 1)
if __name__ == '__main__':
    unittest.main()