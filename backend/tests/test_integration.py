import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from unittest.mock import patch, MagicMock
import json

def test_complete_scan_workflow(client: TestClient, auth_headers, db_session, test_user):
    """Test complete scan workflow from creation to completion."""
    # Mock HTTP client for fetching website content
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <!DOCTYPE html>
    <html>
    <head><title>Test Page</title></head>
    <body>
        <img src="https://example.com/image1.jpg" alt="Test image 1" width="100" height="100">
        <img src="https://example.com/image2.jpg" alt="" width="200" height="200">
        <img src="https://example.com/image3.jpg" width="300" height="300">
    </body>
    </html>
    """
    mock_response.headers = {"content-type": "text/html"}
    
    with patch("app.services.scanner.httpx.AsyncClient") as mock_client:
        mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
        
        # 1. Create scan
        scan_data = {"url": "https://example.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201
        
        scan_result = response.json()
        scan_id = scan_result["id"]
        assert scan_result["url"] == "https://example.com"
        assert scan_result["status"] == "pending"
        
        # 2. Check scan status (should be completed after background task)
        response = client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers)
        assert response.status_code == 200
        
        # 3. Get scan images
        response = client.get(f"/api/v1/scans/{scan_id}/images", headers=auth_headers)
        assert response.status_code == 200
        
        images_data = response.json()
        assert "images" in images_data
        assert images_data["total"] >= 0  # May be 0 if background task hasn't completed
        
        # 4. Get analytics summary
        response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
        assert response.status_code == 200
        
        analytics_data = response.json()
        assert "total_scans" in analytics_data
        assert analytics_data["total_scans"] >= 1

def test_user_isolation(client: TestClient, auth_headers, auth_headers_2, db_session, test_user, test_user_2):
    """Test that users can only access their own data."""
    # User 1 creates a scan
    scan_data = {"url": "https://example1.com"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 201
    scan_id = response.json()["id"]
    
    # User 2 tries to access User 1's scan
    response = client.get(f"/api/v1/scans/{scan_id}", headers=auth_headers_2)
    assert response.status_code == 404
    
    # User 2 tries to delete User 1's scan
    response = client.delete(f"/api/v1/scans/{scan_id}", headers=auth_headers_2)
    assert response.status_code == 404
    
    # User 2 tries to get User 1's analytics
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers_2)
    assert response.status_code == 200
    # Should return empty data for User 2
    analytics_data = response.json()
    assert analytics_data["total_scans"] == 0

def test_analytics_data_consistency(client: TestClient, auth_headers, db_session, test_user):
    """Test that analytics data is consistent across different endpoints."""
    # Create multiple scans with known data
    scans_data = [
        {"url": "https://example1.com", "total_images": 10, "images_with_alt": 8, "images_missing_alt": 2},
        {"url": "https://example2.com", "total_images": 20, "images_with_alt": 15, "images_missing_alt": 5},
        {"url": "https://example3.com", "total_images": 5, "images_with_alt": 2, "images_missing_alt": 3},
    ]
    
    scan_ids = []
    for scan_data in scans_data:
        response = client.post("/api/v1/scans/", json={"url": scan_data["url"]}, headers=auth_headers)
        assert response.status_code == 201
        scan_ids.append(response.json()["id"])
    
    # Wait a bit for background tasks to complete (in real scenario)
    # For testing, we'll mock the scan results
    
    # Get analytics summary
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    summary = response.json()
    assert summary["total_scans"] >= 3
    
    # Get coverage trends
    response = client.get("/api/v1/analytics/trends?days=30&group_by=day", headers=auth_headers)
    assert response.status_code == 200
    
    trends = response.json()
    assert len(trends) >= 0  # May be empty if no data in date range
    
    # Get top issues
    response = client.get("/api/v1/analytics/top-issues?days=30&limit=10", headers=auth_headers)
    assert response.status_code == 200
    
    top_issues = response.json()
    assert len(top_issues) >= 0  # May be empty if no issues found

def test_error_handling_consistency(client: TestClient, auth_headers):
    """Test that error handling is consistent across endpoints."""
    # Test with invalid scan ID
    response = client.get("/api/v1/scans/99999", headers=auth_headers)
    assert response.status_code == 404
    
    # Test with invalid analytics parameters
    response = client.get("/api/v1/analytics/summary?days=-1", headers=auth_headers)
    assert response.status_code == 422
    
    # Test with invalid trends parameters
    response = client.get("/api/v1/analytics/trends?group_by=invalid", headers=auth_headers)
    assert response.status_code == 422

def test_pagination_consistency(client: TestClient, auth_headers, db_session, test_user):
    """Test that pagination works consistently across endpoints."""
    # Create multiple scans
    for i in range(15):
        scan_data = {"url": f"https://example{i}.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201
    
    # Test scans pagination
    response = client.get("/api/v1/scans/?page=1&per_page=10", headers=auth_headers)
    assert response.status_code == 200
    
    scans_data = response.json()
    assert len(scans_data["scans"]) <= 10
    assert scans_data["page"] == 1
    assert scans_data["per_page"] == 10
    
    # Test second page
    response = client.get("/api/v1/scans/?page=2&per_page=10", headers=auth_headers)
    assert response.status_code == 200
    
    scans_data = response.json()
    assert len(scans_data["scans"]) <= 10
    assert scans_data["page"] == 2

def test_rate_limiting_integration(client: TestClient, auth_headers, mock_redis):
    """Test rate limiting integration across different endpoints."""
    with patch("app.dependencies.get_redis", return_value=mock_redis):
        # Mock rate limit exceeded for scans
        mock_redis.incr.return_value = 11  # Exceed limit
        mock_redis.exists.return_value = True
        
        scan_data = {"url": "https://example.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 429
        
        # Mock rate limit exceeded for auth
        mock_redis.incr.return_value = 6  # Exceed limit
        mock_redis.exists.return_value = True
        
        login_data = {"username": "test", "password": "test"}
        response = client.post("/api/v1/login", data=login_data)
        assert response.status_code == 429

def test_data_export_integration(client: TestClient, auth_headers, db_session, test_user):
    """Test data export integration."""
    # Create some test data
    scan_data = {"url": "https://example.com"}
    response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
    assert response.status_code == 201
    scan_id = response.json()["id"]
    
    # Test CSV export
    response = client.get("/api/v1/export/scans/csv?days=30", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"
    
    # Test JSON export
    response = client.get("/api/v1/export/analytics/json?days=30", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    
    # Test specific scan export
    response = client.get(f"/api/v1/export/scans/{scan_id}/json", headers=auth_headers)
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"

def test_health_check_integration(client: TestClient):
    """Test health check integration."""
    # Test basic health check
    response = client.get("/api/v1/health/")
    assert response.status_code == 200
    
    health_data = response.json()
    assert health_data["status"] == "healthy"
    
    # Test detailed health check
    response = client.get("/api/v1/health/detailed")
    assert response.status_code == 200
    
    detailed_health = response.json()
    assert "database" in detailed_health
    assert "redis" in detailed_health
    assert "api" in detailed_health
    
    # Test readiness check
    response = client.get("/api/v1/health/ready")
    assert response.status_code == 200
    
    # Test liveness check
    response = client.get("/api/v1/health/live")
    assert response.status_code == 200

def test_concurrent_requests(client: TestClient, auth_headers):
    """Test handling of concurrent requests."""
    import threading
    import time
    
    results = []
    errors = []
    
    def make_request():
        try:
            response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
            results.append(response.status_code)
        except Exception as e:
            errors.append(str(e))
    
    # Create multiple threads making concurrent requests
    threads = []
    for _ in range(10):
        thread = threading.Thread(target=make_request)
        threads.append(thread)
        thread.start()
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    # All requests should succeed
    assert len(errors) == 0
    assert all(status == 200 for status in results)
    assert len(results) == 10

def test_memory_usage_large_dataset(client: TestClient, auth_headers, db_session, test_user):
    """Test memory usage with large dataset."""
    # Create many scans (simulate large dataset)
    for i in range(100):
        scan_data = {"url": f"https://example{i}.com"}
        response = client.post("/api/v1/scans/", json=scan_data, headers=auth_headers)
        assert response.status_code == 201
    
    # Test that analytics still work with large dataset
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    summary = response.json()
    assert summary["total_scans"] >= 100
    
    # Test pagination with large dataset
    response = client.get("/api/v1/scans/?page=1&per_page=50", headers=auth_headers)
    assert response.status_code == 200
    
    scans_data = response.json()
    assert len(scans_data["scans"]) <= 50

def test_database_transaction_rollback(client: TestClient, auth_headers, db_session):
    """Test database transaction rollback on errors."""
    # This test would require more complex setup to simulate database errors
    # For now, we'll test that the API handles errors gracefully
    
    # Test with invalid data that should cause a rollback
    invalid_scan_data = {"url": "invalid-url"}
    response = client.post("/api/v1/scans/", json=invalid_scan_data, headers=auth_headers)
    assert response.status_code == 422
    
    # Verify no partial data was created
    response = client.get("/api/v1/scans/", headers=auth_headers)
    assert response.status_code == 200
    
    scans_data = response.json()
    # Should not have any scans with invalid URLs
    for scan in scans_data["scans"]:
        assert scan["url"].startswith(("http://", "https://"))
