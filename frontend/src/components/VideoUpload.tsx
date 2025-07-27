import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Lock, AlertCircle, CheckCircle } from 'lucide-react';
import { encryptFile } from '../utils/encryption';
import { UploadProgress } from '../types';

interface VideoUploadProps {
  onUploadSuccess: () => void;
}

const VideoUpload: React.FC<VideoUploadProps> = ({ onUploadSuccess }) => {
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState<UploadProgress | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [encryptionKey, setEncryptionKey] = useState('');

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    
    // Validate file type
    if (!file.type.startsWith('video/')) {
      setError('Please select a valid video file');
      return;
    }

    // Validate file size (100MB limit)
    if (file.size > 100 * 1024 * 1024) {
      setError('File size must be less than 100MB');
      return;
    }

    if (!encryptionKey.trim()) {
      setError('Please enter an encryption key');
      return;
    }

    try {
      setUploading(true);
      setError(null);
      setSuccess(null);

      // Encrypt the file
      const encryptedFile = await encryptFile(file, encryptionKey);

      // Create FormData
      const formData = new FormData();
      formData.append('file', encryptedFile, file.name);
      formData.append('encryption_key', encryptionKey);

      // Upload to server
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          setProgress({
            loaded: event.loaded,
            total: event.total,
            percentage: Math.round((event.loaded / event.total) * 100)
          });
        }
      });

      xhr.addEventListener('load', () => {
        if (xhr.status === 200) {
          setSuccess('File uploaded successfully!');
          setEncryptionKey('');
          onUploadSuccess();
        } else {
          setError('Upload failed. Please try again.');
        }
        setUploading(false);
        setProgress(null);
      });

      xhr.addEventListener('error', () => {
        setError('Upload failed. Please check your connection.');
        setUploading(false);
        setProgress(null);
      });

      xhr.open('POST', '/api/upload');
      xhr.send(formData);

    } catch (err) {
      setError('Encryption failed. Please try again.');
      setUploading(false);
      setProgress(null);
    }
  }, [encryptionKey, onUploadSuccess]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mkv', '.m4v']
    },
    multiple: false,
    disabled: uploading
  });

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Upload Video File
      </h3>

      {/* Encryption Key Input */}
      <div className="mb-4">
        <label htmlFor="encryption-key" className="block text-sm font-medium text-gray-700 mb-2">
          Encryption Key
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-4 w-4" />
          <input
            type="password"
            id="encryption-key"
            value={encryptionKey}
            onChange={(e) => setEncryptionKey(e.target.value)}
            placeholder="Enter your encryption key"
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            disabled={uploading}
          />
        </div>
        <p className="text-xs text-gray-500 mt-1">
          This key will be used to encrypt your video before upload. Keep it safe!
        </p>
      </div>

      {/* Drop Zone */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        {isDragActive ? (
          <p className="text-blue-600">Drop the video file here...</p>
        ) : (
          <div>
            <p className="text-gray-600 mb-2">
              Drag and drop a video file here, or click to select
            </p>
            <p className="text-sm text-gray-500">
              Supported formats: MP4, AVI, MOV, WMV, FLV, WebM, MKV, M4V
            </p>
          </div>
        )}
      </div>

      {/* Progress Bar */}
      {progress && (
        <div className="mt-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Uploading...</span>
            <span>{progress.percentage}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress.percentage}%` }}
            ></div>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mt-4 flex items-center p-3 bg-red-50 border border-red-200 rounded-md">
          <AlertCircle className="h-5 w-5 text-red-500 mr-2" />
          <span className="text-red-700">{error}</span>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mt-4 flex items-center p-3 bg-green-50 border border-green-200 rounded-md">
          <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
          <span className="text-green-700">{success}</span>
        </div>
      )}
    </div>
  );
};

export default VideoUpload; 