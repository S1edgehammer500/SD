import unittest
from Model.offersModel import *

def run_tests():

    class TestOfferCreation(unittest.TestCase):
        def setUp(self):
            self.model = Offers()

        def test1_create_offer(self):
            offerDescription = "Buy one get one free"
            result = self.model.createOffer(offerDescription)
            self.assertEqual(result,1)
            offerDescription2 = "25 percent off if you buy 3"
            self.model.createOffer(offerDescription2)

    class TestUpdateOffer(unittest.TestCase):
        def setUp(self):
            self.model = Offers()

        def test4_update_offerDescription(self):
            id = 1
            offerDescription = 'half off the third order'
            result = self.model.updateOfferDescription(offerDescription, id)
            self.assertEqual(result, 1)

        def test5_update_offerDescription_already_exists(self):
            id = 1
            offerDescription = '25 percent off if you buy 3'
            result = self.model.updateOfferDescription(offerDescription, id)
            self.assertEqual(result, 0)

        def test6_update_offerDescription_invalid_id(self):
            id = 20
            offerDescription = "Should fail"
            result = self.model.updateOfferDescription(offerDescription, id)
            self.assertEqual(result, 0)
        
    class TestDeleteOffer(unittest.TestCase):
        def setUp(self):
            self.model = Offers()

        def test1_delete_offer(self):
            id = 2
            result = self.model.delete_offer(id)
            self.assertEqual(result, 1)

        def test2_delete_nonexistant_inventory(self):
            id = 70
            result = self.model.delete_offer(id)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_offer=loader.loadTestsFromTestCase(TestOfferCreation)
    offer_update=loader.loadTestsFromTestCase(TestUpdateOffer)
    delete_offer=loader.loadTestsFromTestCase(TestDeleteOffer)
    all_tests = unittest.TestSuite([create_offer,offer_update,delete_offer])
    
    runner.run(all_tests)
run_tests()