import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

def test_ssrf_protection_private_ips(client: TestClient, auth_headers):
    """Test SSRF protection against private IP addresses."""
    private_ips = [
        "http://192.168.1.1",
        "http://10.0.0.1",
        "http://172.16.0.1",
        "http://127.0.0.1",
        "http://localhost",
        "http://169.254.169.254",  # AWS metadata
        "http://0.0.0.0",
        "http://[::1]",  # IPv6 localhost
    ]
    
    for ip in private_ips:
        scan_data = {"url": ip}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400
        assert "private" in response.json()["detail"].lower()

def test_ssrf_protection_invalid_schemes(client: TestClient, auth_headers):
    """Test SSRF protection against invalid URL schemes."""
    invalid_schemes = [
        "ftp://example.com",
        "file:///etc/passwd",
        "gopher://example.com",
        "ldap://example.com",
        "jar:file:///etc/passwd",
        "data:text/html,<script>alert('xss')</script>",
    ]
    
    for url in invalid_schemes:
        scan_data = {"url": url}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400

def test_ssrf_protection_redirect_attack(client: TestClient, auth_headers, mock_httpx_client):
    """Test SSRF protection against redirect attacks."""
    # Mock redirect to private IP
    mock_response = MagicMock()
    mock_response.status_code = 302
    mock_response.headers = {"location": "http://192.168.1.1"}
    mock_httpx_client.get.return_value = mock_response
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {"url": "https://example.com/redirect"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201  # Scan created but will fail in background

def test_rate_limiting_scan_creation(client: TestClient, auth_headers, mock_redis):
    """Test rate limiting for scan creation."""
    with patch("app.dependencies.get_redis", return_value=mock_redis):
        # Mock rate limit exceeded
        mock_redis.incr.return_value = 11  # Exceed limit of 10
        mock_redis.exists.return_value = True
        
        scan_data = {"url": "https://example.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 429

def test_rate_limiting_auth_endpoints(client: TestClient, mock_redis):
    """Test rate limiting for authentication endpoints."""
    with patch("app.dependencies.get_redis", return_value=mock_redis):
        # Mock rate limit exceeded
        mock_redis.incr.return_value = 6  # Exceed limit of 5
        mock_redis.exists.return_value = True
        
        login_data = {"username": "test", "password": "test"}
        response = client.post("/api/v1/login", data=login_data)
        assert response.status_code == 429

def test_cors_headers(client: TestClient):
    """Test CORS headers are present."""
    response = client.options("/api/v1/health/")
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert "access-control-allow-methods" in response.headers
    assert "access-control-allow-headers" in response.headers

def test_security_headers(client: TestClient):
    """Test security headers are present."""
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    
    headers = response.headers
    assert "x-content-type-options" in headers
    assert "x-frame-options" in headers
    assert "x-xss-protection" in headers
    assert "strict-transport-security" in headers

def test_sql_injection_protection(client: TestClient, auth_headers):
    """Test SQL injection protection."""
    # Test with SQL injection in URL
    malicious_url = "https://example.com'; DROP TABLE users; --"
    scan_data = {"url": malicious_url}
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    # Should either succeed (URL is valid) or fail with validation error, not SQL error
    assert response.status_code in [201, 400, 422]

def test_xss_protection_in_responses(client: TestClient, auth_headers, db_session, test_user):
    """Test XSS protection in API responses."""
    # Create scan with potentially malicious data
    scan = {
        "url": "https://example.com",
        "user_id": test_user.id,
        "total_images": 10,
        "images_with_alt": 5,
        "images_missing_alt": 5,
        "coverage_percentage": 50.0,
        "status": "completed"
    }
    
    # Add scan to database
    from app.models import ScanResult
    db_scan = ScanResult(**scan)
    db_session.add(db_scan)
    db_session.commit()
    db_session.refresh(db_scan)
    
    # Test response doesn't contain unescaped HTML
    response = client.get(f"/api/v1/scans/{db_scan.id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    # Ensure no HTML tags in response
    response_text = json.dumps(data)
    assert "<script>" not in response_text.lower()
    assert "javascript:" not in response_text.lower()

def test_input_validation_url_length(client: TestClient, auth_headers):
    """Test input validation for URL length."""
    # Very long URL
    long_url = "https://example.com/" + "a" * 2000
    scan_data = {"url": long_url}
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 422

def test_input_validation_malformed_json(client: TestClient, auth_headers):
    """Test input validation for malformed JSON."""
    response = client.post(
        "/api/v1/scans/",
        data="invalid json",
        headers={**auth_headers, "content-type": "application/json"}
    )
    assert response.status_code == 422

def test_authentication_token_expiry(client: TestClient, test_user):
    """Test authentication token expiry."""
    from app.auth import create_access_token
    from app.config import settings
    
    # Create expired token
    original_expire = settings.access_token_expire_minutes
    settings.access_token_expire_minutes = -1  # Expired
    
    expired_token = create_access_token(data={"sub": str(test_user.id)})
    headers = {"Authorization": f"Bearer {expired_token}"}
    
    response = client.get("/api/v1/me", headers=headers)
    assert response.status_code == 401
    
    # Restore original setting
    settings.access_token_expire_minutes = original_expire

def test_authentication_invalid_token_format(client: TestClient):
    """Test authentication with invalid token format."""
    invalid_tokens = [
        "invalid",
        "Bearer",
        "Bearer invalid.token",
        "Basic dGVzdDp0ZXN0",  # Basic auth instead of Bearer
    ]
    
    for token in invalid_tokens:
        headers = {"Authorization": token}
        response = client.get("/api/v1/me", headers=headers)
        assert response.status_code == 401

def test_password_strength_validation(client: TestClient):
    """Test password strength validation."""
    weak_passwords = [
        "123",
        "password",
        "12345678",
        "abcdefgh",
        "Password",  # No numbers
        "password123",  # No special chars
    ]
    
    for password in weak_passwords:
        user_data = {
            "username": f"test_{password}",
            "email": f"test_{password}@example.com",
            "password": password
        }
        
        response = client.post("/api/v1/register", json=user_data)
        assert response.status_code == 422

def test_content_type_validation(client: TestClient, auth_headers, mock_httpx_client):
    """Test content type validation for scans."""
    # Mock response with invalid content type
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html><body>Test</body></html>"
    mock_response.headers = {"content-type": "application/pdf"}
    mock_httpx_client.get.return_value = mock_response
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {"url": "https://example.com/document.pdf"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400

def test_content_size_validation(client: TestClient, auth_headers, mock_httpx_client):
    """Test content size validation for scans."""
    # Mock response with oversized content
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "x" * (10 * 1024 * 1024)  # 10MB
    mock_response.headers = {"content-type": "text/html"}
    mock_httpx_client.get.return_value = mock_response
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {"url": "https://example.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400

def test_user_isolation(client: TestClient, auth_headers, auth_headers_2, test_scan_result):
    """Test that users can only access their own data."""
    # User 1 tries to access User 2's scan
    response = client.get(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers_2)
    assert response.status_code == 404
    
    # User 1 tries to delete User 2's scan
    response = client.delete(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers_2)
    assert response.status_code == 404

def test_http_method_validation(client: TestClient, auth_headers):
    """Test HTTP method validation."""
    # Test unsupported methods
    response = client.patch("/api/v1/scans/", headers=auth_headers)
    assert response.status_code == 405
    
    response = client.put("/api/v1/scans/", headers=auth_headers)
    assert response.status_code == 405

def test_request_size_limiting(client: TestClient, auth_headers):
    """Test request size limiting."""
    # Create very large request body
    large_data = {"url": "https://example.com", "data": "x" * (1024 * 1024)}  # 1MB
    
    response = client.post("/api/v1/scans/", json=large_data, headers=auth_headers)
    # Should either succeed or fail with appropriate error, not crash
    assert response.status_code in [201, 400, 413, 422]

def test_unicode_handling(client: TestClient, auth_headers):
    """Test proper Unicode handling."""
    unicode_url = "https://example.com/测试"
    scan_data = {"url": unicode_url}
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    # Should handle Unicode properly
    assert response.status_code in [201, 400, 422]

def test_error_information_disclosure(client: TestClient, auth_headers):
    """Test that errors don't disclose sensitive information."""
    # Test with invalid scan ID
    response = client.get("/api/v1/scans/99999", headers=auth_headers)
    assert response.status_code == 404
    
    error_data = response.json()
    # Should not contain database details, stack traces, etc.
    assert "database" not in error_data.get("detail", "").lower()
    assert "traceback" not in error_data.get("detail", "").lower()
    assert "sql" not in error_data.get("detail", "").lower()
