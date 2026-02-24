let nextId = 1;

export function generateId() {
  return `id-${Date.now()}-${nextId++}`;
}

export function createInitialBoard() {
  const todoCards = [
    { id: generateId(), title: 'Research project requirements', description: 'Gather and document all project requirements from stakeholders', labels: ['blue'] },
    { id: generateId(), title: 'Set up development environment', description: '', labels: ['green'] },
    { id: generateId(), title: 'Design database schema', description: 'Create ERD and define table relationships', labels: ['yellow'] },
  ];

  const inProgressCards = [
    { id: generateId(), title: 'Build user authentication', description: 'Implement login, signup, and password reset flows', labels: ['red'] },
    { id: generateId(), title: 'Create API endpoints', description: '', labels: ['blue', 'green'] },
  ];

  const doneCards = [
    { id: generateId(), title: 'Project kickoff meeting', description: 'Initial team sync and planning session', labels: ['purple'] },
  ];

  const lists = [
    { id: generateId(), title: 'To Do', cardIds: todoCards.map(c => c.id) },
    { id: generateId(), title: 'In Progress', cardIds: inProgressCards.map(c => c.id) },
    { id: generateId(), title: 'Done', cardIds: doneCards.map(c => c.id) },
  ];

  const cards = {};
  [...todoCards, ...inProgressCards, ...doneCards].forEach(card => {
    cards[card.id] = card;
  });

  return {
    title: 'My Kanban Board',
    lists,
    cards,
  };
}
