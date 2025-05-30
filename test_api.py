import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("Testing Market Intelligence API...")

# 1. Create Organization
print("\n1. Creating organization...")
org_response = requests.post(f"{BASE_URL}/organizations", json={"name": "Test Corp"})
if org_response.status_code == 200:
    org = org_response.json()
    print(f"✅ Created: {org['name']} (ID: {org['id']})")
else:
    print(f"❌ Failed: {org_response.text}")
    exit(1)

# 2. List Organizations
print("\n2. Listing organizations...")
list_response = requests.get(f"{BASE_URL}/organizations")
if list_response.status_code == 200:
    orgs = list_response.json()
    print(f"✅ Found {len(orgs)} organizations")
else:
    print(f"❌ Failed: {list_response.text}")

# 3. Test File Upload (with a simple text file)
print("\n3. Testing file upload...")
with open("test_report5.txt", "rb") as f:
    files = {'file': ("test_report5.txt", f, 'text/plain')}
    data = {'file_type': 'txt'}
    upload_response = requests.post(f"{BASE_URL}/uploads", files=files, data=data)
    if upload_response.status_code == 200:
        upload = upload_response.json()
        print(f"✅ Uploaded: {upload['filename']} (ID: {upload['id']})")
    else:
        print(f"❌ Failed: {upload_response.text}")

print("\n✅ Basic API test complete!") 