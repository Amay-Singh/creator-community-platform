/**
 * Meeting Invite Modal Component - Guardian Agent Validated
 * Implements REQ-10: Meeting invite setup
 */
import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

const MeetingInviteModal = ({ isOpen, onClose, recipient }) => {
  const [meetingData, setMeetingData] = useState({
    title: '',
    description: '',
    date: '',
    time: '',
    duration: 60,
    platform: 'zoom'
  });
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      // Mock API call - replace with actual implementation
      console.log('Sending meeting invite:', { ...meetingData, recipient });
      
      // Simulate API delay
      setTimeout(() => {
        alert('Meeting invite sent successfully!');
        onClose();
        setLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Failed to send meeting invite:', error);
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    setMeetingData({
      ...meetingData,
      [e.target.name]: e.target.value
    });
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <div className="modal-header">
          <h3>Schedule Meeting</h3>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <form onSubmit={handleSubmit} className="meeting-form">
          <div className="form-group">
            <label>Meeting Title:</label>
            <input
              type="text"
              name="title"
              value={meetingData.title}
              onChange={handleInputChange}
              required
              placeholder="Enter meeting title"
            />
          </div>

          <div className="form-group">
            <label>Description:</label>
            <textarea
              name="description"
              value={meetingData.description}
              onChange={handleInputChange}
              placeholder="Meeting description (optional)"
            />
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Date:</label>
              <input
                type="date"
                name="date"
                value={meetingData.date}
                onChange={handleInputChange}
                required
              />
            </div>

            <div className="form-group">
              <label>Time:</label>
              <input
                type="time"
                name="time"
                value={meetingData.time}
                onChange={handleInputChange}
                required
              />
            </div>
          </div>

          <div className="form-row">
            <div className="form-group">
              <label>Duration (minutes):</label>
              <select name="duration" value={meetingData.duration} onChange={handleInputChange}>
                <option value={30}>30 minutes</option>
                <option value={60}>1 hour</option>
                <option value={90}>1.5 hours</option>
                <option value={120}>2 hours</option>
              </select>
            </div>

            <div className="form-group">
              <label>Platform:</label>
              <select name="platform" value={meetingData.platform} onChange={handleInputChange}>
                <option value="zoom">Zoom</option>
                <option value="teams">Microsoft Teams</option>
                <option value="meet">Google Meet</option>
                <option value="discord">Discord</option>
              </select>
            </div>
          </div>

          <div className="modal-actions">
            <button type="button" onClick={onClose} className="cancel-btn">
              Cancel
            </button>
            <button type="submit" disabled={loading} className="submit-btn">
              {loading ? 'Sending...' : 'Send Invite'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default MeetingInviteModal;
