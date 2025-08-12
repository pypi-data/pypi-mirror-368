#!/usr/bin/env python3
import pytest
import pytest_asyncio
import asyncio
import json
import time
import os
import heapq
from unittest.mock import Mock, AsyncMock, patch
from src.context_integrator import ContextIntegrator, ContextUpdate, ContextState, create_context_integrator
from src.transcription_pipeline import ProcessedClip, TranscriptionPipeline

class TestContextIntegrator:
    
    @pytest.fixture
    def mock_openai_client(self):
        """Mock OpenAI client for testing"""
        mock_client = AsyncMock()
        
        # Mock that returns different responses based on call count
        async def create_response(*args, **kwargs):
            # Get call count to vary responses
            call_count = getattr(create_response, 'call_count', 0)
            create_response.call_count = call_count + 1
            
            mock_response = Mock()
            mock_choice = Mock()
            mock_message = Mock()
            
            test_response = {
                "Speaker-Map": {"SPEAKER_1": "Test User", "SPEAKER_2": "AI Assistant"},
                "Next-Context": f"Updated context with new information from segment {call_count + 1}",
                "Summary": f"This segment {call_count + 1} contains test content for verification"
            }
            
            mock_message.content = json.dumps(test_response)
            mock_choice.message = mock_message
            mock_response.choices = [mock_choice]
            return mock_response
        
        mock_client.chat.completions.create.side_effect = create_response
        
        return mock_client
    
    @pytest.fixture
    def sample_processed_clips(self):
        """Create sample processed clips for testing"""
        return [
            ProcessedClip(
                clip_path="/test/clip1.mov",
                start_time=1000.0,
                end_time=1003.0,
                transcription="SPEAKER_1: Hello, this is a test recording",
                visual_description="Screen showing test interface with buttons",
                speakers=["SPEAKER_1"],
                has_audio=True,
                metadata={"test": True},
                priority=(1000.0, 0, 0, 0)  # (start_time, clip_counter, stream_priority, pipeline_priority)
            ),
            ProcessedClip(
                clip_path="/test/clip2.mov", 
                start_time=1003.0,
                end_time=1006.0,
                transcription="SPEAKER_1: Continuing with more test content",
                visual_description="User clicking on menu items in the interface",
                speakers=["SPEAKER_1"],
                has_audio=True,
                metadata={"test": True},
                priority=(1003.0, 1, 0, 0)
            ),
            ProcessedClip(
                clip_path="/test/clip3.mov",
                start_time=1006.0, 
                end_time=1009.0,
                transcription="[NO AUDIO DETECTED]",
                visual_description="Silent screen recording showing file operations",
                speakers=[],
                has_audio=False,
                metadata={"test": True},
                priority=(1006.0, 2, 0, 0)
            )
        ]
    
    @pytest_asyncio.fixture
    async def context_integrator(self, mock_openai_client):
        """Create ContextIntegrator instance with mocked OpenAI"""
        with patch('src.context_integrator.AsyncOpenAI', return_value=mock_openai_client):
            integrator = ContextIntegrator(session_title="Test Session")
            yield integrator
            
            # Cleanup
            if integrator.is_running:
                await integrator.stop_integrator()
    
    @pytest_asyncio.fixture
    async def mock_transcription_pipeline(self, sample_processed_clips):
        """Create mock TranscriptionPipeline that returns sample clips"""
        pipeline = AsyncMock(spec=TranscriptionPipeline)
        pipeline.get_recent_processed_clips = AsyncMock(return_value=sample_processed_clips)
        pipeline.set_callback = Mock()
        return pipeline
    
    @pytest.mark.asyncio
    async def test_context_integrator_creation(self):
        """Test basic ContextIntegrator creation and initialization"""
        with patch('src.context_integrator.AsyncOpenAI'):
            integrator = ContextIntegrator(session_title="Test Session")
            
            assert integrator.session_title == "Test Session"
            assert not integrator.is_running
            assert integrator.context_state.total_clips_processed == 0
            assert "Test Session" in integrator.context_state.context
            assert "UNKNOWN" in integrator.context_state.speakers
            assert len(integrator.ready_priority_queue) == 0
            assert len(integrator.looking_for_set) == 0
            assert len(integrator.not_ready_dict) == 0
    
    @pytest.mark.asyncio
    async def test_factory_function(self):
        """Test create_context_integrator factory function"""
        with patch('src.context_integrator.AsyncOpenAI'):
            integrator = create_context_integrator("Factory Test")
            
            assert isinstance(integrator, ContextIntegrator)
            assert integrator.session_title == "Factory Test"
    
    @pytest.mark.asyncio
    async def test_three_bucket_dependency_tracking_system(self, context_integrator):
        """Test the three-bucket dependency tracking system with clips arriving out of order"""
        
        # Create test clips with different arrival orders
        clip0 = ProcessedClip(
            clip_path="clip0.mov",
            start_time=0.0,
            end_time=5.0,
            transcription="Hello world",
            visual_description="Person speaking",
            speakers=["Speaker 1"],
            has_audio=True,
            metadata={},
            priority=(0.0, 0, 1, 1)  # clip_id=0, stream_priority=1, pipeline_priority=1
        )
        
        clip2 = ProcessedClip(
            clip_path="clip2.mov",
            start_time=10.0,
            end_time=15.0,
            transcription="This is clip 2",
            visual_description="Continued speaking",
            speakers=["Speaker 1"],
            has_audio=True,
            metadata={},
            priority=(10.0, 2, 1, 1)  # clip_id=2 - arrives before clip1
        )
        
        clip1 = ProcessedClip(
            clip_path="clip1.mov",
            start_time=5.0,
            end_time=10.0,
            transcription="This is clip 1",
            visual_description="Person continues",
            speakers=["Speaker 1"],
            has_audio=True,
            metadata={},
            priority=(5.0, 1, 1, 1)  # clip_id=1 - arrives after clip2
        )
        
        # Initial state - all buckets should be empty
        status = await context_integrator.get_context_status()
        assert status['looking_for_count'] == 0
        assert status['not_ready_count'] == 0
        assert status['ready_queue_count'] == 0
        
        # Add clip 0 (should go directly to priority queue)
        await context_integrator._route_clip_through_buckets(clip0)
        status = await context_integrator.get_context_status()
        
        assert status['ready_queue_count'] == 1  # clip0 in ready queue
        assert status['looking_for_count'] == 1  # expecting clip1 next
        assert status['not_ready_count'] == 0
        assert (1, 1, 1) in context_integrator.looking_for_set  # looking for clip1
        
        # Add clip 2 (should go to not_ready_dict since clip1 hasn't arrived)
        await context_integrator._route_clip_through_buckets(clip2)
        status = await context_integrator.get_context_status()
        
        assert status['ready_queue_count'] == 1  # still just clip0
        assert status['looking_for_count'] == 1  # still looking for clip1
        assert status['not_ready_count'] == 1    # clip2 waiting
        assert clip2 in context_integrator.not_ready_dict.values()
        
        # Process clip0 
        await context_integrator._process_ready_clips(force_process=True)
        status = await context_integrator.get_context_status()
        
        assert status['total_clips_processed'] == 1
        assert status['ready_queue_count'] == 0  # clip0 processed
        assert status['looking_for_count'] == 1  # still looking for clip1
        assert status['not_ready_count'] == 1    # clip2 still waiting
        
        # Add clip 1 (should go to ready queue since it's expected)
        await context_integrator._route_clip_through_buckets(clip1)
        status = await context_integrator.get_context_status()
        
        # After routing clip1, it should be in ready queue and clip2 should have moved too
        assert status['ready_queue_count'] == 2  # clip1 ready, clip2 ready
        assert status['not_ready_count'] == 0    # clip2 was found and moved to ready
        assert status['looking_for_count'] == 1  # clip1 was found and moved to ready, clip3 now looking for 
        
        # Process clip1 and clip2
        await context_integrator._process_ready_clips(force_process=True)
        status = await context_integrator.get_context_status()
        
        # After processing clip1, clip2 should stay in ready queue
        assert status['total_clips_processed'] == 3  # clip0 and clip1 and clip2 processed
        assert status['ready_queue_count'] == 0  
        assert status['not_ready_count'] == 0    # clip2 moved out
        assert status['looking_for_count'] == 1  # looking for clip3
        # Process remaining clips (clip2)

        # Verify clips were processed in chronological order (0, 1, 2)
        # This is the key test - despite arriving in order 0, 2, 1
        # they should be processed in chronological order 0, 1, 2
        assert len(context_integrator.processed_updates) == 3
        processed_clips = list(context_integrator.processed_updates)
        
        # Extract clip IDs from priorities to verify order
        clip_ids = [update.priority[1] for update in processed_clips]
        assert clip_ids == [0, 1, 2]  # Chronological order maintained
    
    @pytest.mark.asyncio
    async def test_three_bucket_multi_stream_priorities(self, context_integrator):
        """Test three-bucket system with different stream and pipeline priorities"""
        
        # Create clips from different streams with same clip_id but different priorities
        clip_stream1 = ProcessedClip(
            clip_path="stream1_clip0.mov",
            start_time=0.0,
            end_time=5.0,
            transcription="Stream 1 content",
            visual_description="Stream 1 visual",
            speakers=["Speaker 1"],
            has_audio=True,
            metadata={"stream": 1},
            priority=(0.0, 0, 1, 0)  # stream_priority=1, pipeline_priority=0
        )
        
        clip_stream2 = ProcessedClip(
            clip_path="stream2_clip0.mov", 
            start_time=0.0,
            end_time=5.0,
            transcription="Stream 2 content",
            visual_description="Stream 2 visual",
            speakers=["Speaker 2"],
            has_audio=True,
            metadata={"stream": 2},
            priority=(0.0, 0, 2, 0)  # stream_priority=2, pipeline_priority=0
        )
        
        # Both should go to ready queue since clip_id=0
        await context_integrator._route_clip_through_buckets(clip_stream1)
        await context_integrator._route_clip_through_buckets(clip_stream2)
        
        status = await context_integrator.get_context_status()
        assert status['ready_queue_count'] == 2
        assert status['looking_for_count'] == 2  # looking for next from both streams
        
        # Process clips - should respect priority order
        await context_integrator._process_ready_clips(force_process=True)
        
        # Verify different streams are tracked independently
        expected_looking_for = {(1, 1, 0), (1, 2, 0)}  # expecting clip1 from both streams
        assert context_integrator.looking_for_set == expected_looking_for
    
    @pytest.mark.asyncio
    async def test_single_clip_integration(self, context_integrator, sample_processed_clips):
        """Test integrating a single clip into context"""
        clip = sample_processed_clips[0]
        
        # Test the integration
        update = await context_integrator._integrate_single_clip(clip)
        
        assert update is not None
        assert update.error is None
        assert update.clip_path == clip.clip_path
        assert update.start_time == clip.start_time
        assert update.end_time == clip.end_time
        assert update.priority == clip.priority
        assert len(update.summary) > 0
        assert len(update.updated_context) > 0
        assert isinstance(update.speakers, dict)
        assert update.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_priority_based_clip_ordering(self, context_integrator):
        """Test that clips are stored and retrieved in priority order using heap"""
        # Create clips with different priorities
        clips = [
            ProcessedClip("/test/clip2.mov", 1003.0, 1006.0, "Second", "Visual2", ["S1"], True, {}, (1003.0, 1, 0, 0)),
            ProcessedClip("/test/clip1.mov", 1000.0, 1003.0, "First", "Visual1", ["S1"], True, {}, (1000.0, 0, 0, 0)),
            ProcessedClip("/test/clip3.mov", 1006.0, 1009.0, "Third", "Visual3", ["S1"], True, {}, (1006.0, 2, 0, 0)),
            # Higher stream priority (should come first within same time)
            ProcessedClip("/test/priority_clip.mov", 1000.0, 1003.0, "Priority", "Visual", ["S1"], True, {}, (1000.0, 0, 1, 0))
        ]
        
        # Add clips to heap in non-chronological order
        for clip in clips:
            heapq.heappush(context_integrator.ready_priority_queue, (clip.priority, clip))
        
        # Verify heap returns clips in priority order
        retrieved_clips = []
        while context_integrator.ready_priority_queue:
            _, clip = heapq.heappop(context_integrator.ready_priority_queue)
            retrieved_clips.append(clip)
        
        # Should be in priority order: (1000.0, 0, 0, 0), (1000.0, 0, 1, 0), (1003.0, 1, 0, 0), (1006.0, 2, 0, 0)
        assert retrieved_clips[0].priority == (1000.0, 0, 0, 0)
        assert retrieved_clips[1].priority == (1000.0, 0, 1, 0)  # Higher stream priority
        assert retrieved_clips[2].priority == (1003.0, 1, 0, 0)
        assert retrieved_clips[3].priority == (1006.0, 2, 0, 0)
    
    @pytest.mark.asyncio
    async def test_autoregressive_context_updates(self, context_integrator, sample_processed_clips):
        """Test that context is updated autoregressively between clips"""
        initial_context = context_integrator.context_state.context
        
        # Process first clip
        clip1 = sample_processed_clips[0]
        update1 = await context_integrator._integrate_single_clip(clip1)
        
        # Manually update context state (simulating what _integration_loop does)
        context_integrator.context_state.context = update1.updated_context
        context_integrator.context_state.speakers = update1.speakers
        context_integrator.context_state.total_clips_processed += 1
        
        context_after_clip1 = context_integrator.context_state.context
        
        # Process second clip
        clip2 = sample_processed_clips[1]
        update2 = await context_integrator._integrate_single_clip(clip2)
        
        # Verify contexts are different and progressive
        assert initial_context != context_after_clip1
        assert context_after_clip1 != update2.updated_context
        assert len(update2.updated_context) > 0
        
        # Verify clip-specific information
        assert update1.clip_path != update2.clip_path
        assert update1.start_time != update2.start_time
        assert update1.priority != update2.priority
    
    @pytest.mark.asyncio
    async def test_context_state_management(self, context_integrator, sample_processed_clips):
        """Test context state updates and tracking"""
        initial_clips_processed = context_integrator.context_state.total_clips_processed
        initial_time = context_integrator.context_state.last_update_time
        
        # Process a clip
        clip = sample_processed_clips[0]
        update = await context_integrator._integrate_single_clip(clip)
        
        # Manually update state (simulating integration loop)
        context_integrator.context_state.context = update.updated_context
        context_integrator.context_state.speakers = update.speakers
        context_integrator.context_state.total_clips_processed += 1
        context_integrator.context_state.last_update_time = time.time()
        
        # Verify state updates
        assert context_integrator.context_state.total_clips_processed == initial_clips_processed + 1
        assert context_integrator.context_state.last_update_time > initial_time
        assert context_integrator.context_state.context == update.updated_context
    
    @pytest.mark.asyncio
    async def test_callback_processing(self, context_integrator, sample_processed_clips):
        """Test that the callback system processes clips correctly"""
        # Start the integrator
        context_integrator.is_running = True
        
        # Use force_process_clip to simulate callback processing
        clip = sample_processed_clips[0]
        context_update = await context_integrator.force_process_clip(clip)
        
        # Verify the update was created and stored
        assert context_update is not None
        assert context_update.error is None
        assert context_update.clip_path == clip.clip_path
        assert len(context_integrator.processed_updates) == 1
        assert context_integrator.context_state.total_clips_processed == 1
    
    @pytest.mark.asyncio
    async def test_error_handling(self, mock_openai_client):
        """Test error handling in context integration"""
        # Setup integrator with failing OpenAI client
        mock_openai_client.chat.completions.create.side_effect = Exception("API Error")
        
        with patch('src.context_integrator.AsyncOpenAI', return_value=mock_openai_client):
            integrator = ContextIntegrator()
            
            clip = ProcessedClip(
                clip_path="/test/error_clip.mov",
                start_time=1000.0,
                end_time=1003.0,
                transcription="Test transcription",
                visual_description="Test visual",
                speakers=["SPEAKER_1"],
                has_audio=True,
                metadata={},
                priority=(1000.0, 0, 0, 0)
            )
            
            # Should handle error gracefully
            update = await integrator._integrate_single_clip(clip)
            
            assert update is not None
            assert update.error is not None
            assert "Failed to get response from OpenAI" in update.error
            assert update.summary == ""
            assert update.updated_context == ""
            assert update.priority == clip.priority
    
    @pytest.mark.asyncio
    async def test_get_current_context(self, context_integrator):
        """Test getting current context"""
        initial_context = await context_integrator.get_current_context()
        
        assert isinstance(initial_context, str)
        assert "Test Session" in initial_context
        assert len(initial_context) > 0
    
    @pytest.mark.asyncio
    async def test_get_current_speakers(self, context_integrator):
        """Test getting current speakers"""
        speakers = await context_integrator.get_current_speakers()
        
        assert isinstance(speakers, dict)
        assert "UNKNOWN" in speakers
    
    @pytest.mark.asyncio
    async def test_get_recent_updates(self, context_integrator):
        """Test getting recent context updates"""
        # Initially should be empty
        recent = await context_integrator.get_recent_updates(duration_seconds=30.0)
        assert len(recent) == 0
        
        # Add a mock update
        mock_update = ContextUpdate(
            clip_path="/test/clip.mov",
            start_time=time.time() - 10,  # 10 seconds ago
            end_time=time.time() - 7,
            summary="Test summary",
            updated_context="Test context",
            speakers={"SPEAKER_1": "Test"},
            processing_time=1.0,
            priority=(time.time() - 10, 0, 0, 0)
        )
        context_integrator.processed_updates.append(mock_update)
        
        # Should find the recent update
        recent = await context_integrator.get_recent_updates(duration_seconds=30.0)
        assert len(recent) == 1
        assert recent[0].clip_path == "/test/clip.mov"
        
        # Should not find updates outside time window
        old_recent = await context_integrator.get_recent_updates(duration_seconds=5.0)
        assert len(old_recent) == 0
    
    @pytest.mark.asyncio
    async def test_get_context_status(self, context_integrator):
        """Test getting context integrator status"""
        status = await context_integrator.get_context_status()
        
        assert isinstance(status, dict)
        assert 'is_running' in status
        assert 'session_title' in status
        assert 'session_duration_seconds' in status
        assert 'total_clips_processed' in status
        assert 'recent_updates_count' in status
        assert 'average_processing_time' in status
        assert 'current_context_length' in status
        assert 'speakers_identified' in status
        # Three-bucket system status
        assert 'looking_for_count' in status
        assert 'not_ready_count' in status
        assert 'ready_queue_count' in status
        assert 'looking_for_clips' in status
        assert 'not_ready_clip_ids' in status
        
        assert status['session_title'] == "Test Session"
        assert status['total_clips_processed'] == 0
        assert status['session_duration_seconds'] > 0
    
    @pytest.mark.asyncio
    async def test_export_session_summary(self, context_integrator):
        """Test exporting session summary"""
        # Add some mock updates
        mock_update = ContextUpdate(
            clip_path="/test/clip.mov",
            start_time=time.time() - 100,
            end_time=time.time() - 97,
            summary="Test summary for export",
            updated_context="Context for export",
            speakers={"SPEAKER_1": "Export User"},
            processing_time=1.5,
            priority=(time.time() - 100, 0, 0, 0)
        )
        context_integrator.processed_updates.append(mock_update)
        context_integrator.context_state.speakers = {"SPEAKER_1": "Export User"}
        
        summary = await context_integrator.export_session_summary()
        
        assert isinstance(summary, str)
        assert "# Screen Recording Session Summary" in summary
        assert "Test Session" in summary
        assert "Export User" in summary
        assert "Test summary for export" in summary
        assert "Priority:" in summary
        assert "Duration:" in summary
        assert "Clips Processed:" in summary
    
    @pytest.mark.asyncio
    async def test_start_stop_integrator(self, context_integrator, mock_transcription_pipeline):
        """Test starting and stopping the integrator"""
        assert not context_integrator.is_running
        
        # Start integrator
        await context_integrator.start_integrator(mock_transcription_pipeline)
        assert context_integrator.is_running
        assert context_integrator.transcription_pipeline == mock_transcription_pipeline
        
        # Verify callback was set
        mock_transcription_pipeline.set_callback.assert_called_once_with(context_integrator._on_new_processed_clip)
        
        # Stop integrator
        await context_integrator.stop_integrator()
        assert not context_integrator.is_running
    
    @pytest.mark.asyncio
    async def test_callback_processing_with_deduplication(self, context_integrator, sample_processed_clips):
        """Test that callback processing handles deduplication correctly"""
        # Start the integrator
        context_integrator.is_running = True
        
        # Add some clips to processed set
        context_integrator._processed_clip_paths.add("/test/clip1.mov")
        
        # Try to process the same clip again - should be ignored
        clip = sample_processed_clips[0]  # This is "/test/clip1.mov"
        
        # Simulate the callback being called
        await context_integrator._on_new_processed_clip(clip)
        
        # Should not have been processed again due to deduplication
        assert len(context_integrator.processed_updates) == 0
        assert context_integrator.context_state.total_clips_processed == 0
    
    @pytest.mark.asyncio
    async def test_integration_with_force_processing(self, context_integrator, sample_processed_clips):
        """Test integration using force processing for testing"""
        # Start the integrator
        context_integrator.is_running = True
        
        # Use force_process_clip to simulate processing
        for clip in sample_processed_clips:
            context_update = await context_integrator.force_process_clip(clip)
            assert context_update is not None
            assert context_update.error is None
        
        # Verify all clips were processed
        assert len(context_integrator.processed_updates) == len(sample_processed_clips)
        assert context_integrator.context_state.total_clips_processed == len(sample_processed_clips)
    
    @pytest.mark.asyncio  
    async def test_prompt_template_rendering(self, context_integrator, sample_processed_clips):
        """Test that prompt template renders correctly with clip data"""
        clip = sample_processed_clips[0]
        
        # Get the template and render it manually to verify
        from jinja2 import Template
        template = Template(context_integrator.prompt_template)
        
        rendered = template.render(
            audio_transcription=clip.transcription,
            visual_content=clip.visual_description,
            start=clip.start_time,
            end=clip.end_time,
            idx=1,
            context=context_integrator.context_state.context,
            speakermap=json.dumps(context_integrator.context_state.speakers),
            title=context_integrator.session_title
        )
        
        # Verify key elements are in the rendered prompt
        assert "Test Session" in rendered
        assert "Hello, this is a test recording" in rendered
        assert "Screen showing test interface" in rendered
        assert "1000.0" in rendered
        assert "1003.0" in rendered
        assert "Next-Context" in rendered
        assert "Speaker-Map" in rendered
    
    @pytest.mark.asyncio
    async def test_multi_stream_priority_handling(self, context_integrator):
        """Test that clips from different streams are processed by priority"""
        # Create clips from different streams with different priorities
        clips_multi_stream = [
            # Low priority stream
            ProcessedClip("/test/low_stream_clip.mov", 1000.0, 1003.0, "Low priority", "Visual", ["S1"], True, 
                         {"stream": "low"}, (1000.0, 0, 0, 0)),  # stream_priority=0
            # High priority stream (same time)
            ProcessedClip("/test/high_stream_clip.mov", 1000.0, 1003.0, "High priority", "Visual", ["S1"], True, 
                         {"stream": "high"}, (1000.0, 0, 1, 0)),  # stream_priority=1
            # Different pipeline priority
            ProcessedClip("/test/pipeline_clip.mov", 1000.0, 1003.0, "Pipeline priority", "Visual", ["S1"], True, 
                         {"stream": "pipeline"}, (1000.0, 0, 0, 1)),  # pipeline_priority=1
        ]
        
        # Add clips to heap
        for clip in clips_multi_stream:
            heapq.heappush(context_integrator.ready_priority_queue, (clip.priority, clip))
        
        # Get clips in priority order
        retrieved_clips = []
        while context_integrator.ready_priority_queue:
            _, clip = heapq.heappop(context_integrator.ready_priority_queue)
            retrieved_clips.append(clip)
        
        # Verify priority order: (1000.0, 0, 0, 0), (1000.0, 0, 0, 1), (1000.0, 0, 1, 0)
        assert retrieved_clips[0].metadata["stream"] == "low"       # (1000.0, 0, 0, 0)
        assert retrieved_clips[1].metadata["stream"] == "pipeline"  # (1000.0, 0, 0, 1)
        assert retrieved_clips[2].metadata["stream"] == "high"      # (1000.0, 0, 1, 0)

if __name__ == "__main__":
    pytest.main([__file__]) 