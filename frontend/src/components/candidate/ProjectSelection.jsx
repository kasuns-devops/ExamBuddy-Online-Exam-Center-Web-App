/**
 * Project Selection Component - List available projects/exams
 */
import React, { useState, useEffect } from 'react';
import examService from '../../services/examService';
import './ProjectSelection.css';

const ProjectSelection = ({ onSelectProject }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    setError('');
    try {
      const items = await examService.listAvailableProjects();
      setProjects(items);
    } catch (err) {
      setProjects([]);
      setError(err.message || 'Failed to load exams.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="project-selection">
        <div className="loading">Loading available exams...</div>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="project-selection">
        <div className="no-projects">
          <h2>📋 No Exams Available</h2>
          {error ? (
            <>
              <p>{error}</p>
              <button className="retry-btn" onClick={loadProjects}>Retry</button>
            </>
          ) : (
            <>
              <p>There are currently no exams available to take.</p>
              <p>Please contact your administrator to create exams.</p>
            </>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="project-selection">
      <h1>📚 Select an Exam</h1>
      <p className="subtitle">Choose an exam to begin</p>
      
      <div className="projects-grid">
        {projects.map((project) => (
          <div 
            key={project.id} 
            className="project-card"
            onClick={() => onSelectProject(project)}
          >
            <div className="project-header">
              <h3>{project.name}</h3>
              <span className="question-count">{project.questionCount} Questions</span>
            </div>
            
            <p className="project-description">{project.description}</p>
            
            <div className="project-meta">
              <span className="difficulty">📊 Ready for test or exam mode</span>
            </div>
            
            <button className="start-btn">
              Start Exam →
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectSelection;
