import unittest
import requests
import time
from config import Config

BASE_URL = "http://127.0.0.1:5001/api"  # Your backend API base URL

API_KEY = Config.API_KEY

headers = {
    "X-API-KEY": API_KEY
}

class TestUsersAPI(unittest.TestCase):
    def setUp(self):
        # Define the test user
        self.test_user = {
            "username": "TestingUser",
            "password": "password_123",
            "first_name": "Test",
            "last_name": "User",
            "email": "Testerz@tester.com",
            "date_of_birth": "2003-01-01",
            "goal": "Lose weight gain muscle",
        }
    
    def test_01_register_user(self): # perform register test first - does in alphabetical order so we need to id them accordingly (01)
        """Test user registration endpoint"""
        response = requests.post(f"{BASE_URL}/register", json=self.test_user, headers=headers)  # Call register endpoint with test user json data
        print(f"Register endpoint response status: {response.status_code}") #Response code
        print(f"Register endpoint response data: {response.json()}") # Response data
        success = 201 # Expected response

        # Assert successful registration
        self.assertEqual(response.status_code, success)
        self.assertIn("message", response.json())

        # Verify the user exists in the database
        user_check = requests.get(f"{BASE_URL}/get-id/{self.test_user['username']}",headers=headers) # Call the get id endpoint to retrieve id
        print(f"User check response status: {user_check.status_code}") #response code
        print(f"User check response data: {user_check.json()}") #response data
        success_get_id = 200 # Expected response
        self.assertEqual(user_check.status_code, success_get_id) 
    
    
    def test_02_login_user(self):
        """Test user login endpoint"""
        # Ensure registration happens first
        time.sleep(0.9)  #  time delay, ensure user is registered and in db before login test

        # Login json data
        login_info = {
            "username": self.test_user["username"],
            "password": self.test_user["password"]
        }
        response = requests.post(f"{BASE_URL}/login", json=login_info,headers=headers) # Call login endpoint 
        print(f"Login endpoint response status: {response.status_code}") # Response code
        print(f"Login endpoint response data: {response.json()}") # Reponse data
        success = 200 # Expected response 

        # Assert successful login
        self.assertEqual(response.status_code, success) 
        self.assertIn("user", response.json())

    def test_03_change_email(self):
        """Test user email change endpoint"""

        new_email_info = {
            "user_id": 5, # change to match the test user in testing session
            "email": "tester_new@test.com"
        }
        success = 200 #Expected response
        response = requests.post(f"{BASE_URL}/change-email", json=new_email_info, headers=headers) # Call change email endpoint
        self.assertEqual(response.status_code, success) #Ensure success
        self.assertIn("Successfully updated email", response.json().get('message')) 
        print(f"Change email endpoint response status {response.status_code}")
        print(f"Change email endpoint response data: {response.json()}")


    def test_04_delete_user(self):
        """Test delete user"""
        user_id = 5 #change to match test user in testing session
        response = requests.delete(f"{BASE_URL}/users/delete/{user_id}", headers=headers)
        self.assertEqual(response.status_code, 200)
        print(f"Delete user response status: {response.status_code}")
        print(f"Delete endpoint response data: {response.json()}")
    


if __name__ == "__main__":
    unittest.main()

#from backend run:   py -m unittest discover -s tests
