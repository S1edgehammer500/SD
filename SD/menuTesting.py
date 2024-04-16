import unittest
from Model.menuModel import *

def run_tests():

    class TestmenuCreation(unittest.TestCase):
        def setUp(self):
            self.model = Menu()

        def test1_create_menu(self):
            restaurantName = "Bristol"
            foodName = "Burger"
            result = self.model.createMenu(restaurantName, foodName)
            self.assertEqual(result,1)
            restaurantName2 = "Manchester"
            foodName2 = "Pizza"
            self.model.createMenu(restaurantName2, foodName2)

        def test2_create_existing_menu(self):
            restaurantName = "Bristol"
            foodName = "Burger"
            result = self.model.createMenu(restaurantName, foodName)
            self.assertEqual(result, 0)

        def test4_create_menu_nonexistant_restaurantName(self):
            restaurantName = "Cardiff"
            foodName = "Burger"
            result = self.model.createMenu(restaurantName, foodName)
            self.assertEqual(result, 0)

        def test5_create_menu_nonexistant_foodName(self):
            restaurantName = "Bristol"
            foodName = "Bacon"
            result = self.model.createMenu(restaurantName, foodName)
            self.assertEqual(result, 0)

    class TestUpdatemenu(unittest.TestCase):
        def setUp(self):
            self.model = Menu()

        def test91_update_availability(self):
            availability = False
            ID = 1
            result = self.model.updateAvailability(availability, ID)
            self.assertEqual(result, 1)

        def test92_update_availability_invalid_syntax(self):
            ID = 1
            availability = "Not available"
            result = self.model.updateAvailability(availability, ID)
            self.assertEqual(result, 0)

        def test93_update_availability_invalid_name(self):
            ID = 1
            availability = False
            result = self.model.updateAvailability(availability, ID)
            self.assertEqual(result, 0)

    class TestDeletemenu(unittest.TestCase):
        def setUp(self):
            self.model = Menu()

        def test1_delete_menu(self):
            id = 2
            result = self.model.delete_menu(id)
            self.assertEqual(result, 1)

        def test2_delete_nonexistant_menu(self):
            id = 70
            result = self.model.delete_menu(id)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_menu=loader.loadTestsFromTestCase(TestmenuCreation)
    menu_update=loader.loadTestsFromTestCase(TestUpdatemenu)
    delete_menu=loader.loadTestsFromTestCase(TestDeletemenu)
    all_tests = unittest.TestSuite([create_menu,menu_update,delete_menu])
    
    runner.run(all_tests)
run_tests()