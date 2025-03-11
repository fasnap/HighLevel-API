from django.urls import path
from .views import initiate_auth, fetch_random_contact, retrieve_custom_fields, handle_oauth_callback, modify_random_contact, retrieve_all_contacts

urlpatterns = [
    path("auth/", initiate_auth, name="auth"),  # Redirect to OAuth login
    path('contacts/all/', retrieve_all_contacts, name="retrieve_all_contacts"),
    path("contacts/random/", fetch_random_contact, name="fetch_random_contact"),  # Fetch a random contact
    path("fields/custom/", retrieve_custom_fields, name="retrieve_custom_fields"),  # Retrieve custom fields
    path("oauth/callback/", handle_oauth_callback, name="oauth_callback"),  # Callback after authorization
    path("contacts/update/", modify_random_contact, name="modify_random_contact")
]