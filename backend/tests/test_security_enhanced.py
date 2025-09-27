import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json
import time

def test_jwt_token_security(client: TestClient, test_user):
    """Test JWT token security measures."""
    # Test token creation with different payloads
    from app.auth import create_access_token
    
    # Valid token
    valid_token = create_access_token(data={"sub": str(test_user.id)})
    assert valid_token is not None
    
    # Test token with invalid payload
    with pytest.raises(Exception):
        create_access_token(data={"invalid": "payload"})
    
    # Test token with missing sub
    with pytest.raises(Exception):
        create_access_token(data={"user_id": str(test_user.id)})

def test_password_security(client: TestClient):
    """Test password security measures."""
    # Test password hashing
    from app.auth import get_password_hash, verify_password
    
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original password
    assert hashed != password
    assert len(hashed) > 50  # bcrypt hashes are long
    
    # Should verify correctly
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)
    
    # Test with different passwords
    password2 = "anotherpassword456"
    hashed2 = get_password_hash(password2)
    assert hashed != hashed2  # Different passwords should have different hashes

def test_sql_injection_prevention(client: TestClient, auth_headers, db_session):
    """Test SQL injection prevention."""
    # Test various SQL injection attempts
    malicious_inputs = [
        "'; DROP TABLE users; --",
        "' OR '1'='1",
        "'; INSERT INTO users (username) VALUES ('hacker'); --",
        "' UNION SELECT * FROM users --",
        "'; UPDATE users SET username='hacker' WHERE id=1; --",
    ]
    
    for malicious_input in malicious_inputs:
        # Test in URL field
        scan_data = {"url": f"https://example.com?param={malicious_input}"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        # Should either succeed (valid URL) or fail with validation error, not SQL error
        assert response.status_code in [201, 400, 422]
        
        # Verify no SQL injection occurred
        if response.status_code == 201:
            scan_id = response.json()["id"]
            response = client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
            assert response.status_code == 200
            # URL should be stored as-is, not executed as SQL
            assert malicious_input in response.json()["url"]

def test_xss_prevention(client: TestClient, auth_headers, db_session, test_user):
    """Test XSS prevention."""
    # Test various XSS attempts
    xss_payloads = [
        "<script>alert('xss')</script>",
        "javascript:alert('xss')",
        "<img src=x onerror=alert('xss')>",
        "<svg onload=alert('xss')>",
        "';alert('xss');//",
    ]
    
    for payload in xss_payloads:
        # Test in URL field
        scan_data = {"url": f"https://example.com?param={payload}"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        
        if response.status_code == 201:
            scan_id = response.json()["id"]
            response = client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
            assert response.status_code == 200
            
            # Check that XSS payload is not executed
            response_text = json.dumps(response.json())
            assert "<script>" not in response_text.lower()
            assert "javascript:" not in response_text.lower()
            assert "onerror=" not in response_text.lower()
            assert "onload=" not in response_text.lower()

def test_csrf_protection(client: TestClient, auth_headers):
    """Test CSRF protection measures."""
    # Test that API doesn't rely on cookies for authentication
    # (JWT tokens in headers are CSRF-safe)
    
    # Test with different origins
    headers_with_origin = {
        **auth_headers,
        "Origin": "https://malicious-site.com",
        "Referer": "https://malicious-site.com",
    }
    
    scan_data = {"url": "https://example.com"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=headers_with_origin)
    # Should still work because we use JWT tokens, not cookies
    assert response.status_code == 201

def test_input_validation_security(client: TestClient, auth_headers):
    """Test input validation security."""
    # Test various malicious inputs
    malicious_inputs = [
        {"url": "A" * 10000},  # Very long URL
        {"url": "https://example.com/" + "A" * 10000},  # Very long path
        {"url": "https://" + "A" * 1000 + ".com"},  # Very long domain
        {"url": "https://example.com?" + "&".join([f"param{i}=value{i}" for i in range(1000)])},  # Many parameters
    ]
    
    for malicious_input in malicious_inputs:
        response = client.post("/api/v1/scans/", json=malicious_input, headers=auth_headers)
        # Should either succeed (valid input) or fail with validation error
        assert response.status_code in [201, 400, 422]

def test_rate_limiting_security(client: TestClient, auth_headers, mock_redis):
    """Test rate limiting security measures."""
    with patch("app.dependencies.get_redis", return_value=mock_redis):
        # Test rate limiting with different IPs
        mock_redis.incr.return_value = 1  # Within limit
        mock_redis.exists.return_value = False
        
        scan_data = {"url": "https://example.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Test rate limiting exceeded
        mock_redis.incr.return_value = 11  # Exceed limit
        mock_redis.exists.return_value = True
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 429
        
        # Test rate limiting reset
        mock_redis.incr.return_value = 1  # Within limit again
        mock_redis.exists.return_value = False
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201

def test_authentication_bypass_attempts(client: TestClient):
    """Test various authentication bypass attempts."""
    # Test with no authentication
    scan_data = {"url": "https://example.com"}
    response = client.post("/api/v1/scans/", json=scan_data)
    assert response.status_code == 401
    
    # Test with invalid token format
    invalid_tokens = [
        "invalid",
        "Bearer",
        "Bearer invalid.token",
        "Basic dGVzdDp0ZXN0",  # Basic auth instead of Bearer
        "Bearer " + "A" * 1000,  # Very long token
        "Bearer " + "A" * 10,  # Very short token
    ]
    
    for token in invalid_tokens:
        headers = {"Authorization": token}
        response = client.post("/api/v1/scans/", json=scan_data, headers=headers)
        assert response.status_code == 401
    
    # Test with expired token
    from app.auth import create_access_token
    from app.config import settings
    
    original_expire = settings.access_token_expire_minutes
    settings.access_token_expire_minutes = -1  # Expired
    
    expired_token = create_access_token(data={"sub": "1"})
    headers = {"Authorization": f"Bearer {expired_token}"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=headers)
    assert response.status_code == 401
    
    # Restore original setting
    settings.access_token_expire_minutes = original_expire

def test_authorization_bypass_attempts(client: TestClient, auth_headers, auth_headers_2, test_scan_result):
    """Test various authorization bypass attempts."""
    # Test accessing other user's data
    response = client.get(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers_2)
    assert response.status_code == 404
    
    # Test deleting other user's data
    response = client.delete(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers_2)
    assert response.status_code == 404
    
    # Test accessing non-existent data
    response = client.get("/api/v1/scans/99999", headers=auth_headers)
    assert response.status_code == 404
    
    # Test with invalid scan ID format
    response = client.get("/api/v1/scans/invalid", headers=auth_headers)
    assert response.status_code == 422

def test_data_leakage_prevention(client: TestClient, auth_headers, db_session, test_user, test_user_2):
    """Test data leakage prevention."""
    # Create data for both users
    scan_data_1 = {"url": "https://user1.com"}
    response = client.post("/api/v1/scans/", json=scan_data_1, headers=auth_headers)
    assert response.status_code == 201
    scan_id_1 = response.json()["id"]
    
    scan_data_2 = {"url": "https://user2.com"}
    response = client.post("/api/v1/scans/", json=scan_data_2, headers=auth_headers_2)
    assert response.status_code == 201
    scan_id_2 = response.json()["id"]
    
    # User 1 should not see User 2's data
    response = client.get("/api/v1/scans/", headers=auth_headers)
    assert response.status_code == 200
    
    scans = response.json()["scans"]
    user_1_scan_ids = [scan["id"] for scan in scans]
    assert scan_id_1 in user_1_scan_ids
    assert scan_id_2 not in user_1_scan_ids
    
    # User 2 should not see User 1's data
    response = client.get("/api/v1/scans/", headers=auth_headers_2)
    assert response.status_code == 200
    
    scans = response.json()["scans"]
    user_2_scan_ids = [scan["id"] for scan in scans]
    assert scan_id_2 in user_2_scan_ids
    assert scan_id_1 not in user_2_scan_ids

def test_error_information_disclosure(client: TestClient, auth_headers):
    """Test that errors don't disclose sensitive information."""
    # Test with invalid scan ID
    response = client.get("/api/v1/scans/99999", headers=auth_headers)
    assert response.status_code == 404
    
    error_data = response.json()
    error_detail = error_data.get("detail", "").lower()
    
    # Should not contain sensitive information
    sensitive_terms = [
        "database",
        "sql",
        "traceback",
        "stack trace",
        "internal error",
        "server error",
        "exception",
        "file",
        "line",
        "module",
    ]
    
    for term in sensitive_terms:
        assert term not in error_detail

def test_logging_security(client: TestClient, auth_headers, caplog):
    """Test that logging doesn't expose sensitive information."""
    import logging
    
    # Test with sensitive data
    scan_data = {"url": "https://example.com?password=secret123"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 201
    
    # Check that sensitive data is not logged
    log_messages = caplog.text
    assert "password=secret123" not in log_messages
    assert "secret123" not in log_messages

def test_http_method_security(client: TestClient, auth_headers):
    """Test HTTP method security."""
    # Test unsupported methods
    unsupported_methods = ["PATCH", "PUT", "HEAD", "OPTIONS"]
    
    for method in unsupported_methods:
        response = client.request(method, "/api/v1/scans/", headers=auth_headers)
        assert response.status_code == 405

def test_content_type_security(client: TestClient, auth_headers):
    """Test content type security."""
    # Test with invalid content type
    response = client.post(
        "/api/v1/scans/",
        data="invalid json",
        headers={**auth_headers, "content-type": "text/plain"}
    )
    assert response.status_code == 422
    
    # Test with missing content type
    response = client.post(
        "/api/v1/scans/",
        data='{"url": "https://example.com"}',
        headers=auth_headers
    )
    # Should still work because FastAPI can handle JSON without explicit content-type
    assert response.status_code in [201, 422]

def test_request_size_security(client: TestClient, auth_headers):
    """Test request size security."""
    # Test with very large request body
    large_data = {"url": "https://example.com", "data": "x" * (1024 * 1024)}  # 1MB
    
    response = client.post("/api/v1/scans/", json=large_data, headers=auth_headers)
    # Should either succeed or fail with appropriate error, not crash
    assert response.status_code in [201, 400, 413, 422]

def test_unicode_security(client: TestClient, auth_headers):
    """Test Unicode security handling."""
    # Test with various Unicode inputs
    unicode_inputs = [
        "https://example.com/测试",
        "https://example.com/🚀",
        "https://example.com/测试?param=值",
        "https://example.com/测试#锚点",
    ]
    
    for unicode_input in unicode_inputs:
        scan_data = {"url": unicode_input}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        # Should handle Unicode properly
        assert response.status_code in [201, 400, 422]

def test_timing_attack_prevention(client: TestClient, auth_headers):
    """Test timing attack prevention."""
    # Test that response times are consistent for different inputs
    import time
    
    # Test with valid URL
    start_time = time.time()
    scan_data = {"url": "https://example.com"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    valid_time = time.time() - start_time
    
    # Test with invalid URL
    start_time = time.time()
    scan_data = {"url": "invalid-url"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    invalid_time = time.time() - start_time
    
    # Times should be similar (within reasonable range)
    time_diff = abs(valid_time - invalid_time)
    assert time_diff < 1.0  # Should be within 1 second

def test_session_security(client: TestClient, test_user):
    """Test session security measures."""
    # Test that JWT tokens are stateless
    response = client.post(
        "/api/v1/login",
        data={"username": test_user.username, "password": "testpassword"}
    )
    assert response.status_code == 200
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Token should work immediately
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 200
    
    # Token should not be stored in cookies
    assert "set-cookie" not in response.headers
    
    # Test token refresh
    response = client.post("/api/v1/refresh", headers=headers)
    assert response.status_code == 200
    
    new_token = response.json()["access_token"]
    assert new_token != token  # Should be a new token
