================
django-mtg-res
================

Django MTG RES is a reusable Django app for logging HTTP requests and responses. It provides a simple way to track API calls, debug issues, and maintain audit logs of external service interactions.

Features
--------

* Log HTTP requests and responses with full metadata
* Support for different request/response formats (JSON, text, etc.)
* Flexible reference system to link logs to specific objects
* Safe error handling to prevent logging failures from breaking your app
* Admin interface for viewing and managing logs

Quick start
-----------

1. Install django-mtg-res::

    pip install django-mtg-res

2. Add "django_mtg_res" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...
        'django_mtg_res',
    ]

3. Run migrations to create the RequestLog model::

    python manage.py migrate

4. Start using the RequestLog model in your code::

    from django_mtg_res.models import RequestLog
    import requests

    # Make an API call
    response = requests.get('https://api.example.com/data')
    
    # Log the request and response
    RequestLog.create_request_log(
        url='https://api.example.com/data',
        method='GET',
        request=None,  # No request body for GET
        response=response,
        ref_obj='User',
        ref_id='123',
        remarks='Fetching user data'
    )

Usage Examples
--------------

**Basic logging:**

.. code-block:: python

    from django_mtg_res.models import RequestLog
    
    # Log a simple request
    RequestLog.create_request_log(
        url='https://api.service.com/endpoint',
        method='POST',
        request={'key': 'value'},
        response={'result': 'success'},
        status_code=200
    )

**With reference objects:**

.. code-block:: python

    # Log with reference to a specific model instance
    RequestLog.create_request_log(
        url='https://payment.service.com/charge',
        method='POST',
        request=payment_data,
        response=payment_response,
        ref_obj='Order',
        ref_id=str(order.id),
        remarks='Payment processing'
    )

**Safe logging (won't raise exceptions):**

.. code-block:: python

    # This will not raise exceptions even if logging fails
    RequestLog.create_request_log(
        url=api_url,
        request=request_data,
        response=response_data,
        safely_create=True  # Default is True
    )

Admin Interface
---------------

The app includes Django admin integration. You can view and search request logs in the Django admin panel under "Request Logs".

Requirements
------------

* Python >= 3.10
* Django >= 4.0
* requests >= 2.25.0

License
-------

This project is licensed under the MIT License.

Contributing
------------

Contributions are welcome! Please feel free to submit a Pull Request.

Support
-------

If you encounter any issues or have questions, please open an issue on the project repository.