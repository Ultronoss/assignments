import React, { useState, useRef, useEffect, useCallback } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize, Loader2, Lock } from 'lucide-react';

interface VideoPlayerProps {
  fileId: number;
  filename: string;
  onClose: () => void;
}

interface StreamingChunk {
  request_id: string;
  file_id: number;
  chunk_index: number;
  chunk_data: string;
  is_final: boolean;
  content_type: string;
  status?: string;
  error?: string;
}

const VideoPlayer: React.FC<VideoPlayerProps> = ({ fileId, filename, onClose }) => {
  console.log('VideoPlayer rendered with fileId:', fileId, 'filename:', filename);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [volume, setVolume] = useState(1);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [encryptionKey, setEncryptionKey] = useState('');
  const [showKeyInput, setShowKeyInput] = useState(true);
  const [streamingStatus, setStreamingStatus] = useState<string>('idle');
  const [progress, setProgress] = useState(0);

  const videoRef = useRef<HTMLVideoElement>(null);
  const mediaSourceRef = useRef<MediaSource | null>(null);
  const sourceBufferRef = useRef<SourceBuffer | null>(null);
  const chunksRef = useRef<StreamingChunk[]>([]);
  const requestIdRef = useRef<string | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const eventSourceRef = useRef<EventSource | null>(null);

  // Cleanup function
  const cleanup = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
    }
    if (mediaSourceRef.current && mediaSourceRef.current.readyState === 'open') {
      mediaSourceRef.current.endOfStream();
    }
    chunksRef.current = [];
  }, []);

  useEffect(() => {
    return cleanup;
  }, [cleanup]);

  const handleKeySubmit = async () => {
    if (!encryptionKey.trim()) {
      setError('Please enter an encryption key');
      return;
    }

    setIsLoading(true);
    setError(null);
    setShowKeyInput(false);
    setStreamingStatus('initiating');

    try {
      // Initiate streaming request
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/stream/${fileId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ encryption_key: encryptionKey }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to initiate streaming');
      }

      const data = await response.json();
      requestIdRef.current = data.request_id;
      setStreamingStatus('streaming');

      // Start receiving video chunks
      await startVideoStreaming(data.request_id);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to start streaming');
      setShowKeyInput(true);
      setStreamingStatus('error');
    } finally {
      setIsLoading(false);
    }
  };

  const startVideoStreaming = async (requestId: string) => {
    // Try WebSocket first, fallback to Server-Sent Events
    try {
      await startWebSocketStreaming(requestId);
    } catch (err) {
      console.log('WebSocket failed, trying Server-Sent Events:', err);
      await startEventSourceStreaming(requestId);
    }
  };

  const startWebSocketStreaming = (requestId: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(`ws://localhost:8000/api/ws/stream/${requestId}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        resolve();
      };

      ws.onmessage = (event) => {
        const chunk: StreamingChunk = JSON.parse(event.data);
        handleVideoChunk(chunk);
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(new Error('WebSocket connection failed'));
      };

      ws.onclose = () => {
        console.log('WebSocket closed');
      };
    });
  };

  const startEventSourceStreaming = (requestId: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const apiUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
      const eventSource = new EventSource(`${apiUrl}/api/stream/${fileId}/chunks/${requestId}`);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        console.log('EventSource connected');
        resolve();
      };

      eventSource.onmessage = (event) => {
        const chunk: StreamingChunk = JSON.parse(event.data);
        handleVideoChunk(chunk);
      };

      eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        reject(new Error('EventSource connection failed'));
      };
    });
  };

  const handleVideoChunk = (chunk: StreamingChunk) => {
    if (chunk.status === 'error') {
      setError(chunk.error || 'Streaming error occurred');
      setStreamingStatus('error');
      return;
    }

    if (chunk.status === 'completed') {
      setStreamingStatus('completed');
      return;
    }

    // Store chunk
    chunksRef.current.push(chunk);

    // Initialize MediaSource if not already done
    if (!mediaSourceRef.current) {
      initializeMediaSource();
    }

    // Update progress
    const totalChunks = chunk.chunk_index + 1;
    setProgress((totalChunks / Math.max(totalChunks + 1, 1)) * 100);

    // Add chunk to source buffer
    if (sourceBufferRef.current && !sourceBufferRef.current.updating) {
      try {
        const chunkData = atob(chunk.chunk_data);
        const uint8Array = new Uint8Array(chunkData.length);
        for (let i = 0; i < chunkData.length; i++) {
          uint8Array[i] = chunkData.charCodeAt(i);
        }
        
        sourceBufferRef.current.appendBuffer(uint8Array);
      } catch (err) {
        console.error('Error appending chunk:', err);
      }
    }
  };

  const initializeMediaSource = () => {
    if (!videoRef.current) return;

    const mediaSource = new MediaSource();
    mediaSourceRef.current = mediaSource;

    mediaSource.addEventListener('sourceopen', () => {
      const sourceBuffer = mediaSource.addSourceBuffer('video/mp4; codecs="avc1.42E01E, mp4a.40.2"');
      sourceBufferRef.current = sourceBuffer;

      sourceBuffer.addEventListener('updateend', () => {
        if (sourceBuffer.updating) return;
        
        // Check if we have enough data to start playing
        if (mediaSource.readyState === 'open' && chunksRef.current.length > 0) {
          mediaSource.endOfStream();
          setStreamingStatus('ready');
        }
      });

      sourceBuffer.addEventListener('error', (e) => {
        console.error('SourceBuffer error:', e);
        setError('Error processing video data');
      });
    });

    mediaSource.addEventListener('error', (e) => {
      console.error('MediaSource error:', e);
      setError('Error initializing video player');
    });

    videoRef.current.src = URL.createObjectURL(mediaSource);
  };

  const togglePlay = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const toggleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen();
      }
    }
  };

  if (showKeyInput) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-6 w-96">
          <div className="flex items-center mb-4">
            <Lock className="h-6 w-6 text-blue-500 mr-2" />
            <h2 className="text-xl font-semibold">Enter Encryption Key</h2>
          </div>
          <p className="text-gray-600 mb-4">
            Enter the encryption key to decrypt and play the video: <strong>{filename}</strong>
          </p>
          <input
            type="password"
            value={encryptionKey}
            onChange={(e) => setEncryptionKey(e.target.value)}
            placeholder="Enter encryption key"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            onKeyPress={(e) => {
              if (e.key === 'Enter') {
                handleKeySubmit();
              }
            }}
          />
          {error && (
            <p className="text-red-500 text-sm mt-2">{error}</p>
          )}
          <div className="flex justify-end space-x-2 mt-4">
            <button
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:text-gray-800"
            >
              Cancel
            </button>
            <button
              onClick={handleKeySubmit}
              disabled={isLoading}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:opacity-50 flex items-center"
            >
              {isLoading ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                  Loading...
                </>
              ) : (
                'Play Video'
              )}
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black flex items-center justify-center z-50">
      <div className="relative w-full h-full max-w-6xl max-h-[90vh]">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 bg-black bg-opacity-50 text-white rounded-full p-2 hover:bg-opacity-75"
        >
          ✕
        </button>

        {/* Video container */}
        <div className="relative w-full h-full">
          <video
            ref={videoRef}
            className="w-full h-full object-contain"
            onTimeUpdate={handleTimeUpdate}
            onLoadedMetadata={handleLoadedMetadata}
            onPlay={() => setIsPlaying(true)}
            onPause={() => setIsPlaying(false)}
            onError={() => setError('Video playback error')}
          />

          {/* Loading overlay */}
          {isLoading && (
            <div className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center">
              <div className="text-white text-center">
                <Loader2 className="h-8 w-8 animate-spin mx-auto mb-2" />
                <p>Initializing video stream...</p>
                {streamingStatus === 'streaming' && (
                  <div className="mt-2">
                    <div className="w-64 bg-gray-700 rounded-full h-2">
                      <div 
                        className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress}%` }}
                      ></div>
                    </div>
                    <p className="text-sm mt-1">Receiving video data... {Math.round(progress)}%</p>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Error overlay */}
          {error && (
            <div className="absolute inset-0 bg-black bg-opacity-75 flex items-center justify-center">
              <div className="text-white text-center">
                <p className="text-red-400 mb-4">{error}</p>
                <button
                  onClick={() => {
                    setError(null);
                    setShowKeyInput(true);
                    cleanup();
                  }}
                  className="px-4 py-2 bg-blue-500 rounded-md hover:bg-blue-600"
                >
                  Try Again
                </button>
              </div>
            </div>
          )}

          {/* Video controls */}
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4">
            <div className="flex items-center space-x-4">
              {/* Play/Pause button */}
              <button
                onClick={togglePlay}
                className="text-white hover:text-gray-300"
                disabled={streamingStatus !== 'ready'}
              >
                {isPlaying ? <Pause className="h-6 w-6" /> : <Play className="h-6 w-6" />}
              </button>

              {/* Time display */}
              <div className="text-white text-sm">
                {formatTime(currentTime)} / {formatTime(duration)}
              </div>

              {/* Progress bar */}
              <div className="flex-1">
                <input
                  type="range"
                  min="0"
                  max={duration || 0}
                  value={currentTime}
                  onChange={handleSeek}
                  className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                  disabled={streamingStatus !== 'ready'}
                />
              </div>

              {/* Volume controls */}
              <div className="flex items-center space-x-2">
                <button
                  onClick={toggleMute}
                  className="text-white hover:text-gray-300"
                >
                  {isMuted ? <VolumeX className="h-4 w-4" /> : <Volume2 className="h-4 w-4" />}
                </button>
                <input
                  type="range"
                  min="0"
                  max="1"
                  step="0.1"
                  value={volume}
                  onChange={handleVolumeChange}
                  className="w-16 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer slider"
                />
              </div>

              {/* Fullscreen button */}
              <button
                onClick={toggleFullscreen}
                className="text-white hover:text-gray-300"
              >
                <Maximize className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoPlayer; 