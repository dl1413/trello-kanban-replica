# Assessment 2: Live Design & Velocity Discussion
## Video Transcript for 60-Minute Technical Interview

**Candidate**: [Your Name]
**Position**: Full-Stack Engineer - Rapid Prototyping & Interface Replication
**Date**: [Interview Date]
**Duration**: 60 minutes
**Assessment Focus**: Trello Board UI Replication Project

---

## Section 1: Walkthrough & Detail Review (25 minutes)

### [00:00 - 01:30] Opening & Project Introduction

**Interviewer**: Welcome! Thank you for joining us today. We've reviewed your Trello board replication submission, and we're impressed with what you've built. Can you start by giving us a high-level overview of what you implemented?

**Candidate**: Thank you for having me. For this assessment, I chose to replicate the core Trello board interface, focusing on the main board view with multiple lists and draggable cards. I implemented a full-stack application with:

- A React-based frontend using TypeScript for type safety
- Drag-and-drop functionality for cards between lists
- Real-time-like state management with optimistic updates
- A Node.js/Express backend with a simple persistence layer
- Pixel-perfect UI matching Trello's design system

The key components I replicated include:
- Board header with title and controls
- Multiple draggable lists (columns)
- Cards within lists with full CRUD operations
- Card modal with detailed view
- Visual states for hover, active, and drag interactions

### [01:30 - 05:00] Technical Architecture Deep Dive

**Interviewer**: Let's dive into the technical architecture. Can you walk us through how you structured the application?

**Candidate**: Absolutely. I structured the application following a clean, modular architecture:

**Frontend Architecture:**
```
src/
├── components/
│   ├── Board/
│   │   ├── Board.tsx           # Main board container
│   │   ├── BoardHeader.tsx     # Header with title/controls
│   │   └── Board.module.css    # Board-specific styles
│   ├── List/
│   │   ├── List.tsx            # List container component
│   │   ├── ListHeader.tsx      # List title and menu
│   │   ├── CardList.tsx        # Cards container
│   │   └── List.module.css     # List styling
│   ├── Card/
│   │   ├── Card.tsx            # Individual card
│   │   ├── CardModal.tsx       # Detailed card view
│   │   └── Card.module.css     # Card styling
│   └── shared/
│       ├── Button.tsx          # Reusable button
│       ├── Input.tsx           # Form inputs
│       └── Modal.tsx           # Modal wrapper
├── hooks/
│   ├── useDragAndDrop.ts      # DnD logic abstraction
│   ├── useBoard.ts            # Board state management
│   └── useOptimisticUpdate.ts # Optimistic UI updates
├── store/
│   ├── boardSlice.ts          # Redux/Zustand state
│   └── types.ts               # TypeScript interfaces
├── api/
│   └── client.ts              # API communication
└── utils/
    ├── dragHelpers.ts         # DnD utilities
    └── colors.ts              # Color constants
```

**Backend Architecture:**
```
server/
├── routes/
│   ├── boards.js              # Board endpoints
│   ├── lists.js               # List endpoints
│   └── cards.js               # Card endpoints
├── models/
│   ├── Board.js               # Board data model
│   ├── List.js                # List data model
│   └── Card.js                # Card data model
├── middleware/
│   └── validation.js          # Request validation
└── db/
    └── index.js               # Simple JSON/SQLite persistence
```

The architecture follows the principle of separation of concerns, making each component focused and testable.

### [05:00 - 10:00] CSS & Styling Challenges

**Interviewer**: The visual fidelity is impressive. What were the biggest CSS challenges you faced, and how did you solve them?

**Candidate**: Great question. I encountered several interesting CSS challenges:

**Challenge 1: Drag-and-Drop Visual Feedback**

The most complex styling challenge was creating smooth drag-and-drop interactions with proper visual feedback. I needed to:

- Show a dragging state on the card being moved
- Display a placeholder in the drop zone
- Prevent layout shifts during drag operations
- Maintain smooth animations

**Solution:**
```css
/* Card being dragged */
.card-dragging {
  opacity: 0.5;
  transform: rotate(5deg);
  cursor: grabbing;
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
  z-index: 1000;
}

/* Drop zone placeholder */
.card-placeholder {
  height: 100px; /* Match card height */
  border: 2px dashed #0079bf;
  border-radius: 3px;
  background: rgba(0, 121, 191, 0.1);
  margin: 8px 0;
  transition: all 0.15s ease;
}

/* Prevent layout shift */
.list-content {
  min-height: 50px; /* Ensure space for drop zone */
}
```

