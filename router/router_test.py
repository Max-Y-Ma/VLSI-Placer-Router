from router import GridCell, WaveCell
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
            gridcell_test = [random.randint(0, 2**12 - 1), random.randint(1, 6), random.randint(0, 1)]
            gridcell.set_cost(gridcell_test[0])
            gridcell.set_pred(gridcell_test[1])
            gridcell.set_reached(gridcell_test[2])

            self.assertEqual(gridcell.get_cost(), gridcell_test[0])
            self.assertEqual(gridcell.get_pred(), gridcell_test[1])
            self.assertEqual(gridcell.get_reached(), gridcell_test[2])

        # Test Getter and Setter for WaveCell
        wavecell = WaveCell()
        self.assertEqual(wavecell.get_x(), 0)
        self.assertEqual(wavecell.get_y(), 0)
        self.assertEqual(wavecell.get_pathcost(), 0)
        self.assertEqual(wavecell.get_pred(), 0)
        self.assertEqual(wavecell.get_layer(), 0)

        for i in range(num_basic_test):
            wavecell_test = [random.randint(0, 2**16 - 1), random.randint(0, 2**16 - 1), random.randint(0, 2**28 - 1), random.randint(1, 6), random.randint(0, 1)]
            wavecell.set_x(wavecell_test[0])
            wavecell.set_y(wavecell_test[1])
            wavecell.set_pathcost(wavecell_test[2])
            wavecell.set_pred(wavecell_test[3])
            wavecell.set_layer(wavecell_test[4])

            self.assertEqual(wavecell.get_x(), wavecell_test[0])
            self.assertEqual(wavecell.get_y(), wavecell_test[1])
            self.assertEqual(wavecell.get_pathcost(), wavecell_test[2])
            self.assertEqual(wavecell.get_pred(), wavecell_test[3])
            self.assertEqual(wavecell.get_layer(), wavecell_test[4])

if __name__ == '__main__':
    unittest.main()