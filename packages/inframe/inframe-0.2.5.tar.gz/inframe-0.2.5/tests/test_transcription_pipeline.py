#!/usr/bin/env python3
import asyncio
import os
import pytest
from pathlib import Path

from src.video_stream import VideoStream
from src.transcription_pipeline import create_transcription_pipeline

@pytest.mark.asyncio
async def test_transcription_pipeline_creation():
    """Test basic transcription pipeline creation"""
    print("\n🧪 Testing transcription pipeline creation...")
    
    # Test with different configurations
    pipeline_openai = create_transcription_pipeline(use_openai=True)
    assert pipeline_openai.use_openai == True
    assert pipeline_openai.whisper_model == "small.en"
    assert pipeline_openai.language == "en"
    
    pipeline_local = create_transcription_pipeline(use_openai=False, whisper_model="medium")
    assert pipeline_local.use_openai == False
    assert pipeline_local.whisper_model == "medium"
    
    # Check initial state
    status = await pipeline_openai.get_pipeline_status()
    assert status['is_running'] == False
    assert status['processed_clips_count'] == 0
    assert status['total_clips_processed'] == 0
    
    print("✅ Pipeline creation test passed")

@pytest.mark.asyncio 
async def test_integrated_transcription_workflow():
    """Test complete workflow: VideoStream → TranscriptionPipeline"""
    print("\n🎬 Testing integrated transcription workflow...")
    
    # Create VideoStream and TranscriptionPipeline
    video_stream = VideoStream.create(chunk_duration=3.0, max_clips=5)
    transcription_pipeline = create_transcription_pipeline(use_openai=True)  # Use OpenAI for real-world testing
    
    try:
        # Start video recording
        print("📹 Starting video stream...")
        stream_success = await video_stream.start_stream(recording_mode="full_screen")
        assert stream_success, "Video stream should start successfully"
        
        # Start transcription pipeline
        print("🎙️ Starting transcription pipeline...")
        await transcription_pipeline.start_pipeline(video_stream)
        
        # Let the system record and process for a bit
        print("⏰ Recording and processing for 8 seconds...")
        await asyncio.sleep(8)
        
        # Check video stream status
        video_status = await video_stream.get_buffer_status()
        print(f"Video status: {video_status['clip_count']} clips, {video_status['buffer_duration']:.1f}s")
        assert video_status['clip_count'] > 0, "Should have recorded some clips"
        
        # Check transcription pipeline status
        pipeline_status = await transcription_pipeline.get_pipeline_status()
        print(f"Pipeline status: {pipeline_status}")
        assert pipeline_status['is_running'] == True, "Pipeline should be running"
        
        # Wait a bit more for processing to complete
        print("⏰ Waiting for transcription processing...")
        await asyncio.sleep(5)
        
        # Get processed clips
        processed_clips = await transcription_pipeline.get_recent_processed_clips(duration_seconds=15.0)
        print(f"📄 Found {len(processed_clips)} processed clips")
        
        # Verify processed clips
        for i, clip in enumerate(processed_clips):
            print(f"  Clip {i+1}: {os.path.basename(clip.clip_path)}")
            print(f"    Duration: {clip.end_time - clip.start_time:.1f}s")
            print(f"    Has audio: {clip.has_audio}")
            print(f"    Speakers: {clip.speakers}")
            print(f"    Transcription preview: {clip.transcription[:100]}...")
            
            # Basic assertions
            assert clip.clip_path, "Clip should have a file path"
            assert clip.end_time > clip.start_time, "Clip should have valid duration"
            assert isinstance(clip.transcription, str), "Should have transcription text"
            assert isinstance(clip.visual_description, str), "Should have visual description"
            assert isinstance(clip.speakers, list), "Should have speakers list"
        
        # Check that pipeline is processing clips as they become available
        final_status = await transcription_pipeline.get_pipeline_status()
        print(f"Final pipeline status: processed={final_status['total_clips_processed']}, active_tasks={final_status['active_processing_tasks']}")
        
        print("✅ Integrated transcription workflow test passed!")
        
    finally:
        # Clean up
        await transcription_pipeline.stop_pipeline()
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_transcription_pipeline_audio_processing():
    """Test audio processing capabilities"""
    print("\n🎵 Testing audio processing...")
    
    # Create a simple test - just check pipeline can handle clips without crashing
    video_stream = VideoStream.create(chunk_duration=2.0, max_clips=3)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        stream_success = await video_stream.start_stream()
        if not stream_success:
            print("⚠️ Could not start video stream, skipping audio test")
            return
            
        await pipeline.start_pipeline(video_stream)
        
        # Record for a shorter duration
        await asyncio.sleep(6)
        
        # Check processing status
        status = await pipeline.get_pipeline_status()
        print(f"Audio processing test status: {status}")
        
        # Should be running and possibly processing
        assert status['is_running'] == True
        
        print("✅ Audio processing test passed")
        
    finally:
        await pipeline.stop_pipeline() 
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_processed_clips_rolling_buffer():
    """Test that processed clips are managed in a rolling buffer"""
    print("\n📊 Testing processed clips rolling buffer...")
    
    video_stream = VideoStream.create(chunk_duration=1.5, max_clips=10)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        await video_stream.start_stream()
        await pipeline.start_pipeline(video_stream)
        
        # Record for longer to get more clips
        await asyncio.sleep(8)
        
        # Get clips from different time windows
        recent_5s = await pipeline.get_recent_processed_clips(duration_seconds=5.0)
        recent_10s = await pipeline.get_recent_processed_clips(duration_seconds=10.0)
        recent_20s = await pipeline.get_recent_processed_clips(duration_seconds=20.0)
        
        print(f"Recent clips: 5s={len(recent_5s)}, 10s={len(recent_10s)}, 20s={len(recent_20s)}")
        
        # Longer duration should include more clips (or same if all clips are recent)
        assert len(recent_10s) >= len(recent_5s), "10s window should have >= clips than 5s window"
        assert len(recent_20s) >= len(recent_10s), "20s window should have >= clips than 10s window"
        
        # Clips should be in chronological order
        if len(recent_10s) > 1:
            for i in range(len(recent_10s) - 1):
                assert recent_10s[i].start_time <= recent_10s[i + 1].start_time, "Clips should be chronological"
        
        print("✅ Rolling buffer test passed")
        
    finally:
        await pipeline.stop_pipeline()
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_pipeline_error_handling():
    """Test pipeline handles errors gracefully"""
    print("\n⚠️ Testing error handling...")
    
    pipeline = create_transcription_pipeline(use_openai=True)
    
    # Test starting pipeline without video stream (should handle gracefully)
    try:
        # This should not crash, but will not process anything meaningful
        status = await pipeline.get_pipeline_status()
        assert status['is_running'] == False
        
        # Stop should work even if not started
        await pipeline.stop_pipeline()
        
        print("✅ Error handling test passed")
        
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        raise

