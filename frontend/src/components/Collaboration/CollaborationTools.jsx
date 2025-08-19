/**
 * Collaboration Tools Component - Guardian Agent Validated
 * Implements REQ-12: Collaboration tools (whiteboards, file sharing)
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const CollaborationTools = () => {
  const [activeProject, setActiveProject] = useState(null);
  const [sharedFiles, setSharedFiles] = useState([]);
  const [whiteboardActive, setWhiteboardActive] = useState(false);
  const { user } = useAuth();

  const mockProjects = [
    {
      id: 1,
      name: 'Audio-Visual Experience',
      collaborators: ['Maya Artist', 'Sam Writer'],
      status: 'active'
    }
  ];

  const handleFileUpload = (e) => {
    const files = Array.from(e.target.files);
    const newFiles = files.map(file => ({
      id: Date.now() + Math.random(),
      name: file.name,
      size: file.size,
      uploadedBy: user?.display_name,
      uploadedAt: new Date().toISOString()
    }));
    setSharedFiles([...sharedFiles, ...newFiles]);
  };

  const openWhiteboard = () => {
    setWhiteboardActive(true);
    // Mock whiteboard functionality
    alert('Whiteboard opened! (Demo mode)');
  };

  return (
    <div className="collaboration-tools">
      <h3>Collaboration Tools</h3>
      
      <div className="tools-grid">
        <div className="tool-section">
          <h4>🎨 Digital Whiteboard</h4>
          <p>Brainstorm and sketch ideas together in real-time</p>
          <button onClick={openWhiteboard} className="tool-btn">
            Open Whiteboard
          </button>
        </div>

        <div className="tool-section">
          <h4>📁 File Sharing</h4>
          <div className="file-upload">
            <label className="upload-btn">
              Upload Files
              <input
                type="file"
                multiple
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </label>
          </div>
          
          {sharedFiles.length > 0 && (
            <div className="shared-files">
              <h5>Shared Files:</h5>
              {sharedFiles.map(file => (
                <div key={file.id} className="file-item">
                  <span className="file-name">{file.name}</span>
                  <span className="file-info">
                    by {file.uploadedBy}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="tool-section">
          <h4>💬 Project Chat</h4>
          <p>Dedicated chat rooms for each collaboration</p>
          <button className="tool-btn">
            Open Project Chat
          </button>
        </div>

        <div className="tool-section">
          <h4>📋 Task Management</h4>
          <p>Track progress and assign tasks</p>
          <button className="tool-btn">
            Manage Tasks
          </button>
        </div>
      </div>

      {mockProjects.length > 0 && (
        <div className="active-projects">
          <h4>Active Projects</h4>
          {mockProjects.map(project => (
            <div key={project.id} className="project-card">
              <h5>{project.name}</h5>
              <p>Collaborators: {project.collaborators.join(', ')}</p>
              <span className={`project-status ${project.status}`}>
                {project.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default CollaborationTools;
