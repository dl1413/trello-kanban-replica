import { useState, useEffect, useCallback } from 'react';
import { DragDropContext } from '@hello-pangea/dnd';
import Board from './components/Board';
import Header from './components/Header';
import { loadBoard, saveBoard } from './utils/storage';
import { createInitialBoard, generateId } from './utils/initialData';

function App() {
  const [board, setBoard] = useState(() => loadBoard() || createInitialBoard());

  useEffect(() => {
    saveBoard(board);
  }, [board]);

  const onDragEnd = useCallback((result) => {
    const { source, destination, type } = result;
    if (!destination) return;
    if (source.droppableId === destination.droppableId && source.index === destination.index) return;

    if (type === 'LIST') {
      setBoard(prev => {
        const newLists = [...prev.lists];
        const [moved] = newLists.splice(source.index, 1);
        newLists.splice(destination.index, 0, moved);
        return { ...prev, lists: newLists };
      });
      return;
    }

    // Card drag
    setBoard(prev => {
      const sourceList = prev.lists.find(l => l.id === source.droppableId);
      const destList = prev.lists.find(l => l.id === destination.droppableId);
      if (!sourceList || !destList) return prev;

      const newSourceCardIds = [...sourceList.cardIds];
      const [movedCardId] = newSourceCardIds.splice(source.index, 1);

      if (sourceList.id === destList.id) {
        newSourceCardIds.splice(destination.index, 0, movedCardId);
        const newLists = prev.lists.map(l =>
          l.id === sourceList.id ? { ...l, cardIds: newSourceCardIds } : l
        );
        return { ...prev, lists: newLists };
      }

      const newDestCardIds = [...destList.cardIds];
      newDestCardIds.splice(destination.index, 0, movedCardId);
      const newLists = prev.lists.map(l => {
        if (l.id === sourceList.id) return { ...l, cardIds: newSourceCardIds };
        if (l.id === destList.id) return { ...l, cardIds: newDestCardIds };
        return l;
      });
      return { ...prev, lists: newLists };
    });
  }, []);

  const addList = useCallback((title) => {
    setBoard(prev => ({
      ...prev,
      lists: [...prev.lists, { id: generateId(), title, cardIds: [] }],
    }));
  }, []);

  const updateListTitle = useCallback((listId, title) => {
    setBoard(prev => ({
      ...prev,
      lists: prev.lists.map(l => l.id === listId ? { ...l, title } : l),
    }));
  }, []);

  const deleteList = useCallback((listId) => {
    setBoard(prev => {
      const list = prev.lists.find(l => l.id === listId);
      const newCards = { ...prev.cards };
      if (list) list.cardIds.forEach(id => delete newCards[id]);
      return {
        ...prev,
        lists: prev.lists.filter(l => l.id !== listId),
        cards: newCards,
      };
    });
  }, []);

  const addCard = useCallback((listId, title) => {
    const cardId = generateId();
    setBoard(prev => ({
      ...prev,
      cards: { ...prev.cards, [cardId]: { id: cardId, title, description: '', labels: [] } },
      lists: prev.lists.map(l =>
        l.id === listId ? { ...l, cardIds: [...l.cardIds, cardId] } : l
      ),
    }));
  }, []);

  const updateCard = useCallback((cardId, updates) => {
    setBoard(prev => ({
      ...prev,
      cards: { ...prev.cards, [cardId]: { ...prev.cards[cardId], ...updates } },
    }));
  }, []);

  const deleteCard = useCallback((cardId, listId) => {
    setBoard(prev => {
      const newCards = { ...prev.cards };
      delete newCards[cardId];
      return {
        ...prev,
        cards: newCards,
        lists: prev.lists.map(l =>
          l.id === listId ? { ...l, cardIds: l.cardIds.filter(id => id !== cardId) } : l
        ),
      };
    });
  }, []);

  const updateBoardTitle = useCallback((title) => {
    setBoard(prev => ({ ...prev, title }));
  }, []);

  return (
    <div className="app">
      <Header title={board.title} onUpdateTitle={updateBoardTitle} />
      <DragDropContext onDragEnd={onDragEnd}>
        <Board
          lists={board.lists}
          cards={board.cards}
          onAddList={addList}
          onUpdateListTitle={updateListTitle}
          onDeleteList={deleteList}
          onAddCard={addCard}
          onUpdateCard={updateCard}
          onDeleteCard={deleteCard}
        />
      </DragDropContext>
    </div>
  );
}

export default App;
