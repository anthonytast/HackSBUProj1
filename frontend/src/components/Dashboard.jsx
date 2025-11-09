import { useState, useEffect } from 'react';
import { Calendar, BookOpen, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { canvasAPI, studyPlanAPI } from '../services/api';
import AssignmentList from './AssignmentList';
import StudyPlanView from './StudyPlanView';
import '../styles/Dashboard.css';

function Dashboard({ canvasAuth, googleAuth }) {
  const [assignments, setAssignments] = useState([]);
  const [studyPlan, setStudyPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [assignmentsLoading, setAssignmentsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('assignments');
  const [stats, setStats] = useState({
    totalAssignments: 0,
    tasksCompleted: 0,
    upcomingDeadlines: 0,
  });

  useEffect(() => {
    if (canvasAuth) {
      fetchAssignments();
    }
  }, [canvasAuth]);

  const fetchAssignments = async () => {
    setAssignmentsLoading(true);
    setError(null);
    try {
      const data = await canvasAPI.getAssignments();
      setAssignments(data.assignments || []);
      updateStats(data.assignments || []);
    } catch (err) {
      setError('Failed to fetch assignments: ' + err.message);
    } finally {
      setAssignmentsLoading(false);
    }
  };

  const updateStats = (assignmentList) => {
    const now = new Date();
    const weekFromNow = new Date(now.getTime() + 7 * 24 * 60 * 60 * 1000);
    
    const upcoming = assignmentList.filter(a => {
      if (!a.due_date) return false;
      const dueDate = new Date(a.due_date);
      return dueDate >= now && dueDate <= weekFromNow;
    });

    setStats({
      totalAssignments: assignmentList.length,
      tasksCompleted: studyPlan?.tasks?.filter(t => t.completed).length || 0,
      upcomingDeadlines: upcoming.length,
    });
  };

  const handleGenerateStudyPlan = async () => {
    if (!assignments || assignments.length === 0) {
      setError('No assignments to generate a study plan from');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await studyPlanAPI.generatePlan(assignments);
      if (!data.study_plan || !data.study_plan.tasks) {
        throw new Error('Received invalid study plan from server');
      }
      setStudyPlan(data.study_plan);
      setActiveTab('studyplan');
    } catch (err) {
      setError('Failed to generate study plan: ' + err.message);
      // Keep loading state if we need to retry
      if (err.message.includes('invalid model')) {
        await new Promise(resolve => setTimeout(resolve, 1000));
        try {
          const retryData = await studyPlanAPI.generatePlan(assignments);
          if (retryData.study_plan && retryData.study_plan.tasks) {
            setStudyPlan(retryData.study_plan);
            setActiveTab('studyplan');
            setError(null);
          }
        } catch (retryErr) {
          setError('Failed to generate study plan after retry: ' + retryErr.message);
        }
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCompletePlan = async () => {
    if (!googleAuth) {
      setError('Please authenticate with Google Calendar first');
      return;
    }

    setLoading(true);
    setError(null);
    try {
      const data = await studyPlanAPI.completePlan();
      alert(`Success! Created ${data.events_created} calendar events from ${data.tasks_generated} tasks`);
      setActiveTab('studyplan');
    } catch (err) {
      setError('Failed to complete study plan: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard">
      {/* Stats Cards */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">
            <BookOpen size={24} />
          </div>
          <div className="stat-content">
            <h3>Total Assignments</h3>
            <p className="stat-value">{stats.totalAssignments}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon upcoming">
            <AlertCircle size={24} />
          </div>
          <div className="stat-content">
            <h3>Due This Week</h3>
            <p className="stat-value">{stats.upcomingDeadlines}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon completed">
            <CheckCircle size={24} />
          </div>
          <div className="stat-content">
            <h3>Tasks Completed</h3>
            <p className="stat-value">{stats.tasksCompleted}</p>
          </div>
        </div>

        <div className="stat-card">
          <div className="stat-icon calendar">
            <Calendar size={24} />
          </div>
          <div className="stat-content">
            <h3>Study Sessions</h3>
            <p className="stat-value">{studyPlan?.tasks?.length || 0}</p>
          </div>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="action-bar">
        <button
          onClick={fetchAssignments}
          disabled={(loading || assignmentsLoading) || !canvasAuth}
          className="btn btn-secondary"
        >
          <RefreshCw size={18} />
          Refresh Assignments
        </button>

        <button
          onClick={handleGenerateStudyPlan}
          disabled={(loading || assignmentsLoading) || !canvasAuth || assignments.length === 0}
          className="btn btn-primary"
        >
          Generate Study Plan
        </button>

        <button
          onClick={handleCompletePlan}
          disabled={(loading || assignmentsLoading) || !canvasAuth || !googleAuth}
          className="btn btn-success"
        >
          Complete Plan (Add to Calendar)
        </button>
      </div>

      {/* Error Display */}
      {error && (
        <div className="alert alert-error">
          <AlertCircle size={20} />
          {error}
        </div>
      )}

      {/* Tabs */}
      <div className="tabs">
        <button
          className={`tab ${activeTab === 'assignments' ? 'active' : ''}`}
          onClick={() => setActiveTab('assignments')}
        >
          Assignments ({assignments.length})
        </button>
        <button
          className={`tab ${activeTab === 'studyplan' ? 'active' : ''}`}
          onClick={() => setActiveTab('studyplan')}
        >
          Study Plan {studyPlan && `(${studyPlan.tasks?.length || 0} tasks)`}
        </button>
      </div>

      {/* Content */}
      <div className="tab-content">
        {(loading || assignmentsLoading) ? (
          <div className="loading">
            <RefreshCw className="spin" size={32} />
            <p>Loading...</p>
          </div>
        ) : (
          <>
            {activeTab === 'assignments' && (
              <AssignmentList assignments={assignments} />
            )}
            {activeTab === 'studyplan' && (
              <StudyPlanView studyPlan={studyPlan} />
            )}
          </>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