**Challenge 2: Matching Trello's Exact Colors and Shadows**

I spent significant time extracting the exact design tokens from Trello:

```css
:root {
  /* Primary colors - extracted from Trello */
  --trello-blue: #0079bf;
  --trello-blue-hover: #026aa7;
  --trello-blue-active: #055a8c;

  /* Background colors */
  --board-bg: #0079bf; /* Default blue board */
  --list-bg: #ebecf0;
  --card-bg: #ffffff;

  /* Shadows - pixel-perfect matching */
  --card-shadow: 0 1px 0 rgba(9, 30, 66, 0.25);
  --card-shadow-hover: 0 4px 8px rgba(9, 30, 66, 0.25);
  --list-shadow: 0 1px 0 rgba(9, 30, 66, 0.13);

  /* Spacing - Trello uses 8px grid */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
}
```

**Challenge 3: Responsive Horizontal Scrolling for Lists**

Trello's board scrolls horizontally when you have many lists. I implemented this with:

```css
.board-content {
  display: flex;
  overflow-x: auto;
  overflow-y: hidden;
  height: calc(100vh - 64px); /* Full height minus header */
  padding: 8px;
  gap: 8px;

  /* Custom scrollbar to match Trello */
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.3) transparent;
}

.board-content::-webkit-scrollbar {
  height: 12px;
}

.board-content::-webkit-scrollbar-track {
  background: transparent;
}

.board-content::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6px;
}

.board-content::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.5);
}
```

**Challenge 4: Hover and Active States**

I meticulously replicated every interaction state:

```css
.card {
  background: var(--card-bg);
  border-radius: 3px;
  box-shadow: var(--card-shadow);
  padding: 8px;
  margin: 0 8px 8px;
  cursor: pointer;
  transition: background 0.1s ease, box-shadow 0.1s ease;
}

.card:hover {
  background: #f4f5f7;
  box-shadow: var(--card-shadow-hover);
}

.card:active {
  background: #e4e6ea;
}

/* Edit state */
.card-editing {
  box-shadow: 0 0 0 2px var(--trello-blue);
  background: white;
}
```

### [10:00 - 15:00] Functional Implementation Details

**Interviewer**: Let's talk about the functionality. How did you implement the drag-and-drop system?

**Candidate**: I implemented drag-and-drop using the HTML5 Drag and Drop API with a custom abstraction layer. Let me walk you through the key parts:

**Core Drag-and-Drop Hook:**
```typescript
// hooks/useDragAndDrop.ts
interface DragItem {
  type: 'card' | 'list';
  id: string;
  sourceListId?: string;
  index: number;
}

export const useDragAndDrop = () => {
  const [draggedItem, setDraggedItem] = useState<DragItem | null>(null);
  const [dropTarget, setDropTarget] = useState<{
    listId: string;
    index: number;
  } | null>(null);

  const handleDragStart = useCallback((item: DragItem) => {
    setDraggedItem(item);
    // Add dragging class for visual feedback
    document.body.classList.add('is-dragging');
  }, []);

  const handleDragOver = useCallback((e: DragEvent, listId: string, index: number) => {
    e.preventDefault();
    setDropTarget({ listId, index });
  }, []);

  const handleDrop = useCallback((e: DragEvent) => {
    e.preventDefault();
    if (!draggedItem || !dropTarget) return;

    // Optimistic update for immediate UI feedback
    moveCard(draggedItem, dropTarget);

    // Persist to backend
    saveCardPosition(draggedItem.id, dropTarget.listId, dropTarget.index);

    // Cleanup
    setDraggedItem(null);
    setDropTarget(null);
    document.body.classList.remove('is-dragging');
  }, [draggedItem, dropTarget]);

  return {
    draggedItem,
    dropTarget,
    handleDragStart,
    handleDragOver,
    handleDrop,
  };
};
```

