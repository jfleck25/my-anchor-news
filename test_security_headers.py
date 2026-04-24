import pytest
from unittest.mock import MagicMock
import main

def test_add_security_headers():
    """Test that add_security_headers correctly sets required security headers on the response."""
    # Create a mock response object with a headers dictionary
    response = MagicMock()
    response.headers = {}

    # Call the function
    result = main.add_security_headers(response)

    # Assert the headers were added
    assert result.headers.get('X-Content-Type-Options') == 'nosniff'
    assert result.headers.get('X-Frame-Options') == 'SAMEORIGIN'
    assert result.headers.get('Strict-Transport-Security') == 'max-age=31536000; includeSubDomains'

    # Assert the same object is returned
    assert result is response
