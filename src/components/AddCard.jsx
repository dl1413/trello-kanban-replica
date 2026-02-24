import { useState } from 'react';

function AddCard({ listId, onAdd }) {
  const [adding, setAdding] = useState(false);
  const [title, setTitle] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    const trimmed = title.trim();
    if (trimmed) {
      onAdd(listId, trimmed);
      setTitle('');
    }
  };

  const handleCancel = () => {
    setAdding(false);
    setTitle('');
  };

  if (!adding) {
    return (
      <button className="add-card-btn" onClick={() => setAdding(true)}>
        <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
          <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6z" />
        </svg>
        Add a card
      </button>
    );
  }

  return (
    <form className="add-card-form" onSubmit={handleSubmit}>
      <textarea
        className="add-card-input"
        value={title}
        onChange={e => setTitle(e.target.value)}
        placeholder="Enter a title for this card..."
        autoFocus
        onKeyDown={e => {
          if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSubmit(e); }
          if (e.key === 'Escape') handleCancel();
        }}
      />
      <div className="add-card-actions">
        <button type="submit" className="btn-primary">Add Card</button>
        <button type="button" className="btn-icon" onClick={handleCancel}>
          <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
            <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z" />
          </svg>
        </button>
      </div>
    </form>
  );
}

export default AddCard;
