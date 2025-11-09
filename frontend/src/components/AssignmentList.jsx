import { format } from 'date-fns';
import { BookOpen, Calendar, Clock, Award, Tag } from 'lucide-react';
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

  // Sort assignments by category and estimated time
  const sortedAssignments = [...assignments].sort((a, b) => {
    // Category priority order (quick tasks first, then by time)
    const categoryOrder = {
      'quick_task': 1,
      'medium_effort': 2,
      'long_project': 3,
      'major_project': 4
    };
    
    const aCategory = a.category || 'medium_effort';
    const bCategory = b.category || 'medium_effort';
    
    const aOrder = categoryOrder[aCategory] || 2;
    const bOrder = categoryOrder[bCategory] || 2;
    
    // First sort by category
    if (aOrder !== bOrder) {
      return aOrder - bOrder;
    }
    
    // Then by estimated time (shorter first within same category)
    const aTime = a.estimated_time || 120;
    const bTime = b.estimated_time || 120;
    if (aTime !== bTime) {
      return aTime - bTime;
    }
    
    // Finally by due date (earlier first)
    if (a.due_date && b.due_date) {
      return new Date(a.due_date) - new Date(b.due_date);
    }
    if (a.due_date) return -1;
    if (b.due_date) return 1;
    return 0;
  });

  const getPriorityClass = (dueDate) => {
    if (!dueDate) return 'priority-low';
    
    const now = new Date();
    const due = new Date(dueDate);
    const daysUntilDue = (due - now) / (1000 * 60 * 60 * 24);

    if (daysUntilDue < 2) return 'priority-high';
    if (daysUntilDue < 7) return 'priority-medium';
    return 'priority-low';
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'quick_task': 'Quick Task',
      'medium_effort': 'Medium Effort',
      'long_project': 'Long Project',
      'major_project': 'Major Project'
    };
    return labels[category] || 'Assignment';
  };

  const getCategoryClass = (category) => {
    const classes = {
      'quick_task': 'category-quick',
      'medium_effort': 'category-medium',
      'long_project': 'category-long',
      'major_project': 'category-major'
    };
    return classes[category] || 'category-medium';
  };

  const formatDueDate = (dueDate) => {
    if (!dueDate) return 'No due date';
    try {
      return format(new Date(dueDate), 'MMM dd, yyyy h:mm a');
    } catch {
      return dueDate;
    }
  };

  const formatTime = (minutes) => {
    if (!minutes) return 'N/A';
    if (minutes < 60) return `${minutes} min`;
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (mins === 0) return `${hours} hr`;
    return `${hours} hr ${mins} min`;
  };

  return (
    <div className="assignment-list">
      {sortedAssignments.map((assignment) => (
        <div
          key={assignment.id}
          className={`assignment-card ${getPriorityClass(assignment.due_date)}`}
        >
          <div className="assignment-header">
            <h3>{assignment.title}</h3>
            <div className="header-badges">
              {assignment.category && (
                <span className={`category-badge ${getCategoryClass(assignment.category)}`}>
                  <Tag size={12} />
                  {getCategoryLabel(assignment.category)}
                </span>
              )}
              <span className="course-badge">{assignment.course_name}</span>
            </div>
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

              {assignment.estimated_time && (
                <div className="meta-item">
                  <Clock size={16} />
                  <span>{formatTime(assignment.estimated_time)}</span>
                </div>
              )}

              {assignment.points && (
                <div className="meta-item">
                  <Award size={16} />
                  <span>{assignment.points} points</span>
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
