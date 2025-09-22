import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()


def test_airtable_simple():
    """Simple HTTP test for Airtable connection"""

    api_key = os.getenv('AIRTABLE_API_KEY')
    base_id = os.getenv('AIRTABLE_BASE_ID')
    table_name = os.getenv('AIRTABLE_TABLE_NAME', 'Table 1')

    print(f"API Key: {api_key[:20]}..." if api_key else "No API Key")
    print(f"Base ID: {base_id}")
    print(f"Table Name: {table_name}")

    if not api_key or not base_id:
        print("Missing credentials in .env file")
        return False

    # Airtable API URL
    url = f"https://api.airtable.com/v0/{base_id}/{table_name}"

    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }

    try:
        # First, try to get existing records
        print(f"Testing GET request to: {url}")
        response = requests.get(url, headers=headers)

        print(f"Response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ Successfully connected to Airtable!")
            print(f"✅ Found {len(data.get('records', []))} existing records")

            # Test creating a record
            test_record = {
                "records": [
                    {
                        "fields": {
                            "Name": "Test Blog Entry",
                            "Notes": "This is a test from Python"
                        }
                    }
                ]
            }

            create_response = requests.post(url, headers=headers, json=test_record)

            if create_response.status_code == 200:
                created = create_response.json()
                record_id = created['records'][0]['id']
                print(f"✅ Test record created with ID: {record_id}")

                # Clean up - delete test record
                delete_url = f"{url}/{record_id}"
                delete_response = requests.delete(delete_url, headers=headers)

                if delete_response.status_code == 200:
                    print("✅ Test record cleaned up")

                return True
            else:
                print(f"❌ Failed to create test record: {create_response.status_code}")
                print(f"Response: {create_response.text}")
                return False

        else:
            print(f"❌ Connection failed: {response.status_code}")
            print(f"Response: {response.text}")

            if response.status_code == 404:
                print("\n💡 Possible issues:")
                print("1. Check your Base ID is correct")
                print("2. Check your table name is correct")
                print("3. Make sure the table name doesn't have special characters")
            elif response.status_code == 401:
                print("\n💡 Authentication issue:")
                print("1. Check your Personal Access Token is correct")
                print("2. Make sure the token has the right permissions")
                print("3. Make sure you added your base to the token")

            return False

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("🚀 Testing Airtable Connection...")
    test_airtable_simple()