**Card Component with Drag Handlers:**
```typescript
// components/Card/Card.tsx
const Card: React.FC<CardProps> = ({ card, listId, index }) => {
  const { handleDragStart } = useDragAndDrop();
  const { updateCard, deleteCard } = useBoard();

  return (
    <div
      className="card"
      draggable
      onDragStart={() => handleDragStart({
        type: 'card',
        id: card.id,
        sourceListId: listId,
        index,
      })}
    >
      <div className="card-content">
        {card.labels?.length > 0 && (
          <div className="card-labels">
            {card.labels.map(label => (
              <span key={label.id} className={`label label-${label.color}`} />
            ))}
          </div>
        )}
        <p className="card-title">{card.title}</p>
        {card.description && (
          <span className="card-description-badge">
            <DescriptionIcon />
          </span>
        )}
        {card.dueDate && (
          <div className="card-due-date">
            <CalendarIcon />
            <span>{formatDate(card.dueDate)}</span>
          </div>
        )}
      </div>
    </div>
  );
};
```

**State Management for Board:**
```typescript
// store/boardSlice.ts
interface BoardState {
  lists: List[];
  cards: Record<string, Card[]>;
}

const boardSlice = createSlice({
  name: 'board',
  initialState,
  reducers: {
    moveCard: (state, action: PayloadAction<{
      cardId: string;
      sourceListId: string;
      destListId: string;
      destIndex: number;
    }>) => {
      const { cardId, sourceListId, destListId, destIndex } = action.payload;

      // Remove from source
      const sourceCards = state.cards[sourceListId];
      const cardIndex = sourceCards.findIndex(c => c.id === cardId);
      const [card] = sourceCards.splice(cardIndex, 1);

      // Add to destination
      const destCards = state.cards[destListId];
      destCards.splice(destIndex, 0, card);
    },
    // ... other reducers
  },
});
```

The key insight was to implement optimistic updates - the UI updates immediately while the backend request happens asynchronously. If the backend fails, we roll back the change.

### [15:00 - 20:00] Edge Cases and Minor Details

**Interviewer**: What about the small details? Buttons, modals, form states?

**Candidate**: That's where I spent a lot of time achieving pixel-perfect accuracy. Let me show you some examples:

**Button States:**
```css
/* Primary button - Add Card */
.btn-primary {
  background: var(--trello-blue);
  color: white;
  border: none;
  border-radius: 3px;
  padding: 6px 12px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.1s ease;
}

.btn-primary:hover {
  background: var(--trello-blue-hover);
}

.btn-primary:active {
  background: var(--trello-blue-active);
  transform: translateY(1px);
}

/* Secondary button - Cancel */
.btn-secondary {
  background: transparent;
  color: #172b4d;
  padding: 6px 12px;
  cursor: pointer;
  transition: background 0.1s ease;
}

.btn-secondary:hover {
  background: rgba(9, 30, 66, 0.08);
}
```

**Card Modal Implementation:**
```typescript
// components/Card/CardModal.tsx
const CardModal: React.FC<CardModalProps> = ({ card, listId, onClose }) => {
  const [title, setTitle] = useState(card.title);
  const [description, setDescription] = useState(card.description);

  return (
    <Modal onClose={onClose} className="card-modal">
      <div className="modal-header">
        <TitleIcon />
        <textarea
          className="card-title-edit"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          onBlur={() => updateCardTitle(card.id, title)}
        />
        <button className="modal-close" onClick={onClose}>
          <CloseIcon />
        </button>
      </div>

      <div className="modal-body">
        <div className="modal-section">
          <h3>Description</h3>
          <textarea
            className="card-description-edit"
            value={description}
            placeholder="Add a more detailed description..."
            onChange={(e) => setDescription(e.target.value)}
            onBlur={() => updateCardDescription(card.id, description)}
          />
        </div>

        <div className="modal-sidebar">
          <h4>Add to card</h4>
          <button className="sidebar-btn">
            <LabelIcon /> Labels
          </button>
          <button className="sidebar-btn">
            <ChecklistIcon /> Checklist
          </button>
          <button className="sidebar-btn">
            <CalendarIcon /> Due Date
          </button>
        </div>
      </div>
    </Modal>
  );
};
```

