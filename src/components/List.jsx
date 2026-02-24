import { useState } from 'react';
import { Draggable, Droppable } from '@hello-pangea/dnd';
import Card from './Card';
import AddCard from './AddCard';

function List({ list, index, cards, onUpdateTitle, onDeleteList, onAddCard, onUpdateCard, onDeleteCard }) {
  const [editingTitle, setEditingTitle] = useState(false);
  const [titleValue, setTitleValue] = useState(list.title);
  const [showMenu, setShowMenu] = useState(false);

  const handleTitleSubmit = () => {
    const trimmed = titleValue.trim();
    if (trimmed) {
      onUpdateTitle(list.id, trimmed);
    } else {
      setTitleValue(list.title);
    }
    setEditingTitle(false);
  };

  return (
    <Draggable draggableId={list.id} index={index}>
      {(provided) => (
        <div className="list" ref={provided.innerRef} {...provided.draggableProps}>
          <div className="list-header" {...provided.dragHandleProps}>
            {editingTitle ? (
              <input
                className="list-title-input"
                value={titleValue}
                onChange={e => setTitleValue(e.target.value)}
                onBlur={handleTitleSubmit}
                onKeyDown={e => { if (e.key === 'Enter') handleTitleSubmit(); if (e.key === 'Escape') { setTitleValue(list.title); setEditingTitle(false); } }}
                autoFocus
              />
            ) : (
              <h2 className="list-title" onClick={() => setEditingTitle(true)}>{list.title}</h2>
            )}
            <div className="list-menu-wrapper">
              <button className="list-menu-btn" onClick={() => setShowMenu(!showMenu)}>
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <circle cx="12" cy="5" r="2" />
                  <circle cx="12" cy="12" r="2" />
                  <circle cx="12" cy="19" r="2" />
                </svg>
              </button>
              {showMenu && (
                <div className="list-menu">
                  <button onClick={() => { onDeleteList(list.id); setShowMenu(false); }}>
                    Delete List
                  </button>
                </div>
              )}
            </div>
          </div>
          <Droppable droppableId={list.id} type="CARD">
            {(dropProvided, snapshot) => (
              <div
                className={`list-cards ${snapshot.isDraggingOver ? 'dragging-over' : ''}`}
                ref={dropProvided.innerRef}
                {...dropProvided.droppableProps}
              >
                {cards.map((card, cardIndex) => (
                  <Card
                    key={card.id}
                    card={card}
                    index={cardIndex}
                    listId={list.id}
                    onUpdateCard={onUpdateCard}
                    onDeleteCard={onDeleteCard}
                  />
                ))}
                {dropProvided.placeholder}
              </div>
            )}
          </Droppable>
          <AddCard listId={list.id} onAdd={onAddCard} />
        </div>
      )}
    </Draggable>
  );
}

export default List;
