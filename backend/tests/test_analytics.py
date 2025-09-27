import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.models import User, ScanResult, ImageDetail

def test_analytics_summary(client: TestClient, auth_headers, db_session, test_user):
    """Test analytics summary endpoint."""
    # Create test data
    now = datetime.utcnow()
    
    # Create scans for different time periods
    scans = [
        ScanResult(
            url="https://example1.com",
            user_id=test_user.id,
            total_images=10,
            images_with_alt=8,
            images_missing_alt=2,
            coverage_percentage=80.0,
            status="completed",
            created_at=now - timedelta(days=1)
        ),
        ScanResult(
            url="https://example2.com",
            user_id=test_user.id,
            total_images=20,
            images_with_alt=15,
            images_missing_alt=5,
            coverage_percentage=75.0,
            status="completed",
            created_at=now - timedelta(days=2)
        ),
        ScanResult(
            url="https://example3.com",
            user_id=test_user.id,
            total_images=5,
            images_with_alt=2,
            images_missing_alt=3,
            coverage_percentage=40.0,
            status="completed",
            created_at=now - timedelta(days=3)
        )
    ]
    
    for scan in scans:
        db_session.add(scan)
    
    db_session.commit()
    
    # Test analytics summary
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_scans"] == 3
    assert data["total_images_scanned"] == 35
    assert data["total_images_with_alt"] == 25
    assert data["total_images_missing_alt"] == 10
    assert data["average_coverage_percentage"] == 65.0
    assert len(data["most_common_issues"]) > 0

def test_analytics_summary_no_data(client: TestClient, auth_headers):
    """Test analytics summary with no data."""
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_scans"] == 0
    assert data["total_images_scanned"] == 0
    assert data["average_coverage_percentage"] == 0.0

def test_analytics_summary_different_user(client: TestClient, auth_headers_2, db_session, test_user_2):
    """Test analytics summary for different user."""
    # Create scan for different user
    scan = ScanResult(
        url="https://example.com",
        user_id=test_user_2.id,
        total_images=10,
        images_with_alt=5,
        images_missing_alt=5,
        coverage_percentage=50.0,
        status="completed"
    )
    
    db_session.add(scan)
    db_session.commit()
    
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers_2)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_scans"] == 1
    assert data["total_images_scanned"] == 10

