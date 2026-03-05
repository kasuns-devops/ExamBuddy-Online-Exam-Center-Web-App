import React, { useState } from 'react';
import examService from '../../services/examService';
import './ProjectUploadForm.css';

const ProjectUploadForm = () => {
  const [projectName, setProjectName] = useState('');
  const [projectDescription, setProjectDescription] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('');
  const [ingestionStatus, setIngestionStatus] = useState(null);

  const onSubmit = async (event) => {
    event.preventDefault();

    if (!projectName.trim()) {
      setStatusMessage('Project name is required.');
      return;
    }

    if (!selectedFile) {
      setStatusMessage('Please select a PDF file.');
      return;
    }

    setIsSubmitting(true);
    setStatusMessage('Creating project and uploading PDF...');
    setIngestionStatus(null);

    try {
      const project = await examService.createProject({
        name: projectName.trim(),
        description: projectDescription.trim() || null,
      });

      const uploadResult = await examService.uploadProjectPdf(project.project_id, selectedFile);
      setIngestionStatus(uploadResult);
      setStatusMessage('Project ingestion completed.');

      setProjectName('');
      setProjectDescription('');
      setSelectedFile(null);
    } catch (error) {
      setStatusMessage(error.message || 'Project ingestion failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="project-upload-card">
      <h2>Create Project + Upload PDF</h2>
      <form className="project-upload-form" onSubmit={onSubmit}>
        <label className="project-upload-label">
          Project Name
          <input
            type="text"
            value={projectName}
            onChange={(event) => setProjectName(event.target.value)}
            className="project-upload-input"
            maxLength={200}
            required
          />
        </label>

        <label className="project-upload-label">
          Description
          <textarea
            value={projectDescription}
            onChange={(event) => setProjectDescription(event.target.value)}
            className="project-upload-input"
            rows={3}
            maxLength={1000}
          />
        </label>

        <label className="project-upload-label">
          PDF Question File
          <input
            type="file"
            accept="application/pdf,.pdf"
            onChange={(event) => setSelectedFile(event.target.files?.[0] || null)}
            className="project-upload-input"
            required
          />
        </label>

        <button type="submit" className="project-upload-submit" disabled={isSubmitting}>
          {isSubmitting ? 'Uploading...' : 'Create + Upload'}
        </button>

        {statusMessage && <p className="project-upload-status">{statusMessage}</p>}

        {ingestionStatus && (
          <div className="project-upload-result">
            <p><strong>Project ID:</strong> {ingestionStatus.project_id}</p>
            <p><strong>Status:</strong> {ingestionStatus.status}</p>
            <p><strong>Question Count:</strong> {ingestionStatus.question_count ?? 0}</p>
          </div>
        )}
      </form>
    </div>
  );
};

export default ProjectUploadForm;
