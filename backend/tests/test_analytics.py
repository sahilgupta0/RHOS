from __future__ import annotations

from unittest.mock import AsyncMock, patch

from app.models.analytics import AnalyticsResponse, DashboardStats


def test_get_dashboard_unauthenticated(client):
    """Test get dashboard endpoint without authentication returns 401."""
    response = client.get("/dashboard")
    assert response.status_code == 401


@patch("app.api.analytics.analytics_service.get_dashboard", new_callable=AsyncMock)
def test_get_dashboard_authenticated(mock_get_dashboard, client, auth_header):
    """Test get dashboard endpoint with authentication."""
    mock_stats = {
        "total_patients": 150,
        "patients_today": 5,
        "patients_this_week": 25,
        "high_priority_today": 2,
        "consultations_today": 10,
        "consultations_this_week": 45,
        "follow_ups_pending": 8,
        "referrals_this_month": 3,
    }
    mock_get_dashboard.return_value = DashboardStats(**mock_stats)

    response = client.get("/dashboard", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert data["total_patients"] == 150
    assert data["high_priority_today"] == 2
    mock_get_dashboard.assert_called_once()


def test_get_analytics_unauthenticated(client):
    """Test get analytics endpoint without authentication returns 401."""
    response = client.get("/analytics")
    assert response.status_code == 401


@patch("app.api.analytics.analytics_service.get_analytics", new_callable=AsyncMock)
def test_get_analytics_authenticated(mock_get_analytics, client, auth_header):
    """Test get analytics endpoint with authentication."""
    mock_analytics = {
        "dashboard_stats": {
            "total_patients": 150,
            "patients_today": 5,
            "patients_this_week": 25,
        },
        "disease_distribution": [{"condition": "Hypertension", "count": 45, "percentage": 30.0}],
        "patient_trends": [{"date": "2026-07-19", "count": 10, "high_priority": 1}],
        "village_stats": [
            {
                "village_id": "v001",
                "village_name": "Village A",
                "total_patients": 50,
                "active_cases": 20,
            }
        ],
        "medicine_usage": [
            {
                "medicine_name": "Aspirin",
                "generic_name": "Acetylsalicylic Acid",
                "times_prescribed": 12,
            }
        ],
        "top_symptoms": [{"fever": 25}, {"cough": 18}],
    }
    mock_get_analytics.return_value = AnalyticsResponse(**mock_analytics)

    response = client.get("/analytics?days=30", headers=auth_header)
    assert response.status_code == 200
    data = response.json()
    assert len(data["patient_trends"]) == 1
    assert data["disease_distribution"][0]["condition"] == "Hypertension"
    mock_get_analytics.assert_called_once_with(days=30)
