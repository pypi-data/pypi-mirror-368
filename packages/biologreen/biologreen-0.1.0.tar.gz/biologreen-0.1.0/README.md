# Bio-Logreen Python SDK

The official Python SDK for the Bio-Logreen Facial Authentication API.

## Installation

```bash
pip install biologreen

Usage

from biologreen import BioLogreenClient

client = BioLogreenClient(api_key="YOUR_SECRET_API_KEY")

try:
    # Sign up a new user
    new_user = client.auth.signup_with_face("path/to/image.jpg")
    print(f"New user created with ID: {new_user.user_id}")

    # Log in an existing user
    existing_user = client.auth.login_with_face("path/to/image.jpg")
    print(f"Login successful for user: {existing_user.user_id}")

except Exception as e:
    print(f"An error occurred: {e}")