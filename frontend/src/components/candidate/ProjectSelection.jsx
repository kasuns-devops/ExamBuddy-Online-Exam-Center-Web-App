/**
 * Project Selection Component - List available projects/exams
 */
import React, { useState, useEffect } from 'react';
import './ProjectSelection.css';

const ProjectSelection = ({ onSelectProject }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    // TODO: Replace with actual API call when admin creates projects
    // For now, use mock data
    setTimeout(() => {
      setProjects([
        {
          id: 'demo-project-id',
          name: 'ExamBuddy Sample Question Bank',
          description: 'Mixed sample set (easy/medium/hard, core conceptual + scenario style)',
          questionCount: 10,
          difficulty: 'Mixed',
          topics: ['General Knowledge', 'Programming', 'SQL', 'AWS', 'Security']
        }
      ]);
      setLoading(false);
    }, 500);
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
          <p>There are currently no exams available to take.</p>
          <p>Please contact your administrator to create exams.</p>
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
              <span className="difficulty">
                📊 Difficulty: {project.difficulty}
              </span>
              <div className="topics">
                {project.topics.map((topic, idx) => (
                  <span key={idx} className="topic-tag">{topic}</span>
                ))}
              </div>
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
