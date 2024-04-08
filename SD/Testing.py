import unittest
from passlib.hash import sha256_crypt
from Model.userModel import *
from flask import flash

def run_tests():

    class TestUserCreation(unittest.TestCase):
        def setUp(self):
            self.model = User()

        def test_create_user(self):
            code = "Test17"
            pw = str(1234567)
            al = 'admin'
            br = 1
            result = self.model.saveUserDetails(code,sha256_crypt.hash(pw),al, br)
            self.assertEqual(result,1)

        def test_create_existing_user(self):
            code = "Jake"
            pw = str(1234567)
            al = 'admin'
            br = 1
            result = self.model.saveUserDetails(code, sha256_crypt.hash(pw), al, br)
            self.assertEqual(result, 0)

        def create_user_invalid_code(self):
            code = "This code will be invalid"
            pw = str(12)
            al = 'admin'
            br = 1
            result = self.model.saveUserDetails(code, sha256_crypt.hash(pw), al, br)
            self.assertEqual(result, 0)

        def login_with_no_account(self):
            code = 'Test50'
            pw = str(1234)
            result = self.model.checkCodePassword(code, pw)
            self.assertEqual(result, 0)

        def successful_login(self):
            code = 'Jake'
            pw = 'England'
            result = self.model.checkCodePassword(code, pw)
            self.assertEqual(result, 1)

    class TestUpdateUser(unittest.TestCase):
        def setUp(self):
            self.model = User()

        def test_successful_update_code(self):
            code = 'Test'
            newCode = 'Goat2'
            result = self.model.updateCode(code, newCode)
            self.assertEqual(result, 1)

        def test_existing_update_code(self):
            code = 'Luqmaan'
            newCode = 'Jake'
            result = self.model.updateCode(code, newCode)
            self.assertEqual(result, 0)

        def test_invalid_code_syntax(self):
            code = 'Luqmaan'
            newCode = 'This will be invalid'
            result = self.model.updateCode(code, newCode)
            self.assertEqual(result, 0)

        def test_update_pw(self):
            code = 'Test2'
            pw = str('1234')
            result = self.model.updatePassword(code, pw)
            self.assertEqual(result,1)

        def test_update_al(self):
            code = 'Luqmaan'
            al = 'admin'
            result = self.model.updateAuthorisation(code, al)
            self.assertEqual(result, 1)

        def test_update_br(self):
            code = 'Jake'
            br = 2
            result = self.model.updateBaseRestaurant(code, br)
            self.assertEqual(result, 1)

    class TestDeleteUser(unittest.TestCase):
        def setUp(self):
            self.model = User()

        def test_delete_user(self):
            code = 'Goat'
            result = self.model.deleteUser(code)
            self.assertEqual(result, 1)

        def test_delete_nonexistant_user(self):
            code = 'No one'
            result = self.model.deleteUser(code)
            self.assertEqual(result, 0)

    loader = unittest.TestLoader()
    runner = unittest.TextTestRunner()

    create_user=loader.loadTestsFromTestCase(TestUserCreation)
    user_update=loader.loadTestsFromTestCase(TestUpdateUser)
    delete_users=loader.loadTestsFromTestCase(TestDeleteUser)
    all_tests = unittest.TestSuite([create_user,user_update,delete_users])
    
    runner.run(all_tests)
run_tests()