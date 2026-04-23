import requests
import sys
import json
from datetime import datetime

class StagTracksAPITester:
    def __init__(self, base_url=""):
        self.base_url = base_url
        self.admin_token = None
        self.student_token = None
        self.tests_run = 0
        self.tests_passed = 0
        self.created_items = []
        self.created_reservations = []

    def run_test(self, name, method, endpoint, expected_status, data=None, token=None, params=None):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f'Bearer {token}'

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    return True, response.json()
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    print(f"   Response: {response.json()}")
                except:
                    print(f"   Response: {response.text}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test root API endpoint"""
        return self.run_test("Root Endpoint", "GET", "", 200)

    def test_admin_login(self):
        """Test admin login"""
        success, response = self.run_test(
            "Admin Login",
            "POST",
            "auth/login",
            200,
            data={"username": "admin", "password": "admin123"}
        )
        if success and 'access_token' in response:
            self.admin_token = response['access_token']
            print(f"   Admin token obtained")
            return True
        return False

    def test_student_signup(self):
        """Test student signup"""
        timestamp = datetime.now().strftime('%H%M%S')
        student_data = {
            "username": f"teststudent_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "TestPass123!",
            "role": "student"
        }
        
        success, response = self.run_test(
            "Student Signup",
            "POST",
            "auth/signup",
            200,
            data=student_data
        )
        if success and 'access_token' in response:
            self.student_token = response['access_token']
            self.student_username = student_data['username']
            print(f"   Student token obtained for {self.student_username}")
            return True
        return False

    def test_auth_me_admin(self):
        """Test /auth/me endpoint with admin token"""
        success, response = self.run_test(
            "Auth Me (Admin)",
            "GET",
            "auth/me",
            200,
            token=self.admin_token
        )
        if success and response.get('role') == 'admin':
            print(f"   Admin user verified: {response.get('username')}")
            return True
        return False

    def test_auth_me_student(self):
        """Test /auth/me endpoint with student token"""
        success, response = self.run_test(
            "Auth Me (Student)",
            "GET",
            "auth/me",
            200,
            token=self.student_token
        )
        if success and response.get('role') == 'student':
            print(f"   Student user verified: {response.get('username')}")
            return True
        return False

    def test_create_inventory_item(self):
        """Test creating inventory item (admin only)"""
        item_data = {
            "item_name": "Test Costume",
            "category": "Costume",
            "type": "Dress",
            "year": "1920s",
            "color": "Red",
            "size": "Medium",
            "location": "Rack A1",
            "status": "Available",
            "notes": "Test item for API testing",
            "quantity": 1
        }
        
        success, response = self.run_test(
            "Create Inventory Item",
            "POST",
            "items",
            200,
            data=item_data,
            token=self.admin_token
        )
        if success and 'id' in response:
            self.created_items.append(response['id'])
            print(f"   Item created with ID: {response['id']}")
            return True, response['id']
        return False, None

    def test_get_inventory_items(self):
        """Test getting inventory items"""
        success, response = self.run_test(
            "Get Inventory Items",
            "GET",
            "items",
            200,
            token=self.student_token
        )
        if success and isinstance(response, list):
            print(f"   Found {len(response)} items")
            return True
        return False

    def test_get_single_item(self, item_id):
        """Test getting a single inventory item"""
        success, response = self.run_test(
            "Get Single Item",
            "GET",
            f"items/{item_id}",
            200,
            token=self.student_token
        )
        if success and response.get('id') == item_id:
            print(f"   Item retrieved: {response.get('item_name')}")
            return True
        return False

    def test_update_inventory_item(self, item_id):
        """Test updating inventory item (admin only)"""
        update_data = {
            "color": "Blue",
            "notes": "Updated via API test"
        }
        
        success, response = self.run_test(
            "Update Inventory Item",
            "PUT",
            f"items/{item_id}",
            200,
            data=update_data,
            token=self.admin_token
        )
        if success and response.get('color') == 'Blue':
            print(f"   Item updated successfully")
            return True
        return False

    def test_search_items(self):
        """Test searching inventory items"""
        success, response = self.run_test(
            "Search Items",
            "GET",
            "items",
            200,
            params={"search": "Test"},
            token=self.student_token
        )
        if success:
            print(f"   Search returned {len(response)} items")
            return True
        return False

    def test_create_reservation(self, item_id):
        """Test creating a reservation (student)"""
        reservation_data = {
            "item_id": item_id
        }
        
        success, response = self.run_test(
            "Create Reservation",
            "POST",
            "reservations",
            200,
            data=reservation_data,
            token=self.student_token
        )
        if success and 'id' in response:
            self.created_reservations.append(response['id'])
            print(f"   Reservation created with ID: {response['id']}")
            return True, response['id']
        return False, None

    def test_get_reservations_admin(self):
        """Test getting reservations (admin sees all)"""
        success, response = self.run_test(
            "Get Reservations (Admin)",
            "GET",
            "reservations",
            200,
            token=self.admin_token
        )
        if success and isinstance(response, list):
            print(f"   Admin sees {len(response)} reservations")
            return True
        return False

    def test_get_reservations_student(self):
        """Test getting reservations (student sees own)"""
        success, response = self.run_test(
            "Get Reservations (Student)",
            "GET",
            "reservations",
            200,
            token=self.student_token
        )
        if success and isinstance(response, list):
            print(f"   Student sees {len(response)} reservations")
            return True
        return False

    def test_respond_to_reservation(self, reservation_id):
        """Test admin responding to reservation"""
        response_data = {
            "status": "approved",
            "admin_notes": "Approved for testing"
        }
        
        success, response = self.run_test(
            "Respond to Reservation",
            "PUT",
            f"reservations/{reservation_id}/respond",
            200,
            data=response_data,
            token=self.admin_token
        )
        if success and response.get('status') == 'approved':
            print(f"   Reservation approved successfully")
            return True
        return False

    def test_get_notifications_admin(self):
        """Test getting notifications (admin)"""
        success, response = self.run_test(
            "Get Notifications (Admin)",
            "GET",
            "notifications",
            200,
            token=self.admin_token
        )
        if success and isinstance(response, list):
            print(f"   Admin has {len(response)} notifications")
            return True, response
        return False, []

    def test_get_notifications_student(self):
        """Test getting notifications (student)"""
        success, response = self.run_test(
            "Get Notifications (Student)",
            "GET",
            "notifications",
            200,
            token=self.student_token
        )
        if success and isinstance(response, list):
            print(f"   Student has {len(response)} notifications")
            return True, response
        return False, []

    def test_mark_notification_read(self, notification_id):
        """Test marking notification as read"""
        success, response = self.run_test(
            "Mark Notification Read",
            "PUT",
            f"notifications/{notification_id}/read",
            200,
            token=self.student_token
        )
        return success

    def test_mark_all_notifications_read(self):
        """Test marking all notifications as read"""
        success, response = self.run_test(
            "Mark All Notifications Read",
            "PUT",
            "notifications/read-all",
            200,
            token=self.student_token
        )
        return success

    def test_delete_inventory_item(self, item_id):
        """Test deleting inventory item (admin only)"""
        success, response = self.run_test(
            "Delete Inventory Item",
            "DELETE",
            f"items/{item_id}",
            200,
            token=self.admin_token
        )
        return success

    def cleanup(self):
        """Clean up created test data"""
        print(f"\n🧹 Cleaning up test data...")
        
        # Delete created items
        for item_id in self.created_items:
            self.test_delete_inventory_item(item_id)

def main():
    print("🎭 StageTracks API Testing Suite")
    print("=" * 50)
    
    tester = StagTracksAPITester()
    
    # Test sequence
    try:
        # Basic connectivity
        if not tester.test_root_endpoint()[0]:
            print("❌ Cannot connect to API. Stopping tests.")
            return 1

        # Authentication tests
        if not tester.test_admin_login():
            print("❌ Admin login failed. Stopping tests.")
            return 1

        if not tester.test_student_signup():
            print("❌ Student signup failed. Stopping tests.")
            return 1

        if not tester.test_auth_me_admin():
            print("❌ Admin auth verification failed.")

        if not tester.test_auth_me_student():
            print("❌ Student auth verification failed.")

        # Inventory tests
        success, item_id = tester.test_create_inventory_item()
        if not success:
            print("❌ Item creation failed. Skipping item-dependent tests.")
            item_id = None

        tester.test_get_inventory_items()
        
        if item_id:
            tester.test_get_single_item(item_id)
            tester.test_update_inventory_item(item_id)
            
            # Reservation tests
            success, reservation_id = tester.test_create_reservation(item_id)
            if success:
                tester.test_get_reservations_admin()
                tester.test_get_reservations_student()
                tester.test_respond_to_reservation(reservation_id)

        tester.test_search_items()

        # Notification tests
        admin_notifs_success, admin_notifs = tester.test_get_notifications_admin()
        student_notifs_success, student_notifs = tester.test_get_notifications_student()
        
        # Test notification interactions if we have notifications
        if student_notifs and len(student_notifs) > 0:
            first_notif_id = student_notifs[0].get('id')
            if first_notif_id:
                tester.test_mark_notification_read(first_notif_id)
        
        tester.test_mark_all_notifications_read()

        # Cleanup
        tester.cleanup()

    except Exception as e:
        print(f"❌ Unexpected error during testing: {str(e)}")
        return 1

    # Print results
    print(f"\n📊 Test Results")
    print("=" * 50)
    print(f"Tests passed: {tester.tests_passed}/{tester.tests_run}")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print(f"⚠️  {tester.tests_run - tester.tests_passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())