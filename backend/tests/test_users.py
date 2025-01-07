import unittest
import requests

BASE_URL = "http://127.0.0.1:5001/api"  # Your backend API base URL

class TestUsersAPI(unittest.TestCase):
    def setUp(self):
        # Test user definition
        self.test_user = {
            "username": "test_user",
            "password": "password_123",
            "first_name": "Test",
            "last_name": "User",
            "email": "test_user@test.com",
            "date_of_birth": "2003-01-01",
            "goal": "Lose weight gain muscle",
        }
    
    def test_register_user(self):
        """Test user registration"""
        response = requests.post(f"{BASE_URL}/register", json=self.test_user)  # Call register endpoint with test data
        sucessful = 201 # Expected response
        print(f"Expected response for sucessful registration: {sucessful}, actual response: {response}" )

        
        if response.status_code == 400 and "Username already exists" in response.json().get("error", ""):  #if 400 code the user exists and we can skip this test
            self.skipTest("Test user already exists in the database.")
        
        self.assertEqual(response.status_code, 201) # Assert that register is sucessful 201 
        self.assertIn("message", response.json())
    
    def test_login_user(self):
        """Test user login """
        login_info = { # Using our now registered user's data to test login endpoint
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/login", json=login_info) # Call login endpoint with test data
        sucessful = 200 # Expected response
        print(f"Expected response for sucessful login: {sucessful}, actual response: {response}")
        
        self.assertEqual(response.status_code, 200) # Assert that login was sucessful
        self.assertIn("user", response.json())


if __name__ == "__main__":
    unittest.main()