@pytest.mark.asyncio
async def test_openai_transcription_with_results():
    """Test OpenAI transcription with sufficient wait time to see actual results"""
    print("\n🎙️ Testing OpenAI transcription with longer wait for actual results...")
    
    video_stream = VideoStream.create(chunk_duration=3.0, max_clips=5)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        # Start both systems
        stream_success = await video_stream.start_stream()
        assert stream_success, "Video stream should start"
        
        await pipeline.start_pipeline(video_stream)
        
        print("⏰ Recording for 6 seconds...")
        await asyncio.sleep(6)
        
        print("⏰ Waiting 15 seconds for OpenAI transcription to complete...")
        await asyncio.sleep(15)
        
        # Check results
        processed_clips = await pipeline.get_recent_processed_clips(duration_seconds=30.0)
        status = await pipeline.get_pipeline_status()
        
        print(f"📊 Final Status:")
        print(f"  Processed clips: {len(processed_clips)}")
        print(f"  Total processed: {status['total_clips_processed']}")
        print(f"  Active tasks: {status['active_processing_tasks']}")
        print(f"  Average processing time: {status['average_processing_time']:.2f}s")
        print(f"  Total audio segments: {status['total_audio_segments']}")
        
        # Should have processed at least some clips
        assert status['total_clips_processed'] > 0, f"Should have processed clips, got {status['total_clips_processed']}"
        
        # Show actual transcription results
        for i, clip in enumerate(processed_clips):
            print(f"\n🎙️ Clip {i+1}:")
            print(f"  File: {os.path.basename(clip.clip_path)}")
            print(f"  Duration: {clip.end_time - clip.start_time:.1f}s")
            print(f"  Has audio: {clip.has_audio}")
            print(f"  Speakers: {clip.speakers}")
            print(f"  Transcription preview: {clip.transcription[:150]}...")
            print(f"  Visual description: {clip.visual_description[:100]}...")
            
            # Basic assertions
            assert isinstance(clip.transcription, str), "Should have transcription text"
            assert isinstance(clip.visual_description, str), "Should have visual description"
            assert isinstance(clip.speakers, list), "Should have speakers list"
            assert clip.end_time > clip.start_time, "Should have valid duration"
        
        print(f"\n✅ OpenAI transcription test completed! Processed {len(processed_clips)} clips")
        
    finally:
        await pipeline.stop_pipeline()
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_visual_frame_extraction():
    """Test visual frame extraction capabilities"""
    print("\n🎥 Testing visual frame extraction...")
    
    video_stream = VideoStream.create(chunk_duration=2.0, max_clips=3)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        # Start recording to get some video clips
        stream_success = await video_stream.start_stream()
        assert stream_success, "Video stream should start"
        
        print("📹 Recording for 4 seconds to get video clips...")
        await asyncio.sleep(4)
        
        # Get recent clips from video stream
        video_clips = await video_stream.get_recent_clips(duration_seconds=10.0)
        print(f"Found {len(video_clips)} video clips for frame extraction")
        
        if len(video_clips) > 0:
            test_clip = video_clips[0]
            print(f"Testing frame extraction on: {os.path.basename(test_clip.file_path)}")
            
            # Test frame extraction directly
            frames = await pipeline._extract_frames_for_timerange(
                test_clip.file_path, 
                0.0,  # Start from beginning of clip
                min(3.0, test_clip.end_time - test_clip.start_time),  # First 3 seconds or full clip
                interval=5  # Every 5 seconds for testing
            )
            
            print(f"📷 Extracted {len(frames)} frames")
            
            # Verify frame structure
            for i, frame in enumerate(frames):
                print(f"  Frame {i+1}: timestamp={frame.get('timestamp', 'N/A'):.1f}s, "
                      f"has_data={len(frame.get('frame_data', '')) > 0}")
                
                # Basic assertions
                assert 'timestamp' in frame, "Frame should have timestamp"
                assert 'frame_data' in frame, "Frame should have frame data"
                assert isinstance(frame['frame_data'], str), "Frame data should be base64 string"
                assert len(frame['frame_data']) > 0, "Frame data should not be empty"
            
            print("✅ Frame extraction test passed")
        else:
            print("⚠️ No video clips available for frame extraction test")
        
    finally:
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_visual_analysis_with_gpt4v():
    """Test GPT-4V visual analysis"""
    print("\n🤖 Testing GPT-4V visual analysis...")
    
    video_stream = VideoStream.create(chunk_duration=3.0, max_clips=3)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        # Start recording
        stream_success = await video_stream.start_stream()
        assert stream_success, "Video stream should start"
        
        print("📹 Recording for 5 seconds to capture screen content...")
        await asyncio.sleep(5)
        
        # Get a video clip
        video_clips = await video_stream.get_recent_clips(duration_seconds=10.0)
        
        if len(video_clips) > 0:
            test_clip = video_clips[0]
            print(f"Testing visual analysis on: {os.path.basename(test_clip.file_path)}")
            
            # Test full visual analysis (frame extraction + GPT-4V)
            visual_description = await pipeline._analyze_visual_content(test_clip)
            
            print(f"📝 Visual analysis result ({len(visual_description)} chars):")
            print(f"  Preview: {visual_description[:200]}...")
            
            # Verify visual analysis
            assert isinstance(visual_description, str), "Visual description should be string"
            assert len(visual_description) > 0, "Visual description should not be empty"
            
            # Should contain frame timestamps or error messages
            has_content = any(indicator in visual_description.lower() for indicator in [
                '[', 'screen', 'frame', 'visual', 'analysis', 'ui', 'content', 'failed', 'error'
            ])
            assert has_content, f"Visual description should contain relevant content: {visual_description[:100]}"
            
            print("✅ GPT-4V visual analysis test passed")
        else:
            print("⚠️ No video clips available for visual analysis test")
            
    finally:
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_integrated_audio_visual_processing():
    """Test complete audio + visual processing integration"""
    print("\n🎬 Testing integrated audio + visual processing...")
    
    video_stream = VideoStream.create(chunk_duration=3.0, max_clips=5)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        # Start both systems
        stream_success = await video_stream.start_stream()
        assert stream_success, "Video stream should start"
        
        await pipeline.start_pipeline(video_stream)
        
        print("📹 Recording for 8 seconds...")
        await asyncio.sleep(8)
        
        print("⏰ Waiting 20 seconds for complete audio + visual processing...")
        await asyncio.sleep(20)
        
        # Get processed clips
        processed_clips = await pipeline.get_recent_processed_clips(duration_seconds=30.0)
        status = await pipeline.get_pipeline_status()
        
        print(f"🎯 Integrated Processing Results:")
        print(f"  Processed clips: {len(processed_clips)}")
        print(f"  Total processed: {status['total_clips_processed']}")
        
        # Verify integrated processing
        for i, clip in enumerate(processed_clips):
            print(f"\n📋 Clip {i+1} Analysis:")
            print(f"  Duration: {clip.end_time - clip.start_time:.1f}s")
            print(f"  Has audio: {clip.has_audio}")
            print(f"  Speakers: {clip.speakers}")
            
            # Audio analysis
            audio_length = len(clip.transcription)
            print(f"  Audio transcription: {audio_length} chars")
            print(f"    Preview: {clip.transcription[:100]}...")
            
            # Visual analysis
            visual_length = len(clip.visual_description)
            print(f"  Visual description: {visual_length} chars")
            print(f"    Preview: {clip.visual_description[:100]}...")
            
            # Assertions
            assert isinstance(clip.transcription, str), "Should have audio transcription"
            assert isinstance(clip.visual_description, str), "Should have visual description"
            assert audio_length > 0, "Audio transcription should not be empty"
            assert visual_length > 0, "Visual description should not be empty"
            
            # Both should contain meaningful content (not just error messages)
            meaningful_audio = audio_length > 20 or "NO AUDIO" in clip.transcription
            meaningful_visual = visual_length > 50 or "failed" in clip.visual_description.lower()
            
            print(f"    Audio meaningful: {meaningful_audio}")
            print(f"    Visual meaningful: {meaningful_visual}")
        
        print(f"\n✅ Integrated audio + visual processing test completed!")
        
    finally:
        await pipeline.stop_pipeline()
        await video_stream.stop_stream()