**Form States - Adding a New Card:**
```typescript
// components/List/AddCard.tsx
const AddCard: React.FC<AddCardProps> = ({ listId }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [title, setTitle] = useState('');

  const handleSubmit = async () => {
    if (!title.trim()) return;

    await createCard(listId, { title });
    setTitle('');
    setIsEditing(true); // Keep form open for quick adds
  };

  if (!isEditing) {
    return (
      <button
        className="add-card-btn"
        onClick={() => setIsEditing(true)}
      >
        <PlusIcon /> Add a card
      </button>
    );
  }

  return (
    <div className="add-card-form">
      <textarea
        autoFocus
        placeholder="Enter a title for this card..."
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSubmit();
          }
        }}
      />
      <div className="form-actions">
        <button className="btn-primary" onClick={handleSubmit}>
          Add card
        </button>
        <button
          className="btn-icon"
          onClick={() => setIsEditing(false)}
        >
          <CloseIcon />
        </button>
      </div>
    </div>
  );
};
```

Every interaction - from button clicks to form submissions to keyboard shortcuts - was carefully implemented to match Trello's behavior.

### [20:00 - 25:00] Performance and Accessibility

**Interviewer**: Did you consider performance and accessibility?

**Candidate**: Yes, absolutely. Here are the key optimizations:

**Performance Optimizations:**

1. **React.memo for Card Components:**
```typescript
export const Card = React.memo<CardProps>(({ card, listId, index }) => {
  // ... component logic
}, (prevProps, nextProps) => {
  return prevProps.card.id === nextProps.card.id &&
         prevProps.card.title === nextProps.card.title &&
         prevProps.listId === nextProps.listId;
});
```

2. **Virtualization for Large Lists:**
```typescript
// For boards with 100+ cards per list
import { FixedSizeList } from 'react-window';

const CardList: React.FC<CardListProps> = ({ cards, listId }) => {
  if (cards.length > 50) {
    return (
      <FixedSizeList
        height={600}
        itemCount={cards.length}
        itemSize={100}
        width="100%"
      >
        {({ index, style }) => (
          <div style={style}>
            <Card card={cards[index]} listId={listId} index={index} />
          </div>
        )}
      </FixedSizeList>
    );
  }

  return <>{cards.map((card, index) => ...)}</>;
};
```

3. **Debounced Backend Saves:**
```typescript
const debouncedSave = useMemo(
  () => debounce((cardId: string, updates: Partial<Card>) => {
    api.updateCard(cardId, updates);
  }, 500),
  []
);
```

**Accessibility Features:**

```tsx
// Proper ARIA labels
<button
  aria-label="Add a new card"
  onClick={handleAddCard}
>
  <PlusIcon aria-hidden="true" />
  Add a card
</button>

// Keyboard navigation
<div
  role="button"
  tabIndex={0}
  onKeyDown={(e) => {
    if (e.key === 'Enter' || e.key === ' ') {
      handleCardClick();
    }
  }}
>
  {card.title}
</div>

// Screen reader announcements
const [announcement, setAnnouncement] = useState('');

const handleCardMove = (card: Card, newList: string) => {
  // ... move logic
  setAnnouncement(`Card "${card.title}" moved to ${newList}`);
};

<div role="status" aria-live="polite" className="sr-only">
  {announcement}
</div>
```

---

## Section 2: Workflow & Velocity Discussion (20 minutes)

### [25:00 - 30:00] Development Speed and Tooling

**Interviewer**: You completed this in 3-4 hours. How did you achieve that speed? Walk us through your workflow.

**Candidate**: Speed was critical for this assessment, so I used several strategies:

**1. AI-Assisted Development with GitHub Copilot and ChatGPT:**

I leveraged AI tools extensively to accelerate development:

- **Component Scaffolding**: Used Copilot to generate boilerplate React components
  ```typescript
  // I'd type: "Create a Card component with drag and drop"
  // Copilot would generate 80% of the structure
  ```

- **CSS Generation**: Used ChatGPT to generate initial CSS from descriptions
  - "Create CSS for a card with hover state matching Trello"
  - Got base styles, then refined manually

- **Type Definitions**: Copilot excelled at generating TypeScript interfaces
  ```typescript
  // Typing "interface Card" would auto-suggest complete definitions
  interface Card {
    id: string;
    title: string;
    description: string;
    // ... Copilot fills in the rest
  }
  ```

**Time Saved**: ~45 minutes on boilerplate code

**2. Design Token Extraction:**

Instead of manually measuring spacing and colors, I used browser DevTools to extract values directly from Trello:

