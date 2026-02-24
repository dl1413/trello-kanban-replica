import { useState } from 'react';

function Header({ title, onUpdateTitle }) {
  const [editing, setEditing] = useState(false);
  const [value, setValue] = useState(title);

  const handleSubmit = () => {
    const trimmed = value.trim();
    if (trimmed) {
      onUpdateTitle(trimmed);
    } else {
      setValue(title);
    }
    setEditing(false);
  };

  return (
    <header className="header">
      <div className="header-left">
        <svg className="header-logo" viewBox="0 0 24 24" width="24" height="24" fill="white">
          <rect x="2" y="2" width="8" height="18" rx="1.5" />
          <rect x="14" y="2" width="8" height="12" rx="1.5" />
        </svg>
        {editing ? (
          <input
            className="header-title-input"
            value={value}
            onChange={e => setValue(e.target.value)}
            onBlur={handleSubmit}
            onKeyDown={e => { if (e.key === 'Enter') handleSubmit(); if (e.key === 'Escape') { setValue(title); setEditing(false); } }}
            autoFocus
          />
        ) : (
          <h1 className="header-title" onClick={() => setEditing(true)}>{title}</h1>
        )}
      </div>
    </header>
  );
}

export default Header;