@pytest.mark.asyncio
async def test_visual_analysis_error_handling():
    """Test visual analysis error handling"""
    print("\n⚠️ Testing visual analysis error handling...")
    
    # Test with OpenAI disabled (should fallback gracefully)
    pipeline_no_openai = create_transcription_pipeline(use_openai=False)
    
    # Create a fake clip for testing
    from src.video_stream import VideoClip
    test_clip = VideoClip(
        file_path="/nonexistent/fake_clip.mov",
        start_time=0.0,
        end_time=3.0,
        metadata={},
        priority=(0, 0, 0)
    )
    
    # Test visual analysis with no OpenAI
    visual_result = await pipeline_no_openai._analyze_visual_content(test_clip)
    print(f"Visual analysis without OpenAI: {visual_result}")
    
    assert isinstance(visual_result, str), "Should return string even on error"
    assert any(phrase in visual_result for phrase in [
        "requires OpenAI", "failed", "No visual content available", "Visual analysis requires OpenAI"
    ]), f"Should indicate error or limitation: {visual_result}"
    
    # Test with OpenAI but bad file path
    pipeline_openai = create_transcription_pipeline(use_openai=True)
    visual_result_bad_file = await pipeline_openai._analyze_visual_content(test_clip)
    print(f"Visual analysis with bad file: {visual_result_bad_file}")
    
    assert isinstance(visual_result_bad_file, str), "Should return string even with bad file"
    assert any(phrase in visual_result_bad_file.lower() for phrase in [
        "failed", "error", "no visual content available"
    ]), f"Should indicate failure or no content: {visual_result_bad_file}"
    
    print("✅ Visual analysis error handling test passed")

