import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import json

def test_create_scan_success(client: TestClient, auth_headers, mock_httpx_client):
    """Test successful scan creation."""
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201
        
        data = response.json()
        assert data["url"] == scan_data["url"]
        assert data["status"] == "pending"
        assert "id" in data
        assert "created_at" in data

def test_create_scan_invalid_url(client: TestClient, auth_headers):
    """Test scan creation with invalid URL."""
    scan_data = {
        "url": "not-a-valid-url"
    }
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 422

def test_create_scan_ssrf_protection(client: TestClient, auth_headers):
    """Test SSRF protection with private IP."""
    scan_data = {
        "url": "http://192.168.1.1"
    }
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 400
    assert "private" in response.json()["detail"].lower()

def test_create_scan_unauthorized(client: TestClient):
    """Test scan creation without authentication."""
    scan_data = {
        "url": "https://example.com"
    }
    
    response = client.post("/api/v1/scans/", json=scan_data)
    assert response.status_code == 401

def test_get_scans_list(client: TestClient, auth_headers, test_scan_result):
    """Test getting scans list."""
    response = client.get("/api/v1/scans/", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "scans" in data
    assert "total" in data
    assert "page" in data
    assert "per_page" in data
    assert len(data["scans"]) >= 1

def test_get_scans_list_pagination(client: TestClient, auth_headers, db_session, test_user):
    """Test scans list pagination."""
    # Create multiple scans
    for i in range(15):
        scan = {
            "url": f"https://example{i}.com",
            "user_id": test_user.id,
            "total_images": 5,
            "images_with_alt": 3,
            "images_missing_alt": 2,
            "coverage_percentage": 60.0,
            "status": "completed"
        }
        db_session.add(ScanResult(**scan))
    
    db_session.commit()
    
    # Test first page
    response = client.get("/api/v1/scans/?page=1&per_page=10", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["scans"]) == 10
    assert data["page"] == 1
    assert data["per_page"] == 10

def test_get_scan_by_id(client: TestClient, auth_headers, test_scan_result):
    """Test getting scan by ID."""
    response = client.get(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == test_scan_result.id
    assert data["url"] == test_scan_result.url

def test_get_scan_by_id_not_found(client: TestClient, auth_headers):
    """Test getting non-existent scan."""
    response = client.get("/api/v1/scans/99999", headers=auth_headers)
    assert response.status_code == 404

def test_get_scan_by_id_unauthorized(client: TestClient, test_scan_result, auth_headers_2):
    """Test getting scan from different user."""
    response = client.get(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers_2)
    assert response.status_code == 404

def test_get_scan_images(client: TestClient, auth_headers, test_scan_result, test_image_details):
    """Test getting scan images."""
    response = client.get(f"/api/v1/scans/{test_scan_result.id}/images", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "images" in data
    assert "total" in data
    assert len(data["images"]) == 3

def test_get_scan_images_pagination(client: TestClient, auth_headers, test_scan_result, db_session):
    """Test scan images pagination."""
    # Create many image details
    for i in range(25):
        image = ImageDetail(
            scan_id=test_scan_result.id,
            image_url=f"https://example.com/image{i}.jpg",
            alt_text=f"Image {i}",
            has_alt=True,
            is_decorative=False,
            width=100,
            height=100
        )
        db_session.add(image)
    
    db_session.commit()
    
    response = client.get(f"/api/v1/scans/{test_scan_result.id}/images?page=1&per_page=10", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data["images"]) == 10
    assert data["page"] == 1

def test_delete_scan(client: TestClient, auth_headers, test_scan_result):
    """Test deleting scan."""
    response = client.delete(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers)
    assert response.status_code == 204

def test_delete_scan_not_found(client: TestClient, auth_headers):
    """Test deleting non-existent scan."""
    response = client.delete("/api/v1/scans/99999", headers=auth_headers)
    assert response.status_code == 404

def test_delete_scan_unauthorized(client: TestClient, test_scan_result, auth_headers_2):
    """Test deleting scan from different user."""
    response = client.delete(f"/api/v1/scans/{test_scan_result.id}", headers=auth_headers_2)
    assert response.status_code == 404

def test_retry_scan(client: TestClient, auth_headers, test_scan_result, mock_httpx_client):
    """Test retrying scan."""
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        response = client.post(f"/api/v1/scans/{test_scan_result.id}/retry", headers=auth_headers)
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "pending"

def test_retry_scan_not_found(client: TestClient, auth_headers):
    """Test retrying non-existent scan."""
    response = client.post("/api/v1/scans/99999/retry", headers=auth_headers)
    assert response.status_code == 404

def test_scan_rate_limiting(client: TestClient, auth_headers, mock_redis):
    """Test scan rate limiting."""
    with patch("app.dependencies.get_redis", return_value=mock_redis):
        # Mock rate limit exceeded
        mock_redis.incr.return_value = 11  # Exceed limit
        mock_redis.exists.return_value = True
        
        scan_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 429

def test_scan_with_background_task(client: TestClient, auth_headers, mock_httpx_client):
    """Test scan with background task execution."""
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201
        
        # Verify scan was created
        data = response.json()
        scan_id = data["id"]
        
        # Check scan status
        response = client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
        assert response.status_code == 200

def test_scan_invalid_scheme(client: TestClient, auth_headers):
    """Test scan with invalid URL scheme."""
    scan_data = {
        "url": "ftp://example.com"
    }
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 400

def test_scan_localhost_protection(client: TestClient, auth_headers):
    """Test protection against localhost URLs."""
    scan_data = {
        "url": "http://localhost:8080"
    }
    
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 400

def test_scan_private_network_protection(client: TestClient, auth_headers):
    """Test protection against private network URLs."""
    private_urls = [
        "http://10.0.0.1",
        "http://172.16.0.1",
        "http://192.168.0.1",
        "http://127.0.0.1"
    ]
    
    for url in private_urls:
        scan_data = {"url": url}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400

def test_scan_content_type_validation(client: TestClient, auth_headers, mock_httpx_client):
    """Test content type validation."""
    # Mock response with invalid content type
    mock_httpx_client.get.return_value.headers = {"content-type": "application/pdf"}
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {
            "url": "https://example.com/document.pdf"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400

def test_scan_content_size_validation(client: TestClient, auth_headers, mock_httpx_client):
    """Test content size validation."""
    # Mock response with oversized content
    mock_httpx_client.get.return_value.text = "x" * (10 * 1024 * 1024)  # 10MB
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 400

def test_scan_http_error_handling(client: TestClient, auth_headers, mock_httpx_client):
    """Test HTTP error handling."""
    # Mock HTTP error response
    mock_httpx_client.get.return_value.status_code = 404
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value = mock_httpx_client
        
        scan_data = {
            "url": "https://example.com/notfound"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201  # Scan created but will fail in background

def test_scan_timeout_handling(client: TestClient, auth_headers):
    """Test scan timeout handling."""
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        # Mock timeout exception
        mock_client.return_value.__aenter__.return_value.get.side_effect = Exception("Timeout")
        
        scan_data = {
            "url": "https://example.com"
        }
        
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201  # Scan created but will fail in background
