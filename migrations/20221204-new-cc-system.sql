UPDATE submissions SET sub = 'countryclub' WHERE club = true AND sub IS NULL;
DELETE FROM modactions WHERE kind IN ('club_allow','club_ban','club_post','unclub_post');
ALTER TABLE submissions DROP COLUMN club;
ALTER TABLE users DROP COLUMN club_allowed;
