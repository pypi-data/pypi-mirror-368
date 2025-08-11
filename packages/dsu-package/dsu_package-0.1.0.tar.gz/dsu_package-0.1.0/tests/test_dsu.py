import unittest
from dsu_package.dsu import DSU

class TestDSU(unittest.TestCase):

    def test_union_and_find(self):
        dsu = DSU(5) 

        for i in range(5):
            for j in range(i + 1, 5):
                self.assertNotEqual(dsu.find(i), dsu.find(j))

        self.assertTrue(dsu.union(0, 1))
        self.assertEqual(dsu.find(0), dsu.find(1))

        self.assertTrue(dsu.union(1, 2))
        self.assertEqual(dsu.find(0), dsu.find(2))

        self.assertFalse(dsu.union(0, 2))

        self.assertTrue(dsu.union(3, 4))
        self.assertEqual(dsu.find(3), dsu.find(4))

        self.assertTrue(dsu.union(2, 3))
        self.assertEqual(dsu.find(0), dsu.find(4))

    def test_single_element(self):
        dsu = DSU(1)
        self.assertEqual(dsu.find(0), 0)
        self.assertFalse(dsu.union(0, 0))  

if __name__ == "__main__":
    unittest.main()
