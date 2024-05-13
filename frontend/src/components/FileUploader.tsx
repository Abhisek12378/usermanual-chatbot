import React from 'react';

interface FileUploaderProps {
  onFileSelected: (file: File) => void; // Callback when a file is selected
}

const FileUploader: React.FC<FileUploaderProps> = ({ onFileSelected }) => {
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files ? event.target.files[0] : null;
    if (selectedFile) {
      onFileSelected(selectedFile); // Notify parent component about the file selection
    }
  };

  return (
    <div>
      <input type="file" onChange={handleFileChange} />
    </div>
  );
};

export default FileUploader;
