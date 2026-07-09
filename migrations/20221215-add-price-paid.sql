BEGIN;
ALTER TABLE award_relationships ADD COLUMN price_paid INTEGER NOT NULL DEFAULT 0;
ALTER TABLE award_relationships ALTER COLUMN kind SET NOT NULL;

-- populate existing awards, this should match the values in files/helpers/config/awards.py

-- deprecated
UPDATE award_relationships SET price_paid = 3000 WHERE kind = 'ghost';
UPDATE award_relationships SET price_paid = 10000 WHERE kind = 'nword';
-- fistmas 2021
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'snow';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'gingerbread';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'lights';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'candycane';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'fireplace';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'grinch';
-- homoween 2021 and 2022
UPDATE award_relationships SET price_paid = 500 WHERE kind = 'haunt';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'upsidedown';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'stab';
UPDATE award_relationships SET price_paid = 200 WHERE kind = 'spiders';
UPDATE award_relationships SET price_paid = 200 WHERE kind = 'fog';
-- homoween 2022
UPDATE award_relationships SET price_paid = 600 WHERE kind = 'jumpscare';
UPDATE award_relationships SET price_paid = 500 WHERE kind = 'hw-bite';
UPDATE award_relationships SET price_paid = 500 WHERE kind = 'hw-vax';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'hw-grinch';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'flashlight';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'candy-corn';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'ectoplasm';
UPDATE award_relationships SET price_paid = 200 WHERE kind = 'bones';
UPDATE award_relationships SET price_paid = 200 WHERE kind = 'pumpkin';
-- standard
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'marsify';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'shit';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'fireflies';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'train';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'scooter';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'wholesome';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'firework';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'confetti';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'ricardo';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'tilt';
UPDATE award_relationships SET price_paid = 150 WHERE kind = 'glowie';
UPDATE award_relationships SET price_paid = 777 WHERE kind = 'rehab';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'agendaposter';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'offsitementions';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'lootbox';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'beano';
UPDATE award_relationships SET price_paid = 1000 WHERE kind = 'unpin';
UPDATE award_relationships SET price_paid = 1250 WHERE kind = 'flairlock';
UPDATE award_relationships SET price_paid = 1500 WHERE kind = 'pin';
UPDATE award_relationships SET price_paid = 1500 WHERE kind = 'progressivestack';
UPDATE award_relationships SET price_paid = 1500 WHERE kind = 'pizzashill';
UPDATE award_relationships SET price_paid = 1500 WHERE kind = 'bird';
UPDATE award_relationships SET price_paid = 2000 WHERE kind = 'spider';
UPDATE award_relationships SET price_paid = 2750 WHERE kind = 'deflector';
UPDATE award_relationships SET price_paid = 3000 WHERE kind = 'marsey';
UPDATE award_relationships SET price_paid = 3000 WHERE kind = 'ban';
UPDATE award_relationships SET price_paid = 3500 WHERE kind = 'unban';
UPDATE award_relationships SET price_paid = 4000 WHERE kind = 'benefactor';
UPDATE award_relationships SET price_paid = 5000 WHERE kind = 'eye';
UPDATE award_relationships SET price_paid = 10000 WHERE kind = 'grass';
UPDATE award_relationships SET price_paid = 20000 WHERE kind = 'unblockable';
UPDATE award_relationships SET price_paid = 20000 WHERE kind = 'fish';
UPDATE award_relationships SET price_paid = 20000 WHERE kind = 'pause';
UPDATE award_relationships SET price_paid = 40000 WHERE kind = 'unpausable';
UPDATE award_relationships SET price_paid = 50000 WHERE kind = 'alt';
UPDATE award_relationships SET price_paid = 50000 WHERE kind = 'checkmark';
-- wpd
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'owoify';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'rainbow';
-- house awards
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'Furry';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'Femboy';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'Vampire';
UPDATE award_relationships SET price_paid = 400 WHERE kind = 'Racist';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'Furry Founder';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'Femboy Founder';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'Vampire Founder';
UPDATE award_relationships SET price_paid = 300 WHERE kind = 'Racist Founder';
COMMIT;
