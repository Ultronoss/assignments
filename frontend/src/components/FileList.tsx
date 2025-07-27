import React, { useState } from 'react';
import { Download, Trash2, FileVideo, Calendar, HardDrive, Play } from 'lucide-react';
import { FileInfo } from '../types';
import VideoPlayer from './VideoPlayer';

interface FileListProps {
  files: FileInfo[];
  onFileDeleted: () => void;
}

const FileList: React.FC<FileListProps> = ({ files, onFileDeleted }) => {
  const [downloading, setDownloading] = useState<number | null>(null);
  const [deleting, setDeleting] = useState<number | null>(null);
  const [encryptionKey, setEncryptionKey] = useState('');
  const [showKeyInput, setShowKeyInput] = useState<number | null>(null);
  const [playingFile, setPlayingFile] = useState<FileInfo | null>(null);

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const handleDownload = async (file: FileInfo) => {
    if (!encryptionKey.trim()) {
      setShowKeyInput(file.id);
      return;
    }

    try {
      setDownloading(file.id);
      setShowKeyInput(null);

      const response = await fetch(`/api/files/${file.id}/decrypt`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ encryption_key: encryptionKey }),
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = file.original_filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        setEncryptionKey('');
      } else {
        const error = await response.json();
        alert(`Download failed: ${error.detail}`);
      }
    } catch (error) {
      alert('Download failed. Please check your encryption key.');
    } finally {
      setDownloading(null);
    }
  };

  const handleDelete = async (fileId: number) => {
    if (!window.confirm('Are you sure you want to delete this file?')) {
      return;
    }

    try {
      setDeleting(fileId);
      const response = await fetch(`/api/files/${fileId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        onFileDeleted();
      } else {
        alert('Failed to delete file');
      }
    } catch (error) {
      alert('Failed to delete file');
    } finally {
      setDeleting(null);
    }
  };

  const handlePlay = (file: FileInfo) => {
    console.log('Play button clicked for file:', file);
    setPlayingFile(file);
  };

  if (files.length === 0) {
    return (
      <div className="text-center py-12">
        <FileVideo className="mx-auto h-12 w-12 text-gray-400 mb-4" />
        <p className="text-gray-500">No files uploaded yet</p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {files.map((file) => (
        <div key={file.id} className="bg-white rounded-lg shadow-sm border p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex-shrink-0">
                <FileVideo className="h-8 w-8 text-blue-500" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-gray-900 truncate">
                  {file.original_filename}
                </p>
                <div className="flex items-center space-x-4 text-xs text-gray-500">
                  <div className="flex items-center">
                    <HardDrive className="h-3 w-3 mr-1" />
                    {formatFileSize(file.file_size)}
                  </div>
                  <div className="flex items-center">
                    <Calendar className="h-3 w-3 mr-1" />
                    {formatDate(file.upload_date)}
                  </div>
                </div>
                <div className="mt-1">
                  <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                    file.processing_status === 'processed' 
                      ? 'bg-green-100 text-green-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {file.processing_status}
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {/* Encryption Key Input */}
              {showKeyInput === file.id && (
                <input
                  type="password"
                  value={encryptionKey}
                  onChange={(e) => setEncryptionKey(e.target.value)}
                  placeholder="Enter encryption key"
                  className="px-3 py-1 border border-gray-300 rounded text-sm"
                  onKeyPress={(e) => {
                    if (e.key === 'Enter') {
                      handleDownload(file);
                    }
                  }}
                />
              )}
              
              {/* Play Button */}
              <button
                onClick={() => handlePlay(file)}
                disabled={!file.is_processed}
                className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-green-700 bg-green-100 hover:bg-green-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
              >
                <Play className="h-4 w-4 mr-1" />
                Play
              </button>
              
              {/* Download Button */}
              <button
                onClick={() => handleDownload(file)}
                disabled={downloading === file.id}
                className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-blue-700 bg-blue-100 hover:bg-blue-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
              >
                {downloading === file.id ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                ) : (
                  <Download className="h-4 w-4 mr-1" />
                )}
                Download
              </button>
              
              {/* Delete Button */}
              <button
                onClick={() => handleDelete(file.id)}
                disabled={deleting === file.id}
                className="inline-flex items-center px-3 py-1 border border-transparent text-sm font-medium rounded-md text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 disabled:opacity-50"
              >
                {deleting === file.id ? (
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-red-600"></div>
                ) : (
                  <Trash2 className="h-4 w-4 mr-1" />
                )}
                Delete
              </button>
            </div>
          </div>
        </div>
      ))}
      
      {/* Video Player Modal */}
      {playingFile && (
        <VideoPlayer
          fileId={playingFile.id}
          filename={playingFile.original_filename}
          onClose={() => setPlayingFile(null)}
        />
      )}
    </div>
  );
};

export default FileList; 