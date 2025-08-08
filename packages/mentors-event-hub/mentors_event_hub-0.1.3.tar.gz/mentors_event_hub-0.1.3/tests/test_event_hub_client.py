import pytest
from unittest.mock import Mock, patch
from mentors_event_hub.event_hub_client import EventHubClient
from mentors_event_hub.repository.event_repository import EventRepository


class MockRepository(EventRepository):
    def __init__(self):
        self.events = []
    
    def event_handler(self, **kwargs):
        payload = self.build_payload(**kwargs)
        self.events.append(payload)


class TestEventHubClient:
    
    def test_init(self):
        repo = MockRepository()
        client = EventHubClient("test-project", "web", repo)
        
        assert client.project == "test-project"
        assert client.layer == "web"
        assert client.repository == repo
    
    @patch.dict('os.environ', {'AZURE_SERVICE_BUS_CONNECTION_STRING': 'test-connection'})
    @patch('mentors_event_hub.event_hub_client.AzureServiceBusRepository')
    def test_create_azure_client(self, mock_azure_repo):
        client = EventHubClient.create_azure_client("test-project", "api")
        
        assert client.project == "test-project"
        assert client.layer == "api"
        mock_azure_repo.assert_called_once_with('test-connection', 'events')
    
    def test_create_azure_client_no_connection_string(self):
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Azure Service Bus connection string é obrigatória"):
                EventHubClient.create_azure_client("test-project")
    
    def test_send_event(self):
        repo = MockRepository()
        client = EventHubClient("test-project", "web", repo)
        
        client.send_event(
            event_type="TEST_EVENT",
            message="Test message",
            object="test_object",
            tags=["test"]
        )
        
        assert len(repo.events) == 1
        event = repo.events[0]
        assert event["project"] == "test-project"
        assert event["layer"] == "web"
        assert event["event_type"] == "TEST_EVENT"
        assert event["message"] == "Test message"
        assert event["object"] == "test_object"
        assert event["tags"] == ["test"]
    
    def test_send_error(self):
        repo = MockRepository()
        client = EventHubClient("test-project", "service", repo)
        
        try:
            1 / 0
        except Exception as e:
            client.send_error(e, context="test_context", user_id=123)
        
        assert len(repo.events) == 1
        event = repo.events[0]
        assert event["event_type"] == "ERROR"
        assert event["message"] == "division by zero"
        assert event["object"] == "test_context"
        assert "ZeroDivisionError" in event["tags"]
        assert "Traceback" in event["obs"]
    
    def test_capture_errors_decorator(self):
        repo = MockRepository()
        client = EventHubClient("test-project", "web", repo)
        
        @client.capture_errors("test_function")
        def failing_function():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError):
            failing_function()
        
        assert len(repo.events) == 1
        event = repo.events[0]
        assert event["event_type"] == "ERROR"
        assert event["message"] == "Test error"
        assert "ValueError" in event["tags"]