```javascript
// Console snippet I ran on Trello.com
const styles = window.getComputedStyle(document.querySelector('.list-card'));
console.log({
  background: styles.background,
  borderRadius: styles.borderRadius,
  boxShadow: styles.boxShadow,
  padding: styles.padding,
  margin: styles.margin,
});
```

I created a design-tokens.json file with all extracted values for quick reference.

**Time Saved**: ~30 minutes of guessing and adjusting

**3. Vite for Lightning-Fast Development:**

Used Vite instead of Create React App:
```bash
npm create vite@latest trello-clone -- --template react-ts
```

**Benefits**:
- Instant HMR (Hot Module Replacement)
- Fast build times
- Native ES modules
- TypeScript out of the box

**Time Saved**: ~20 minutes on build configuration and waiting for rebuilds

**4. Component Library for Common Patterns:**

I used Headless UI for complex components like modals and dropdowns:
```typescript
import { Dialog } from '@headlessui/react';

// Pre-built accessibility, focus management, keyboard navigation
<Dialog open={isOpen} onClose={onClose}>
  {/* Modal content */}
</Dialog>
```

**Time Saved**: ~40 minutes on accessibility and focus management

**5. CSS Modules for Scoped Styling:**

Instead of wrestling with global CSS, I used CSS Modules:
```typescript
import styles from './Card.module.css';

<div className={styles.card} />
```

No naming conflicts, fast to write, easy to maintain.

**Time Saved**: ~15 minutes on style debugging

### [30:00 - 35:00] Automation and Efficiency Tools

**Interviewer**: What other automation or tools did you use?

**Candidate**: Several key tools:

**1. ESLint + Prettier for Auto-Formatting:**
```json
// .vscode/settings.json
{
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  }
}
```

Every save auto-formats code. Zero time spent on formatting.

**2. TypeScript for Catching Errors Early:**

Type checking caught bugs during development, not at runtime:
```typescript
// This error is caught immediately:
const card: Card = {
  id: '1',
  title: 'Test',
  // Missing required fields - TypeScript error!
};
```

**3. React DevTools for State Debugging:**

Used React DevTools profiler to identify performance bottlenecks:
- Saw which components re-render unnecessarily
- Added React.memo where needed
- Optimized in ~10 minutes

**4. Chrome DevTools for Pixel-Perfect Comparison:**

I used a technique where I:
1. Take screenshot of Trello board
2. Open in one Chrome tab
3. Open my replica in another tab
4. Rapidly switch between tabs to spot differences

This made visual QA extremely fast.

**5. Git with Frequent Commits:**

I committed every major feature:
```bash
git commit -m "Add drag and drop for cards"
git commit -m "Implement card modal"
git commit -m "Add list header with menu"
```

If something broke, easy to revert.

### [35:00 - 40:00] Non-Conventional Methods

**Interviewer**: You mentioned some interesting techniques. Are there any non-conventional methods you used that really accelerated development?

**Candidate**: Yes! A few unconventional approaches:

**1. Screenshot-Driven Development:**

Instead of constantly referencing Trello in another window, I:
- Took detailed screenshots of every component state
- Organized them in a `/references` folder
- Used them as direct visual specs

```
references/
├── board-overview.png
├── card-default.png
├── card-hover.png
├── card-dragging.png
├── modal-open.png
└── list-menu.png
```

This kept me focused in my IDE without context switching.

**2. Copy-Paste-Modify Pattern:**

For similar components (like buttons), I:
- Built one perfect button
- Copy-pasted it for other button types
- Modified only what's different

Not DRY initially, but extremely fast. Refactored later.

**3. Mock Data First, Backend Later:**

I built the entire UI with mock data:
```typescript
const MOCK_BOARD = {
  id: '1',
  title: 'My Trello Board',
  lists: [...],
  cards: {...},
};
```

Built all functionality with mocks, then swapped in API calls at the end. This avoided backend debugging during UI development.

**4. "Good Enough" Backend:**

For persistence, I didn't set up a database. I used:
```typescript
// server/db/index.js
const fs = require('fs');
const DATA_FILE = './data.json';

const db = {
  read: () => JSON.parse(fs.readFileSync(DATA_FILE)),
  write: (data) => fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2)),
};
```

Simple, fast, no database setup time required. Good enough for the demo.

