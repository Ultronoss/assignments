import React, { useState, useEffect } from 'react';
import VideoUpload from './components/VideoUpload';
import FileList from './components/FileList';
import { FileInfo } from './types';

function App() {
  const [files, setFiles] = useState<FileInfo[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchFiles = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/files');
      if (response.ok) {
        const data = await response.json();
        setFiles(data);
      }
    } catch (error) {
      console.error('Error fetching files:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchFiles();
  }, []);

  const handleUploadSuccess = () => {
    fetchFiles();
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Secure Video Upload
          </h1>
          <p className="text-gray-600">
            Upload your videos with client-side encryption for enhanced security
          </p>
        </header>

        <div className="max-w-4xl mx-auto">
          <VideoUpload onUploadSuccess={handleUploadSuccess} />
          
          <div className="mt-12">
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Uploaded Files
            </h2>
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              </div>
            ) : (
              <FileList files={files} onFileDeleted={handleUploadSuccess} />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App; 