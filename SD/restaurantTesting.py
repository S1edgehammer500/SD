import unittest
from Model.restaurantModel import *

def run_tests():

    class TestRestaurantCreation(unittest.TestCase):
        def setUp(self):
            self.model = Restaurant()

        def test_create_restaurant(self):
            name = "America"
            numberOfTables = 20
            result = self.model.createRestaurant(name, numberOfTables)
            self.assertEqual(result,1)

        def test_create_existing_restaurant(self):
            name = "Bristol"
            numberOfTables = 20 
            result = self.model.createRestaurant(name, numberOfTables)
            self.assertEqual(result, 0)

        def create_restaurant_invalid_name(self):
            name = "h"
            numberOfTables = 20
            result = self.model.createRestaurant(name, numberOfTables)
            self.assertEqual(result, 0)

        def create_restaurant_invalid_tables(self):
            name = "Stockholm"
            numberOfTables = 200
            result = self.model.createRestaurant(name, numberOfTables)
            self.assertEqual(result, 0)

    class TestUpdateRestaurant(unittest.TestCase):
        def setUp(self):
            self.model = Restaurant()

        def test_successful_update_name(self):
            name = 'Liverpool'
            newName = 'Cardiff'
            result = self.model.updateRestaurantName(name, newName)
            self.assertEqual(result, 1)

        def test_existing_update_name(self):
            name = 'Bristol'
            newName = 'Manchester'
            result = self.model.updateRestaurantName(name, newName)
            self.assertEqual(result, 0)

        def test_invalid_name_syntax(self):
            name = 'Bristol'
            newName = 'h'
            result = self.model.updateRestaurantName(name, newName)
            self.assertEqual(result, 0)

        def test_update_tables(self):
            name = 'Bristol'
            numberOfTables = 80
            result = self.model.updateNumberOfTables(name, numberOfTables)
            self.assertEqual(result, 1)

        def test_update_tables_invalid_syntax(self):
            name = 'Bristol'
            numberOfTables = 200
            result = self.model.updateNumberOfTables(name, numberOfTables)
            self.assertEqual(result, 0)

    class TestDeleteRestaurant(unittest.TestCase):
        def setUp(self):
            self.model = Restaurant()

        def test_delete_restaurant(self):
            name = 'America'
            result = self.model.deleteRestaurant(name)
            self.assertEqual(result, 1)

        def test_delete_nonexistant_restaurant(self):
            name = 'Nowhere'
            result = self.model.deleteRestaurant(name)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_restaurant=loader.loadTestsFromTestCase(TestRestaurantCreation)
    restaurant_update=loader.loadTestsFromTestCase(TestUpdateRestaurant)
    delete_restaurant=loader.loadTestsFromTestCase(TestDeleteRestaurant)
    all_tests = unittest.TestSuite([create_restaurant,restaurant_update,delete_restaurant])
    
    runner.run(all_tests)
run_tests()