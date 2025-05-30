import requests
import json
from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import OrganizationCreate, Organization

BASE_URL = "http://localhost:8000/api/v1"

print("Testing Market Intelligence API...")

# Store the created organization ID for use in other tests
global created_org_id
global created_org_data
created_org_id = None
created_org_data = None

client = TestClient(app)

def test_create_organization():
    global created_org_id, created_org_data
    org_data = {"name": "Test Organization"}
    response = client.post("/api/v1/organizations", json=org_data)
    assert response.status_code in (200, 201)
    data = response.json()
    assert "id" in data
    assert data["name"] == org_data["name"]
    created_org_id = data["id"]
    created_org_data = data

def test_get_organization():
    global created_org_id, created_org_data
    assert created_org_id is not None, "Organization must be created first"
    response = client.get(f"/api/v1/organizations/{created_org_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_org_id
    assert data["name"] == created_org_data["name"]

def test_list_organizations():
    global created_org_id
    response = client.get("/api/v1/organizations")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert any(org["id"] == created_org_id for org in data)

def test_update_organization():
    global created_org_id
    updated_data = {"name": "Updated Organization"}
    response = client.put(f"/api/v1/organizations/{created_org_id}", json=updated_data)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == created_org_id
    assert data["name"] == updated_data["name"]
    # Optional: confirm update persisted
    get_response = client.get(f"/api/v1/organizations/{created_org_id}")
    assert get_response.status_code == 200
    get_data = get_response.json()
    assert get_data["name"] == updated_data["name"]

def test_delete_organization():
    global created_org_id
    response = client.delete(f"/api/v1/organizations/{created_org_id}")
    assert response.status_code in (200, 204)
    # Optional: confirm deletion
    get_response = client.get(f"/api/v1/organizations/{created_org_id}")
    assert get_response.status_code == 404

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