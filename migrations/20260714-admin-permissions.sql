ALTER TABLE users
ADD COLUMN IF NOT EXISTS admin_permissions varchar(2000) DEFAULT '' NOT NULL;
