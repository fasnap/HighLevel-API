from django.shortcuts import redirect
import requests
import json
import random
from django.http import JsonResponse

# API Credentials
CLIENT_ID = "65c0a9a4277b2961322c545a-ls8q934d"
CLIENT_SECRET = "94af4663-c0c7-4340-9ce5-39b38e88c146"
REDIRECT_URI = "https://google.com"
LOCATION_ID = "k1F38z3A0efRMHeVkk3v"
CUSTOM_FIELD_NAME = "DFS Booking Zoom Link"
API_VERSION = "2021-07-28"
BASE_URL = "https://services.leadconnectorhq.com"

def initiate_auth(request):
    """Redirect user to HighLevel OAuth authorization page"""
    scope = "contacts.readonly+contacts.write+locations/customFields.readonly"
    auth_url = (
        f"https://marketplace.gohighlevel.com/oauth/chooselocation?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope={scope}"
    )
    return redirect(auth_url)

def exchange_auth_code_for_token(auth_code):
    """Exchange auth code for an access token"""
    url = f"{BASE_URL}/oauth/token"
    payload = {
        "grant_type": "authorization_code",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
        "redirect_uri": REDIRECT_URI
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"  # ✅ Ensures correct format
    }
    response = requests.post(url, data=payload, headers=headers)  # ✅ Use `data=payload`
    if response.status_code != 200:
        print(f"Error getting access token: {response.text}")
        return None
    return response.json()

def handle_oauth_callback(request):
    """Process OAuth callback and store the access token"""
    auth_code = request.GET.get("code")  
    if not auth_code:
        return initiate_auth(request)  
    
    token_data = exchange_auth_code_for_token(auth_code)
    if not token_data or "access_token" not in token_data:
        return JsonResponse({"error": "Failed to get access token", "details": token_data}, status=400)
    
    access_token = token_data.get("access_token")  
    request.session["access_token"] = access_token
    request.session.modified = True
    return JsonResponse({"message": "Access token stored successfully", "access_token": access_token})

def prepare_api_headers(access_token):
    """Return standardized API headers"""
    return {
        "Authorization": f"Bearer {access_token}",
        "Version": "2021-07-28",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
def retrieve_all_contacts(request):
    """Fetch all contacts from HighLevel API"""
    access_token = request.session.get('access_token')  # ✅ Get token from session
    if not access_token:
        return JsonResponse({"error": "Missing access token. Please authenticate first."}, status=401)

    url = f"{BASE_URL}/contacts/?locationId={LOCATION_ID}"
    headers = prepare_api_headers(access_token)
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return JsonResponse({
            "error": "Failed to fetch contacts", 
            "details": response.text
        }, status=response.status_code)    
    
    contacts = response.json().get("contacts", [])
    if not contacts:
        return JsonResponse({"error": "No contacts found"}, status=404)
    
    return JsonResponse({"contacts": contacts})

def fetch_random_contact(request):
    """Fetch a random contact from the API"""    
    access_token = request.session.get('access_token')  # ✅ Get token from session
    if not access_token:
        return JsonResponse({"error": "Missing access token. Please authenticate first."}, status=401)

    url = f"{BASE_URL}/contacts/?locationId={LOCATION_ID}"
    headers = prepare_api_headers(access_token)
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return JsonResponse({
            "error": "Failed to fetch contacts", 
            "details": response.text
        }, status=response.status_code)
        
    contacts = response.json().get("contacts", [])
    if not contacts:
        return JsonResponse({"error": "No contacts found"}, status=404)
        
    random_contact = random.choice(contacts)
    return JsonResponse({
        "random_contact_id": random_contact["id"],
        "name": random_contact.get("name", "Unknown"),
        "email": random_contact.get("email", "No Email"),
        "phone": random_contact.get("phone", "No Phone")
    })

def retrieve_custom_fields(request):
    """Fetch all custom fields for contacts"""
    access_token = request.session.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Missing access token. Please authenticate first."}, status=401)

    url = f"{BASE_URL}/locations/{LOCATION_ID}/customFields?model=contact"
    headers = prepare_api_headers(access_token)
    
    response = requests.get(url, headers=headers)
    print(f"Custom Fields API Response: {response.status_code}")
    
    if response.status_code != 200:
        return JsonResponse({
            "error": "Failed to fetch custom fields", 
            "details": response.text
        }, status=response.status_code)
        
    custom_fields = response.json().get("customFields", [])
    return JsonResponse({"custom_fields": custom_fields})

def locate_custom_field_id(access_token, field_name):
    """Find a specific custom field ID by name"""
    url = f"{BASE_URL}/locations/{LOCATION_ID}/customFields?model=contact"
    headers = prepare_api_headers(access_token)
    
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching custom fields: {response.text}")
        return None
    
    custom_fields = response.json().get("customFields", [])
    
    # Try different possible field name properties in the API response
    for field in custom_fields:
        if (field.get("name") == field_name or 
            field.get("fieldName") == field_name or 
            field.get("displayName") == field_name):
            return field.get("id")
    
    return None

def modify_random_contact(request):
    """Update a random contact with the specified custom field value"""
    access_token = request.session.get('access_token')
    if not access_token:
        return JsonResponse({"error": "Missing access token. Please authenticate first."}, status=401)

    headers = prepare_api_headers(access_token)

    # Step 1: Get a random contact
    contacts_url = f"{BASE_URL}/contacts/?locationId={LOCATION_ID}"
    contacts_response = requests.get(contacts_url, headers=headers)
    
    if contacts_response.status_code != 200:
        return JsonResponse({
            "error": "Failed to fetch contacts", 
            "details": contacts_response.text
        }, status=contacts_response.status_code)
    
    contacts = contacts_response.json().get("contacts", [])
    if not contacts:
        return JsonResponse({"error": "No contacts found"}, status=404)
    
    # Select a random contact
    random_contact = random.choice(contacts)
    contact_id = random_contact["id"]
    contact_name = random_contact.get("name", "Unknown Contact")
    
    # Step 2: Get the custom field ID
    custom_field_id = locate_custom_field_id(access_token, CUSTOM_FIELD_NAME)
    
    # Step 3: Update the contact with the custom field
    update_url = f"{BASE_URL}/contacts/{contact_id}"
    
    if custom_field_id:
        # Use ID if we found it
        update_data = {
            "customFields": [
                {
                    "id": custom_field_id,
                    "value": "TEST"
                }
            ]
        }
    else:
        # Try with name if ID not found (API may create the field)
        update_data = {
            "customFields": [
                {
                    "name": CUSTOM_FIELD_NAME,
                    "value": "TEST"
                }
            ]
        }
    
    print(f"Updating contact {contact_id} ({contact_name}) with data: {json.dumps(update_data)}")
    
    update_response = requests.put(
        update_url, 
        headers=headers, 
        json=update_data
    )
    
    print(f"Update response: {update_response.status_code}")
    
    if update_response.status_code != 200:
        return JsonResponse({
            "error": "Failed to update contact", 
            "details": update_response.text,
            "contact_id": contact_id,
            "contact_name": contact_name,
            "data_attempted": update_data
        }, status=update_response.status_code)
    
    return JsonResponse({
        "message": "Contact updated successfully",
        "contact_id": contact_id,
        "contact_name": contact_name,
        "custom_field_updated": CUSTOM_FIELD_NAME,
        "custom_field_id": custom_field_id,
        "updated_value": "TEST"
    })
    