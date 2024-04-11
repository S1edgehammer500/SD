import unittest
from Model.inventoryModel import *

def run_tests():

    class TestinventoryCreation(unittest.TestCase):
        def setUp(self):
            self.model = Inventory()

        def test1_create_inventory(self):
            restaurantName = "Bristol"
            itemName = "Tomato"
            result = self.model.createInventory(id, restaurantName, itemName)
            self.assertEqual(result,1)
            restaurantName2 = "Manchester"
            itemName2 = "Tomato"
            self.model.createInventory(restaurantName2, itemName2)

        def test2_create_existing_inventory(self):
            restaurantName = "Bristol"
            itemName = "Tomato"
            result = self.model.createInventory(restaurantName, itemName)
            self.assertEqual(result, 0)

        def test4_create_inventory_nonexistant_restaurantName(self):
            restaurantName = "Cardiff"
            itemName = "Tomato"
            result = self.model.createInventory(restaurantName, itemName)
            self.assertEqual(result, 0)

        def test5_create_inventory_nonexistant_itemName(self):
            restaurantName = "Bristol"
            itemName = "Bacon"
            result = self.model.createInventory(restaurantName, itemName)
            self.assertEqual(result, 0)

    class TestUpdateinventory(unittest.TestCase):
        def setUp(self):
            self.model = Inventory()

        def test4_update_restaurantName(self):
            id = 1
            restaurantName = 'Manchester'
            self.model.setInventoryDetails(id)
            result = self.model.updateRestaurantName(restaurantName, id)
            self.assertEqual(result, 1)

        def test5_update_restaurantName_nonexistant(self):
            id = 1
            restaurantName = 'Cardiff'
            self.model.setInventoryDetails(id)
            result = self.model.updateRestaurantName(restaurantName, id)
            self.assertEqual(result, 0)

        def test6_update_restaurantName_invalid_id(self):
            id = 20
            restaurantName = "Bristol"
            result = self.model.updateRestaurantName(restaurantName, id)
            self.assertEqual(result, 0)
        
        def test7_update_itemName(self):
            id = 1
            itemName = "Lettuce"
            result = self.model.updateitemName(itemName, id)
            self.assertEqual(result, 1)

        def test8_update_itemName_invalid_syntax(self):
            id = 'Pizza'
            itemName = "Not available"
            result = self.model.updateitemName(itemName, id)
            self.assertEqual(result, 0)

        def test9_update_itemName_invalid_id(self):
            id = 'Nothing'
            itemName = False
            result = self.model.updateitemName(itemName, id)
            self.assertEqual(result, 0)
        
        def test91_update_allergy(self):
            id = 'Pizza'
            allergy = "No allergy risks"
            result = self.model.updateAllergyInfo(allergy, id)
            self.assertEqual(result, 1)

        def test92_update_allergy_invalid_syntax(self):
            id = 'Pizza'
            allergy = "h"
            result = self.model.updateAllergyInfo(allergy, id)
            self.assertEqual(result, 0)

        def test93_update_allergy_invalid_id(self):
            id = 'Nothing'
            allergy = "No allergy risk"
            result = self.model.updateAllergyInfo(allergy, id)
            self.assertEqual(result, 0)

    class TestDeleteinventory(unittest.TestCase):
        def setUp(self):
            self.model = inventory()

        def test1_delete_inventory(self):
            id = 'Burger'
            result = self.model.delete_inventory(id)
            self.assertEqual(result, 1)

        def test2_delete_nonexistant_inventory(self):
            id = 'Nothing'
            result = self.model.delete_inventory(id)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_inventory=loader.loadTestsFromTestCase(TestinventoryCreation)
    inventory_update=loader.loadTestsFromTestCase(TestUpdateinventory)
    delete_inventory=loader.loadTestsFromTestCase(TestDeleteinventory)
    all_tests = unittest.TestSuite([create_inventory,inventory_update,delete_inventory])
    
    runner.run(all_tests)
run_tests()