**5. AI Pair Programming:**

I used ChatGPT as a rubber duck and code reviewer:
- Pasted complex functions and asked "What's wrong here?"
- Asked for refactoring suggestions
- Got algorithm implementations (like drag-drop calculations)

This was like having a senior dev on call.

### [40:00 - 45:00] Time Breakdown

**Interviewer**: Can you break down how you spent the 3-4 hours?

**Candidate**: Here's my approximate time breakdown:

**Initial Setup (30 minutes):**
- Project scaffolding with Vite: 5 min
- Installing dependencies: 5 min
- Setting up ESLint/Prettier: 5 min
- Taking reference screenshots from Trello: 10 min
- Setting up project structure: 5 min

**Core UI Implementation (90 minutes):**
- Board layout and header: 15 min
- List component: 20 min
- Card component: 20 min
- CSS styling (colors, shadows, spacing): 35 min

**Drag-and-Drop (45 minutes):**
- Implementing drag handlers: 20 min
- Visual feedback (dragging states): 15 min
- Testing and bug fixes: 10 min

**Card Modal (30 minutes):**
- Modal component: 15 min
- Card detail view: 10 min
- Edit functionality: 5 min

**Backend & API (20 minutes):**
- Express server setup: 5 min
- API endpoints: 10 min
- Simple file-based persistence: 5 min

**Polish & Testing (25 minutes):**
- Fixing visual inconsistencies: 10 min
- Cross-browser testing: 5 min
- Keyboard accessibility: 5 min
- Final QA: 5 min

**Total: ~240 minutes (4 hours)**

The key was staying focused, using tools aggressively, and not over-engineering.

---

## Section 3: Scalability & Component Design (15 minutes)

### [45:00 - 50:00] Production Architecture

**Interviewer**: This is impressive for a prototype. How would you evolve this into a production-ready system?

**Candidate**: Great question. Here's how I'd scale this:

**1. State Management Refactoring:**

Current: Local component state + simple Redux
Future: More sophisticated state management

```typescript
// Current approach
const [cards, setCards] = useState<Card[]>([]);

// Production approach - Normalized state
interface NormalizedState {
  boards: {
    byId: Record<string, Board>;
    allIds: string[];
  };
  lists: {
    byId: Record<string, List>;
    allIds: string[];
  };
  cards: {
    byId: Record<string, Card>;
    allIds: string[];
  };
}

// Benefits:
// - No duplicate data
// - O(1) lookups
// - Easier updates
// - Better performance
```

**2. Real-Time Collaboration:**

Add WebSocket support for multi-user editing:

```typescript
// Backend - Socket.io
io.on('connection', (socket) => {
  socket.on('card:move', (data) => {
    // Broadcast to all other users
    socket.broadcast.emit('card:moved', data);
  });

  socket.on('card:update', (data) => {
    socket.broadcast.emit('card:updated', data);
  });
});

// Frontend - React hooks
const useRealtimeBoard = (boardId: string) => {
  const socket = useSocket();

  useEffect(() => {
    socket.on('card:moved', (data) => {
      dispatch(moveCard(data));
    });

    socket.on('card:updated', (data) => {
      dispatch(updateCard(data));
    });
  }, [socket]);
};
```

**3. Proper Database Schema:**

Replace JSON file with PostgreSQL:

```sql
-- Tables
CREATE TABLE boards (
  id UUID PRIMARY KEY,
  title VARCHAR(255),
  background_color VARCHAR(7),
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);

CREATE TABLE lists (
  id UUID PRIMARY KEY,
  board_id UUID REFERENCES boards(id) ON DELETE CASCADE,
  title VARCHAR(255),
  position INTEGER,
  created_at TIMESTAMP
);

CREATE TABLE cards (
  id UUID PRIMARY KEY,
  list_id UUID REFERENCES lists(id) ON DELETE CASCADE,
  title VARCHAR(255),
  description TEXT,
  position INTEGER,
  due_date TIMESTAMP,
  created_at TIMESTAMP
);

CREATE TABLE card_labels (
  id UUID PRIMARY KEY,
  card_id UUID REFERENCES cards(id) ON DELETE CASCADE,
  label_id UUID REFERENCES labels(id),
  created_at TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_lists_board_id ON lists(board_id);
CREATE INDEX idx_cards_list_id ON cards(list_id);
CREATE INDEX idx_cards_position ON cards(list_id, position);
```

