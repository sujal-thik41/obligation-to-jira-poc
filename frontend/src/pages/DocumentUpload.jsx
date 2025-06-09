import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { useObligations } from '../context/ObligationContext';

const DocumentUpload = () => {
  const [file, setFile] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);
  const navigate = useNavigate();
  
  const { uploadDocument, loading, error } = useObligations();

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    
    try {
      // Simulate upload progress
      const interval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 95) {
            clearInterval(interval);
            return 95;
          }
          return prev + 5;
        });
      }, 100);
      
      await uploadDocument(file);
      
      clearInterval(interval);
      setUploadProgress(100);
      
      // Navigate to obligations list after successful upload
      setTimeout(() => {
        navigate('/obligations');
      }, 1000);
    } catch (err) {
      console.error('Upload failed:', err);
    }
  };

  const isValidFileType = file && (
    file.type === 'application/pdf' || 
    file.type === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' ||
    file.type === 'application/docx'
  );

  return (
    <div className="max-w-3xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-800">Upload Document</h1>
        <p className="text-gray-600 mt-2">
          Upload a PDF or DOCX file to extract obligations
        </p>
      </div>

      <div 
        className={`border-2 border-dashed rounded-lg p-8 text-center ${
          isDragging ? 'border-indigo-500 bg-indigo-50' : 'border-gray-300'
        } ${loading ? 'opacity-50' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
      >
        <input
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          accept=".pdf,.docx"
          className="hidden"
          disabled={loading}
        />
        
        {!file ? (
          <div>
            <svg 
              className="mx-auto h-12 w-12 text-gray-400" 
              stroke="currentColor" 
              fill="none" 
              viewBox="0 0 48 48" 
              aria-hidden="true"
            >
              <path 
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" 
                strokeWidth={2} 
                strokeLinecap="round" 
                strokeLinejoin="round" 
              />
            </svg>
            <p className="mt-2 text-sm text-gray-600">
              Drag and drop a file here, or{' '}
              <button
                type="button"
                className="text-indigo-600 hover:text-indigo-500 font-medium"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
              >
                browse
              </button>{' '}
              to select a file
            </p>
            <p className="mt-1 text-xs text-gray-500">PDF or DOCX up to 10MB</p>
          </div>
        ) : (
          <div>
            <div className="flex items-center justify-center mb-4">
              <svg 
                className="h-8 w-8 text-indigo-500" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path 
                  fillRule="evenodd" 
                  d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" 
                  clipRule="evenodd" 
                />
              </svg>
              <span className="ml-2 text-gray-700">{file.name}</span>
            </div>
            
            <button
              type="button"
              className="text-sm text-gray-600 hover:text-gray-500"
              onClick={() => setFile(null)}
              disabled={loading}
            >
              Change file
            </button>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-4 bg-red-50 p-4 rounded-md">
          <div className="flex">
            <div className="flex-shrink-0">
              <svg 
                className="h-5 w-5 text-red-400" 
                fill="currentColor" 
                viewBox="0 0 20 20"
              >
                <path 
                  fillRule="evenodd" 
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" 
                  clipRule="evenodd" 
                />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">Upload Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      {uploadProgress > 0 && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-indigo-600 h-2.5 rounded-full" 
              style={{ width: `${uploadProgress}%` }}
            ></div>
          </div>
          <p className="text-sm text-gray-600 mt-1 text-right">
            {uploadProgress === 100 ? 'Complete!' : `${uploadProgress}%`}
          </p>
        </div>
      )}

      <div className="mt-6 flex justify-end">
        <button
          type="button"
          className={`px-4 py-2 rounded-md text-white font-medium ${
            file && isValidFileType && !loading
              ? 'bg-indigo-600 hover:bg-indigo-700'
              : 'bg-gray-300 cursor-not-allowed'
          }`}
          onClick={handleUpload}
          disabled={!file || !isValidFileType || loading}
        >
          {loading ? 'Processing...' : 'Extract Obligations'}
        </button>
      </div>
    </div>
  );
};

export default DocumentUpload;
