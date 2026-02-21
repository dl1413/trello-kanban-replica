# Trello Kanban Board Replica

A fully functional Trello-style Kanban board built with React and Vite.

## Features

- **Drag & Drop** - Reorder cards within lists and move cards between lists. Reorder lists themselves.
- **Cards** - Create, edit, and delete cards with titles, descriptions, and color labels.
- **Lists** - Create, rename, and delete lists (columns).
- **Board Title** - Click to edit the board name.
- **Labels** - Color-coded labels on cards (green, yellow, orange, red, purple, blue).
- **Persistence** - All data saved to localStorage automatically.
- **Responsive** - Horizontal scrolling for many lists.

## Tech Stack

- React 18
- Vite
- @hello-pangea/dnd (drag and drop)
- CSS (no framework — custom Trello-style design)

## Getting Started

```bash
npm install
npm run dev
```

Open http://localhost:5173 in your browser.

## Build

```bash
npm run build
npm run preview
```