def test_coverage_trends_daily(client: TestClient, auth_headers, db_session, test_user):
    """Test coverage trends with daily grouping."""
    now = datetime.utcnow()
    
    # Create scans for different days
    for i in range(5):
        scan = ScanResult(
            url=f"https://example{i}.com",
            user_id=test_user.id,
            total_images=10,
            images_with_alt=8,
            images_missing_alt=2,
            coverage_percentage=80.0,
            status="completed",
            created_at=now - timedelta(days=i)
        )
        db_session.add(scan)
    
    db_session.commit()
    
    response = client.get("/api/v1/analytics/trends?days=7&group_by=day", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    assert "period" in data[0]
    assert "coverage_percentage" in data[0]
    assert "total_images" in data[0]

def test_coverage_trends_weekly(client: TestClient, auth_headers, db_session, test_user):
    """Test coverage trends with weekly grouping."""
    now = datetime.utcnow()
    
    # Create scans for different weeks
    for i in range(3):
        scan = ScanResult(
            url=f"https://example{i}.com",
            user_id=test_user.id,
            total_images=10,
            images_with_alt=8,
            images_missing_alt=2,
            coverage_percentage=80.0,
            status="completed",
            created_at=now - timedelta(weeks=i)
        )
        db_session.add(scan)
    
    db_session.commit()
    
    response = client.get("/api/v1/analytics/trends?days=30&group_by=week", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0

def test_coverage_trends_monthly(client: TestClient, auth_headers, db_session, test_user):
    """Test coverage trends with monthly grouping."""
    now = datetime.utcnow()
    
    # Create scans for different months
    for i in range(3):
        scan = ScanResult(
            url=f"https://example{i}.com",
            user_id=test_user.id,
            total_images=10,
            images_with_alt=8,
            images_missing_alt=2,
            coverage_percentage=80.0,
            status="completed",
            created_at=now - timedelta(days=i*30)
        )
        db_session.add(scan)
    
    db_session.commit()
    
    response = client.get("/api/v1/analytics/trends?days=90&group_by=month", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0

def test_top_issues(client: TestClient, auth_headers, db_session, test_user):
    """Test top issues endpoint."""
    now = datetime.utcnow()
    
    # Create scans with different issues
    scans = [
        ScanResult(
            url="https://example1.com",
            user_id=test_user.id,
            total_images=10,
            images_with_alt=5,
            images_missing_alt=5,
            coverage_percentage=50.0,
            status="completed",
            created_at=now - timedelta(days=1)
        ),
        ScanResult(
            url="https://example2.com",
            user_id=test_user.id,
            total_images=20,
            images_with_alt=10,
            images_missing_alt=10,
            coverage_percentage=50.0,
            status="completed",
            created_at=now - timedelta(days=2)
        )
    ]
    
    for scan in scans:
        db_session.add(scan)
    
    db_session.commit()
    
    response = client.get("/api/v1/analytics/top-issues?days=30&limit=10", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0
    assert "issue" in data[0]
    assert "count" in data[0]
    assert "severity" in data[0]


def test_analytics_unauthorized(client: TestClient):
    """Test analytics endpoints without authentication."""
    endpoints = [
        "/api/v1/analytics/summary",
        "/api/v1/analytics/trends",
        "/api/v1/analytics/top-issues",
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 401

def test_analytics_invalid_parameters(client: TestClient, auth_headers):
    """Test analytics endpoints with invalid parameters."""
    # Test invalid days parameter
    response = client.get("/api/v1/analytics/summary?days=-1", headers=auth_headers)
    assert response.status_code == 422
    
    # Test invalid group_by parameter
    response = client.get("/api/v1/analytics/trends?group_by=invalid", headers=auth_headers)
    assert response.status_code == 422
    
    # Test invalid limit parameter
    response = client.get("/api/v1/analytics/top-issues?limit=-1", headers=auth_headers)
    assert response.status_code == 422

def test_analytics_date_range_filtering(client: TestClient, auth_headers, db_session, test_user):
    """Test analytics with date range filtering."""
    now = datetime.utcnow()
    
    # Create old scan (outside range)
    old_scan = ScanResult(
        url="https://old.com",
        user_id=test_user.id,
        total_images=10,
        images_with_alt=5,
        images_missing_alt=5,
        coverage_percentage=50.0,
        status="completed",
        created_at=now - timedelta(days=60)  # Outside 30-day range
    )
    
    # Create recent scan (within range)
    recent_scan = ScanResult(
        url="https://recent.com",
        user_id=test_user.id,
        total_images=10,
        images_with_alt=8,
        images_missing_alt=2,
        coverage_percentage=80.0,
        status="completed",
        created_at=now - timedelta(days=5)  # Within 30-day range
    )
    
    db_session.add(old_scan)
    db_session.add(recent_scan)
    db_session.commit()
    
    # Test with 30-day range
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_scans"] == 1  # Only recent scan
    assert data["total_images_scanned"] == 10

def test_analytics_performance_large_dataset(client: TestClient, auth_headers, db_session, test_user):
    """Test analytics performance with large dataset."""
    now = datetime.utcnow()
    
    # Create many scans
    for i in range(100):
        scan = ScanResult(
            url=f"https://example{i}.com",
            user_id=test_user.id,
            total_images=10,
            images_with_alt=8,
            images_missing_alt=2,
            coverage_percentage=80.0,
            status="completed",
            created_at=now - timedelta(days=i % 30)
        )
        db_session.add(scan)
    
    db_session.commit()
    
    # Test analytics performance
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_scans"] == 100

def test_analytics_edge_cases(client: TestClient, auth_headers, db_session, test_user):
    """Test analytics edge cases."""
    now = datetime.utcnow()
    
    # Test with scan having 0 images
    zero_images_scan = ScanResult(
        url="https://zero.com",
        user_id=test_user.id,
        total_images=0,
        images_with_alt=0,
        images_missing_alt=0,
        coverage_percentage=0.0,
        status="completed",
        created_at=now
    )
    
    # Test with scan having 100% coverage
    perfect_scan = ScanResult(
        url="https://perfect.com",
        user_id=test_user.id,
        total_images=10,
        images_with_alt=10,
        images_missing_alt=0,
        coverage_percentage=100.0,
        status="completed",
        created_at=now
    )
    
    db_session.add(zero_images_scan)
    db_session.add(perfect_scan)
    db_session.commit()
    
    response = client.get("/api/v1/analytics/summary?days=30", headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert data["total_scans"] == 2
    assert data["average_coverage_percentage"] == 50.0  # (0 + 100) / 2
