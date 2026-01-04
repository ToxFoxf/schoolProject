import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { projectsAPI, issuesAPI } from '../../services/api';
import { Plus, FileText, Trash2, Edit2 } from 'lucide-react';
import './Projects.css';

const Projects = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [issues, setIssues] = useState([]);
  const [showNewProjectModal, setShowNewProjectModal] = useState(false);
  const [showNewIssueModal, setShowNewIssueModal] = useState(false);
  const [loading, setLoading] = useState(true);
  const [newProject, setNewProject] = useState({ name: '', description: '' });
  const [newIssue, setNewIssue] = useState({ title: '', description: '', priority: 'Medium' });

  useEffect(() => {
    fetchProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      fetchIssues(selectedProject.id);
    }
  }, [selectedProject]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await projectsAPI.getAll();
      setProjects(data);
      if (data.length > 0 && !selectedProject) {
        setSelectedProject(data[0]);
      }
    } catch (error) {
      console.error('Error fetching projects:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchIssues = async (projectId) => {
    try {
      const data = await issuesAPI.getByProject(projectId);
      setIssues(data);
    } catch (error) {
      console.error('Error fetching issues:', error);
    }
  };

  const handleCreateProject = async (e) => {
    e.preventDefault();
    try {
      const projectData = {
        name: newProject.name,
        description: newProject.description,
        icon: '📦',
        color: '#5e6ad2'
      };
      const created = await projectsAPI.create(projectData);
      setProjects([...projects, created]);
      setNewProject({ name: '', description: '' });
      setShowNewProjectModal(false);
    } catch (error) {
      console.error('Error creating project:', error);
    }
  };

  const handleCreateIssue = async (e) => {
    e.preventDefault();
    if (!selectedProject) return;
    
    try {
      const issueData = {
        title: newIssue.title,
        description: newIssue.description,
        projectId: selectedProject.id,
        priority: newIssue.priority
      };
      const created = await issuesAPI.create(issueData);
      setIssues([...issues, created]);
      setNewIssue({ title: '', description: '', priority: 'Medium' });
      setShowNewIssueModal(false);
    } catch (error) {
      console.error('Error creating issue:', error);
    }
  };

  const handleDeleteProject = async (id) => {
    if (window.confirm('Delete this project?')) {
      try {
        await projectsAPI.delete(id);
        setProjects(projects.filter(p => p.id !== id));
        if (selectedProject?.id === id) {
          setSelectedProject(projects[0] || null);
        }
      } catch (error) {
        console.error('Error deleting project:', error);
      }
    }
  };

  const handleDeleteIssue = async (id) => {
    if (window.confirm('Delete this issue?')) {
      try {
        await issuesAPI.delete(id);
        setIssues(issues.filter(i => i.id !== id));
      } catch (error) {
        console.error('Error deleting issue:', error);
      }
    }
  };

  const handleStatusChange = async (issueId, newStatus) => {
    try {
      const updated = await issuesAPI.updateStatus(issueId, newStatus);
      setIssues(issues.map(i => i.id === issueId ? updated : i));
    } catch (error) {
      console.error('Error updating issue status:', error);
    }
  };

  const statusOptions = ['Backlog', 'Todo', 'In Progress', 'In Review', 'Done'];
  const priorityOptions = ['Low', 'Medium', 'High', 'Urgent'];

  const getStatusColor = (status) => {
    const colors = {
      'Backlog': '#8a8f98',
      'Todo': '#5e6ad2',
      'In Progress': '#f59e0b',
      'In Review': '#8b5cf6',
      'Done': '#10b981'
    };
    return colors[status] || '#8a8f98';
  };

  const getPriorityColor = (priority) => {
    const colors = {
      'Low': '#10b981',
      'Medium': '#3b82f6',
      'High': '#f59e0b',
      'Urgent': '#ef4444'
    };
    return colors[priority] || '#8a8f98';
  };

  if (loading) {
    return <div className="projects-container">Loading...</div>;
  }

  return (
    <div className="projects-container">
      <div className="projects-sidebar">
        <div className="projects-header">
          <h2>Projects</h2>
          <button 
            className="btn-icon"
            onClick={() => setShowNewProjectModal(true)}
            title="New project"
          >
            <Plus size={20} />
          </button>
        </div>

        <div className="projects-list">
          {projects.map(project => (
            <div
              key={project.id}
              className={`project-item ${selectedProject?.id === project.id ? 'active' : ''}`}
              onClick={() => setSelectedProject(project)}
            >
              <div className="project-item-left">
                <span className="project-icon">{project.icon}</span>
                <span className="project-name">{project.name}</span>
              </div>
              <button
                className="btn-delete"
                onClick={(e) => {
                  e.stopPropagation();
                  handleDeleteProject(project.id);
                }}
              >
                <Trash2 size={16} />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="projects-main">
        {selectedProject ? (
          <>
            <div className="project-header">
              <div>
                <h1>{selectedProject.name}</h1>
                <p className="project-description">{selectedProject.description}</p>
              </div>
              <button 
                className="btn-primary"
                onClick={() => setShowNewIssueModal(true)}
              >
                <Plus size={20} />
                New Issue
              </button>
            </div>

            <div className="issues-board">
              {statusOptions.map(status => (
                <div key={status} className="status-column">
                  <div className="column-header">
                    <span className="status-badge" style={{ borderColor: getStatusColor(status) }}>
                      {status}
                    </span>
                    <span className="issue-count">{issues.filter(i => i.status === status).length}</span>
                  </div>

                  <div className="issues-column">
                    {issues.filter(i => i.status === status).map(issue => (
                      <div key={issue.id} className="issue-card">
                        <div className="issue-header">
                          <h4>{issue.title}</h4>
                          <button
                            className="btn-delete-small"
                            onClick={() => handleDeleteIssue(issue.id)}
                          >
                            <Trash2 size={14} />
                          </button>
                        </div>

                        <p className="issue-description">{issue.description}</p>

                        <div className="issue-meta">
                          <select
                            className="status-select"
                            value={issue.status}
                            onChange={(e) => handleStatusChange(issue.id, e.target.value)}
                          >
                            {statusOptions.map(s => (
                              <option key={s} value={s}>{s}</option>
                            ))}
                          </select>

                          <span 
                            className="priority-badge"
                            style={{ backgroundColor: getPriorityColor(issue.priority) }}
                          >
                            {issue.priority}
                          </span>
                        </div>

                        {issue.dueDate && (
                          <div className="issue-due-date">
                            Due: {new Date(issue.dueDate).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : (
          <div className="no-project">
            <FileText size={48} />
            <p>No projects yet. Create one to get started!</p>
          </div>
        )}
      </div>

      {/* New Project Modal */}
      {showNewProjectModal && (
        <div className="modal-overlay" onClick={() => setShowNewProjectModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Project</h2>
            <form onSubmit={handleCreateProject}>
              <div className="form-group">
                <label>Project Name</label>
                <input
                  type="text"
                  value={newProject.name}
                  onChange={(e) => setNewProject({ ...newProject, name: e.target.value })}
                  placeholder="Enter project name"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newProject.description}
                  onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                  placeholder="Enter project description"
                />
              </div>
              <div className="modal-buttons">
                <button type="button" className="btn-cancel" onClick={() => setShowNewProjectModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* New Issue Modal */}
      {showNewIssueModal && (
        <div className="modal-overlay" onClick={() => setShowNewIssueModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <h2>Create New Issue</h2>
            <form onSubmit={handleCreateIssue}>
              <div className="form-group">
                <label>Title</label>
                <input
                  type="text"
                  value={newIssue.title}
                  onChange={(e) => setNewIssue({ ...newIssue, title: e.target.value })}
                  placeholder="Enter issue title"
                  required
                />
              </div>
              <div className="form-group">
                <label>Description</label>
                <textarea
                  value={newIssue.description}
                  onChange={(e) => setNewIssue({ ...newIssue, description: e.target.value })}
                  placeholder="Enter issue description"
                />
              </div>
              <div className="form-group">
                <label>Priority</label>
                <select
                  value={newIssue.priority}
                  onChange={(e) => setNewIssue({ ...newIssue, priority: e.target.value })}
                >
                  {priorityOptions.map(p => (
                    <option key={p} value={p}>{p}</option>
                  ))}
                </select>
              </div>
              <div className="modal-buttons">
                <button type="button" className="btn-cancel" onClick={() => setShowNewIssueModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn-primary">Create</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Projects;
