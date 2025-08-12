#!/usr/bin/env python3
import asyncio
import pytest
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from src.context_querier import ContextQuerier, QueryResult, create_context_querier
from src.context_integrator import ContextIntegrator, ContextUpdate, ContextState
import json

class TestContextQuerier:
    
    @pytest.fixture
    def mock_context_integrator(self):
        """Create a mock ContextIntegrator for testing"""
        integrator = AsyncMock(spec=ContextIntegrator)
        
        # Mock context state
        integrator.get_current_context = AsyncMock(return_value=(
            "Screen Recording Session: Test Session\n"
            "Session started: 2024-01-15 10:00:00\n"
            "User is working on a coding project, editing Python files and running tests. "
            "Multiple browser tabs are open with documentation. The session has been "
            "focused on implementing async functionality."
        ))
        
        integrator.get_current_speakers = AsyncMock(return_value={
            "SPEAKER_1": "Developer",
            "SPEAKER_2": "AI Assistant"
        })
        
        # Mock context status
        integrator.get_context_status = AsyncMock(return_value={
            'is_running': True,
            'last_update_time': time.time(),
            'total_clips_processed': 5,
            'current_context_length': 500
        })
        
        # Mock recent updates
        sample_updates = [
            ContextUpdate(
                clip_path="/tmp/clip1.mov",
                start_time=10.0,
                end_time=15.0,
                summary="Developer opened VS Code and started editing main.py file",
                updated_context="Updated context...",
                speakers={"SPEAKER_1": "Developer"},
                processing_time=0.5,
                priority=(0, 1, 0, 0)
            ),
            ContextUpdate(
                clip_path="/tmp/clip2.mov",
                start_time=15.0,
                end_time=20.0,
                summary="Developer ran pytest command to execute unit tests",
                updated_context="Updated context...",
                speakers={"SPEAKER_1": "Developer"},
                processing_time=0.3,
                priority=(0, 2, 0, 0)
            ),
            ContextUpdate(
                clip_path="/tmp/clip3.mov",
                start_time=20.0,
                end_time=25.0,
                summary="AI Assistant provided feedback on code structure and suggested improvements",
                updated_context="Updated context...",
                speakers={"SPEAKER_2": "AI Assistant"},
                processing_time=0.7,
                priority=(0, 3, 0, 0)
            )
        ]
        
        integrator.get_recent_updates = AsyncMock(return_value=sample_updates)
        integrator.set_callback = Mock()  # Mock callback setter
        
        return integrator
    
    @pytest.fixture
    def mock_openai_response(self):
        """Create a mock OpenAI response"""
        return {
            "answer": "The developer is currently working on implementing async functionality in Python. They have been editing main.py and running tests to verify the implementation.",
            "speakers_referenced": ["SPEAKER_1"],
            "confidence": 0.9,
            "context_used": "Recent coding activity and test execution"
        }
    
    @pytest.fixture
    def context_querier(self):
        """Create a ContextQuerier instance for testing"""
        with patch('src.context_querier.AsyncOpenAI') as mock_openai:
            mock_client = AsyncMock()
            mock_openai.return_value = mock_client
            return ContextQuerier(
                openai_api_key="test-key",
                query_interval_seconds=1.0  # Short interval for testing
            )
    
    def test_context_querier_creation(self):
        """Test that ContextQuerier can be created successfully"""
        with patch('src.context_querier.AsyncOpenAI') as mock_openai:
            querier = ContextQuerier(openai_api_key="test-key")
            assert querier is not None
            assert querier.query_task is None  # No task until start is called
            assert querier.model == "gpt-4o-mini"
            assert querier.is_running == False
            assert querier.total_queries == 0
            mock_openai.assert_called_once_with(api_key="test-key")
    
    def test_factory_function(self):
        """Test the create_context_querier factory function"""
        with patch('src.context_querier.AsyncOpenAI'):
            querier = create_context_querier(
                openai_api_key="test-key", 
                model="gpt-4",
                query_interval_seconds=60.0
            )
            assert querier is not None
            assert querier.query_task is None  # No task until start is called
            assert querier.model == "gpt-4"
            assert querier.query_interval_seconds == 60.0
    
    @pytest.mark.asyncio
    async def test_start_stop_querier(self, context_querier, mock_context_integrator):
        """Test starting and stopping the querier with a query task"""
        assert context_querier.is_running == False
        assert context_querier.query_task is None
        
        # Start querier with a task
        query_task = "What is the developer working on?"
        await context_querier.start_querier(mock_context_integrator, query_task)
        assert context_querier.is_running == True
        assert context_querier.query_task == query_task
        assert context_querier.context_integrator == mock_context_integrator
        
        # Verify callback was set (no longer uses monitoring_task)
        mock_context_integrator.set_callback.assert_called_once_with(context_querier._on_context_update)
        
        # Wait a moment for callback setup
        await asyncio.sleep(0.1)
        
        # Stop querier
        await context_querier.stop_querier()
        assert context_querier.is_running == False
    
    @pytest.mark.asyncio
    async def test_start_querier_twice(self, context_querier, mock_context_integrator):
        """Test that starting querier twice doesn't cause issues"""
        await context_querier.start_querier(mock_context_integrator, "Test task")
        
        # Try to start again - should return early and not cause issues
        await context_querier.start_querier(mock_context_integrator, "Different task")
        
        # Should still be running with the original task
        assert context_querier.is_running == True
        assert context_querier.query_task == "Test task"  # Should keep original task
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_context_update_callback(self, context_querier, mock_context_integrator, mock_openai_response):
        """Test that context update callbacks work correctly"""
        await context_querier.start_querier(mock_context_integrator, "What is happening?")
        
        # Mock OpenAI response
        with patch.object(context_querier, '_call_openai_for_query', return_value=mock_openai_response):
            # Create a test context update
            test_update = ContextUpdate(
                clip_path="/tmp/test.mov",
                start_time=25.0,
                end_time=30.0,
                summary="User opened a new file",
                updated_context="Updated context...",
                speakers={"SPEAKER_1": "Developer"},
                processing_time=0.4,
                priority=(0, 4, 0, 0)
            )
            
            # Simulate callback being called
            await context_querier._on_context_update(test_update)
            
            # Should have run a query
            latest_result = await context_querier.get_latest_result()
            assert latest_result is not None
            assert latest_result.answer == mock_openai_response["answer"]
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_context_update_respects_interval(self, context_querier, mock_context_integrator):
        """Test that context updates respect query interval"""
        context_querier.query_interval_seconds = 10.0  # Long interval
        await context_querier.start_querier(mock_context_integrator, "What is happening?")
        
        # Set recent query time
        context_querier.last_query_time = time.time()
        
        # Create a test context update
        test_update = ContextUpdate(
            clip_path="/tmp/test.mov",
            start_time=25.0,
            end_time=30.0,
            summary="User opened a new file",
            updated_context="Updated context...",
            speakers={"SPEAKER_1": "Developer"},
            processing_time=0.4,
            priority=(0, 4, 0, 0)
        )
        
        # Mock _run_query to track calls
        run_query_called = False
        original_run_query = context_querier._run_query
        
        async def mock_run_query(*args, **kwargs):
            nonlocal run_query_called
            run_query_called = True
            return await original_run_query(*args, **kwargs)
        
        with patch.object(context_querier, '_run_query', side_effect=mock_run_query):
            # Simulate callback being called
            await context_querier._on_context_update(test_update)
            
            # Should not have run query due to interval
            assert not run_query_called
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_force_query(self, context_querier, mock_context_integrator, mock_openai_response):
        """Test forcing a query to run immediately"""
        query_task = "What is the developer working on?"
        await context_querier.start_querier(mock_context_integrator, query_task)
        
        with patch.object(context_querier, '_call_openai_for_query', return_value=mock_openai_response):
            result = await context_querier.force_query()
            
            # Verify result
            assert isinstance(result, QueryResult)
            assert result.query_task == query_task
            assert result.answer == mock_openai_response["answer"]
            assert result.confidence == 0.9
            assert result.error is None
            assert result.context_length > 0
            assert result.clips_processed == 5
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_force_query_without_integrator(self, context_querier):
        """Test that force_query fails without context integrator"""
        with pytest.raises(ValueError, match="No context integrator attached"):
            await context_querier.force_query()
    
    @pytest.mark.asyncio
    async def test_force_query_without_task(self, context_querier, mock_context_integrator):
        """Test that force_query fails without query task"""
        context_querier.context_integrator = mock_context_integrator
        with pytest.raises(ValueError, match="No query task set"):
            await context_querier.force_query()
    
    @pytest.mark.asyncio
    async def test_run_query_with_openai_error(self, context_querier, mock_context_integrator):
        """Test running query when OpenAI fails"""
        await context_querier.start_querier(mock_context_integrator, "Test task")
        
        # Mock OpenAI to return None (failure)
        with patch.object(context_querier, '_call_openai_for_query', return_value=None):
            await context_querier._run_query()
            
            # Check that an error result was stored
            latest_result = await context_querier.get_latest_result()
            assert latest_result is not None
            assert latest_result.answer == ""
            assert latest_result.error == "Failed to get response from OpenAI"
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_run_query_with_exception(self, context_querier, mock_context_integrator):
        """Test running query when exception occurs"""
        await context_querier.start_querier(mock_context_integrator, "Test task")
        
        # Mock context integrator to raise exception
        mock_context_integrator.get_current_context.side_effect = Exception("Test error")
        
        await context_querier._run_query()
        
        # Check that an error result was stored
        latest_result = await context_querier.get_latest_result()
        assert latest_result is not None
        assert latest_result.answer == ""
        assert latest_result.error == "Test error"
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_query_results_tracking(self, context_querier, mock_context_integrator, mock_openai_response):
        """Test that query results are tracked correctly"""
        await context_querier.start_querier(mock_context_integrator, "What is happening?")
        
        # Initially no results
        latest = await context_querier.get_latest_result()
        assert latest is None
        
        history = await context_querier.get_query_history()
        assert len(history) == 0
        
        # Run a few queries
        with patch.object(context_querier, '_call_openai_for_query', return_value=mock_openai_response):
            for i in range(3):
                await context_querier._run_query()
        
        # Check results
        latest = await context_querier.get_latest_result()
        assert latest is not None
        assert latest.query_task == "What is happening?"
        
        history = await context_querier.get_query_history()
        assert len(history) == 3
        
        # Test limited history
        limited_history = await context_querier.get_query_history(limit=2)
        assert len(limited_history) == 2
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_get_querier_stats(self, context_querier, mock_context_integrator, mock_openai_response):
        """Test getting querier statistics"""
        query_task = "What is the developer working on?"
        await context_querier.start_querier(mock_context_integrator, query_task)
        
        # Initial stats
        stats = await context_querier.get_querier_stats()
        assert stats['query_task'] == query_task
        assert stats['is_running'] == True
        assert stats['total_queries'] == 0
        assert stats['latest_answer_preview'] == "No results yet"
        
        # Run some queries
        with patch.object(context_querier, '_call_openai_for_query', return_value=mock_openai_response):
            await context_querier._run_query()
            await context_querier._run_query()
        
        # Check updated stats
        stats = await context_querier.get_querier_stats()
        assert stats['total_queries'] == 2
        assert stats['results_stored'] == 2
        assert stats['average_processing_time'] > 0
        assert stats['latest_confidence'] == 0.9
        assert "async functionality" in stats['latest_answer_preview']
        
        await context_querier.stop_querier()
    
    def test_format_recent_updates(self, context_querier):
        """Test formatting of recent updates for prompts"""
        updates = [
            ContextUpdate(
                clip_path="/tmp/clip1.mov",
                start_time=10.0,
                end_time=15.0,
                summary="Developer opened VS Code",
                updated_context="",
                speakers={},
                processing_time=0.5,
                priority=(0, 1, 0, 0)
            ),
            ContextUpdate(
                clip_path="/tmp/clip2.mov",
                start_time=15.0,
                end_time=20.0,
                summary="Developer ran tests",
                updated_context="",
                speakers={},
                processing_time=0.3,
                priority=(0, 2, 0, 0),
                error="Some error"  # This should be skipped
            ),
            ContextUpdate(
                clip_path="/tmp/clip3.mov",
                start_time=20.0,
                end_time=25.0,
                summary="AI provided feedback",
                updated_context="",
                speakers={},
                processing_time=0.7,
                priority=(0, 3, 0, 0)
            )
        ]
        
        formatted = context_querier._format_recent_updates(updates)
        lines = formatted.split('\n')
        
        # Should have 2 lines (error update skipped)
        assert len(lines) == 2
        assert "[10.0s - 15.0s] Developer opened VS Code" in lines[0]
        assert "[20.0s - 25.0s] AI provided feedback" in lines[1]
        
        # Test empty updates
        empty_formatted = context_querier._format_recent_updates([])
        assert empty_formatted == "No recent activity."
    
    @pytest.mark.asyncio
    async def test_call_openai_for_query_success(self, context_querier):
        """Test successful OpenAI API call"""
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "answer": "Test answer",
            "speakers_referenced": ["SPEAKER_1"],
            "confidence": 0.9,
            "context_used": "Test context"
        })
        
        with patch.object(context_querier.openai_client.chat.completions, 'create', new_callable=AsyncMock, return_value=mock_response):
            result = await context_querier._call_openai_for_query("Test prompt")
            
            assert result is not None
            assert result["answer"] == "Test answer"
            assert result["confidence"] == 0.9
    
    @pytest.mark.asyncio
    async def test_call_openai_for_query_failure(self, context_querier):
        """Test OpenAI API call failure"""
        with patch.object(context_querier.openai_client.chat.completions, 'create', new_callable=AsyncMock, side_effect=Exception("API Error")):
            result = await context_querier._call_openai_for_query("Test prompt")
            assert result is None
    
    @pytest.mark.asyncio
    async def test_template_includes_query_task(self, context_querier, mock_context_integrator):
        """Test that the template properly includes the query task"""
        query_task = "What is the developer working on?"
        await context_querier.start_querier(mock_context_integrator, query_task)
        
        # Mock OpenAI call to capture the prompt
        captured_prompt = None
        
        async def mock_openai_call(prompt):
            nonlocal captured_prompt
            captured_prompt = prompt
            return {
                "answer": "Test answer",
                "speakers_referenced": [],
                "confidence": 0.8,
                "context_used": "Test context"
            }
        
        with patch.object(context_querier, '_call_openai_for_query', side_effect=mock_openai_call):
            await context_querier._run_query()
            
            # Verify the query task was included in the prompt
            assert captured_prompt is not None
            assert query_task in captured_prompt
            assert "Query Task:" in captured_prompt
        
        await context_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_different_query_tasks(self, mock_context_integrator):
        """Test that different query tasks work correctly"""
        tasks = [
            "What programming languages are being used?",
            "Are there any errors in the code?",
            "How long has this session been running?",
            "What files are being edited?"
        ]
        
        mock_response = {
            "answer": "Test answer",
            "speakers_referenced": [],
            "confidence": 0.8,
            "context_used": "Test context"
        }
        
        for task in tasks:
            with patch('src.context_querier.AsyncOpenAI') as mock_openai_class:
                mock_client = AsyncMock()
                mock_openai_class.return_value = mock_client
                
                querier = ContextQuerier(openai_api_key="test-key")
                await querier.start_querier(mock_context_integrator, task)
                
                with patch.object(querier, '_call_openai_for_query', return_value=mock_response):
                    result = await querier.force_query()
                    
                    # Verify each task works
                    assert result.query_task == task
                    assert result.answer == "Test answer"
                    assert result.error is None
                
                await querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_integration_with_context_integrator(self):
        """Test integration with a real ContextIntegrator instance"""
        # Create real instances
        with patch('src.context_querier.AsyncOpenAI') as mock_openai_class:
            mock_client = AsyncMock()
            mock_openai_class.return_value = mock_client
            querier = ContextQuerier(
                openai_api_key="test-key",
                query_interval_seconds=1.0
            )
            
        with patch('src.context_integrator.AsyncOpenAI') as mock_openai_class:
            mock_client = AsyncMock()
            mock_openai_class.return_value = mock_client
            integrator = ContextIntegrator(openai_api_key="test-key", session_title="Test Session")
        
        # Mock OpenAI response for querier
        mock_response = {
            "answer": "This is a test session that just started",
            "speakers_referenced": ["UNKNOWN"],
            "confidence": 0.8,
            "context_used": "Initial context state"
        }
        
        with patch.object(querier, '_call_openai_for_query', return_value=mock_response):
            # Start querier monitoring the integrator
            await querier.start_querier(integrator, "What is happening in this session?")
            
            # Force a query
            result = await querier.force_query()
            
            # Verify the integration works
            assert result.answer == mock_response["answer"]
            assert result.error is None
            assert result.context_length > 0
            
            # Stop querier
            await querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_query_deque_max_size(self, context_querier, mock_context_integrator, mock_openai_response):
        """Test that query results deque respects max size"""
        # Create querier with small max size
        with patch('src.context_querier.AsyncOpenAI'):
            small_querier = ContextQuerier(max_results=3)  # Small size for testing
        
        await small_querier.start_querier(mock_context_integrator, "Test task")
        
        with patch.object(small_querier, '_call_openai_for_query', return_value=mock_openai_response):
            # Run more queries than max size
            for i in range(5):
                await small_querier._run_query()
            
            # Should only keep the last 3 results
            history = await small_querier.get_query_history()
            assert len(history) == 3
            assert len(small_querier.query_results) == 3
        
        await small_querier.stop_querier()
    
    @pytest.mark.asyncio
    async def test_reusable_querier_with_different_tasks(self, context_querier, mock_context_integrator, mock_openai_response):
        """Test that the same querier can be reused with different tasks"""
        
        # First task
        first_task = "What is being developed?"
        await context_querier.start_querier(mock_context_integrator, first_task)
        
        with patch.object(context_querier, '_call_openai_for_query', return_value=mock_openai_response):
            result1 = await context_querier.force_query()
            assert result1.query_task == first_task
        
        await context_querier.stop_querier()
        
        # Second task (reusing same querier)
        second_task = "Are there any bugs in the code?"
        await context_querier.start_querier(mock_context_integrator, second_task)
        
        with patch.object(context_querier, '_call_openai_for_query', return_value=mock_openai_response):
            result2 = await context_querier.force_query()
            assert result2.query_task == second_task
        
        await context_querier.stop_querier()
        
        # Verify both results are stored in history
        history = await context_querier.get_query_history()
        assert len(history) == 2
        assert history[0].query_task == first_task
        assert history[1].query_task == second_task 