**4. API Design Evolution:**

Move from simple REST to GraphQL for flexible queries:

```graphql
# Current REST approach requires multiple requests
GET /api/boards/1
GET /api/boards/1/lists
GET /api/boards/1/cards

# GraphQL - single request with exact data needed
query GetBoard($boardId: ID!) {
  board(id: $boardId) {
    id
    title
    lists {
      id
      title
      cards {
        id
        title
        labels {
          color
        }
        dueDate
      }
    }
  }
}
```

**5. Performance Optimizations:**

```typescript
// Implement optimistic updates with rollback
const optimisticUpdate = async (action, rollback) => {
  // Update UI immediately
  dispatch(action);

  try {
    // Sync with backend
    await api.sync(action);
  } catch (error) {
    // Rollback on failure
    dispatch(rollback);
    showError('Update failed');
  }
};

// Batch backend updates
const batchQueue = new Map();
const flushBatch = debounce(async () => {
  const updates = Array.from(batchQueue.values());
  await api.batchUpdate(updates);
  batchQueue.clear();
}, 500);
```

### [50:00 - 55:00] Data Modeling & Consistency

**Interviewer**: How would you handle data consistency in a multi-user environment?

**Candidate**: Data consistency is critical for collaboration. Here's my approach:

**1. Operational Transformation (OT) or CRDT:**

For conflict-free editing:

```typescript
// Operational Transformation example
interface Operation {
  type: 'INSERT' | 'DELETE' | 'MOVE';
  path: string[];
  value?: any;
  oldValue?: any;
  timestamp: number;
  userId: string;
}

class OTEngine {
  transform(op1: Operation, op2: Operation): [Operation, Operation] {
    // Transform two concurrent operations
    // Returns transformed versions that can be applied in any order
    // Example: Both users move same card
    if (op1.type === 'MOVE' && op2.type === 'MOVE') {
      // Resolve conflict based on timestamp or user priority
      return [adjustedOp1, adjustedOp2];
    }
  }
}
```

**2. Version Control for Cards:**

Track changes like git:

```typescript
interface CardVersion {
  id: string;
  cardId: string;
  version: number;
  data: Card;
  diff: Partial<Card>;
  author: string;
  timestamp: Date;
}

// On update
const updateCard = async (cardId: string, updates: Partial<Card>) => {
  const currentVersion = await db.getLatestVersion(cardId);

  // Check for conflicts
  if (clientVersion !== currentVersion.version) {
    // Merge or prompt user
    return handleConflict(updates, currentVersion);
  }

  // Create new version
  await db.createVersion({
    cardId,
    version: currentVersion.version + 1,
    data: { ...currentVersion.data, ...updates },
    diff: updates,
    author: currentUser.id,
    timestamp: new Date(),
  });
};
```

**3. Presence Indicators:**

Show who's viewing/editing what:

```typescript
interface UserPresence {
  userId: string;
  userName: string;
  avatar: string;
  viewingCardId?: string;
  editingCardId?: string;
  lastActivity: Date;
}

// Track presence
const usePresence = (boardId: string) => {
  const [presence, setPresence] = useState<Map<string, UserPresence>>();

  useEffect(() => {
    // Send heartbeat every 5 seconds
    const interval = setInterval(() => {
      socket.emit('presence:update', {
        boardId,
        activity: getCurrentActivity(),
      });
    }, 5000);

    // Listen for other users
    socket.on('presence:users', (users) => {
      setPresence(new Map(users.map(u => [u.userId, u])));
    });
  }, [boardId]);
};

// UI: Show avatars on cards being edited
{usersEditingCard.map(user => (
  <Avatar key={user.id} src={user.avatar} size="sm" />
))}
```

**4. Conflict Resolution UI:**

```typescript
const ConflictDialog = ({ local, remote, onResolve }) => {
  return (
    <Modal>
      <h2>Conflicting Changes Detected</h2>
      <div className="conflict-sides">
        <div className="conflict-local">
          <h3>Your Changes</h3>
          <CardPreview card={local} />
          <button onClick={() => onResolve('local')}>
            Keep Mine
          </button>
        </div>
        <div className="conflict-remote">
          <h3>Their Changes</h3>
          <CardPreview card={remote} />
          <button onClick={() => onResolve('remote')}>
            Use Theirs
          </button>
        </div>
      </div>
      <button onClick={() => onResolve('merge')}>
        Merge Both
      </button>
    </Modal>
  );
};
```

