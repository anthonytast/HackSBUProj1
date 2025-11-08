import { format } from 'date-fns';
import { BookOpen, Calendar, Clock, Award } from 'lucide-react';
import '../styles/AssignmentList.css';

function AssignmentList({ assignments }) {
  if (!assignments || assignments.length === 0) {
    return (
      <div className="empty-state">
        <BookOpen size={48} />
        <h3>No Assignments Found</h3>
        <p>Connect to Canvas and refresh to see your assignments</p>
      </div>
    );
  }

  const getPriorityClass = (dueDate) => {
    if (!dueDate) return 'priority-low';
    
    const now = new Date();
    const due = new Date(dueDate);
    const daysUntilDue = (due - now) / (1000 * 60 * 60 * 24);

    if (daysUntilDue < 2) return 'priority-high';
    if (daysUntilDue < 7) return 'priority-medium';
    return 'priority-low';
  };

  const formatDueDate = (dueDate) => {
    if (!dueDate) return 'No due date';
    try {
      return format(new Date(dueDate), 'MMM dd, yyyy h:mm a');
    } catch {
      return dueDate;
    }
  };

  return (
    <div className="assignment-list">
      {assignments.map((assignment) => (
        <div
          key={assignment.id}
          className={`assignment-card ${getPriorityClass(assignment.due_date)}`}
        >
          <div className="assignment-header">
            <h3>{assignment.title}</h3>
            <span className="course-badge">{assignment.course_name}</span>
          </div>

          <div className="assignment-details">
            {assignment.description && (
              <p className="assignment-description">
                {assignment.description.length > 150
                  ? assignment.description.substring(0, 150) + '...'
                  : assignment.description}
              </p>
            )}

            <div className="assignment-meta">
              <div className="meta-item">
                <Calendar size={16} />
                <span>{formatDueDate(assignment.due_date)}</span>
              </div>

              {assignment.points && (
                <div className="meta-item">
                  <Award size={16} />
                  <span>{assignment.points} points</span>
                </div>
              )}

              {assignment.estimated_time && (
                <div className="meta-item">
                  <Clock size={16} />
                  <span>{assignment.estimated_time} min</span>
                </div>
              )}
            </div>

            {assignment.assignment_type && (
              <span className="assignment-type">{assignment.assignment_type}</span>
            )}
          </div>

          {assignment.html_url && (
            <a
              href={assignment.html_url}
              target="_blank"
              rel="noopener noreferrer"
              className="assignment-link"
            >
              View in Canvas →
            </a>
          )}
        </div>
      ))}
    </div>
  );
}

export default AssignmentList;