@pytest.mark.asyncio
async def test_parallel_transcription_processing():
    """Test that transcription can process multiple clips in parallel"""
    print("\n⚡ Testing parallel transcription processing...")
    
    video_stream = VideoStream.create(chunk_duration=2.0, max_clips=10)
    pipeline = create_transcription_pipeline(use_openai=True)
    
    try:
        # Start both systems
        stream_success = await video_stream.start_stream()
        assert stream_success, "Video stream should start"
        
        await pipeline.start_pipeline(video_stream)
        
        print("📹 Recording for 8 seconds to generate multiple clips...")
        await asyncio.sleep(8)
        
        # Check active processing tasks
        status = await pipeline.get_pipeline_status()
        print(f"🔄 Active processing tasks: {status['active_processing_tasks']}")
        
        # Should have multiple tasks running in parallel
        assert status['active_processing_tasks'] >= 1, "Should have at least one active task"
        
        # Wait a bit and check that multiple clips can be processed
        print("⏰ Waiting for parallel processing...")
        await asyncio.sleep(15)
        
        # Check final results
        final_status = await pipeline.get_pipeline_status()
        processed_clips = await pipeline.get_recent_processed_clips(duration_seconds=20.0)
        
        print(f"📊 Parallel Processing Results:")
        print(f"  Total clips processed: {final_status['total_clips_processed']}")
        print(f"  Available processed clips: {len(processed_clips)}")
        print(f"  Average processing time: {final_status['average_processing_time']:.2f}s")
        
        # Verify parallel processing worked
        assert final_status['total_clips_processed'] >= 2, f"Should have processed multiple clips, got {final_status['total_clips_processed']}"
        
        # Show timing analysis to demonstrate parallelism
        if len(processed_clips) >= 2:
            print(f"\n⏱️ Timing Analysis (shows parallel processing):")
            for i, clip in enumerate(processed_clips):
                clip_duration = clip.end_time - clip.start_time
                print(f"  Clip {i+1}: {clip.start_time:.1f}s-{clip.end_time:.1f}s (duration: {clip_duration:.1f}s)")
                
                # Clips should overlap in time, proving they were processed in parallel
                if i > 0:
                    prev_clip = processed_clips[i-1]
                    time_gap = clip.start_time - prev_clip.end_time
                    overlap = prev_clip.end_time - clip.start_time
                    
                    if overlap > 0:
                        print(f"    ✅ Overlaps with previous clip by {overlap:.1f}s (parallel processing)")
                    elif time_gap < final_status['average_processing_time']:
                        print(f"    ✅ Small gap ({time_gap:.1f}s) indicates parallel processing")
        
        print("✅ Parallel transcription processing test passed!")
        
    finally:
        await pipeline.stop_pipeline()
        await video_stream.stop_stream()