### [55:00 - 60:00] Testing, Deployment & Final Thoughts

**Interviewer**: Last few questions - how would you approach testing and deployment for production?

**Candidate**: Comprehensive testing strategy:

**1. Testing Pyramid:**

```typescript
// Unit Tests - Component logic
describe('Card', () => {
  it('renders card title', () => {
    render(<Card card={mockCard} />);
    expect(screen.getByText(mockCard.title)).toBeInTheDocument();
  });

  it('calls onDragStart when dragging', () => {
    const onDragStart = jest.fn();
    render(<Card card={mockCard} onDragStart={onDragStart} />);
    fireEvent.dragStart(screen.getByRole('article'));
    expect(onDragStart).toHaveBeenCalledWith(mockCard.id);
  });
});

// Integration Tests - Component interactions
describe('Board', () => {
  it('moves card between lists', async () => {
    render(<Board board={mockBoard} />);
    const card = screen.getByText('Card 1');

    // Drag from List A to List B
    await dragAndDrop(card, screen.getByTestId('list-2'));

    // Verify card appears in new list
    within(screen.getByTestId('list-2'))
      .getByText('Card 1');
  });
});

// E2E Tests - Full user flows
describe('Trello Clone E2E', () => {
  it('complete card lifecycle', () => {
    cy.visit('/board/1');

    // Create card
    cy.get('[data-testid="add-card"]').click();
    cy.get('[data-testid="card-title-input"]').type('New Task{enter}');

    // Edit card
    cy.contains('New Task').click();
    cy.get('[data-testid="description"]').type('Description');
    cy.get('[data-testid="save"]').click();

    // Move card
    cy.contains('New Task').drag('[data-testid="list-2"]');

    // Verify persistence
    cy.reload();
    cy.get('[data-testid="list-2"]').should('contain', 'New Task');
  });
});
```

**2. Performance Testing:**

```typescript
// Lighthouse CI for performance budgets
module.exports = {
  ci: {
    collect: {
      numberOfRuns: 3,
    },
    assert: {
      assertions: {
        'categories:performance': ['error', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.95 }],
        'first-contentful-paint': ['error', { maxNumericValue: 2000 }],
        'interactive': ['error', { maxNumericValue: 3500 }],
      },
    },
  },
};
```

**3. Deployment Architecture:**

```yaml
# Docker Compose for easy deployment
version: '3.8'
services:
  frontend:
    build: ./client
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://api:5000

  api:
    build: ./server
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/trello
    depends_on:
      - db

  db:
    image: postgres:14
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=trello
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass

volumes:
  postgres_data:
```

**4. CI/CD Pipeline:**

```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test
      - name: Run E2E tests
        run: npm run test:e2e

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to production
        run: |
          docker build -t trello-clone .
          docker push registry/trello-clone:latest
          kubectl rollout restart deployment/trello-clone
```

**Final Thoughts:**

This project demonstrated my ability to:
1. ✅ Replicate complex UI with extreme detail
2. ✅ Implement functional interactions (drag-drop, modals, forms)
3. ✅ Use modern tools to accelerate development (AI, Vite, TypeScript)
4. ✅ Think about production scalability (real-time, database, testing)
5. ✅ Balance speed with quality (3-4 hours, but high fidelity)

The prototype is production-ready with clear paths for enhancement. I'm confident in my ability to deliver high-quality work quickly while maintaining attention to detail.

**Interviewer**: Thank you! This has been an excellent walkthrough. We appreciate your thoroughness and technical depth.

**Candidate**: Thank you for the opportunity! I enjoyed the challenge and look forward to hearing from you.

---

## End of Transcript

**Total Duration**: 60 minutes
**Sections Covered**:
- ✅ Walkthrough & Detail Review (25 min)
- ✅ Workflow & Velocity Discussion (20 min)
- ✅ Scalability & Component Design (15 min)

**Key Strengths Demonstrated**:
- Visual engineering maturity
- Velocity & efficiency mindset
- Strong technical judgment
- Holistic ownership thinking
- Production-ready architecture knowledge
