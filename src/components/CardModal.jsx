import { useState, useEffect } from 'react';

const LABEL_OPTIONS = ['green', 'yellow', 'orange', 'red', 'purple', 'blue'];

const LABEL_COLORS = {
  green: '#61bd4f',
  yellow: '#f2d600',
  orange: '#ff9f1a',
  red: '#eb5a46',
  purple: '#c377e0',
  blue: '#0079bf',
};

function CardModal({ card, onClose, onUpdate, onDelete }) {
  const [title, setTitle] = useState(card.title);
  const [description, setDescription] = useState(card.description);
  const [labels, setLabels] = useState(card.labels);
  const [editingDesc, setEditingDesc] = useState(false);

  useEffect(() => {
    const handleEsc = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleEsc);
    return () => document.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const handleTitleBlur = () => {
    const trimmed = title.trim();
    if (trimmed && trimmed !== card.title) onUpdate({ title: trimmed });
    if (!trimmed) setTitle(card.title);
  };

  const handleDescSave = () => {
    onUpdate({ description });
    setEditingDesc(false);
  };

  const toggleLabel = (color) => {
    const newLabels = labels.includes(color)
      ? labels.filter(l => l !== color)
      : [...labels, color];
    setLabels(newLabels);
    onUpdate({ labels: newLabels });
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>

        <div className="modal-header">
          <svg viewBox="0 0 24 24" width="20" height="20" fill="#42526e" className="modal-icon">
            <rect x="3" y="3" width="18" height="18" rx="2" fill="none" stroke="#42526e" strokeWidth="2" />
            <path d="M7 7h10v2H7zm0 4h10v2H7zm0 4h6v2H7z" />
          </svg>
          <input
            className="modal-title-input"
            value={title}
            onChange={e => setTitle(e.target.value)}
            onBlur={handleTitleBlur}
            onKeyDown={e => { if (e.key === 'Enter') e.target.blur(); }}
          />
        </div>

        <div className="modal-section">
          <h3 className="modal-section-title">Labels</h3>
          <div className="label-picker">
            {LABEL_OPTIONS.map(color => (
              <button
                key={color}
                className={`label-option ${labels.includes(color) ? 'selected' : ''}`}
                style={{ backgroundColor: LABEL_COLORS[color] }}
                onClick={() => toggleLabel(color)}
              >
                {labels.includes(color) && (
                  <svg viewBox="0 0 24 24" width="14" height="14" fill="white">
                    <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z" />
                  </svg>
                )}
              </button>
            ))}
          </div>
        </div>

        <div className="modal-section">
          <h3 className="modal-section-title">Description</h3>
          {editingDesc ? (
            <div className="desc-editor">
              <textarea
                className="desc-textarea"
                value={description}
                onChange={e => setDescription(e.target.value)}
                placeholder="Add a more detailed description..."
                autoFocus
              />
              <div className="desc-actions">
                <button className="btn-primary" onClick={handleDescSave}>Save</button>
                <button className="btn-secondary" onClick={() => { setDescription(card.description); setEditingDesc(false); }}>Cancel</button>
              </div>
            </div>
          ) : (
            <div
              className={`desc-display ${description ? '' : 'empty'}`}
              onClick={() => setEditingDesc(true)}
            >
              {description || 'Add a more detailed description...'}
            </div>
          )}
        </div>

        <div className="modal-section">
          <button className="btn-danger" onClick={onDelete}>Delete Card</button>
        </div>
      </div>
    </div>
  );
}

export default CardModal;
