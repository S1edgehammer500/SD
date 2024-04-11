import unittest
from Model.itemModel import *

def run_tests():

    class TestItemCreation(unittest.TestCase):
        def setUp(self):
            self.model = Item()

        def test1_create_item(self):
            name = "Cheese"
            quantity = 60
            stockLimit = 90
            result = self.model.createItem(name, quantity, stockLimit)
            self.assertEqual(result,1)
            name2 = "Lettuce"
            quantity2 = 30
            stockLimit2 = 60
            self.model.createItem(name2, quantity2, stockLimit2)

        def test2_create_existing_item(self):
            name = "Cheese"
            quantity = 60
            stockLimit = 90
            result = self.model.createItem(name, quantity, stockLimit)
            self.assertEqual(result, 0)

        def test3_create_item_invalid_name(self):
            name = "h"
            quantity = 20
            stockLimit = 50
            result = self.model.createItem(name, quantity, stockLimit)
            self.assertEqual(result, 0)

        def test4_create_item_invalid_quantity1(self):
            name = "Cookie"
            quantity = 0
            stockLimit = 70
            result = self.model.createItem(name, quantity, stockLimit)
            self.assertEqual(result, 0)

        def test5_create_item_invalid_quantity2(self):
            name = "Cookie"
            quantity = 80
            stockLimit = 60
            result = self.model.createItem(name, quantity, stockLimit)
            self.assertEqual(result, 0)

        def test6_create_item_invalid_stock(self):
            name = "Cookie"
            quantity = 20
            stockLimit = 0
            result = self.model.createItem(name, quantity, stockLimit)
            self.assertEqual(result, 0)

    class TestUpdateitem(unittest.TestCase):
        def setUp(self):
            self.model = Item()

        def test1_successful_update_name(self):
            name = 'Cheese'
            newName = 'Tomato'
            result = self.model.updateItemName(name, newName)
            self.assertEqual(result, 1)

        def test2_existing_update_name(self):
            name = 'Tomato'
            newName = 'Lettuce'
            result = self.model.updateItemName(name, newName)
            self.assertEqual(result, 0)

        def test3_invalid_name_syntax(self):
            name = 'Tomato'
            newName = 'h'
            result = self.model.updateItemName(name, newName)
            self.assertEqual(result, 0)

        def test4_update_quantity(self):
            name = 'Tomato'
            quantity = 30
            result = self.model.updateQuantity(quantity, name)
            self.assertEqual(result, 1)

        def test5_update_quantity_invalid_syntax(self):
            name = 'Tomato'
            quantity = 0
            result = self.model.updateQuantity(quantity, name)
            self.assertEqual(result, 0)

        def test6_update_quantity_invalid_name(self):
            name = 'Nothing'
            quantity = 30
            result = self.model.updateQuantity(quantity, name)
            self.assertEqual(result, 0)
        
        def test91_update_stock(self):
            name = 'Tomato'
            stock = 98
            result = self.model.updateStockLimit(stock, name)
            self.assertEqual(result, 1)

        def test92_update_allergy_invalid_syntax(self):
            name = 'Tomato'
            stock = 0
            result = self.model.updateStockLimit(stock, name)
            self.assertEqual(result, 0)

        def test93_update_allergy_invalid_name(self):
            name = 'Nothing'
            stock = 57
            result = self.model.updateStockLimit(stock, name)
            self.assertEqual(result, 0)

        def test94_update_quantity_invalid_syntax2(self):
            name = 'Tomato'
            quantity = 61
            result = self.model.updateQuantity(quantity, name)
            self.assertEqual(result, 0)

    class TestDeleteitem(unittest.TestCase):
        def setUp(self):
            self.model = Item()

        def test1_delete_item(self):
            name = 'Lettuce'
            result = self.model.delete_item(name)
            self.assertEqual(result, 1)

        def test2_delete_nonexistant_item(self):
            name = 'Nothing'
            result = self.model.delete_item(name)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_item=loader.loadTestsFromTestCase(TestItemCreation)
    item_update=loader.loadTestsFromTestCase(TestUpdateitem)
    delete_item=loader.loadTestsFromTestCase(TestDeleteitem)
    all_tests = unittest.TestSuite([create_item,item_update,delete_item])
    
    runner.run(all_tests)
run_tests()