import { useState } from 'react';
import { Draggable } from '@hello-pangea/dnd';
import CardModal from './CardModal';

const LABEL_COLORS = {
  green: '#61bd4f',
  yellow: '#f2d600',
  orange: '#ff9f1a',
  red: '#eb5a46',
  purple: '#c377e0',
  blue: '#0079bf',
};

function Card({ card, index, listId, onUpdateCard, onDeleteCard }) {
  const [showModal, setShowModal] = useState(false);

  return (
    <>
      <Draggable draggableId={card.id} index={index}>
        {(provided, snapshot) => (
          <div
            className={`card ${snapshot.isDragging ? 'dragging' : ''}`}
            ref={provided.innerRef}
            {...provided.draggableProps}
            {...provided.dragHandleProps}
            onClick={() => setShowModal(true)}
          >
            {card.labels.length > 0 && (
              <div className="card-labels">
                {card.labels.map(label => (
                  <span
                    key={label}
                    className="card-label"
                    style={{ backgroundColor: LABEL_COLORS[label] || label }}
                  />
                ))}
              </div>
            )}
            <span className="card-title">{card.title}</span>
            {card.description && (
              <div className="card-badges">
                <svg viewBox="0 0 24 24" width="14" height="14" fill="#6b778c">
                  <path d="M4 5h16v2H4zm0 4h16v2H4zm0 4h10v2H4z" />
                </svg>
              </div>
            )}
          </div>
        )}
      </Draggable>
      {showModal && (
        <CardModal
          card={card}
          onClose={() => setShowModal(false)}
          onUpdate={(updates) => onUpdateCard(card.id, updates)}
          onDelete={() => { onDeleteCard(card.id, listId); setShowModal(false); }}
        />
      )}
    </>
  );
}

export default Card;
