import { format } from 'date-fns';
import { CheckCircle, Circle, Clock, Calendar, AlertTriangle } from 'lucide-react';
import '../styles/StudyPlanView.css';

function StudyPlanView({ studyPlan }) {
  if (!studyPlan) {
    return (
      <div className="empty-state">
        <Calendar size={48} />
        <h3>No Study Plan Generated</h3>
        <p>Generate a study plan from your assignments to see your personalized schedule</p>
      </div>
    );
  }

  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return '#ef4444';
      case 'medium':
        return '#f59e0b';
      case 'low':
        return '#10b981';
      default:
        return '#6b7280';
    }
  };

  const groupTasksByDate = (tasks) => {
    const grouped = {};
    tasks?.forEach((task) => {
      const date = task.suggested_date;
      if (!grouped[date]) {
        grouped[date] = [];
      }
      grouped[date].push(task);
    });
    return grouped;
  };

  const groupedTasks = groupTasksByDate(studyPlan.tasks);

  return (
    <div className="study-plan-view">
      {studyPlan.overview && (
        <div className="plan-overview">
          <h3>Study Plan Overview</h3>
          <p>{studyPlan.overview}</p>
        </div>
      )}

      <div className="plan-stats">
        <div className="plan-stat">
          <span className="stat-label">Total Tasks</span>
          <span className="stat-value">{studyPlan.tasks?.length || 0}</span>
        </div>
        <div className="plan-stat">
          <span className="stat-label">Total Hours</span>
          <span className="stat-value">
            {Math.round(
              (studyPlan.tasks?.reduce((sum, task) => sum + task.duration_minutes, 0) || 0) / 60
            )}h
          </span>
        </div>
        <div className="plan-stat">
          <span className="stat-label">Days to Cover</span>
          <span className="stat-value">{Object.keys(groupedTasks).length}</span>
        </div>
      </div>

      <div className="tasks-timeline">
        {Object.entries(groupedTasks).map(([date, tasks]) => (
          <div key={date} className="date-group">
            <div className="date-header">
              <Calendar size={20} />
              <h4>{format(new Date(date), 'EEEE, MMMM dd, yyyy')}</h4>
              <span className="task-count">{tasks.length} tasks</span>
            </div>

            <div className="tasks-for-date">
              {tasks.map((task, index) => (
                <div key={index} className="task-card">
                  <div className="task-header">
                    <div className="task-title-section">
                      <Circle size={20} className="task-checkbox" />
                      <div>
                        <h5>{task.task_name}</h5>
                        <p className="task-assignment">{task.assignment_title}</p>
                      </div>
                    </div>
                    <span
                      className="priority-badge"
                      style={{ backgroundColor: getPriorityColor(task.priority) }}
                    >
                      {task.priority || 'medium'}
                    </span>
                  </div>

                  {task.description && (
                    <p className="task-description">{task.description}</p>
                  )}

                  <div className="task-meta">
                    <div className="meta-item">
                      <Clock size={16} />
                      <span>{task.duration_minutes} min</span>
                    </div>
                    <div className="meta-item">
                      <Calendar size={16} />
                      <span>{task.suggested_start_time}</span>
                    </div>
                    <span className="course-label">{task.course_name}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>

      {studyPlan.tips && (
        <div className="study-tips">
          <div className="tips-header">
            <AlertTriangle size={20} />
            <h4>Study Tips</h4>
          </div>
          <ul>
            {studyPlan.tips.map((tip, index) => (
              <li key={index}>{tip}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

export default StudyPlanView;
