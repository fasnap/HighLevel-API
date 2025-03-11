from django.urls import path
from .views import get_auth_code, get_random_contact, get_custom_fields, debug_session, update_highlevel_contact, update_random_contact, get_all_contacts

urlpatterns = [
    path("login/", get_auth_code, name="login"),  # Redirect to OAuth login
    path('get-all-contacts/', get_all_contacts, name="get_all_contacts"),
    path("get-contact/", get_random_contact, name="get_random_contact"),  # Fetch a random contact
    path("custom-field/", get_custom_fields, name="get_custom_fields"),  # Update contact field
    path("debug-session/", debug_session, name="debug_session"),
    path("oauth/callback/", update_highlevel_contact, name="oauth_callback"),  # Callback after authorization
    path("update-contact/", update_random_contact, name="update_contact")
]