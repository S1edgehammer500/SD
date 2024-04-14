import unittest
from Model.ordersModel import *

def run_tests():

    class TestOrderCreation(unittest.TestCase):
        def setUp(self):
            self.model = Order()

        def test1_create_order(self):
            restaurantName = "Bristol"
            status = "Cooking"
            tableNumber = 43
            startTime = None
            readyTime = None
            result = self.model.createOrder(restaurantName, status, tableNumber, startTime, readyTime)
            self.assertEqual(result,1)
            tableNumber2 = 64
            self.model.createOrder(restaurantName, status, tableNumber2, startTime, readyTime)

        def test2_create_order_nonexistant_restaurant(self):
            restaurantName = "Nowhere"
            status = "Cooking"
            tableNumber = 43
            startTime = None
            readyTime = None
            result = self.model.createOrder(restaurantName, status, tableNumber, startTime, readyTime)
            self.assertEqual(result,0)

        def test3_add_to_food_list(self):
            orderID = 1
            foodName = "Burger"
            foodName2 = "Pizza"
            result = self.model.addFoodToOrder(orderID, foodName)
            self.assertEqual(result,1)
            self.model.addFoodToOrder(orderID, foodName2)

        def test4_add_nonexistant_food(self):
            orderID = 1
            foodName = "Nothing"
            result = self.model.addFoodToOrder(orderID, foodName)
            self.assertEqual(result, 0)

        def test5_add_food_to_nonexistant_ID(self):
            orderID = 30
            foodName = "Burger"
            result = self.model.addFoodToOrder(orderID, foodName)
            self.assertEqual(result, 0)

        def test6_remove_food_from_list(self):
            orderID = 1
            foodName = "Pizza"
            foodListID = 2
            result = self.model.removeFoodFromOrder(orderID, foodName, foodListID)
            self.assertEqual(result, 1)

        def test7_remove_nonexistant_foodList(self):
            orderID = 1
            foodName = "Burger"
            foodListID = 20
            result = self.model.removeFoodFromOrder(orderID, foodName, foodListID)
            self.assertEqual(result, 0)

        def test8_remove_food_not_in_list(self):
            orderID = 2
            foodName = "Burger"
            foodListID = 1
            result = self.model.removeFoodFromOrder(orderID, foodName, foodListID)
            self.assertEqual(result, 0)

        def test9_add_to_discount_list(self):
            orderID = 1
            discountID = 1
            discountID2 = 2
            result = self.model.addDiscountToOrder(orderID, discountID)
            self.assertEqual(result,1)
            self.model.addDiscountToOrder(orderID, discountID2)

        def test91_add_nonexistant_discount(self):
            orderID = 1
            discountID = 3
            result = self.model.addDiscountToOrder(orderID, discountID)
            self.assertEqual(result, 0)

        def test92_add_discount_to_nonexistant_ID(self):
            orderID = 30
            discountID = 1
            result = self.model.addDiscountToOrder(orderID, discountID)
            self.assertEqual(result, 0)

        def test93_remove_discount_from_list(self):
            orderID = 1
            discountID = 2
            discountListID = 1
            result = self.model.removeDiscountFromOrder(orderID, discountID, discountListID)
            self.assertEqual(result, 1)

        def test94_remove_nonexistant_discountList(self):
            orderID = 1
            discountID = 1
            discountListID = 20
            result = self.model.removeFoodFromOrder(orderID, discountID, discountListID)
            self.assertEqual(result, 0)

        def test95_remove_discount_not_in_list(self):
            orderID = 2
            discountID = 1
            discountListID = 1
            result = self.model.removeFoodFromOrder(orderID, discountID, discountListID)
            self.assertEqual(result, 0)


    class TestUpdateOrder(unittest.TestCase):
        def setUp(self):
            self.model = Order()

        def test1_update_restaurantName(self):
            id = 1
            restaurantName = 'Bristol'
            result = self.model.updateRestaurantName(restaurantName, id)
            self.assertEqual(result, 1)

        def test2_update_nonexistant_restaurant(self):
            id = 1
            restaurantName = 'Nowhere'
            result = self.model.updateRestaurantName(restaurantName, id)
            self.assertEqual(result, 0)

        def test3_update_restaurantName_invalid_id(self):
            id = 20
            restaurantName = 'Bristol'
            result = self.model.updateRestaurantName(restaurantName, id)
            self.assertEqual(result, 0)

        def test4_update_status(self):
            id = 1
            status = 'Cooking'
            result = self.model.updateStatus(status, id)
            self.assertEqual(result, 1)

        def test5_update_status_invalid_syntax(self):
            id = 1
            status = 'Nothing'
            result = self.model.updateStatus(status, id)
            self.assertEqual(result, 1)

        def test6_update_status_invalid_id(self):
            id = 20
            status = 'Ready'
            result = self.model.updateStatus(status, id)
            self.assertEqual(result, 0)

        def test7_update_price(self):
            id = 1
            price = 80
            result = self.model.updatePrice(price, id)
            self.assertEqual(result, 1)

        def test8_update_price_invalid_syntax(self):
            id = 1
            price = -1
            result = self.model.updatePrice(price, id)
            self.assertEqual(result, 1)

        def test9_update_price_invalid_id(self):
            id = 20
            price = 70
            result = self.model.updateStatus(price, id)
            self.assertEqual(result, 0)

        def test91_update_tableNumber(self):
            id = 1
            table = 1
            self.model.setOrderDetails(id)
            result = self.model.updateTable(table, id)
            self.assertEqual(result, 1)

        def test92_update_table_invalid_syntax(self):
            id = 1
            table = 31 #Bristol only has 20
            self.model.setOrderDetails(id)
            result = self.model.updateTable(table, id)
            self.assertEqual(result, 1)

        def test93_update_table_invalid_id(self):
            id = 20
            table = 18
            result = self.model.updateTable(table, id)
            self.assertEqual(result, 0)

        def test94_update_startTime(self):
            id = 1
            startTime = "2024-08-02 20:13:38"
            result = self.model.updateStartTime(startTime, id)
            self.assertEqual(result, 1)

        def test95_update_startTime_invalid_syntax(self):
            id = 1
            startTime = "2024-03-02 20:13:38" #Before today
            result = self.model.updateStartTime(startTime, id)
            self.assertEqual(result, 1)

        def test96_update_startTime_invalid_id(self):
            id = 20
            startTime = "2024-08-02 20:13:38"
            result = self.model.updateStartTime(startTime, id)
            self.assertEqual(result, 0)

        def test97_update_readyTime(self):
            id = 1
            readyTime = "2024-09-02 20:13:38"
            result = self.model.updateReadyTime(readyTime, id)
            self.assertEqual(result, 1)

        def test98_update_readyTime_invalid_syntax(self):
            id = 1
            readyTime = "2024-06-02 20:13:38" #Before start time
            result = self.model.updateReadyTime(readyTime, id)
            self.assertEqual(result, 1)

        def test99_update_readyTime_invalid_id(self):
            id = 20
            readyTime = "2024-09-02 20:13:38"
            result = self.model.updateReadyTime(readyTime, id)
            self.assertEqual(result, 0)
        
    class TestDeleteOrder(unittest.TestCase):
        def setUp(self):
            self.model = Order()

        def test1_delete_offer(self):
            id = 2
            result = self.model.delete_order(id)
            self.assertEqual(result, 1)

        def test2_delete_nonexistant_inventory(self):
            id = 70
            result = self.model.delete_order(id)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_order=loader.loadTestsFromTestCase(TestOrderCreation)
    order_update=loader.loadTestsFromTestCase(TestUpdateOrder)
    delete_order=loader.loadTestsFromTestCase(TestDeleteOrder)
    all_tests = unittest.TestSuite([create_order,order_update,delete_order])
    
    runner.run(all_tests)
run_tests()