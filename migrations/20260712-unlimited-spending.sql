ALTER TABLE users
ADD COLUMN IF NOT EXISTS unlimited_spending boolean DEFAULT false NOT NULL;