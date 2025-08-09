# Django Iran SMS

## Overview

A Django-based SMS integration system for simplifying in-country SMS usage in Iran, leveraging the `parsianwebco.ir` , `melipayamak.com` , `kavenegar.com` service with JWT authentication. Developed by the Chelseru team, drfiransms is designed to support additional services in future releases.

## Features

- Integration with `parsianwebco.ir` , `melipayamak.com` , `kavenegar.com`
- JWT-based authentication using `rest_framework_simplejwt`
- Scalable and extensible for other SMS providers
- Easy installation and configuration

## Installation

### Prerequisites

- Python 3.11
- Django 5.1 or higher

### Installation via pip

```bash
pip install django-iran-sms
```

### Configuration
In your Django project's settings.py, add the following parameters:

### settings.py

```bash
INSTALLED_APPS = [
...
'drfiransms', # When used in DRF.

]
```

```bash
DJANGO_IRAN_SMS = {
    'AUTHENTICATION': 'rest_framework_simplejwt',  # Specify the authentication method
    'SMS_BACKEND': 'PARSIAN_WEBCO_IR',  # Set the SMS provider backend
    'OTP_CODE': {
        'LENGTH': 6,  # Default length of OTP code
        'EXPIRE_PER_MINUTES': 2,  # Default expiration time in minutes
    },
    'PARSIAN_WEBCO_IR': {
        'API_KEY': 'API_KEY obtained from sms.parsianwebco.ir',  # API key from the SMS provider
        'TEMPLATES': {
            'OTP_CODE': 1,  # Template ID for OTP code
        }
    },
    'MELI_PAYAMAK_COM': {
        'USERNAME': 'Username used to log in to the melipayamak.com website.',
        'PASSWORD': 'API_KEY obtained from melipayamak.com',
        'FROM': '50004001001516',  # The sender number that should be received from the web service.
    },
    'KAVENEGAR_COM': {
        'API_KEY': 'API_KEY obtained from kavenegar.com',
        'FROM': '2000660110'
    }

}
```

## Django Iran SMS Configuration

The configuration parameters for `DJANGO_IRAN_SMS` can be set as follows:

### Authentication
Currently, only `rest_framework_simplejwt` is supported for authentication.

### SMS Backend
You can choose one of the following SMS providers:
- `PARSIAN_WEBCO_IR`
- `MELI_PAYAMAK_COM`
- `KAVENEGAR_COM`

### OTP Code
The `OTP_CODE` parameter is a dictionary containing the following keys:

- **`LENGTH`**: Specifies the length of the OTP code. It must be between **3 and 10** digits. If not provided, the default value is **6**.
- **`EXPIRE_PER_MINUTES`**: Defines the expiration time of the OTP code in minutes. It must be greater than **0**. If not provided, the default value is **2** minutes.




## Usage
### URL Configuration
In your urls.py, include the following views:

- OTPCodeSend: For sending OTP codes.
- Authentication: For handling authentication and optional registration.

### urls.py
```bash
from drfiransms.views import OTPCodeSend, Authentication, MessageSend

urlpatterns += [
    path('lur/send-code/', OTPCodeSend.as_view(), name='send_code'),  # Endpoint to send OTP code
    path('lur/authentication/', Authentication.as_view(), name='authentication'),  # Endpoint for authentication
    path('lur/send-message/', MessageSend.as_view(), name='send_message'), # Endpoint to send Message
]
```

## Sending Verification Code via API
To send a POST request for receiving a verification code for a mobile number, use the following structure:

```bash
curl -X POST https://djangoiransms.chelseru.com/lur/send-code/ \
     -H "Content-Type: application/json" \
     -d '{
           "mobile": "09123456789"
         }'
```
```bash
curl -X POST https://djangoiransms.chelseru.com/lur/authentication/ \
     -H "Content-Type: application/json" \
     -d '{
           "mobile": "09123456789",
           "code": "108117114",
           "group": "1"
         }'
```
- group: An attribute for times when there is a need to segment users, for example a user with a phone number can register as both a driver and a passenger.
This attribute is not required and if not entered, the default value will be 0.

```bash
curl -X POST https://djangoiransms.chelseru.com/lur/send-message/ \
     -H "Content-Type: application/json" \
     -d '{
           "mobile_number": "09123456789",
           "message_text": "hello luristan."
         }'
```
## User Table
Djangosms automatically creates a User table in the Django admin with two fields:

- mobile: Stores the user's mobile number.
- user: A one-to-one relationship with Django's default User model.
- group: An attribute for times when there is a need to segment users, for example a user with a phone number can register as both a driver and a passenger.
This attribute is not required and if not entered, the default value will be 0.

## OTP Code Table
drfsms automatically creates an OTP Code table in the Django admin with two fields:
- mobile: Stores the user's mobile number.
- code: Stores the OTP Code.
  
## JWT Authentication
Djangoiransms supports JWT authentication using the rest_framework_simplejwt package. The system is compatible with this authentication method for secure communication with the SMS gateway. Other authentication and login methods are currently under development.

## Future Plans
- Support for additional SMS providers.
- Enhanced error handling.
- Rate limiting and monitoring.
- Contribution


A Django package for seamless integration with Iranian SMS services like ParsianWebCo , Kavenegar and Melipayamak.
Contributions are welcome! Please submit pull requests or report issues on the GitHub repository.

## License
MIT License
