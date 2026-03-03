# Kanban App Database Schema

## Overview

The application uses **SQLite** to persist user accounts and kanban boards. The schema is intentionally simple:

- **Users**: Basic user records with hardcoded credentials (MVP stage).
- **Boards**: One board per user; board structure (columns and cards) stored as JSON for flexibility.

This approach avoids deep normalization while maintaining enough structure for future evolution.

---

## Schema

### `users` table

Stores user accounts. For MVP, only one hardcoded user exists, but the schema supports multiple users for future expansion.

```sql
CREATE TABLE users (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT NOT NULL UNIQUE,
  password_hash TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
- `id` - Unique user identifier.
- `username` - Login username (must be unique).
- `password_hash` - **MVP stage:** for demonstration, this will be plain-text or simple hash. In production, use bcrypt/argon2.
- `created_at` - Account creation timestamp.

**MVP Note:** The hardcoded user `user`/`password` will be stored in this table at initialization time.

---

### `boards` table

Stores kanban boards. Each user starts with exactly one board. The board structure (columns, cards, ordering) is stored as a JSON blob for maximum flexibility.

```sql
CREATE TABLE boards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id INTEGER NOT NULL UNIQUE,
  title TEXT NOT NULL DEFAULT 'My Board',
  data JSON NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

**Columns:**
- `id` - Unique board identifier.
- `user_id` - Reference to the owning user (one board per user).
- `title` - Human-readable board title.
- `data` - Complete board structure as JSON. See structure below.
- `created_at` - Board creation timestamp.
- `updated_at` - Last modification timestamp (auto-updated on changes).

**Board Data JSON Structure:**

The `data` column stores the entire kanban board as JSON matching the frontend's `BoardData` type:

```json
{
  "columns": [
    {
      "id": "col-backlog",
      "title": "Backlog",
      "cardIds": ["card-1", "card-2"]
    },
    {
      "id": "col-progress",
      "title": "In Progress",
      "cardIds": ["card-3"]
    }
  ],
  "cards": {
    "card-1": {
      "id": "card-1",
      "title": "Design login page",
      "details": "Create mockups and get feedback."
    },
    "card-2": {
      "id": "card-2",
      "title": "Set up database",
      "details": "Initialize SQLite with schema."
    }
  }
}
```

This structure:
- Maintains column order and title in the `columns` array.
- Stores cards by ID in a lookup object for O(1) access.
- Supports rich relational queries via JSON functions if needed in the future.

---

## Design Rationale

### Why JSON for Board Data?

1. **Simplicity**: The frontend already works with a `BoardData` JavaScript object; storing it directly in JSON avoids translation.
2. **Flexibility**: No need to normalize columns and cards into separate tables during MVP.
3. **Frontend Parity**: Frontend state maps 1:1 to the database, reducing sync issues.
4. **Future Extensibility**: As the app grows, individual column and card tables can be introduced without breaking the API.

### Why One Board Per User (MVP)?

The business requirement states: *"For the MVP, there will only be 1 Kanban board per signed in user."*

The `UNIQUE` constraint on `user_id` enforces this. The API can be extended later to support multiple boards per user.

### Why Plain-Text Passwords?

For MVP with hardcoded credentials, plain-text is acceptable. Before moving to production:
- Use bcrypt or similar for password hashing.
- Implement proper authentication tokens (JWT/sessions).
- Add password reset flows.

---

## Initialization

On first run, the backend will:

1. Create the database file (`:memory:` or `kanban.db` in the project root).
2. Run migrations to create `users` and `boards` tables.
3. Seed the MVP user:
   ```sql
   INSERT INTO users (username, password_hash) VALUES ('user', 'password');
   ```
4. Create an empty board for that user with default columns (Backlog, Discovery, In Progress, Review, Done).

---

## API Contract

### `/api/board` (GET)

**Request:** None (authenticated user from session).

**Response:**
```json
{
  "board": {
    "id": 1,
    "title": "My Board",
    "data": { ... }
  }
}
```

### `/api/board` (POST / PUT)

**Request:**
```json
{
  "data": { ... }
}
```

**Response:** Updated board with new `updated_at` timestamp.

---

## Future Enhancements

1. **Multiple Boards**: Remove `UNIQUE` constraint; add board name and list endpoint.
2. **Collaboration**: Add `board_members` table and per-board permissions.
3. **Card Normalization**: Move to separate `cards` table with `column_id` foreign key for better querying.
4. **Audit Trail**: Add `audit_logs` table to track changes.
5. **Full-Text Search**: Index card titles and details for search.
6. **AI Integration**: Store conversation history and AI-generated suggestions in a separate `ai_interactions` table.

---

## Migration Strategy

Migrations will be simple Python scripts in `backend/migrations/`:

- `001_init_schema.sql` - Creates `users` and `boards` tables.
- `002_seed_mvp_user.py` - Inserts the hardcoded MVP user and default board.

The backend will auto-run pending migrations on startup.
