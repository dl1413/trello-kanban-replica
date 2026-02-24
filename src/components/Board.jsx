import { Droppable } from '@hello-pangea/dnd';
import List from './List';
import AddList from './AddList';

function Board({ lists, cards, onAddList, onUpdateListTitle, onDeleteList, onAddCard, onUpdateCard, onDeleteCard }) {
  return (
    <Droppable droppableId="board" type="LIST" direction="horizontal">
      {(provided) => (
        <div className="board" ref={provided.innerRef} {...provided.droppableProps}>
          {lists.map((list, index) => (
            <List
              key={list.id}
              list={list}
              index={index}
              cards={list.cardIds.map(id => cards[id]).filter(Boolean)}
              onUpdateTitle={onUpdateListTitle}
              onDeleteList={onDeleteList}
              onAddCard={onAddCard}
              onUpdateCard={onUpdateCard}
              onDeleteCard={onDeleteCard}
            />
          ))}
          {provided.placeholder}
          <AddList onAdd={onAddList} />
        </div>
      )}
    </Droppable>
  );
}

export default Board;
