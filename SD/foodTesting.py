import unittest
from Model.foodModel import *

def run_tests():

    class TestFoodCreation(unittest.TestCase):
        def setUp(self):
            self.model = Food()

        def test1_create_food(self):
            name = "Omelette"
            price = 17.58
            allergyInfo = "Contains eggs"
            result = self.model.createFood(name, price, allergyInfo)
            self.assertEqual(result,1)
            name2 = "Burger"
            price2 = 15.36
            allergyInfo2 = "No allergy risk"
            self.model.createFood(name2, price2, allergyInfo2)

        def test2_create_existing_food(self):
            name = "Omelette"
            price = 17.58
            allergyInfo = "Contains eggs"
            result = self.model.createFood(name, price, allergyInfo)
            self.assertEqual(result, 0)

        def test3_create_food_invalid_name(self):
            name = "h"
            price = 20
            allergyInfo = "Contains eggs"
            result = self.model.createFood(name, price, allergyInfo)
            self.assertEqual(result, 0)

        def test4_create_food_invalid_price(self):
            name = "Pizza"
            price = 0
            allergyInfo = "Contains cheese"
            result = self.model.createFood(name, price, allergyInfo)
            self.assertEqual(result, 0)

        def test5_create_food_invalid_allergy(self):
            name = "Pizza"
            price = 20
            allergyInfo = "h"
            result = self.model.createFood(name, price, allergyInfo)
            self.assertEqual(result, 0)

    class TestUpdateFood(unittest.TestCase):
        def setUp(self):
            self.model = Food()

        def test1_successful_update_name(self):
            name = 'Omelette'
            newName = 'Pizza'
            result = self.model.updateFoodName(name, newName)
            self.assertEqual(result, 1)

        def test2_existing_update_name(self):
            name = 'Pizza'
            newName = 'Burger'
            result = self.model.updateFoodName(name, newName)
            self.assertEqual(result, 0)

        def test3_invalid_name_syntax(self):
            name = 'Pizza'
            newName = 'h'
            result = self.model.updateFoodName(name, newName)
            self.assertEqual(result, 0)

        def test4_update_price(self):
            name = 'Pizza'
            price = 15.36
            result = self.model.updatePrice(price, name)
            self.assertEqual(result, 1)

        def test5_update_price_invalid_syntax(self):
            name = 'Pizza'
            price = 0
            result = self.model.updatePrice(price, name)
            self.assertEqual(result, 0)

        def test6_update_price_invalid_name(self):
            name = 'Nothing'
            price = 15.36
            result = self.model.updatePrice(price, name)
            self.assertEqual(result, 0)
        
        def test91_update_allergy(self):
            name = 'Pizza'
            allergy = "No allergy risks"
            result = self.model.updateAllergyInfo(allergy, name)
            self.assertEqual(result, 1)

        def test92_update_allergy_invalid_syntax(self):
            name = 'Pizza'
            allergy = "h"
            result = self.model.updateAllergyInfo(allergy, name)
            self.assertEqual(result, 0)

        def test93_update_allergy_invalid_name(self):
            name = 'Nothing'
            allergy = "No allergy risk"
            result = self.model.updateAllergyInfo(allergy, name)
            self.assertEqual(result, 0)

    class TestDeleteFood(unittest.TestCase):
        def setUp(self):
            self.model = Food()

        def test1_delete_food(self):
            name = 'Burger'
            result = self.model.delete_food(name)
            self.assertEqual(result, 1)

        def test2_delete_nonexistant_food(self):
            name = 'Nothing'
            result = self.model.delete_food(name)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_food=loader.loadTestsFromTestCase(TestFoodCreation)
    food_update=loader.loadTestsFromTestCase(TestUpdateFood)
    delete_food=loader.loadTestsFromTestCase(TestDeleteFood)
    all_tests = unittest.TestSuite([create_food,food_update,delete_food])
    
    runner.run(all_tests)
run_tests()