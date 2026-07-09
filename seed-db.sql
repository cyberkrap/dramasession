INSERT INTO public.users (
	username, passhash, created_utc, admin_level, over_18, is_activated, 
	original_username, defaultsorting, defaultsortingcomments, defaulttime, namecolor, titlecolor, theme, themecolor,
	cardview, reddit, pronouns, verified, profileurl, highres,
	marsify, last_viewed_post_notifs, last_viewed_log_notifs, last_viewed_reddit_notifs
) VALUES
('AutoJanny', '', extract(epoch from now()), 0, true, true, 
	'AutoJanny', 'hot', 'top', 'day', 'ff66ac', 'ff66ac', 'dark', 'ff66ac',
	false, 'old.reddit.com', 'clean/itup', 'Verified', '/i/pfps/1.webp', '/i/pfps/1.webp',
	0, 0, 0, 0),
('Snappy', '', extract(epoch from now()), 0, true, true, 
	'Snappy', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	false, 'old.reddit.com', 'beep/boop', 'Verified', '/i/pfps/2.webp', '/i/pfps/2.webp',
	0, 0, 0, 0),
('longpostbot', '', extract(epoch from now()), 0, true, true, 
	'longpostbot', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	false, 'old.reddit.com', 'tl/dr', 'Verified', '/i/pfps/3.webp', '/i/pfps/3.webp',
	0, 0, 0, 0),
('zozbot', '', extract(epoch from now()), 0, true, true, 
	'zozbot', 'hot', 'top', 'day', '62ca56', 'e4432d', 'dark', '30409f',
	false, 'old.reddit.com', 'zoz/zle', 'Verified', '/i/pfps/4.webp', '/i/pfps/4.webp',
	0, 0, 0, 0);

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5
-- Dumped by pg_dump version 14.6 (Ubuntu 14.6-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: badge_defs; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.badge_defs VALUES (186, 'Gigavaxxer', 'Vaccinated 10 people during Homoween 2022.', 1667275065);
INSERT INTO public.badge_defs VALUES (187, 'CDC Goon', 'Vaccinated 100 people during Homoween 2022.', 1667275076);
INSERT INTO public.badge_defs VALUES (188, 'Zombiechad', 'Zombified 10 people during Homoween 2022.', 1667275093);
INSERT INTO public.badge_defs VALUES (190, 'Soapy-Mouthed Angel', 'This user has made a lifelong commitment to purity of tongue 😇', 1667694324);
INSERT INTO public.badge_defs VALUES (193, 'Web Design Is My Passion', 'This user is a very special boy who set his very own profile background 🤗', 1670213168);
INSERT INTO public.badge_defs VALUES (136, 'TRAIN 2022', 'Beware: Found to be one of the most transmisic commenters on the site!', NULL);
INSERT INTO public.badge_defs VALUES (137, 'Lottershe Winner', 'This user won the Lottershe grand prize.', NULL);
INSERT INTO public.badge_defs VALUES (192, 'Social Justice Berserker', 'This user has taken a solemn vow to Speak No Evil ⚔', 1667695138);
INSERT INTO public.badge_defs VALUES (194, 'Master Baiter 2021', 'The cunning mastermind behind the ruse which was voted best rdrama bait of 2021.', 1670627103);
INSERT INTO public.badge_defs VALUES (140, 'Y''all Seein'' Eye', 'Gets notified when other sites talk about us', NULL);
INSERT INTO public.badge_defs VALUES (141, 'Marsey Typographer', 'For substantial and exceptional contributions to Marsey Alphabet.', NULL);
INSERT INTO public.badge_defs VALUES (142, 'Punching Down', 'This user mogs incels.', NULL);
INSERT INTO public.badge_defs VALUES (143, 'Marsey God', 'Contributed 100 (or more!!!!) Marsey emojis ✨😻', NULL);
INSERT INTO public.badge_defs VALUES (144, 'Energy Drink Enjoyer', 'Grip ''N Sip.', NULL);
INSERT INTO public.badge_defs VALUES (147, 'Freebase Fiend', 'From the crack grew a glass rose.', NULL);
INSERT INTO public.badge_defs VALUES (148, 'Blackpilled', 'Proud incel ally.', NULL);
INSERT INTO public.badge_defs VALUES (149, 'Thin', 'This user has verified that they are calorically disciplined.', NULL);
INSERT INTO public.badge_defs VALUES (139, 'Auspicious Incident', 'This user was fired from a volunteer position', NULL);
INSERT INTO public.badge_defs VALUES (150, 'Verified', 'Bought a Blue Checkmark.', NULL);
INSERT INTO public.badge_defs VALUES (151, 'Responsible Citizen', 'This user upheld democracy by committing voter fraud.', NULL);
INSERT INTO public.badge_defs VALUES (152, 'Amateur Hathead', 'Collected 25 unique hats', NULL);
INSERT INTO public.badge_defs VALUES (155, 'Ride Or Die Dramalo/Dramalette', 'When I die show no pity / Send my soul to the juggalo city / Dig my grave six feet deep / And put two matches by my feet / Put two hatchets on my chest / And tell my homies I did my best / WHOOP WHOOP', NULL);
INSERT INTO public.badge_defs VALUES (197, 'Best Marsey 2021', 'The creator of the best Marsey emote of 2021, as voted by rdrama users.', 1670627291);
INSERT INTO public.badge_defs VALUES (198, 'Best Drama Post 2021', 'The author of the best drama post of 2021, as voted by rdrama users.', 1670627332);
INSERT INTO public.badge_defs VALUES (199, 'Dramatard of the Year 2021', 'Voted as the best rdrama user of 2021. Congratulations!', 1670627437);
INSERT INTO public.badge_defs VALUES (21, 'Paypig', 'Contributed at least $5', NULL);
INSERT INTO public.badge_defs VALUES (22, 'Renthog', 'Contributed at least $10', NULL);
INSERT INTO public.badge_defs VALUES (23, 'Landchad', 'Contributed at least $20', NULL);
INSERT INTO public.badge_defs VALUES (24, 'Terminally online turboautist', 'Contributed at least $50', NULL);
INSERT INTO public.badge_defs VALUES (157, 'A Minor Setback', 'Lost a 1,000 dramacoin bet. Keep going!', NULL);
INSERT INTO public.badge_defs VALUES (158, 'Just One More Hand', 'Lost a 10,000 dramacoin bet. But it''s fine, you''re due for a big win!', NULL);
INSERT INTO public.badge_defs VALUES (160, 'Lil Goombler', 'Won a 1,000 dramacoin bet. Nice job!', NULL);
INSERT INTO public.badge_defs VALUES (162, 'King Goombler', 'Won a 100,000 dramacoin bet. Wipe your sweaty palms off and bet it all again, you''re on a roll!', NULL);
INSERT INTO public.badge_defs VALUES (163, 'Marsey Jacobs', 'Designed 10 hats!', NULL);
INSERT INTO public.badge_defs VALUES (166, 'Giorgio Armarsey', 'Designed 250 hats 😲', NULL);
INSERT INTO public.badge_defs VALUES (164, 'Marsey de Givenchy', 'Designed 50 hats, holy cap.', NULL);
INSERT INTO public.badge_defs VALUES (180, 'Marsey Consoomer', 'Conned rDrama out of sick merch in exchange for a donation to Redbubble.', 1664417205);
INSERT INTO public.badge_defs VALUES (203, 'Best rdrama OC 2022', 'The creator or commissioner of the best rdrama original content of 2022, as voted by rdrama users.', 1670627675);
INSERT INTO public.badge_defs VALUES (183, '2022 Spooooooky Marsey Artist', 'Contributed a VERY SCARY Marsey for Halloween 2022!', 1666225718);
INSERT INTO public.badge_defs VALUES (168, 'BITTEN!', 'This user has been forcibly recruited to House Vampire', NULL);
INSERT INTO public.badge_defs VALUES (170, 'Marsified', 'This user''s comments get Marsified automatically', NULL);
INSERT INTO public.badge_defs VALUES (167, 'OwOified', 'This user''s comments get OwOified automatically', NULL);
INSERT INTO public.badge_defs VALUES (169, 'Early Life Checked', 'The Early Life section of this user is on full display', NULL);
INSERT INTO public.badge_defs VALUES (172, 'God Save The Kween', 'Commemorative badge awarded for outliving Her Maj', NULL);
INSERT INTO public.badge_defs VALUES (174, 'George', '@Marsey went to Spokane to fight @TrailerParkBride, but George the Mountain Lion was the real winner.', NULL);
INSERT INTO public.badge_defs VALUES (175, 'Pressuring Peer', 'You have applied pressure to poor souls undergoing rehabilitation [n] times. Shame on you!', 1663105259);
INSERT INTO public.badge_defs VALUES (4, 'White Hat', 'Discreetly reported an exploit', NULL);
INSERT INTO public.badge_defs VALUES (176, 'Fish Of The Year', 'Awarded for outstanding achievement in the field of achievement. Well done!', 1663340894);
INSERT INTO public.badge_defs VALUES (177, 'Sweatshop Laborer', 'lmao thanks retard', 1663616592);
INSERT INTO public.badge_defs VALUES (178, 'Marseyhypebeast', 'This user owns OFFICIAL MARSEY MERCH and has waaaaay more sex than you.', 1663616913);
INSERT INTO public.badge_defs VALUES (179, 'Spider!', 'This user is currently best friends with a spider', 1663696289);
INSERT INTO public.badge_defs VALUES (184, 'Homoween 2022 Survivor', 'Awarded for surviving Homoween 2022', 1666225785);
INSERT INTO public.badge_defs VALUES (1, 'Alpha User', 'Joined during open alpha', NULL);
INSERT INTO public.badge_defs VALUES (2, 'Verified Email', 'Verified Email', NULL);
INSERT INTO public.badge_defs VALUES (3, 'Code Contributor', 'Contributed to the site''s source code', NULL);
INSERT INTO public.badge_defs VALUES (185, 'Hallowgrinch', 'TP this Halloween-hating loser''s house.', 1666226224);
INSERT INTO public.badge_defs VALUES (6, 'Beta User', 'Joined during open beta', NULL);
INSERT INTO public.badge_defs VALUES (7, 'Bug Chaser', 'Found a bug', NULL);
INSERT INTO public.badge_defs VALUES (10, 'Bronze Recruiter', 'Recruited 1 friend to join the site', NULL);
INSERT INTO public.badge_defs VALUES (11, 'Silver Recruiter', 'Recruited 10 friends to join the site', NULL);
INSERT INTO public.badge_defs VALUES (12, 'Gold Recruiter', 'Recruited 100 friends to join the site', NULL);
INSERT INTO public.badge_defs VALUES (15, 'Idea Maker', 'Had a good idea for the site which was implemented by the developers', NULL);
INSERT INTO public.badge_defs VALUES (16, 'Marsey Master', 'Contributed 10 (or more!!!!) Marsey emojis ✨', NULL);
INSERT INTO public.badge_defs VALUES (17, 'Marsey Artisan', 'Contributed a Marsey emoji ✨', NULL);
INSERT INTO public.badge_defs VALUES (18, 'Artisan', 'Contributed to site artwork', NULL);
INSERT INTO public.badge_defs VALUES (181, 'INFECTED', 'This user is a mindless zombie.', 1666073382);
INSERT INTO public.badge_defs VALUES (182, 'VAXXMAXXED', 'This user is a mindless zombie.', 1666074754);
INSERT INTO public.badge_defs VALUES (85, 'Sigma User', '', NULL);
INSERT INTO public.badge_defs VALUES (145, 'Amphetamine Aficionado', 'Totally not addicted™', NULL);
INSERT INTO public.badge_defs VALUES (146, 'Coffee Consoomer', 'Don''t talk to me until I''ve had my soy latte.', NULL);
INSERT INTO public.badge_defs VALUES (60, 'Unironically Retarded', 'Demonstrated a wholesale inability to read the room', NULL);
INSERT INTO public.badge_defs VALUES (61, 'Lab Rat', 'Helped test features in development', NULL);
INSERT INTO public.badge_defs VALUES (62, 'Master Baiter', 'For outstanding achievement in the field of catching fish', NULL);
INSERT INTO public.badge_defs VALUES (63, 'Balls', 'I wrote carp on my balls as a sign of submission', NULL);
INSERT INTO public.badge_defs VALUES (64, 'The Other Kind Of Good Journalist', 'Contributed positive media attention to the site', NULL);
INSERT INTO public.badge_defs VALUES (65, '2021 Spooooooky Marsey Artist', 'Contributed a VERY SCARY Marsey for Halloween 2021!', NULL);
INSERT INTO public.badge_defs VALUES (66, 'Sk8r Boi', 'Certifies that this user is NOT a poser', NULL);
INSERT INTO public.badge_defs VALUES (67, 'Unpausable', 'Spent 40,000 coins on an unpausable profile anthem', NULL);
INSERT INTO public.badge_defs VALUES (68, 'Pause Button', 'Spent 20,000 coins on a profile anthem pause button', NULL);
INSERT INTO public.badge_defs VALUES (69, 'Little Big Spender', 'Dropped 10,000 coins at the shop', NULL);
INSERT INTO public.badge_defs VALUES (70, 'Big Spender', 'Dropped 100,000 coins at the shop', NULL);
INSERT INTO public.badge_defs VALUES (71, 'Big Big Spender', 'Dropped 250,000 coins at the shop', NULL);
INSERT INTO public.badge_defs VALUES (72, 'Big Big Big Spender', 'Dropped 500,000 coins at the shop', NULL);
INSERT INTO public.badge_defs VALUES (73, 'Le Rich Gentlesir', 'Spent a fucking million coins at the shop', NULL);
INSERT INTO public.badge_defs VALUES (74, 'Grass Toucher', 'Awarded for molesting plant life', NULL);
INSERT INTO public.badge_defs VALUES (189, 'Super Spreader', 'Zombified 100 people during Homoween 2022.', 1667275100);
INSERT INTO public.badge_defs VALUES (76, 'Low Roller', 'Bought 10 lootboxes', NULL);
INSERT INTO public.badge_defs VALUES (77, 'Middle Roller', 'Bought 50 lootboxes', NULL);
INSERT INTO public.badge_defs VALUES (78, 'High Roller', 'Bought 150 lootboxes', NULL);
INSERT INTO public.badge_defs VALUES (79, 'Merchant', 'Contributed a new line of product to Marsey''s Coin Emporium', NULL);
INSERT INTO public.badge_defs VALUES (80, 'Artist Laureate', '', NULL);
INSERT INTO public.badge_defs VALUES (81, 'Patron of the Arts', 'Sponsored the creation of an approved Marsey', NULL);
INSERT INTO public.badge_defs VALUES (83, 'All-Seeing Eye', 'Can view private profiles', NULL);
INSERT INTO public.badge_defs VALUES (84, 'Alt-Seeing Eye', 'Can see alts', NULL);
INSERT INTO public.badge_defs VALUES (86, 'Holly Jolly Marsey Artist', 'Contributed a VERY JOLLY Marsey for Christmas 2021!', NULL);
INSERT INTO public.badge_defs VALUES (87, 'Unblockable', 'This user is unblockable', NULL);
INSERT INTO public.badge_defs VALUES (88, 'Provider', 'This user provided a bountiful feast for Thanksgiving', NULL);
INSERT INTO public.badge_defs VALUES (89, 'Dinner', 'Yes, it is edible', NULL);
INSERT INTO public.badge_defs VALUES (90, 'Fish', 'This user cannot be unfollowed', NULL);
INSERT INTO public.badge_defs VALUES (91, 'Grinch', 'This user is a joyless grinch who pays money to avoid having fun', NULL);
INSERT INTO public.badge_defs VALUES (92, 'NFT Artist', 'Drew a marsey that was used as an NFT', NULL);
INSERT INTO public.badge_defs VALUES (93, 'NFT Owner', 'Bought a marsey NFT', NULL);
INSERT INTO public.badge_defs VALUES (94, 'Progressive Stack Award', 'Upvotes/downvotes on this user''s posts and comments have double the ranking effect', NULL);
INSERT INTO public.badge_defs VALUES (95, 'Bird Site Award', 'This user is limited to 140 characters', NULL);
INSERT INTO public.badge_defs VALUES (96, 'Flairlock Award', 'This user''s flair has been locked by someone else', NULL);
INSERT INTO public.badge_defs VALUES (97, 'Pizzashill Award', 'This user has to make their posts and comments more than 280 characters', NULL);
INSERT INTO public.badge_defs VALUES (98, 'Marsey Award', 'This user is limited to posting marseys', NULL);
INSERT INTO public.badge_defs VALUES (99, 'Sidebar Artist', 'Contributed artwork featured on the sidebar', NULL);
INSERT INTO public.badge_defs VALUES (100, 'True Believer', 'This user sees through communist lies', NULL);
INSERT INTO public.badge_defs VALUES (101, 'Banner Artist', 'Contributed a banner image to the site', NULL);
INSERT INTO public.badge_defs VALUES (103, 'Benefactor', 'Gave the Benefactor award to someone', NULL);
INSERT INTO public.badge_defs VALUES (104, 'BADASS OUTLAW', 'Bad boy who does not play by the rules', NULL);
INSERT INTO public.badge_defs VALUES (105, 'SCAM', 'lmao get fucked retard', NULL);
INSERT INTO public.badge_defs VALUES (153, 'Professional Hathead', 'Collected 100 unique hats', NULL);
INSERT INTO public.badge_defs VALUES (107, 'Certified BIPOC', 'The mayocide starts now', NULL);
INSERT INTO public.badge_defs VALUES (108, 'Nword Pass', 'With great power comes great responsibility', NULL);
INSERT INTO public.badge_defs VALUES (154, 'Fiscally Irresponsible Hathead', 'Collected 250 unique hats', NULL);
INSERT INTO public.badge_defs VALUES (110, 'Wolf Artisan', 'Contributed a Zombie Wolf emoji ✨', NULL);
INSERT INTO public.badge_defs VALUES (111, 'Wolf Master', 'Contributed 10 (or more!!!!) Zombie Wolf emojis ✨', NULL);
INSERT INTO public.badge_defs VALUES (112, 'Platy Artisan', 'Contributed a Platy emoji ✨', NULL);
INSERT INTO public.badge_defs VALUES (113, 'Platy Master', 'Contributed 10 (or more!!!!) Platy emojis ✨', NULL);
INSERT INTO public.badge_defs VALUES (109, 'Rehab Award', 'Prevented from gambling', NULL);
INSERT INTO public.badge_defs VALUES (114, 'Capy Artisan', 'Contributed a Capy emoji ✨', NULL);
INSERT INTO public.badge_defs VALUES (115, 'Capy Master', 'Contributed 10 (or more!!!!) Capy emojis ✨', NULL);
INSERT INTO public.badge_defs VALUES (116, 'Outreach Award', 'Brought invaluable drama to the starving masses off-site', NULL);
INSERT INTO public.badge_defs VALUES (128, 'Fart-Free', 'This user does NOT fart.', NULL);
INSERT INTO public.badge_defs VALUES (117, 'Stone Skeptic', 'This user rejects igneous lies', NULL);
INSERT INTO public.badge_defs VALUES (129, 'Misinformation Superspreader', 'This poster was fact checked by real American patriots', NULL);
INSERT INTO public.badge_defs VALUES (130, 'Columbine Enthusiast (TEMPORAL FLUX EDITION)', 'This user is an acclaimed Reb+VoDKa slash author', NULL);
INSERT INTO public.badge_defs VALUES (159, 'It''s Over', 'Lost a 100,000 dramacoin bet. It''s fucking over.', NULL);
INSERT INTO public.badge_defs VALUES (161, 'Pro Goombler', 'Won a 10,000 dramacoin bet. Some would say to quit while you''re ahead, but they didn''t just win 10k - keep at it!', NULL);
INSERT INTO public.badge_defs VALUES (165, 'Marsey Chanel', 'Designed 100 hats!!!', NULL);
INSERT INTO public.badge_defs VALUES (28, 'Chud', 'Marked as a chud', NULL);
INSERT INTO public.badge_defs VALUES (171, 'Rainbowed', 'This user has super cute text', NULL);
INSERT INTO public.badge_defs VALUES (135, '1st Birthgay Bash Survivor', 'Awarded for surviving rDrama''s first annual Birthgay Bash', NULL);
INSERT INTO public.badge_defs VALUES (75, 'Homoween 2021 Survivor', 'Awarded for surviving Homoween 2021', NULL);
INSERT INTO public.badge_defs VALUES (59, 'Lolcow', 'Beautiful and valid milk provider', NULL);
INSERT INTO public.badge_defs VALUES (25, 'Marsey''s Sugar Daddy', 'Contributed at least $100', NULL);
INSERT INTO public.badge_defs VALUES (26, 'JIDF Bankroller', 'Donated at least $250', NULL);
INSERT INTO public.badge_defs VALUES (27, 'Rich Bich', 'Contributed at least $500', NULL);
INSERT INTO public.badge_defs VALUES (118, 'Hit!', 'Confirmed removal of a r/stupidpol post for hate speech or threatening violence', NULL);
INSERT INTO public.badge_defs VALUES (119, 'BIG Hit!', 'Confirmed removal of a /r/stupidpol MODERATOR''S post for hate speech or threatening violence', NULL);
INSERT INTO public.badge_defs VALUES (120, 'Msar Bomba', 'Confirmed ban of a r/stupidpol user', NULL);
INSERT INTO public.badge_defs VALUES (121, 'Order of Marsey, 2nd Class', 'Confirmed temp ban of a r/stupidpol moderator', NULL);
INSERT INTO public.badge_defs VALUES (122, 'Order of Marsey, 1st Class', 'Confirmed permanent ban of a /r/stupidpol moderator', NULL);
INSERT INTO public.badge_defs VALUES (123, 'Hero of the Marsey Union', 'Awarded to all soldiers who served during the Special Military Operation to de-nazify r/stupidpol', NULL);
INSERT INTO public.badge_defs VALUES (124, 'COOL GUY', 'This user does NOT watch anime', NULL);
INSERT INTO public.badge_defs VALUES (125, 'Certified LOSER', 'This user watches anime', NULL);
INSERT INTO public.badge_defs VALUES (126, 'Survivor', 'This user braved the Oregon Trail and lived to tell the tale', NULL);
INSERT INTO public.badge_defs VALUES (127, 'Wagonfire', 'This user braved the Oregon Trail and fucking died lmao', NULL);
INSERT INTO public.badge_defs VALUES (131, '21st Century Hitlerite (TEMPORAL FLUX EDITION)', 'This user lost the love of their life in 1940s Berlin', NULL);
INSERT INTO public.badge_defs VALUES (132, 'Duterte''s Most Wanted (TEMPORAL FLUX EDITION)', 'dude weed lmao what year is it', NULL);
INSERT INTO public.badge_defs VALUES (133, 'Rockstar', 'This user submitted an original piece to the song contest', NULL);
INSERT INTO public.badge_defs VALUES (134, '1 Year Old 🥰', 'This user has wasted an ENTIRE YEAR of their life here! Happy birthday!', NULL);
INSERT INTO public.badge_defs VALUES (208, 'Best Drama Post 2022', 'The author of the best drama post of 2022, as voted by rdrama users.', 1670628577);
INSERT INTO public.badge_defs VALUES (212, 'Dramatard of the Year 2022', 'Voted as the best rdrama user of 2022. Congratulations!', 1670719153);
INSERT INTO public.badge_defs VALUES (213, 'Best Marsey 2022', 'The creator of the best Marsey emote of 2022, as voted by rdrama users.', 1670719193);
INSERT INTO public.badge_defs VALUES (214, 'Master Baiter 2022', 'The cunning mastermind behind the ruse which was voted best rdrama bait of 2022.', 1670719221);
INSERT INTO public.badge_defs VALUES (215, 'Own Goal', 'Don''t take this user''s advice on sportsball betting.', 1671150354);
INSERT INTO public.badge_defs VALUES (216, 'Human Rights Abuse Profiteer', 'I hope those 6500 deaths were worth the dramacoin.', 1671150403);
INSERT INTO public.badge_defs VALUES (217, 'Ghost of Qatar', 'Finished in the top 10 of the World Cup 2022 betting leaderboard.', 1671150449);
INSERT INTO public.badge_defs VALUES (221, 'Perfect Pundit', 'Finished #1 on the FIFA World Cup betting leaderboard. Congrats!', 1671151427);
INSERT INTO public.badge_defs VALUES (102, 'Fistmas 21 Survivor', 'Awarded for surviving Fistmas 2021', NULL);
INSERT INTO public.badge_defs VALUES (222, 'Fistmas 22 Survivor', 'Awarded for surviving Fistmas 2022 which may or may not have even happened', 1671157460);
INSERT INTO public.badge_defs VALUES (156, 'Hole Neglecter', 'Let a hole they owned die', NULL);
INSERT INTO public.badge_defs VALUES (224, 'Died of Starvation', 'Couldn''t work out which elf had the most calories', 1672289576);
INSERT INTO public.badge_defs VALUES (225, 'Monkey Playdate', 'Forgot to check their worry levels during Advent of Code 2022, completing at least 1 star.', 1672289660);
INSERT INTO public.badge_defs VALUES (226, 'Stargazer', 'Kept themselves unworried throughout all of Advent of Code 2022, completing all 50 stars.', 1672289696);
INSERT INTO public.badge_defs VALUES (227, 'Saved Christmas with Teh Codez', 'Got the highest score and completed all 50 stars during Advent of Code 2022.', 1672289744);
INSERT INTO public.badge_defs VALUES (229, 'Certified MONSTER Cock', 'This user submit a photo of their dick and it was confirmed to be HUGE', 1674147916);
INSERT INTO public.badge_defs VALUES (230, 'Itty Bitty Clitty', 'This user submit a photo of their dick and it was determined to be more similar to a sad, undersized clit', 1674147964);


--
-- Name: badge_defs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.badge_defs_id_seq', 230, true);


--
-- PostgreSQL database dump complete
--

--
-- PostgreSQL database dump
--

-- Dumped from database version 14.5
-- Dumped by pg_dump version 14.6 (Ubuntu 14.6-1.pgdg20.04+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Data for Name: hat_defs; Type: TABLE DATA; Schema: public; Owner: -
--

INSERT INTO public.hat_defs VALUES (716, 'Baked Beans Bucket Hat', 'This neighbor is wearing beans!', 2, 500, NULL, 1663647585);
INSERT INTO public.hat_defs VALUES (1104, 'Neurohelmet', 'Saddle up, Mechwarrior!', 2, 500, NULL, 1669751799);
INSERT INTO public.hat_defs VALUES (1002, 'Hearty Hands', 'I dont think hands should do that...', 2, 500, NULL, 1667084251);
INSERT INTO public.hat_defs VALUES (1003, 'Dragged', 'HELLLLLLLLLLPPPPPPPPPPPPPPPPP', 2, 500, NULL, 1667084272);
INSERT INTO public.hat_defs VALUES (718, 'Literally Me', 'Sving music, jazz? PTOOEY!', 2, 500, NULL, 1663801724);
INSERT INTO public.hat_defs VALUES (719, 'The Matrix', 'The Matrix is an allegory of the transgender experience that you and everyone else got suckered into watching', 2, 1000, NULL, 1663836639);
INSERT INTO public.hat_defs VALUES (720, 'The Matrix Resurrections', 'Wachowski moment', 2, 1000, NULL, 1663836967);
INSERT INTO public.hat_defs VALUES (721, 'Booba2', 'TFW you see Canadian trans teacher with huge knockers', 2, 1000, NULL, 1663861867);
INSERT INTO public.hat_defs VALUES (722, 'Darth Vader Helmet', 'Cool-looking guy from Star Tre', 2, 500, NULL, 1663892277);
INSERT INTO public.hat_defs VALUES (725, 'New Years Glasses', 'Happy New Year!', 2, 500, NULL, 1663892467);
INSERT INTO public.hat_defs VALUES (726, 'Operator', 'This classical variables has been quantized and is now a Hermitian operator on a Hillbert space.', 2, 500, NULL, 1663893198);
INSERT INTO public.hat_defs VALUES (990, 'Grass', 'Ass and cash also accepted.', 2, 500, NULL, 1666508354);
INSERT INTO public.hat_defs VALUES (1, 'Ushanka', 'The People''s Hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1004, 'Gimme Hands', 'Give me coin, or give me balls', 2, 500, NULL, 1667084296);
INSERT INTO public.hat_defs VALUES (1006, 'Rainbow Dash', 'OMG RAINBOW DASH FROM MLP!?', 2, 500, NULL, 1667168572);
INSERT INTO public.hat_defs VALUES (736, 'Marsey Slime Hat', 'Let this cute little slime marsey climb on your crusty head.', 2, 500, NULL, 1664085993);
INSERT INTO public.hat_defs VALUES (728, 'Kanohi Akaku (Kopaka)', 'Toa of Ice. The obligatory lone wolf character. You''re Lego Sasuke.', 2, 500, NULL, 1663969562);
INSERT INTO public.hat_defs VALUES (729, 'Kanohi Kaukau (Gali)', 'Toa of Water. Lmao, you picked the girl one!', 2, 500, NULL, 1663969637);
INSERT INTO public.hat_defs VALUES (730, 'Kanohi Miru (Lewa)', 'Toa of Air. You''re the funny one of the group, or maybe you just know that the axe was the coolest weapon.', 2, 500, NULL, 1663969803);
INSERT INTO public.hat_defs VALUES (731, 'Kanohi Kakama (Pohatu)', 'Toa of Stone. You''re everybody''s pal and just want the team to stick together. Why is your element separate from Earth? It''s anybody''s guess!', 2, 500, NULL, 1663969919);
INSERT INTO public.hat_defs VALUES (732, 'Kanohi Avohkii (Takanuva)', 'Toa of Light. Well aren''t you just a special snowflake? Fuckin'' think you''re the Chosen One over here or something.', 2, 500, NULL, 1663970033);
INSERT INTO public.hat_defs VALUES (733, 'Kanohi Ignika', 'The Mask of Life. Matoro died for you, and you''re using your life to shitpost about trans people?', 2, 500, NULL, 1663970127);
INSERT INTO public.hat_defs VALUES (734, 'Kanohi Pakari (Onua)', 'Toa of Earth. The wisdom of the group, but wisdom is useless if you don''t share it. Why is your element separate from Stone? Answer me that, wise guy!', 2, 500, NULL, 1663970191);
INSERT INTO public.hat_defs VALUES (735, 'The Yakub', 'Proof that science has, in fact, gone too far', 2, 500, NULL, 1664054894);
INSERT INTO public.hat_defs VALUES (737, 'Duel Wielding', 'Oh shit you''re packing? My bad carry on', 2, 500, NULL, 1664088304);
INSERT INTO public.hat_defs VALUES (3, 'Cat Ears I', 'Mew :3', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (738, 'Godots Visor', '"An A-press is an A-press, you can''t say it''s only half." - TJ "Henry" Yoshi', 2, 500, NULL, 1664189703);
INSERT INTO public.hat_defs VALUES (741, 'Eazy-E Hat', 'BIPOCs wtih Attitude', 2, 500, NULL, 1664339102);
INSERT INTO public.hat_defs VALUES (743, 'Face Hugger', 'This thing bled acid! Who knows what it''s gonna'' do when it''s dead!', 2, 500, NULL, 1664402395);
INSERT INTO public.hat_defs VALUES (740, 'Sleepy', '...Please... ...Let me sleep... ...A little more... ...Please...', 2, 1000, NULL, 1664285288);
INSERT INTO public.hat_defs VALUES (744, 'Webbed', 'It isn''t cum on your face this time-Happy Halloween', 2, 500, NULL, 1664415784);
INSERT INTO public.hat_defs VALUES (745, 'The Jason', 'Slash away those filthy campers jason-Happy Halloween', 2, 500, NULL, 1664415825);
INSERT INTO public.hat_defs VALUES (746, 'Sawwed', 'Ouch you need an Advil?-Happy Halloween', 2, 500, NULL, 1664415857);
INSERT INTO public.hat_defs VALUES (749, 'Stacked', 'Now you''re cute and delicious.', 2, 500, NULL, 1664595845);
INSERT INTO public.hat_defs VALUES (752, 'Gas Mask', 'When the nukes hit you''re first prepared!', 2, 500, NULL, 1664595913);
INSERT INTO public.hat_defs VALUES (747, 'Football Helmet', 'For those who want CTE', 2, 500, NULL, 1664589824);
INSERT INTO public.hat_defs VALUES (748, 'Anti-Foid', 'Down with the Necromatriarchy!', 2, 500, NULL, 1664590716);
INSERT INTO public.hat_defs VALUES (755, 'Ski-mask EYES', 'When 2 eyes isn''t enough have 6!-smokey', 2, 500, NULL, 1664600641);
INSERT INTO public.hat_defs VALUES (757, 'Beanie baby tag', 'Now you''re a plush, into the jar with you-parx5', 2, 500, NULL, 1664602656);
INSERT INTO public.hat_defs VALUES (758, 'Target', 'Bullseye!', 2, 500, NULL, 1664604233);
INSERT INTO public.hat_defs VALUES (760, 'Foxy Grandpa', 'Goddamn you are one foxy grandpa-SalaciousWombat', 2, 500, NULL, 1664633035);
INSERT INTO public.hat_defs VALUES (764, 'Generic Religious Figurehead', 'Good morning', 2, 500, NULL, 1664640654);
INSERT INTO public.hat_defs VALUES (762, 'Cthulhu Mask', 'I would kiss that cutie.', 2, 500, NULL, 1664638109);
INSERT INTO public.hat_defs VALUES (763, 'Top Hat (pentagram)', 'mages vs matriarchy headgear', 2, 500, NULL, 1664638170);
INSERT INTO public.hat_defs VALUES (770, 'Shroom head', 'You really went so long without a shower mushrooms grew?', 2, 500, NULL, 1664658333);
INSERT INTO public.hat_defs VALUES (771, 'Escoffion', 'Look dark... AND STYLISH!', 2, 500, NULL, 1664658375);
INSERT INTO public.hat_defs VALUES (772, 'Attifet', 'You''re a European woman in the 1600s??', 2, 500, NULL, 1664658421);
INSERT INTO public.hat_defs VALUES (774, 'French Fries', 'Now your salty and tasty!', 2, 500, NULL, 1664658675);
INSERT INTO public.hat_defs VALUES (775, 'Condiment Top', 'Now you can squirt out tasty condiments!', 2, 500, NULL, 1664658867);
INSERT INTO public.hat_defs VALUES (767, 'bleh', 'froggy go “bleh”', 2, 500, NULL, 1664646019);
INSERT INTO public.hat_defs VALUES (768, 'PLAYER 1', 'you only have 2 lives left oop', 2, 500, NULL, 1664646508);
INSERT INTO public.hat_defs VALUES (783, 'A Beautiful Mind', 'Or a euphemism for schizophrenia', 2, 1000, NULL, 1664825990);
INSERT INTO public.hat_defs VALUES (784, 'Yolo swag 420 rekt', 'Also known as the epilepsy inducer', 2, 1000, NULL, 1664826603);
INSERT INTO public.hat_defs VALUES (782, 'Fatass minecrap streamer mask', 'I suck his dick / for hours at a time / stare at his nutsack / while I hold back my cum tonite', 2, 500, NULL, 1664768706);
INSERT INTO public.hat_defs VALUES (777, 'Fat and Stinky Visor', 'Why would you put those pins on a visor?!', 2, 500, NULL, 1664683498);
INSERT INTO public.hat_defs VALUES (778, 'Coke Jail', 'You drank pepsi, to coke jail with you.-CocaColaMan', 2, 500, NULL, 1664727469);
INSERT INTO public.hat_defs VALUES (779, 'nemean lion hood', 'Like a true roman, wear a lion!-gudi', 2, 500, NULL, 1664728578);
INSERT INTO public.hat_defs VALUES (780, 'Winged Hussar', 'To battle with wings on your head!', 2, 500, NULL, 1664731432);
INSERT INTO public.hat_defs VALUES (786, 'Ricks hair', 'Wubba lubba dub dub', 2, 500, NULL, 1664930047);
INSERT INTO public.hat_defs VALUES (781, 'BTC', 'Only wear this if you''re worth billions.', 2, 500, NULL, 1664750970);
INSERT INTO public.hat_defs VALUES (803, 'BERSERKER HELM', 'BERSERKER HELM', 2, 500, NULL, 1665088512);
INSERT INTO public.hat_defs VALUES (790, 'LGBTUSSR Officer Hat 2', 'Be fascist and GAYYY!', 2, 1000, NULL, 1664994701);
INSERT INTO public.hat_defs VALUES (793, 'Pornhub', 'We all know why you bought this...', 2, 500, NULL, 1664995981);
INSERT INTO public.hat_defs VALUES (795, 'Ass Eater', 'Good announcement, now show us eating yours.', 2, 500, NULL, 1664996448);
INSERT INTO public.hat_defs VALUES (796, 'Pinhead Mask', 'Your mask is a bit... small.-Happy Halloween!', 2, 500, NULL, 1664997385);
INSERT INTO public.hat_defs VALUES (801, 'Ramen', 'Eatin'' ramen, watchin'' ramen, bein'' ramen', 2, 500, NULL, 1665000479);
INSERT INTO public.hat_defs VALUES (804, 'TF2 Stacked', 'Why wear one hat when you can wear 3!-momomo', 2, 500, NULL, 1665102373);
INSERT INTO public.hat_defs VALUES (806, 'Lotus', 'Now you look and smell pretty like a lotus!-sarah', 2, 500, NULL, 1665103737);
INSERT INTO public.hat_defs VALUES (797, 'Happy Halloween', '🦇 a spooopy title for you 🎃', 2, 500, NULL, 1664998497);
INSERT INTO public.hat_defs VALUES (798, 'BOO', '👻 floating little baby ghosties …… BOO!', 2, 500, NULL, 1664998569);
INSERT INTO public.hat_defs VALUES (799, 'Boobies', 'sorry no, not those kind of boobies', 2, 500, NULL, 1664998710);
INSERT INTO public.hat_defs VALUES (800, 'Peekaboo', 'this little guy will watch over you, just remember to feed him!', 2, 500, NULL, 1664998845);
INSERT INTO public.hat_defs VALUES (1103, 'The MacArthur', 'Fuck you Truman you fucking communist', 2, 500, NULL, 1669320357);
INSERT INTO public.hat_defs VALUES (723, 'Hohol', 'Мій предок :)', 2, 500, NULL, 1663892328);
INSERT INTO public.hat_defs VALUES (982, 'Pochita', 'Friendly chainsaw devil hat', 2, 500, NULL, 1666467185);
INSERT INTO public.hat_defs VALUES (1136, 'Sonichu', 'Go! Sonichu! Go out and zap to the extreme!', 2, 500, NULL, 1673117074);
INSERT INTO public.hat_defs VALUES (750, 'Cave Man', 'UNGA BUNGA UNGA BUNGA OOO OOO', 2, 500, NULL, 1664595865);
INSERT INTO public.hat_defs VALUES (753, 'Doom Guy', 'RIP AND TEAR', 2, 500, NULL, 1664595933);
INSERT INTO public.hat_defs VALUES (991, 'Clocked', 'No hun don''t worry you totally pass', 2, 1000, NULL, 1666508772);
INSERT INTO public.hat_defs VALUES (1139, 'Lunar New Year', '新年快乐!', 2, 1000, NULL, 1673554101);
INSERT INTO public.hat_defs VALUES (974, 'Kitsune Mask I', 'Some weeb furry shit idfk', 2, 500, NULL, 1666459502);
INSERT INTO public.hat_defs VALUES (807, 'The Capy', 'You''re the chosen one! No one can hurt you!', 2, 500, NULL, 1665104052);
INSERT INTO public.hat_defs VALUES (1007, 'Red Halloween Mask', 'Worth a month’s rent, or just being a Top 10 Gigavaxxer or Zigger during Homoween 2022.', 2, 0, NULL, 1667274742);
INSERT INTO public.hat_defs VALUES (1000, 'BADASS DAD', 'A hat for the BADASS dads!', 2, 500, NULL, 1667083950);
INSERT INTO public.hat_defs VALUES (1005, 'The BIRD', 'FUCK YOU, FUCK YOU, ANDDDDDD FUCK YOUUUUUUUUUUUUU', 2, 500, NULL, 1667084316);
INSERT INTO public.hat_defs VALUES (1140, 'Yiff In Hell', 'Translation: "I''m really desperate for social acceptance."', 2, 500, NULL, 1674463260);
INSERT INTO public.hat_defs VALUES (1141, 'NCR Ranger Helmet', '"Patrolling the rdrama almost makes you wish for a nuclear winter"', 2, 500, NULL, 1675539483);
INSERT INTO public.hat_defs VALUES (965, 'FDJ', '"Jetzt bin ich ein Freier Deutsche Jugendfunktionär"', 2, 500, NULL, 1665686729);
INSERT INTO public.hat_defs VALUES (969, 'Elite Pedo Sniper', 'The shemagh gives you +10 accuracy', 2, 500, NULL, 1665817338);
INSERT INTO public.hat_defs VALUES (933, 'Rascal', 'See this person 3 times and they have to give you something-Minecraft MV22', 2, 500, NULL, 1665434625);
INSERT INTO public.hat_defs VALUES (966, 'Noble 6 helmet', 'Alive in a cave in Azod, Reach,', 2, 500, NULL, 1665691416);
INSERT INTO public.hat_defs VALUES (967, 'Punished Snake', 'What are we, some kind of "metal gear V The Phantom Pain?"', 2, 500, NULL, 1665704742);
INSERT INTO public.hat_defs VALUES (912, 'EldenRing', 'Finally the elden lord!', 2, 500, NULL, 1665355539);
INSERT INTO public.hat_defs VALUES (918, 'Bell pepper (green)', 'Why would you choose the WORST bell pepper??', 2, 500, NULL, 1665417034);
INSERT INTO public.hat_defs VALUES (919, 'Bell pepper (yellow)', 'Not the worst bell pepper, not the best. Perfectly balanced.', 2, 500, NULL, 1665417061);
INSERT INTO public.hat_defs VALUES (920, 'corvo attano mask', 'Time to get stealthy', 2, 500, NULL, 1665422211);
INSERT INTO public.hat_defs VALUES (924, 'Duel Wielding 2', 'Duel Wielding in style!', 2, 500, NULL, 1665428048);
INSERT INTO public.hat_defs VALUES (925, 'USA', 'Show off your America pride!', 2, 500, NULL, 1665428183);
INSERT INTO public.hat_defs VALUES (926, 'TV', 'Look ma''! Im on the tele!', 2, 500, NULL, 1665428714);
INSERT INTO public.hat_defs VALUES (92, 'Top Hat (black)', 'Traditional. Classy. Elegant.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (927, 'Wizard', 'You''re a wizard harry!', 2, 500, NULL, 1665429019);
INSERT INTO public.hat_defs VALUES (928, 'astolfo 1', 'Anime weeb lmao', 2, 500, NULL, 1665433824);
INSERT INTO public.hat_defs VALUES (930, 'Afonso 3', 'ATGs cunt bf', 2, 500, NULL, 1665434079);
INSERT INTO public.hat_defs VALUES (931, 'Nose', 'That''s one big SNIFFER', 2, 500, NULL, 1665434351);
INSERT INTO public.hat_defs VALUES (932, 'Sniffer', 'Awaken this ancient dinosaur and put it on your head!-Minecraft MV22', 2, 500, NULL, 1665434600);
INSERT INTO public.hat_defs VALUES (934, 'Tuff Golem', 'Let this little guy show off how cool you are-Minecraft MV22', 2, 500, NULL, 1665434655);
INSERT INTO public.hat_defs VALUES (935, 'Proud Virgin', 'You should be proud to be a virgin!', 2, 500, NULL, 1665535261);
INSERT INTO public.hat_defs VALUES (939, 'Xanax bar', 'When you''re down or sad take a xannex!', 2, 500, NULL, 1665536735);
INSERT INTO public.hat_defs VALUES (940, 'Walter white', 'COOK WITH ME JESSIE', 2, 500, NULL, 1665536970);
INSERT INTO public.hat_defs VALUES (943, 'Tawhid Finger I', 'Praise the one above', 2, 500, NULL, 1665539751);
INSERT INTO public.hat_defs VALUES (944, 'Tawhid Finger II', 'This is for you lord!', 2, 500, NULL, 1665539936);
INSERT INTO public.hat_defs VALUES (946, 'I love STIMS', 'Gotta love stimulants!', 2, 500, NULL, 1665605747);
INSERT INTO public.hat_defs VALUES (947, 'Red Ducky', 'You gotta love this cute hat!', 2, 500, NULL, 1665607061);
INSERT INTO public.hat_defs VALUES (948, 'Imperial Japan', 'BE PART OF IMPERIAL ARMY NOW', 2, 500, NULL, 1665609099);
INSERT INTO public.hat_defs VALUES (952, 'Italian Sin', 'ITALIANS ATTACK', 2, 500, NULL, 1665615049);
INSERT INTO public.hat_defs VALUES (954, 'Bowl', 'GET OUT OF THE BOWL', 2, 500, NULL, 1665615343);
INSERT INTO public.hat_defs VALUES (955, 'Gambler', 'PLAY THIS MAN IN BLACK JACK NOW', 2, 500, NULL, 1665615565);
INSERT INTO public.hat_defs VALUES (890, 'Starfall', 'What a stary night!', 2, 1000, NULL, 1665340169);
INSERT INTO public.hat_defs VALUES (888, 'Balloons I', '99 luftballons', 2, 1000, NULL, 1665339993);
INSERT INTO public.hat_defs VALUES (889, 'Balloons II', 'Upular (LOOK THIS SONG UP IT IS SO GOOD)', 2, 1000, NULL, 1665340023);
INSERT INTO public.hat_defs VALUES (963, 'Buried', 'You''re buried in sand?! HOW DID THIS HAPPEN?', 2, 500, NULL, 1665616459);
INSERT INTO public.hat_defs VALUES (968, 'Bloody Tusks', '🐘🐘🐘🐘🐘🐘🐘🐘', 2, 500, NULL, 1665728710);
INSERT INTO public.hat_defs VALUES (923, 'Bartman', 'Have a cow idfc', 2, 500, NULL, 1665425863);
INSERT INTO public.hat_defs VALUES (980, 'Homoween 2022', 'HAPPY HOMOWEEN 2022, COCKTOBER 31ST BABY 🎉', 2, 0, NULL, 1666466571);
INSERT INTO public.hat_defs VALUES (970, 'CCCP', 'Reserved for communists, patriots and comrades of the Union of Soviet Socialist Republics.', 2, 500, NULL, 1666408651);
INSERT INTO public.hat_defs VALUES (978, 'Glitch 2', 'OOOooo that don''t look good. Better go get that fixed.', 2, 1000, NULL, 1666462293);
INSERT INTO public.hat_defs VALUES (979, 'Evil Eye', 'The eternal eye has opened', 2, 1000, NULL, 1666462388);
INSERT INTO public.hat_defs VALUES (971, 'DOOT DOOT', 'thank you for the hat mr skeltal', 2, 1000, NULL, 1666458989);
INSERT INTO public.hat_defs VALUES (976, 'Bloody Eyes', 'Eldritch headgear', 2, 1000, NULL, 1666462111);
INSERT INTO public.hat_defs VALUES (977, 'Glitch 1', 'Stop punching the monitor, Kyle', 2, 1000, NULL, 1666462267);
INSERT INTO public.hat_defs VALUES (714, 'Captain Falcon', 'The chad that every smash player wanted to imitate, if only his moveset included a shower.', 2, 500, NULL, 1663474615);
INSERT INTO public.hat_defs VALUES (715, 'Inspector Gadget', '"Go go Gadget Brown Bricks!"', 2, 500, NULL, 1663477536);
INSERT INTO public.hat_defs VALUES (724, 'Spartan Helmet', 'THIS IS SPARTA!', 2, 500, NULL, 1663892367);
INSERT INTO public.hat_defs VALUES (983, 'MLP Tiara', 'A tiara for everypony!', 2, 500, NULL, 1666468737);
INSERT INTO public.hat_defs VALUES (998, 'The Miracle of Birth', 'Relive your birthday!', 2, 500, NULL, 1666908681);
INSERT INTO public.hat_defs VALUES (751, 'Butter', 'Southern-fried and full of love.', 2, 500, NULL, 1664595886);
INSERT INTO public.hat_defs VALUES (754, 'Crusader helmet', 'RETAKE THE HOLY LAND!', 2, 500, NULL, 1664595954);
INSERT INTO public.hat_defs VALUES (996, 'Kerfus', 'Nie wkładaj kutasa do elementów ruchomych maszyny.', 2, 500, NULL, 1666733127);
INSERT INTO public.hat_defs VALUES (766, 'book', 'i can read! heheh', 2, 500, NULL, 1664645746);
INSERT INTO public.hat_defs VALUES (997, 'Spermitarian', '2 lil troopers!', 2, 500, NULL, 1666742226);
INSERT INTO public.hat_defs VALUES (787, 'Turban', 'Turban with Bindi Dot (Namaste)', 2, 500, NULL, 1664980060);
INSERT INTO public.hat_defs VALUES (788, 'LGBTUSSR Officer Hat', 'Rule with an iron fist... And use that iron fist for more than ruling ;)', 2, 1000, NULL, 1664994148);
INSERT INTO public.hat_defs VALUES (993, 'Autumn Leaves', 'we call it fall becoz leaf fall down p:', 2, 1000, NULL, 1666729982);
INSERT INTO public.hat_defs VALUES (808, 'The Capy 2', 'The drippiest and pimpiest capybara out there.', 2, 500, NULL, 1665104484);
INSERT INTO public.hat_defs VALUES (1001, 'Uzi', '*Italian noises*', 2, 500, NULL, 1667083976);
INSERT INTO public.hat_defs VALUES (1010, 'WallStreetBets', 'stonks', 2, 1000, NULL, 1667402952);
INSERT INTO public.hat_defs VALUES (676, 'Kepi', 'Army cap for those unlucky enough to be French', 2, 500, NULL, 1663303083);
INSERT INTO public.hat_defs VALUES (678, 'Turkroach', 'Come on Carp this one''s hilarious. It''s semi transparent to clarify', 2, 500, NULL, 1663305640);
INSERT INTO public.hat_defs VALUES (679, 'Judge Dredd', 'THIS USER IS THE LAW', 2, 500, NULL, 1663309533);
INSERT INTO public.hat_defs VALUES (680, 'Hat Stack', 'You are as presumptuous as you are poor and Irish. Challenge not the majesty of my tower of hats.', 2, 500, NULL, 1663310312);
INSERT INTO public.hat_defs VALUES (809, 'Neon cat', 'Nya~ Nya for the neon cat!', 2, 500, NULL, 1665107083);
INSERT INTO public.hat_defs VALUES (813, 'Oni mask 1', 'A scary demonic spirit from japan!? Fucking weeb', 2, 500, NULL, 1665187283);
INSERT INTO public.hat_defs VALUES (814, 'Oni mask 2', 'Time to get funky, Japanese style.', 2, 500, NULL, 1665187310);
INSERT INTO public.hat_defs VALUES (684, 'cans dot wav', 'I am your host, the man they call Ghost.', 2, 500, NULL, 1663378616);
INSERT INTO public.hat_defs VALUES (685, 'The Lawlz II', 'Ben 10 aficionado and connoisseur.', 2, 500, NULL, 1663400628);
INSERT INTO public.hat_defs VALUES (815, 'Top Hat (WPD)', 'A trans-dimensional crossover hat from rDrama’s much cooler big brother', 2, 500, NULL, 1665188158);
INSERT INTO public.hat_defs VALUES (686, 'Pingas', 'Snooping as usual, I see!', 2, 500, NULL, 1663400760);
INSERT INTO public.hat_defs VALUES (687, 'Robbie Rotten', 'Number one hairstyle!', 2, 500, NULL, 1663400876);
INSERT INTO public.hat_defs VALUES (688, 'Stephanie', 'I am not a creep. It was the third image result when I googled "Robbie Rotten hair png"', 2, 500, NULL, 1663400979);
INSERT INTO public.hat_defs VALUES (816, 'Impaled', 'Guess you''re not a vampire.', 2, 500, NULL, 1665188791);
INSERT INTO public.hat_defs VALUES (689, 'Sportacus', 'Official mascot of /h/fatpeoplehate', 2, 500, NULL, 1663401163);
INSERT INTO public.hat_defs VALUES (681, 'Avatar State', 'But when the world needed him most, the Dramatar vanished', 2, 500, NULL, 1663357705);
INSERT INTO public.hat_defs VALUES (682, 'Vampire Mask', 'Totally a current member of House Vampire', 2, 500, NULL, 1663368597);
INSERT INTO public.hat_defs VALUES (817, 'Cyborg', 'Hey do you know the terminator?', 2, 500, NULL, 1665188940);
INSERT INTO public.hat_defs VALUES (818, 'Jarhead', 'What every elden lord needs... A JAR', 2, 500, NULL, 1665189072);
INSERT INTO public.hat_defs VALUES (822, 'Spyglass', 'LAND HOEE', 2, 500, NULL, 1665189991);
INSERT INTO public.hat_defs VALUES (824, 'Hokage', 'You''re finally the HOKAGE!', 2, 500, NULL, 1665190384);
INSERT INTO public.hat_defs VALUES (825, 'Squash', 'Goofy ahh squash on your zombie head.', 2, 500, NULL, 1665190923);
INSERT INTO public.hat_defs VALUES (827, 'Dragon', 'The official hat for @RagnarDanneskjold! Vote Rangar for jannie 2022!', 2, 500, NULL, 1665197323);
INSERT INTO public.hat_defs VALUES (829, 'Femboy', 'Aww what a cute girl! ... Why does "she" have a dick', 2, 500, NULL, 1665255610);
INSERT INTO public.hat_defs VALUES (831, 'On fire', 'HOLY SHIT DUDE YOU''RE ON FIRE.', 2, 1000, NULL, 1665259064);
INSERT INTO public.hat_defs VALUES (832, 'Flowing Petals', 'You look so cute as the petals fall.', 2, 1000, NULL, 1665259202);
INSERT INTO public.hat_defs VALUES (833, 'Butterflies', 'You give me butterflies...', 2, 1000, NULL, 1665259809);
INSERT INTO public.hat_defs VALUES (834, 'Third Eyes', 'OPEN YOUR EYES SHEEPLE', 2, 1000, NULL, 1665259830);
INSERT INTO public.hat_defs VALUES (836, 'BUBBLES', 'AHHH YEAH LETS GOOO BUBBLE TIMES', 2, 1000, NULL, 1665259869);
INSERT INTO public.hat_defs VALUES (838, 'Bats', 'Closest you''ll ever be to batman.', 2, 1000, NULL, 1665260209);
INSERT INTO public.hat_defs VALUES (839, 'Confetti', 'WOOOO you must be special you have confetti!', 2, 1000, NULL, 1665260585);
INSERT INTO public.hat_defs VALUES (840, 'Crawling spider', 'AHHH SPIDER HIT IT', 2, 1000, NULL, 1665260749);
INSERT INTO public.hat_defs VALUES (842, 'Cursor', 'You should click this users profile!', 2, 1000, NULL, 1665260982);
INSERT INTO public.hat_defs VALUES (699, 'Gendo', '"Get in the fucking robot, Marsey."', 2, 500, NULL, 1663431457);
INSERT INTO public.hat_defs VALUES (698, 'Osama', 'Did you ever see that picture of the bin Laden family in the 70''s?', 2, 500, NULL, 1663431148);
INSERT INTO public.hat_defs VALUES (690, 'Dragon Ball Scouter', 'It''s Over 9000!', 2, 500, NULL, 1663428978);
INSERT INTO public.hat_defs VALUES (695, 'Keep Yourself Safe', 'Clicking the "Get Them Help" button is too difficult', 2, 1000, NULL, 1663430574);
INSERT INTO public.hat_defs VALUES (696, 'YoloSwagStudios', 'A parody of The Onion''s cartoonist? Sure, why not.', 2, 500, NULL, 1663430838);
INSERT INTO public.hat_defs VALUES (697, 'Communist Propaganda Poster', 'Marsey Lovers of the world, unite!', 2, 500, NULL, 1663430940);
INSERT INTO public.hat_defs VALUES (700, 'Tariq Nasneed', '"take the thong out yo bussy, playa" -The Buck Breaker, 2020', 2, 500, NULL, 1663431707);
INSERT INTO public.hat_defs VALUES (701, 'Crusader Kings II Theocratic Emperor', 'Pope Glitterhoof ''the Pious'' died horsing around.', 2, 500, NULL, 1663432063);
INSERT INTO public.hat_defs VALUES (702, 'Crusader Kings II Iqta Emperor', 'Four wives. No inheritance issues. Yearly Ramadan. What''s not to love? Inshallah.', 2, 500, NULL, 1663432349);
INSERT INTO public.hat_defs VALUES (703, 'Crusader Kings II Feudal Emperor', '"No one told me I''d lose my tribal levies upon government change..."', 2, 500, NULL, 1663432506);
INSERT INTO public.hat_defs VALUES (704, 'Crusader Kings II Merchant-Republic Emperor', '"You are the Grand Prince of the Principality. The Master Manipulator. The Man behind the curtain. You are... currently losing the Patrician Elective..."', 2, 500, NULL, 1663433054);
INSERT INTO public.hat_defs VALUES (705, 'Crusader Kings II Imperial Emperor', '"Why do all my runs end in restoring the Roman Empire?"', 2, 500, NULL, 1663433156);
INSERT INTO public.hat_defs VALUES (706, 'Dolan', 'Gooby pls', 2, 500, NULL, 1663433251);
INSERT INTO public.hat_defs VALUES (707, 'Live Tucker Reaction', 'Your look of concerned bewilderment will outrage millions.', 2, 500, NULL, 1663433476);
INSERT INTO public.hat_defs VALUES (710, 'Neuron activation', 'Once the autism awakened, it never went away.', 2, 500, NULL, 1663433999);
INSERT INTO public.hat_defs VALUES (711, 'Penguin Classics', 'Required Reading', 2, 500, NULL, 1663434089);
INSERT INTO public.hat_defs VALUES (713, 'Marseyrain', 'Gloomy day, hope the weather clears up', 2, 500, NULL, 1663439931);
INSERT INTO public.hat_defs VALUES (2, 'Fur Hat', 'The first step on your path to fursuit ownership', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (4, 'Cat Ears II', 'Meow :3', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (5, 'Playboy Bunny', 'Will this bring daddy back?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (6, 'Macaroni', 'Get it? Like the song lol', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (7, 'Pirate', 'BUTT pirate', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (8, 'Pirate Captain', 'Like a regular butt pirate, but for tops only', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (9, 'Dreads', 'Finally, an excuse for poor hygiene', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (10, 'The XXXTentacion', 'Pay homage to your favorite dead criminal!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (12, 'The Elvis', 'Remember when this dude nailed a 13-year-old?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (13, 'Gussy Hat', 'Let everyone know that you''re NOT a rapist. Honest.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1008, 'Time for Chili', 'You''re just mad because there''s no clock in your hat', 2, 500, NULL, 1667342600);
INSERT INTO public.hat_defs VALUES (972, 'Evil Pumpkin', 'Rrrrrrrrrr!', 2, 500, NULL, 1666459022);
INSERT INTO public.hat_defs VALUES (984, 'ICEED', 'Something about Coldtwinge on WPD?', 2, 500, NULL, 1666473550);
INSERT INTO public.hat_defs VALUES (975, 'Kitsune Mask II', 'Some more weeb furry shit idfk', 2, 500, NULL, 1666459532);
INSERT INTO public.hat_defs VALUES (1107, 'Fire Sword', 'Tahu''s Fire Sword. It allows the user to channel fire energy.', 2, 500, NULL, 1670205482);
INSERT INTO public.hat_defs VALUES (973, 'Pet Bee', 'Lookit him go! Buzz buzz buzz!!!!', 2, 1000, NULL, 1666459221);

INSERT INTO public.hat_defs VALUES (830, 'Femboy hooters', 'Yes you ARE on the menu', 2, 500, NULL, 1665255628);
INSERT INTO public.hat_defs VALUES (835, 'Rain', 'It''s a sad rainy day', 2, 1000, NULL, 1665259850);
INSERT INTO public.hat_defs VALUES (837, 'Aura (blue)', 'Such power!', 2, 1000, NULL, 1665259885);
INSERT INTO public.hat_defs VALUES (14, 'Riveter', 'Can you do it? Really?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (995, 'Annoying user', 'This user IS ANNOYING', 2, 500, NULL, 1666730032);
INSERT INTO public.hat_defs VALUES (15, 'Top Hat (leprechaun)', 'LLM but Irish', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (843, 'Pet Snek', 'This user has a pet snek', 2, 1000, NULL, 1665261142);
INSERT INTO public.hat_defs VALUES (1013, 'Moon and Stars', 'Become one with the moon and stars!', 2, 500, NULL, 1667516075);
INSERT INTO public.hat_defs VALUES (16, 'Drinky Beer Hat', 'I actually didn''t know these were real things until I made this', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (844, 'Snek Peek', 'When the friendly snek sees over your head', 2, 500, NULL, 1665261263);
INSERT INTO public.hat_defs VALUES (17, 'Viking', 'Rape, pillage, never bathe. Live the dream.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (532, 'Under His Eye', 'WATCH ANOTHER SHOW', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (845, 'Loading', 'please wait', 2, 1000, NULL, 1665261780);
INSERT INTO public.hat_defs VALUES (1014, 'Pilgrim', 'die injun die', 2, 500, NULL, 1667517948);
INSERT INTO public.hat_defs VALUES (921, 'Dishonored Overseer mask', 'Protect the dark one!', 2, 500, NULL, 1665422229);
INSERT INTO public.hat_defs VALUES (893, 'Heart Poof', '*POOF POOF*', 2, 1000, NULL, 1665340533);
INSERT INTO public.hat_defs VALUES (929, 'astolfo 2', 'Pretty pink hair!', 2, 500, NULL, 1665433847);
INSERT INTO public.hat_defs VALUES (949, 'Kasa 1', 'Keeps the sun out your eyes but blinds you at the same time!', 2, 500, NULL, 1665609122);
INSERT INTO public.hat_defs VALUES (951, 'Kasa 3', 'This is just a basket. What farmers wore this?? BLIND ONES?', 2, 500, NULL, 1665609168);
INSERT INTO public.hat_defs VALUES (1105, '1337 Code', ':siren: HACKING IN PROGRESS :siren:', 2, 1000, NULL, 1670132502);
INSERT INTO public.hat_defs VALUES (1012, 'Marsey Slain', 'You monster... what have you done..', 2, 500, NULL, 1667516047);
INSERT INTO public.hat_defs VALUES (1016, 'Antlers', 'Be careful. I''ll shoot ya!', 2, 500, NULL, 1667531769);
INSERT INTO public.hat_defs VALUES (712, 'Thursday The 20th', '20% off on every Thursday. 30% off on the 20th of every month. 50% off on Thurday the 20th!', 2, 500, NULL, 1663434472);
INSERT INTO public.hat_defs VALUES (1017, 'Gloomy Bear', 'Is he safe to pet?', 2, 500, NULL, 1667792513);
INSERT INTO public.hat_defs VALUES (22, 'Southern Gentleman', 'Slaveowner? Fried chicken chain founder? You decide!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1018, 'Seatbelt', 'Don''t worry! You''re safe in a crash. Unless you’re not.', 2, 500, NULL, 1668042586);
INSERT INTO public.hat_defs VALUES (23, 'Cowboy I', 'Make him wish he could quit you', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1021, 'Kerfus III', 'just a little guy...', 2, 500, NULL, 1668477716);
INSERT INTO public.hat_defs VALUES (24, 'Cowboy II', 'You''re my favorite deputy!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (25, 'Halo', 'Dramamine criticized this one and now I''m too self-conscious about it to write a description', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (26, 'Fedora I', 'M''arsey', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (27, 'Bowler', 'Why would you need a hat to go bowling?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (28, 'Du Rag (black)', 'Shitty bandana 1/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (848, 'Music Notes', 'LALALA LA LA', 2, 1000, NULL, 1665262588);
INSERT INTO public.hat_defs VALUES (849, 'Cloudy', 'What a cloudy day.', 2, 1000, NULL, 1665263018);
INSERT INTO public.hat_defs VALUES (850, 'TREX', 'RAWRRRRRRRRRRRRr', 2, 500, NULL, 1665268343);
INSERT INTO public.hat_defs VALUES (29, 'Du Rag (red)', 'Shitty bandana 2/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (30, 'Du Rag (blue)', 'Shitty bandana 3/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (31, 'Du Rag (purple)', 'Shitty bandana 4/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (32, 'Du Rag (green)', 'Shitty bandana 5/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (851, 'Dr Pepper', 'The best soda as a hat!', 2, 500, NULL, 1665268361);
INSERT INTO public.hat_defs VALUES (33, 'Du Rag (yellow)', 'Shitty bandana 6/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (852, 'Pikmin leaf', 'A classic of the wii you''re now a pikmin!', 2, 500, NULL, 1665268398);
INSERT INTO public.hat_defs VALUES (34, 'Ash Ketchum', 'You''re not so different, you and he', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (35, 'The Hotep', 'Traditional kangwear. POC ONLY.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (36, 'Roman', 'Reddit delenda est', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (37, 'Confederate Soldier Cap', 'Basically the Gryffindor of American history', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (38, 'Northern Aggressor Soldier Cap', 'Slytherin irl', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (39, 'Rhodesian Light Infantry Beret', 'Rhodesians never die. Immortality guaranteed!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (40, 'Magyar Headdress', 'Channel your inner QuadNarca and join Orban''s elite cavalry', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (41, 'The Senator Warren', 'heya heya heya heya heya heya heya heya heya heya heya', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (42, 'Please Be Patient I Have Autism', 'The OFFICIAL hat of rDrama.net', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (44, 'Watermelmet', 'Hydration and head protection all rolled into one stylish headpiece', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (45, 'Frankenstein', 'Akshually, Frankenstein was the scientist. The monster didn''t have a name.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (46, 'The Drumpf', 'Orange hair bad', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (47, 'Tinfoil Hat', 'Keep Bill Gates'' 5G vaccine OUT of your precious brain!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (48, 'Fez', 'Isn''t it CUTE?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (49, 'Ching Chong', 'Me Chinese Me No Dumb Me Stick Finger In Daddy''s Bum', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (50, 'Octopus Friend', 'Awwwwwww!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (51, 'In The Navy', 'It''s not gay', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (52, 'Seaman', 'semen lol', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (53, 'Flower Crown I', 'oh god i have to write descriptions for 15 flower crowns', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (54, 'Flower Crown II', 'A very cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (55, 'Flower Crown III', 'A super cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (56, 'Flower Crown IV', 'A really cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (57, 'Flower Crown V', 'The cutest flower crown?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (58, 'Flower Crown VI', 'An extremely cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (59, 'Flower Crown VII', 'A flower crown that''s just so cute', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (60, 'Flower Crown VIII', 'A majorly cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (61, 'Flower Crown IX', 'A mega cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (62, 'Flower Crown X', 'An ultra cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (63, 'Flower Crown XI', 'Definitely the cutest flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (64, 'Flower Crown XII', 'A hella cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (65, 'Flower Crown XIII', 'An experimental anti-gravity cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (66, 'Flower Crown XIV', 'An adorably cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (67, 'Flower Crown XV', 'The final cute flower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (68, 'Bow', 'What a cute little bow omg', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (69, 'BIPOCsmoke', 'It''s a Newport. You know it''s a Newport.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (70, 'Gigachin', 'Aw yeah, this user definitely supports trans rights', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (71, 'Queensguard', 'A bear died for this', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (72, 'Queen Crown', 'Don''t be a drag', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (73, 'King Crown', 'King is like the n word, only racists and black people should be allowed to say it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (74, 'Pope Hat', 'Matthew 16:18', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (75, 'Heebhead', 'Do NOT google the Lavon Affair', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (76, 'Zoomie Zoom Zoom', 'Underage user, do not interact', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (77, 'Sombrero I', 'El Autistico', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (78, 'Sombrero II', 'El Autistico Grandisimo', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (79, 'Crypto Billionaire', 'Sorry about the ice cream machine', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (80, 'Burger King Crown', 'I''m gonna say it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (81, 'Burger King', 'You can have it your way and you still chose this', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (82, 'Wendys', 'Sassy social media intern', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (83, 'KFC', 'Popeyes is too far away', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (84, 'In-N-Out', 'Kill the commiefornian', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (85, 'Carls Jr', 'Purveyor of literally the finest food in the world', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (86, 'Whataburger', 'Texans don''t know any better', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (87, 'Five Guys', 'I love having 5 guys in my mouth', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (88, 'Taco Bell', 'Enabler of drunken mistakes', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (854, 'Cute Spider', 'My friend Heather calls them web friends', 2, 500, NULL, 1665268447);
INSERT INTO public.hat_defs VALUES (859, 'Freddy Krueger', 'Haunt other people''s nightmares and dreams!', 2, 500, NULL, 1665269059);
INSERT INTO public.hat_defs VALUES (860, 'Turkey Turkey', '🦃 gobble gobble gobble gobble 🦃', 2, 500, NULL, 1665269774);
INSERT INTO public.hat_defs VALUES (862, 'Predator', 'Not the reddit sort', 2, 500, NULL, 1665269828);
INSERT INTO public.hat_defs VALUES (864, 'Predator II', 'Suck that face faggot', 2, 500, NULL, 1665269878);
INSERT INTO public.hat_defs VALUES (870, 'Windmill', 'Why is there a windmill on your head-', 2, 500, NULL, 1665272605);
INSERT INTO public.hat_defs VALUES (869, 'Fluffy Marsey', 'AAAAAHHHHHH LOOK HOW CUTE', 2, 500, NULL, 1665272581);
INSERT INTO public.hat_defs VALUES (1108, 'Mistletoe', 'Catch me french kissing my cousin under here Christmas Eve 2017', 2, 500, NULL, 1670382589);
INSERT INTO public.hat_defs VALUES (1022, 'Kerfus IV', 'uwu? uwu.........? meow?', 2, 500, NULL, 1668478084);
INSERT INTO public.hat_defs VALUES (89, 'Marsey-In-A-Box', 'Awww you''re playing make-believe!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (90, 'Orthodox Hood', 'User is a schismatic lunatic', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (853, 'Crab head', '🦀🦀🦀🦀🦀🦀🦀🦀🦀', 2, 500, NULL, 1665268419);
INSERT INTO public.hat_defs VALUES (861, 'Bowl Cut', 'Who cut your hair? Your mom?', 2, 500, NULL, 1665269794);
INSERT INTO public.hat_defs VALUES (866, 'Venom Mask', 'PUT THE TOUNGUE AWAY', 2, 500, NULL, 1665272503);
INSERT INTO public.hat_defs VALUES (871, 'Kirby Beanie', 'Be careful he''ll swallow you', 2, 500, NULL, 1665272632);
INSERT INTO public.hat_defs VALUES (872, 'Pinwheels', 'Holland hat holland hat', 2, 1000, NULL, 1665272653);
INSERT INTO public.hat_defs VALUES (894, 'Jellyfish Fields', 'Great on Krabby Patties', 2, 1000, NULL, 1665340702);
INSERT INTO public.hat_defs VALUES (884, 'Lightning strike', '*ZAP*', 2, 1000, NULL, 1665339450);
INSERT INTO public.hat_defs VALUES (950, 'Kasa 2', 'The most known farmer hat from japan!', 2, 500, NULL, 1665609141);
INSERT INTO public.hat_defs VALUES (631, 'Country Club Visor', 'What country club members wear when discussing your reddit account', 2, 500, NULL, 1663033011);
INSERT INTO public.hat_defs VALUES (632, 'Jotaro Hat', 'The iconic cap of a buff punchy weebshit guy', 2, 500, NULL, 1663033206);
INSERT INTO public.hat_defs VALUES (629, 'Marisas Big Witch Hat', 'Fascism is when witches wear big hats, the bigger the hat the more fascist you are.', 2, 500, NULL, 1663010108);
INSERT INTO public.hat_defs VALUES (633, 'Man, I Love Fishing', 'post-wall appreciator', 2, 500, NULL, 1663043038);
INSERT INTO public.hat_defs VALUES (635, 'Gagged n Blinded', 'Ask me about my sex swing', 2, 500, NULL, 1663049833);
INSERT INTO public.hat_defs VALUES (634, 'Roxy Hair', 'Dommy mommy animatronic wolf', 2, 500, NULL, 1663043599);
INSERT INTO public.hat_defs VALUES (638, 'Chen', 'HONKS VIOLENLTY', 2, 500, NULL, 1663100660);
INSERT INTO public.hat_defs VALUES (636, 'Senjutsu', 'HAAAAAAAAVE YOU SEEN THE WRITING ON THE WALL?', 2, 500, NULL, 1663094125);
INSERT INTO public.hat_defs VALUES (640, 'Bored Ape', 'DO NOT RIGHT CLICK!', 2, 500, NULL, 1663105351);
INSERT INTO public.hat_defs VALUES (641, 'MUSHROOM CLOUD', 'The Samson Option has been invoked.', 2, 1000, NULL, 1663121242);
INSERT INTO public.hat_defs VALUES (643, 'Only One Large Snake Not Mating', 'Looks cute until she''s on YOUR head', 2, 500, NULL, 1663132332);
INSERT INTO public.hat_defs VALUES (644, 'Poppy', 'The TRUE rDrama mascot', 2, 500, NULL, 1663132488);
INSERT INTO public.hat_defs VALUES (645, 'The SRDine', 'CANNED', 2, 500, NULL, 1663132545);
INSERT INTO public.hat_defs VALUES (646, 'Turtle Helmet', 'u/awkwardtheturtle is VERY mad at you', 2, 500, NULL, 1663132947);
INSERT INTO public.hat_defs VALUES (648, 'Diamond Helmet', 'So I did some mining off camera...', 2, 500, NULL, 1663133082);
INSERT INTO public.hat_defs VALUES (873, 'Jaws', 'AHH WATCH OUT BELOW YOU', 2, 500, NULL, 1665272685);
INSERT INTO public.hat_defs VALUES (1110, 'Brave Shill', 'Show others that you use Brave Browser.', 2, 500, NULL, 1670803448);
INSERT INTO public.hat_defs VALUES (1112, 'Mexico Flag', 'Mexicanos al grito de guerra', 2, 1000, NULL, 1670815485);
INSERT INTO public.hat_defs VALUES (1113, 'Postal Conscience', '"Good or Insane? The choice is yours!" (From Postal 3!)', 2, 500, NULL, 1670890618);
INSERT INTO public.hat_defs VALUES (1114, 'Djenter', '000-0-000-0-000-0-000-0-000-0-000-0-000-0-000-0', 2, 500, NULL, 1670901458);
INSERT INTO public.hat_defs VALUES (1120, 'Present Bow', 'the ghost of christmas present', 2, 0, NULL, 1671231987);
INSERT INTO public.hat_defs VALUES (1119, 'Winter Cap', 'cold air goes brrrrr', 2, 0, NULL, 1671231828);
INSERT INTO public.hat_defs VALUES (1118, 'Santa Hat III', 'ho ho ho', 2, 0, NULL, 1671231728);
INSERT INTO public.hat_defs VALUES (1024, 'Snowfall', 'I''m dreaming, of a BIPOC Christmas...', 2, 1000, NULL, 1668549688);
INSERT INTO public.hat_defs VALUES (1025, 'Christmas Wreath', 'Prepare to feel my wreath.', 2, 500, NULL, 1668549747);
INSERT INTO public.hat_defs VALUES (1026, 'Christmas Wreath II', 'All I want for Christmas is fresh bussy.', 2, 500, NULL, 1668550006);
INSERT INTO public.hat_defs VALUES (1027, 'Lucario Ears', 'The pokémon that birthed a million furries.', 2, 500, NULL, 1668551206);
INSERT INTO public.hat_defs VALUES (1028, 'Pikachu Hat', 'The world''s second most iconic mouse mascot.', 2, 500, NULL, 1668551580);
INSERT INTO public.hat_defs VALUES (1029, 'Christmas Lights', 'Roping just got a lot more festive!', 2, 1000, NULL, 1668552614);
INSERT INTO public.hat_defs VALUES (1031, 'Snowman', 'A carrot can be used for more than just the nose.', 2, 500, NULL, 1668556379);
INSERT INTO public.hat_defs VALUES (1032, 'Umbreon Ears II', 'The egyptian moon dog.', 2, 500, NULL, 1668557141);
INSERT INTO public.hat_defs VALUES (1033, 'Sylveon', 'The notorious ribbon dog.', 2, 500, NULL, 1668557845);
INSERT INTO public.hat_defs VALUES (1037, 'Plague Doctor', 'What ails you, my friend?', 2, 500, NULL, 1668558833);
INSERT INTO public.hat_defs VALUES (1038, 'Bloodborne Hunter Hat and Mask', 'It''s a swell night for a hunt.', 2, 500, NULL, 1668649242);
INSERT INTO public.hat_defs VALUES (1040, 'Meowth Hat and Whiskers', 'Blasting off again.', 2, 500, NULL, 1668650455);
INSERT INTO public.hat_defs VALUES (1041, 'Dream Mask', 'I suck his dick for hours at a time, stare at his nutsack while I hold back my cum tonight, and when he ask me what position I say doggy style', 2, 500, NULL, 1668650964);
INSERT INTO public.hat_defs VALUES (1043, 'Magic Circle', 'Automatically unlocks on your 30th birthday if you stayed true to your inceldom.', 2, 1000, NULL, 1668652370);
INSERT INTO public.hat_defs VALUES (1044, 'Magic Circle II', 'Don''t worry sweetie, magic powers are TOTALLY better than having sex.', 2, 1000, NULL, 1668652691);
INSERT INTO public.hat_defs VALUES (1045, 'Magic Circle III', 'This still won''t let you summon an anime succubus waifu.', 2, 1000, NULL, 1668653088);
INSERT INTO public.hat_defs VALUES (1046, 'Magic Circle IV', 'Swiggity swoodle, your dick is now a noodle.', 2, 1000, NULL, 1668653382);
INSERT INTO public.hat_defs VALUES (1047, 'Firefox Shill', 'Just pray that no more of your users discover Brave.', 2, 500, NULL, 1668654054);
INSERT INTO public.hat_defs VALUES (1019, 'Kerfus I', 'we ask that you please do NOT fuck the robot cat!', 2, 500, NULL, 1668476687);
INSERT INTO public.hat_defs VALUES (1020, 'Kerfus II', 'salesman kitty :3', 2, 500, NULL, 1668477006);
INSERT INTO public.hat_defs VALUES (1023, 'Kerfus V', 'GET VORED BITCH', 2, 500, NULL, 1668478570);
INSERT INTO public.hat_defs VALUES (91, 'Afro', 'Pool''s closed motherlover', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (18, 'Nonspecific Military Officer Hat', '[removed]', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (19, 'Soviet Officer I', 'OUR hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (408, 'Chef Hat II', 'Toque blanche', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (414, 'Trilby', '*tip*', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (419, 'Alimony Hair', 'Stay norwooding, king', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1048, 'United Kingdom Flag', 'RULE BRITANNIA, BRITANNIA RULES THE WAVES', 2, 1000, NULL, 1668709623);
INSERT INTO public.hat_defs VALUES (1049, 'United States of America Flag', 'The best goddamn country on this planet and everyone knows it.', 2, 1000, NULL, 1668709826);
INSERT INTO public.hat_defs VALUES (1050, 'Canada Flag', 'Number one in the world at keeping the mentally ill safe.', 2, 1000, NULL, 1668710045);
INSERT INTO public.hat_defs VALUES (1053, 'England Flag', 'IT''S COMING HOME, IT''S COOOOMING HOME', 2, 1000, NULL, 1668710363);
INSERT INTO public.hat_defs VALUES (1054, 'Brazil Flag', 'Gib mone pl0x or I report u huehuehue', 2, 1000, NULL, 1668710960);
INSERT INTO public.hat_defs VALUES (1055, 'Germany Flag', 'Klappe zu, Affe tot.', 2, 1000, NULL, 1668711193);
INSERT INTO public.hat_defs VALUES (1056, 'Argentina Flag', 'LOS MALVINAS SON ARGENTINAS', 2, 1000, NULL, 1668711374);
INSERT INTO public.hat_defs VALUES (1057, 'China Flag', '动态网自由门 天安門 天安门 法輪功 李洪志 Free Tibet 六四天安門事件 The Tiananmen Square protests of 1989 天安門大屠殺 The Tiananmen Square Massacre 反右派鬥爭 The Anti-Rightist Struggle 大躍進政策 The Great Leap Forward 文化大革命 The Great Proletarian Cultural Revolution', 2, 1000, NULL, 1668711609);
INSERT INTO public.hat_defs VALUES (1058, 'France Flag', 'C''est la vie.', 2, 1000, NULL, 1668711767);
INSERT INTO public.hat_defs VALUES (1059, 'Spain Flag', 'Cada loco con su tema.', 2, 1000, NULL, 1668711951);
INSERT INTO public.hat_defs VALUES (1060, 'Israel Flag', 'A show of support to the last bastion of democracy in the middle east.', 2, 1000, NULL, 1668712425);
INSERT INTO public.hat_defs VALUES (1061, 'Italy Flag', 'When the moon hits your eye like a big pizza pie, that''s amore.', 2, 1000, NULL, 1668712465);
INSERT INTO public.hat_defs VALUES (1062, 'Scotland Flag', 'FREEEEEEEEEEEEEDOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOM!!!', 2, 1000, NULL, 1668712499);
INSERT INTO public.hat_defs VALUES (1063, 'Ukraine Flag', 'Slava Ukraini!', 2, 1000, NULL, 1668712521);
INSERT INTO public.hat_defs VALUES (1064, 'Portugal Flag', 'Aqui se faz, aqui se paga.', 2, 1000, NULL, 1668712672);
INSERT INTO public.hat_defs VALUES (1065, 'Netherlands (Dutch) Flag', 'Joost fuck my shit up.', 2, 1000, NULL, 1668712717);
INSERT INTO public.hat_defs VALUES (1066, 'Australia Flag', 'The world''s most overcrowded prison colony.', 2, 1000, NULL, 1668712883);
INSERT INTO public.hat_defs VALUES (1067, 'India Flag', 'Please do the needful.', 2, 1000, NULL, 1668713144);
INSERT INTO public.hat_defs VALUES (1068, 'Poland Flag', 'Kurwa.', 2, 1000, NULL, 1668713159);
INSERT INTO public.hat_defs VALUES (1069, 'Russia Flag', 'Making Nazis seethe since 1942.', 2, 1000, NULL, 1668713214);
INSERT INTO public.hat_defs VALUES (1070, 'Pride Flag', 'Never forget that this is a primarily gay community. Dude bussy lmao.', 2, 1000, NULL, 1668713844);
INSERT INTO public.hat_defs VALUES (1071, 'Trans Flag', 'Just in case you forgot, trans lives matter.', 2, 1000, NULL, 1668713920);
INSERT INTO public.hat_defs VALUES (1072, 'Trans Flag II', 'Your egg is cracked; wear it with pride!', 2, 1000, NULL, 1668714108);
INSERT INTO public.hat_defs VALUES (1073, 'Pride Flag II', 'This user is a proud supporter of LGBTQ+ rights.', 2, 1000, NULL, 1668714598);
INSERT INTO public.hat_defs VALUES (1086, 'Melee Shine', 'That aint Falco.', 2, 1000, NULL, 1668880040);
INSERT INTO public.hat_defs VALUES (1089, 'Ring of Fire', 'Love is a burning thing, and it makes a fiery ring.', 2, 1000, NULL, 1668881782);
INSERT INTO public.hat_defs VALUES (1091, 'Ring of Fire II', 'Bound by wild desire, I fell into a ring of fire.', 2, 1000, NULL, 1668882874);
INSERT INTO public.hat_defs VALUES (1092, 'Triggered Banner', 'Include a content warning next time, you insensitive asswipe.', 2, 1000, NULL, 1668884298);
INSERT INTO public.hat_defs VALUES (1093, 'Anime Speed Lines', 'It''s just like in my Chinese cartoons!', 2, 1000, NULL, 1668899890);
INSERT INTO public.hat_defs VALUES (1096, 'Ghost of Qatar', 'Ghost of Qatar World Cup 2022 Exclusive Hat', 2, 500, NULL, 1668979015);
INSERT INTO public.hat_defs VALUES (1078, 'Spinning Santa Hat', '🎅🔄', 2, 1000, NULL, 1668755506);
INSERT INTO public.hat_defs VALUES (1082, 'Aleister Crowley', 'Kippys a bitch, become a cult leader!', 2, 500, NULL, 1668829567);
INSERT INTO public.hat_defs VALUES (1074, 'Scottish Sticky Note', 'idk why its scottish the dude who submit it just called it that and wrote something in a scottish accent here but ????? what makes the sticky note scottish ?????????', 2, 500, NULL, 1668720533);
INSERT INTO public.hat_defs VALUES (1076, 'Snow Globe', 'Snow globe full of partially transparent webp flakes', 2, 1000, NULL, 1668755503);
INSERT INTO public.hat_defs VALUES (1079, 'Spinning Christmas Elf Hat', 'It''s time to go green.', 2, 1000, NULL, 1668755556);
INSERT INTO public.hat_defs VALUES (1100, 'World Cup Mascot', 'This user supports the 2022 World Cup and watched it for Jungkook!', 2, 500, NULL, 1669007389);
INSERT INTO public.hat_defs VALUES (874, 'Carp', 'My 100th hat and a Thank you to carp. Now 150 more!', 2, 500, NULL, 1665272718);
INSERT INTO public.hat_defs VALUES (1077, 'Premium Snow Globe', 'Snow globe with a more premium base.', 2, 1000, NULL, 1668755505);
INSERT INTO public.hat_defs VALUES (93, 'Wizard I', 'Three decades a KHHV', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (94, 'Wizard II', 'Avada kedavra ✨', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (95, 'Witch I', 'Hex the patriarchy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (96, 'Witch II', 'Bardfinn cosplay gear', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (97, 'Sun Hat', 'Tradwife simplicity', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (98, 'Obey Snapback', 'The timeless classic', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (99, 'Thug Life Snapback', 'User confirmed mayo', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (655, 'Thigarette', 'Smokers are jokers', 2, 1000, NULL, 1663160917);
INSERT INTO public.hat_defs VALUES (101, 'Make America Great Again', 'The official headgear of stochastic terrorists everywhere', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (656, 'Thigarette (BIPOC)', 'Smokers are JOKERS', 2, 1000, NULL, 1663161103);
INSERT INTO public.hat_defs VALUES (654, 'VR', 'Be honest, you bought it for porn', 2, 500, NULL, 1663153216);
INSERT INTO public.hat_defs VALUES (642, 'Spotlight', 'Lights, Camera, Action!', 2, 1000, NULL, 1663122185);
INSERT INTO public.hat_defs VALUES (651, 'Chainmail Helmet', 'Shameless coloniser of (((villagers)))', 2, 500, NULL, 1663133337);
INSERT INTO public.hat_defs VALUES (653, 'Freddy Mask', '[JUMPSCARE]', 2, 500, NULL, 1663133417);
INSERT INTO public.hat_defs VALUES (102, 'Born To Feel', 'Do you pee standing up?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (657, 'Coins', 'The Princess Is In Another Castle', 2, 1000, NULL, 1663200349);
INSERT INTO public.hat_defs VALUES (103, 'Fortunate Son', 'BORN TO SHIT FORCED TO WIPE', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (104, 'WWI', 'How is this supposed to offer any meaningful protection??', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (105, 'Pickelhaube', 'Inarguably the most fashionable of all contemporary military headgear ', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (106, 'Wehrmacht', 'What a cool helmet, I bet the people who wore it were real classy folks ', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (108, 'Helmet w Dog Tags', 'More like dog fags lol', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (109, 'Urban Camo Helmet', 'Man urban camo is cool', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (110, 'Nightvision Helmet', 'Four-eyed freak', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (111, 'Helmet w Mesh', 'Sexy fishnet stocking helmet', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (112, 'Tojo Helmet', 'Artifact from Weeb War II', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (113, 'Officers Cap', 'Get fragged bozo', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (114, 'Jailbird Cap', 'The apex of prison fashion. Why did we stop using this?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (659, 'Brain Worms', 'This explains a lot.', 2, 500, NULL, 1663229235);
INSERT INTO public.hat_defs VALUES (674, 'Fat Rat Grab', 'He''ll cook you dinner, the useful rodent', 2, 500, NULL, 1663295500);
INSERT INTO public.hat_defs VALUES (665, 'Diddy Kong Hat', '"He''s back again and about time too! And this time he''s in the mood! He can fly real high with his jetpack on! With his pistols out, he''s one tough Kong!"', 2, 500, NULL, 1663279805);
INSERT INTO public.hat_defs VALUES (666, 'Gamer Hat', 'When you want everyone to know your opinions on the female gender', 2, 500, NULL, 1663279854);
INSERT INTO public.hat_defs VALUES (670, 'Miners Helmet', 'Everybody wants to have sex with them', 2, 500, NULL, 1663280073);
INSERT INTO public.hat_defs VALUES (671, 'The Son of Man', 'Hide your face with an apple', 2, 500, NULL, 1663280110);
INSERT INTO public.hat_defs VALUES (115, 'P-Hat (green)', 'Zezima fanboy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (116, 'P-Hat (red)', 'おれはPigAmericanですおれはばか i am average american man i enjoy bad game runescape', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (117, 'P-Hat (yellow)', 'PISS HAT PISS HAT', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (118, 'P-Hat (blue)', 'Ughhhh coming up with different descriptions for RuneScape party hats', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (119, 'P-Hat (pink)', 'It''s pink.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (120, 'P-Hat (rainbow)', 'LGBTscape 😍', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (121, 'Newsboy', 'Or newsgirl. It''s okay, the hat is actually gender-neutral.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (122, 'Whirly Tard Hat I', 'Wouldn''t it be neat if they could make one that like uses body heat or whatever to keep the propeller in a state of constant motion', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (123, 'Dunce Cap', 'You retard. Imbecile. Utter buffoon. Oaf. Nincompoop. Idiot. Moron. CLOWN.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (124, 'Beret', 'Literally the most basic possible hat choice. Please do better. ', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (125, 'Mario', 'BING BING WAHOO ', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (126, 'Luigi', 'LING LING LAHOO', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (127, 'Wing Cap', 'If the hat''s wings are what provide the thrust necessary for flight then how does it stay on and let YOU fly with it huh', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (128, 'Metal Mario', 'Mario hat but with yelling and lots of double bass and distorted guitars and shit heck yeah', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (129, 'Cappy', 'A sentient hat-creature that''s actually a pretty horrifying parasite if you think about it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (130, 'Wario', 'For the fat, yellow, extremely flatulent dramautist (in loving memory of Bidpots)', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (131, 'Waluigi', 'Coming soon to Smash for sure', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (132, 'Top Hat (kek)', 'Technically a top hat, shut up', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (133, 'Top Hat (white)', 'Oh, how dignified', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (135, 'Top Hat (checkered)', 'Actually chessed, but that''s not really a word.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (136, 'Top Hat (march hare)', 'April hare, May hare, June hare, July hare,', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (137, 'Top Hat (mad hatter)', 'Hatters mad [x24]', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (533, 'Uncle Sam', 'The world needs our brand of democracy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (139, 'Top Hat (uncle sam)', 'THIS HAT WAS FACT-CHECKED BY TRUE AMERICAN PATRIOTS', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (140, 'Fireperson I', 'In loving memory of r/HateForFirefighters', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (141, 'Constable', 'Useless bong cop nonsense', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (142, 'NYPD Officer', 'This user is authorized to stop, frisk and cavity search you at any time for any reason', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (143, 'Crossing Guard', 'We love Officer Marsey!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (144, 'Paper Sailor', 'As idle as a paper ship, upon a paper ocean. Paper, paper, everywhere.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (145, 'FBI', 'Federal Bussy Inspector', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (146, 'CIA', 'Cisgender Incineration Agency', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (147, 'ATF', 'Ass-Tickling Faggot. HIDE YOUR DOG!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (148, 'Graduate', 'This hat signifies that the bearer has completed four (4) years of pan-african gender studies coursework', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (149, 'Nurse', 'Minor TikTok celebrity, OnlyFans top 91%', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (150, 'Farmer', 'Feed & Seed shopper', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (151, 'Farmette', 'Feed & Seed shoppette', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (152, 'Kung Lao', 'Why did I make a Kung Lao hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (153, 'Top Hat (steampunk)', 'Like a regular top hat but with goggles and gears', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (154, 'Brain Hat', 'Peter Griffin''s dog', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (155, 'The TED_SIMP', 'Wear this hat to express your undying adoration for carp', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (667, 'The Orb', 'Ponder into one''s soul', 2, 500, NULL, 1663279906);
INSERT INTO public.hat_defs VALUES (652, 'Leather Helmet', 'Wow, what a n00b', 2, 500, NULL, 1663133381);
INSERT INTO public.hat_defs VALUES (669, 'Backwards cap 2', 'lookin'' cool', 2, 500, NULL, 1663280007);
INSERT INTO public.hat_defs VALUES (396, 'Obey Snapback w Blunt', 'dude weed lmao', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1080, 'Dancing Baby Crown', 'wear it.', 2, 1000, NULL, 1668757508);
INSERT INTO public.hat_defs VALUES (663, 'Santa Hat II', '''Tis the season!', 2, 500, NULL, 1663279621);
INSERT INTO public.hat_defs VALUES (672, 'Birthday Hat', 'Ruins every thread on October 1st (ed: what does this mean????)', 2, 500, NULL, 1663280145);
INSERT INTO public.hat_defs VALUES (156, 'The Brandon', 'Listen here fat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (158, 'The King George', 'Proto-drag if you think about it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (159, 'The Mao', 'Our hair!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (160, 'The Young Stalin', 'Pockmarks not included', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (161, 'The Ripe Stalin', 'An homage to the #1 most prolific killer of commies in world history', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (162, 'The Austrian Painter', 'For aficionados of mid-20th century fine artists slash authors', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (164, 'Modern Major General', 'For my military knowledge, though I''m plucky and adventury / Has only been brought down to the beginning of the century / But still, in matters vegetable, animal, and mineral / I am the very model of a modern Major-General', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (165, 'Red Star Cap', 'Cannon fodder', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (166, 'Cartman', 'Fat antisemite - the archetypal rDrama user', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (167, 'Cheesehead', 'For fans of the Green Gay Fudge Packers', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (168, 'Kyle', 'ngl I don''t watch South Park so idk the difference between this and Stan', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (169, 'Stan', 'ngl I don''t watch South Park so idk the difference between this and Kyle', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (170, 'Kenny II', 'Like Kenny I except it shows more of your ugly face', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (171, 'The Cleopatra', 'Did you know she was actually white?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (172, 'Pimp Hat I', 'Women are objects', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (138, 'Top Hat (red)', 'Top hat, menstrual edition', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (157, 'The Brandon II', 'LISTEN HERE FAT', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (100, 'Supreme Snapback', 'Drip so hard omg', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (107, 'Chair Force', 'Yeah I''m a combat veteran, I''ve seen shit you wouldn''t believe. One time the wifi was out for almost an hour. ', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (173, 'Devil Horns', 'Satan is so cool and quirky!!!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (174, 'Nooticer', 'THIS USER IS ENGAGED IN THOUGHTCRIME. DO NOT INTERACT.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (175, 'Airpods', 'oh god oh fuck he cant hear us', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (176, 'Maskmaxxer', 'Why aren''t there two? Are you trying to kill us?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (177, 'The Tupac', 'dead nigger storage', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (178, 'Media Executive', 'despite making up just 2% of the population,', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (179, 'Surgeon', 'Lobotomize me daddy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (180, 'Mouseketeer', 'please don''t sue please don''t sue please don''t sue please don''t sue please don''t sue', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (181, 'Karen', 'Let me speak to your manager', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (182, 'Badass Fighter Ace', ' Top Gun™ Maverick® Now Showing In Theaters!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (183, 'Taqiyah', 'It''s not a yarmulke I swear', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (184, 'Cock', 'DM me yours!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (185, 'Nervous, Sweating', '>mfw', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (186, 'The Cat', 'does this really need a description', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (187, 'Noose', 'Cope or rope', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (188, 'The Penny', 'This shower cap bonnet is perfect for hiding nappy, alopecia-ridden hair', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (189, 'Hard Hat (yellow)', 'A rock hard, throbbing, veiny hat. Check out the girth on this thing', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (190, 'Hard Hat (white)', 'The mayo variant of the hard hat, used to signify someone of importance, or a visitor, at a job site', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (191, 'Beret (TF2)', 'Stylish vidya-variant of the beret', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (192, 'Texas Ten Gallon', 'Yeehaw!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (193, 'Demoman', 'KaBOOM', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (194, 'Fireperson II', 'For extinguishing hot threads', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (195, 'Miners Hat', 'Please don''t touch minors', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (196, 'Old Man Hat', 'AKA the Wizdumb', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (197, 'Pimp Hat II', 'Women are people and they deserve respect just kidding they should suck my penis', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (198, 'Whirly Tard Hat II', 'Propeller go brrrrrrrrrr', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (199, 'Family Man Free Hat', 'It''s a good show!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (200, 'Engineer', 'Choo choo!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (201, 'Vexillaurius Helmet', 'Degenerates like you belong on rDrama', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (202, 'Astronaut Helmet', 'See you, space marsey', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (134, 'Top Hat (striped)', 'Tim Burton''s take on the top hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (11, 'The 6ix9ine', 'The finest piece of snitch couture on the market', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (534, 'Para Para Sakura', 'セックスする!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (259, 'Marsey Headbang', 'She''s banging on your head lmao get it', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (258, 'Clownpaint', 'WHOOP WHOOP MATHOFACKO', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (213, 'The Penny II', 'Out of the shower :marseybath: cap, into the bandana', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (278, 'The Justinian', 'Glory to God who has thought me worthy to finish this work. Solomon, I have outdone you.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (263, 'Colonizing Oppressor', 'Why would you ADMIT to this?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (264, 'The TracingWoodgrains', 'Bweaking nuwus!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (265, 'Cat Ears (devil horns)', 'Has science gone too far?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (268, 'The TracingWoodgrains II', '*nuzzles your bulge mid-interview* OwO whats this', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (273, 'Pilot Hat', 'Daily nonstop flights to Bussyville', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (536, 'The Banzai Bandana', 'May Marsey live ten thousand years!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (538, 'Timmy Turner', 'So you''re telling me I can wish for ANYTHING?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (539, 'Fairly Oddparent', 'Obtuse, rubber goose, green moose, guava juice, giant snake, birthday cake, large fries, chocolate shake!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (540, 'Oney', 'Look Tomar, it''s you.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (541, 'Morshu', 'Lamp Oil, Rope, Bombs! You want it? It''s yours, my friend! As long as you have enough RUPEES.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (542, 'Link (Faces of Evil)', 'Could you eat an octorok?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (406, 'Amogus', 'I saw you vent', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (415, 'WANTED', 'Dangerous thought criminal. Wanted DEAD ONLY.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (421, 'Emperor Hat', 'Made in China', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1081, 'Happy Plumbob', '5th gen Sims 4 plumbob', 2, 1000, NULL, 1668758641);
INSERT INTO public.hat_defs VALUES (877, 'Reaper Hood I', 'Spooooooky!', 2, 500, NULL, 1665314511);
INSERT INTO public.hat_defs VALUES (878, 'Reaper Hood II', 'Now with scythe!', 2, 500, NULL, 1665314534);
INSERT INTO public.hat_defs VALUES (397, 'Funko Pop', '...and then he turned himself into Funko Pop. Funniest shit I ever saw.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (668, 'Maxwell Hat', 'Scribblethot', 2, 500, NULL, 1663279953);
INSERT INTO public.hat_defs VALUES (543, 'Harkinian (Faces of Evil)', 'Marsey mah boy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (544, 'Train Conductor', 'It’s MY neurodivergence and I get to choose the special interest', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (546, 'Reimu Bow', 'Gensokyo border control', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (547, 'The Microdose', 'A smaller, safer dose for those who need to self-medicate in public.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (548, 'The Snooplet', 'I can exercise you, this can be your phys ed, spend all your cizzoins, just perch me on your hizzead', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (550, 'The Entertainment', 'A prize for clever birthday boys that save their tokens.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (553, 'Banana Bucket Hat', 'Peanut butter jelly time', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (552, 'Doomer Beanie', 'blackpilled again', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (554, 'Clop', 'DM me for MLP clop ERP', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (561, 'The Lawlz', 'Have Max the Dog join you on your PFP. Rest in paradise king!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (558, 'Suicide King', 'Lost it all in the 52 cards', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (560, 'Dual-Wield Katanas', 'Forged from real Nippon steel, folded 1000 times, shipped directly to your local mall kiosk.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (564, 'The African Kufi', 'The white man doesn''t want you to know that this website was created by an AFRICAN king', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (563, 'The Dundee', 'That''s not a hat. THIS is a hat!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (566, 'Heart Crown (rainbow)', '❤🧡💛💚💙💜', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (565, 'Sparkles Crown', '✨✨✨', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (572, 'Heart Crown (sparkles)', '💕💛💔💗♥🖤✨💙 or something idk', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (573, 'CENSORED', '💔literally 1984 💔', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (574, 'Heart Crown (Rainbow II)', 'More gay than the other rainbow heart crown 👍', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (575, 'Heart Crown (superstraight)', '🖤🧡🖤🧡🖤🧡', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (567, 'Heart Crown (blue and purple)', '💙💜', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (568, 'Emoji Crown (hearts and shooting stars)', '💫This is techically the dizzy symbol, but it looks like a shooting star for Apple users 😘', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (576, 'Emoji Crown (sunflower honeypot)', '🌻🍯✨', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (578, 'Baddie Cap', 'All real baddies wear this hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (579, 'Skull Mask', '💀Stop the spread!💀', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (580, 'DUM post it note', 'For when u dum :(', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (581, 'I Pee In Pools Cap', 'Share your stance on pool urination', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (582, 'Bee Crown', 'Buzz buzz buzz', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (584, 'Flower Crown (sunflowermoji)', 'A very cute sunflower crown', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (585, 'Fire Crown', '🔥🔥🔥', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (586, 'Weeb Angry Symbol', '😠', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (587, 'Fedora (Red Hat Enterprise Linux)', 'Reminds me of 2004', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (583, 'Weird Banner', 'You may only wear this if you are weird! No appropriation by non weirdos, thx', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (588, 'Large Bow (light pink and blue)', 'It really is a very large bow', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (589, 'The Penny III', 'ALOPECIA B-GONE', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (590, 'Top Hat (rattlesnake)', 'Top hat decorated with rattlesnake', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (591, 'PLA Hat', '中国梦', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (592, 'Du Rag (flames)', 'Shitty bandana 7/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (593, 'Top Hat (red and black)', 'This isn''t the right hat for everyone, but is it the right hat for you?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (594, 'Tin Foil Fedora', 'm''lady, I must warn you of the elecromagnetic mind control rays', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (595, 'The Coon', 'Davy Crockett wore it and now it’s on rDrama', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (597, 'White bow Headband', 'simplicity', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (598, 'Du Rag (black and red)', 'Shitty headband 8/6', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (599, 'Tricorn Hat (brown leather)', 'ruggedized and heavy duty tricorn hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (600, 'Captain America Cap', 'WOW I HECKIN LOVE SUPERERO', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (601, 'Cowboy Hat (Jewish)', 'brown leather cowboy hat with a six pointed star', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (602, 'Cowboy Hat (American)', 'Yeehaw faggot', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (603, 'Balaclava (Shark teeth)', '🦈', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (604, 'Backwards Cap', 'How do you do fellow r/teenagers', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (606, 'Fancy Hat (blue and black)', 'made with stable diffusion!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (607, 'Cheerful colorful knit hat with flower', 'also made with stable diffusion!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (608, 'Hat of the Future (art deco)', 'According to Stable Diffusion, this is the hat of the future. It''s also art deco, because that gave cooler results.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (569, 'Paul', 'cringe and dramaphobic llama', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (535, 'The Soren', 'discuss', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (577, 'Zoomie Zoom Zoom II', 'Underage user, do not interact', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (618, 'Cuban Pete', 'Given only to the biggest space assholes.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (619, 'Marsified', 'become the marsey', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (620, 'Glowing Pickelhaube', 'Glows in the dark, like a secret police', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (559, 'Roulette', 'Around and around it goes', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (551, 'Soyjak Pointing', ':O Dude dude DUDE! Look at this user :OOOOOO', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (555, 'Egg_irl', 'Ask me about my pronouns', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (280, 'Gold Laurel Wreath', 'Veni, vidi, vici', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (332, 'Hairlet', 'It never even began', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (266, 'King Crown II', 'King is our word but you can say kang', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (267, 'Furry Marsey', 'Never forget that Marsey is a furry OC and this site is themed around fanart of her', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (270, 'Perry the Platypus', 'Platybussy > Platygussy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (271, 'Zorro', 'Z!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (274, 'Shemagh', 'Shemagh is such an ugly word. It sounds like a phlegmy noise. Even looks like the word phlegm.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (275, 'Bloods', 'BRIPS GET THA BLATT BLATT', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (276, 'Conscience', 'i can be yuor angle or your devil', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (269, 'SCARY GUN', 'He called it an AK-74u but I''m not sure if that''s right idk idk', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (537, 'The Celtic Kufi', 'Irish were the REAL slaves, stay woke my deartháir', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (549, 'The Bumper Sticker', 'Turn yourself into a legal liability that could threaten the very site itself!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (571, 'Purple Emoji Crown', '💜💜💜when ur selfie needs an emoji crown with a 🌻, a 👻, and a 🐻 but u still gotta fit that purple aesthetic 💜💜💜', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (570, 'Carl', 'based and dramapilled llama', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (828, 'monopoly thimbler', 'Even thimblier than the last one', 2, 500, NULL, 1665250441);
INSERT INTO public.hat_defs VALUES (846, 'Twinkle', 'TWINKle', 2, 1000, NULL, 1665261883);
INSERT INTO public.hat_defs VALUES (1117, 'Necrotomigaud', 'R1 - User in rDrama fades away', 2, 500, NULL, 1671165496);
INSERT INTO public.hat_defs VALUES (1121, 'Affliction', '“Fear and frailty finally claim their due.” – Narrator', 2, 500, NULL, 1671233929);
INSERT INTO public.hat_defs VALUES (875, 'Aces Strawhat', 'Idfk what this is man why are you submitting these esoteric fucking hats with no indication of what they are AAAHHHHH', 2, 500, NULL, 1665314089);
INSERT INTO public.hat_defs VALUES (1122, 'Driller Helmet DRG', 'If it ain''t drillable, it''s probably flammable.', 2, 500, NULL, 1671236444);
INSERT INTO public.hat_defs VALUES (1124, 'Farseer helm', 'Farseer helm', 2, 500, NULL, 1671621813);
INSERT INTO public.hat_defs VALUES (1130, 'Kluxxer', 'Kluxxing', 2, 500, NULL, 1671649262);
INSERT INTO public.hat_defs VALUES (531, 'Zen', 'follow the fish follow the fish follow the fish follow the fish follow the fish', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (612, 'Wizard Hat (pixel)', 'Some sort of vidya thing idfk', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (614, 'Chickenhead', '🤗', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (621, 'The Soren II', 'Soren is an idea, not a person. Shoot him. It’s okay, the bullets do nothing. Try it!', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (279, 'Libertarian', 'This user has certainly read Atlas Shrugged', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (282, 'Green Laurel Wreath', 'Render unto Caesar the things which belong to Caesar', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (557, 'Cottagecore', 'Show your solidarity with men-who-have-sex-with-men by giving them a safe, public space to do whatever it is they''re doing back there.', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (622, 'Colonial Chapeau', 'Whatever happens/we have got/the Maxim gun/and they have not', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (624, 'Metal Gear', 'Detected!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (291, 'Yea Daddy Choker', 'Remember who you belong to', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (296, 'Sunhat II', 'Yellow to camouflage you from the sun, cunningly making it believe you are one of its own kind. And then you strike.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (298, 'Flower Bonnet', 'An indescribably cute flower cro- bonnet.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (299, 'Raspberry Hat', 'Little sissy French girl hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (300, 'Lemonsqueezer', 'Iconic kiwi headwear with a very stupid name', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (301, 'Dickhead', 'Really proud of the name for this one. Well done, me!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (627, 'Pedo Sniper (right)', 'I''m not which is worse - being a pedo, or being left handed?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (628, 'Gnome Child', 'My mum says: A friendly look, a kindly smile one good act, and life''s worthwhile!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (308, 'Pothead', 'Cali-grown cast iron goodness', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (311, 'The Lucas Roberts', '#DropKiwiFarms #MandatoryHRTForAllKids', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (317, 'AI-Generated Hat', 'Stable Diffusion recommended a 10k price point for this 🤔', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (318, 'Headphones (black)', 'Situational awareness: 0', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (320, 'Summer Hat', '[incoherent Hawaiian gibbering]', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (321, 'Attention Whore', 'DUDE BUSSY LMAO MARSEY HECKIN VALIDERINO AMIRITE BTW I AM TRANS', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (322, 'Pirate Hat II', 'Swab the POOP deck with your TONGUE', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (323, 'Mafioso', 'Something something gabagool 🤌', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (325, 'The Sal', 'Watch me go nowhere in two weeks (I AM SO DEPRESSED)', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (328, 'Skidmarks', 'Hit me with your car daddy 🤪', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (329, 'Behind Bars', 'Uh oh, someone forgot to say In Minecraft', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (330, 'Panzer Driver', 'No war crimes here, just tanks!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (331, 'Ghostly Gibus', '(achievement item: not tradable or marketable)', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (333, 'Astronaut Helmet II', 'Used for intrepid explorers of Hollywood basements', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (335, 'Kippah', 'rDrama: a light unto nations', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (337, 'The Tim Pool', 'No one can make fun of you for being bald if you never ever ever ever take it off', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (338, 'Digigoggles', 'DIGIMON. DIGITAL MONSTERS. DIGIMON ARE THE CHAMPIONS.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (339, 'Sorting Hat', 'HUFFLEPUFF!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (340, 'Metroid', 'Some sort of alien parasite thing I think. It wants a kiss.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (341, 'The One Hat', 'One hat to rule them all', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (342, 'Kawaii Usage Hat', 'Bunny bunny bunny bunny bunny bunny bunny bunny bunny bunny bunny bunny', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (343, 'Shroomjak (red)', '🍄🍄🍄🍄🍄🍄🍄🍄', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (20, 'Nonspecific Military Officer Hat II', '[removed]', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (21, 'Soviet Officer II', 'High fashion war criminal chic', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (212, 'Sneed', 'From the business formerly known as Chuck''s Seeduck and Feeduck', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (214, 'Hijab', 'The ONLY way to stop being a whore', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (215, 'Cock II', 'Honk honk', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (216, 'Cummies', 'Yummy yummy cummies in my tummy tummies', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (211, 'Zombiewolf Helmet', 'Everyone knows it''s rDrama''s true mascot', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (218, 'Clown Wig', 'Why so serious?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (219, 'Jimmy Hat', 'Don''t be silly, wrap your willy!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (220, 'Bane Mask', 'If I pull that off, will you die?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (221, 'Wolf Ears I', 'OwO what''s this?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (222, 'Smugjak', 'I''m drunk and can''t think of a good description lol', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (223, 'Foolproof Disguise', 'What''s that, officer? You''re looking for [USERNAME GOES HERE CARP CAN''T CODE]? Never heard of him!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (224, 'Brain Slug', 'This poor brain slug is STARVING TO DEATH :(', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (272, 'Harry Potter', 'General in the Mages vs. Matriarchy war', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (324, 'Lord of the Flies', 'Sucks to yer ass-mar!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (314, 'Bright Idea II', 'Guys. GUYS. Bait sub idea: r/HateForGoodThing', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (316, 'Globohomo', 'The gay agenda is no longer optional.', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (313, 'Bright Idea I', 'Guys. GUYS. BAIT SUB IDEA: r/LoveForBadThing', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (225, 'Pat Hat', 'Who''s Daddy;s special little boy?', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (277, 'Cool Wine Aunt', 'It''s pruno, don''t pretend you''re fancy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (284, 'The Gary Plauche', 'We can''t expect God to do all the work', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (292, 'Marsey Smug Mask', 'I''m not seething, you''re seething', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (295, 'Pinkhat', 'It''s a hat and it''s pink and your nan looks adorable in it. Not you, though.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (400, 'Current Thing (support)', 'Slava Ukraini!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (881, 'Fedora (ice)', 'Cooool as ice😎', 2, 500, NULL, 1665327379);
INSERT INTO public.hat_defs VALUES (885, 'Coin Fall (red)', 'ITS RAINING MONEYYYYYY', 2, 1000, NULL, 1665339781);
INSERT INTO public.hat_defs VALUES (886, 'Coin Fall (green)', 'CHA-CHING!', 2, 1000, NULL, 1665339812);
INSERT INTO public.hat_defs VALUES (847, 'Flaming Sword', '??????????', 2, 1000, NULL, 1665262102);
INSERT INTO public.hat_defs VALUES (310, 'Bandit Bandana', 'This thread ain''t big enough fer the  of us', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (327, 'Ageplayer', 'It''s cool if it''s not your thing, just don''t yuck someone else''s yum :)', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (312, 'Super Saiyan', 'Taqueria ‘Goku''', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (226, 'Gay Saudi Headpiece', 'Saudis are all homosexuals and they use this to hide the cum in their receding hairlines', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (227, 'Snekshat', 'Snek Shat Hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (228, 'Pride Hat I', 'We''re here, we''re queer, get used to it!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (229, 'Marsey Ears', '@Dramarama''s first hat and it is PERFECT', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (230, 'Halo II', 'Daddy''s lil angel 😈', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (231, 'Egg', 'Uh oh, someone''s got egg on his/her/their/xer/spiderself''s face', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (232, 'Donut', 'You ever try fucking a donut?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (233, 'Player One', 'Mom says it''s my turn!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (234, 'Okapi', 'Big throbbing okapi cock 🤤', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (235, 'Emo Hair I', '''''Rawr'''' means ''''I love you'''' in Dinosaur :3', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (236, 'Ram Horns', 'Not quite sure what a ram is tbh but here are its horns. Like is it a boy sheep? A goat? Some animal of its own? Who knows!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (237, 'Bunny Ears', 'BUNNY!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (238, 'Pinhead', 'Dirty Dan''s best friend', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (239, 'Mojo Jojo', 'I once knew a Mexican dude named Nick who pronounced Mojo Jojo as mohohoho', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (240, 'Backstabbed', 'I have information that will lead to the arrest of Hillary Rodh-- ack!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (241, 'The Garry_Chess', 'I AM A DOCTOR I AM IMPORTANT HURRDURR', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (242, 'Aussie Hat', 'Gday, cunt', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (243, 'Night Cap', 'Imagine putting a fucking :marseytom: hat on before bed lmao', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (244, 'Anime I', 'YIKES! CRINGE!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (245, 'The Brianna Laundrie', 'RIP Brianna and RIP r/FriendsOfBrian', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (246, 'Lains Bear Kigurumi', 'And you don''t seem to understand / A shame, you seemed an honest man', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (248, 'Furfag Pride', 'We`re here, we fuck animals get used to it.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (249, 'why', 'BOOHOO NIGGA', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (250, 'Grass Toucher', 'Makes you immune to being told to touch grass', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (251, 'Napoleon', 'Liberté, ordre public', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (252, 'Average rDrama Hat Designer', 'USE THE FUCKING TEMPLATE', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (253, 'Phrygian Cap', 'Liberté, égalité, fraternité', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (254, 'Three Lil Marseys', 'It''s three Marseys. They''re little. What more do you want from me here?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (255, 'KN95 Mask', 'We are all in this together. If you are serious about flattening the curve, you will wear this.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (256, 'Confusion', '????????????????????????????', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (257, 'Umbreon Ears', 'For legal reasons, we cannot actually call these Umbreon Ears. Please refer to them as something else.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (260, 'Carphead', 'A legally viable excuse to have Carp on top of you in public', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (261, 'Journoid Scum', 'The wearer of this hat was coming right for you, I saw it. The shooting was purely self-defense.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (262, 'Delicious Feet', 'feet > bussy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (344, 'Slava Ukraini', 'Slava Ukraini!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (345, 'Gigachad Mask', 'Average rDrama user', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (346, 'Pumpkin Remains', 'A gory pumpkin scalp', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (347, 'Peek-A-Boo Marsey', 'AAAAHHH GET IT OFF GET IT OFF GETITOFF AAAAAAHHHHHHH', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (348, 'Hazmat Suit', 'Standard-issue PPE for wading through the cesspit that is rDrama', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (349, 'Cat Ears (wiggly)', 'MEOW MEOW MEOW MEOW MEOW MEOW MEOW', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (350, 'Marionette Strings', 'Dance, puppet, dance', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (351, 'PaRappa Beanie', 'This is technically a furry item fyi', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (353, 'Double Ds (hat)', 'double deez nuts lmao', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (354, 'SNIFFED', 'Extremely uncomfortable for almost everyone involved', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (356, 'Santa Hat I', 'Frozen Frozen Frozen (like ho ho ho get it), merry Fistmas!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (357, 'Scumbag Steve', '>comes to your gay poz mixer >wears a rubber', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (358, 'Umbrella Hat', 'Covered in dirty yellow and white streaks', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (359, 'Ridin With Biden', 'You ridin''?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (360, 'NFT', 'Right clicking is STRICTLY prohibited', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (361, 'The Bog', 'Will you take the call?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (362, 'Googly Eyes', 'My eyes are up here', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (363, 'Kanohi Hau', 'A description was not provided but google says it''s a Bionicle thing. I think those are like Legos. Mysterious Lego mask oooooooh', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (364, 'The Yugi', 'Children''s card game world champ', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (365, 'Maid Cap', 'CLEAN IT UP MAID 🤣 FOR A RESPECTABLE WAGE 🤣🤣🤣', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (366, 'BLACKED', 'You were built for BBC', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (368, 'Wonder Tiara', '(Lynda Carter''s version, of course)', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (369, 'Fisherman Hat', 'The text is completely indecipherable at this scale. I have no idea if that makes it worthless or adds to the joke.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (370, 'Crosshair', 'You deserve this.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (371, 'DONT CARE DIDNT ASK YOUR WHITE', 'DONT CARE + DIDNT ASK + YOUR WHITE', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (372, 'Dragonborn', 'Dragon Shout: FEED/AND/SEED', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (373, 'Sun Hat III', 'So many sun hats to choose from, so little sun.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (374, 'Anglerfish', 'It''s not Snoo''s scalp. Stop asking that.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (375, 'Nun Headpiece', 'Bandeau and veil, coif not included', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (376, 'Colovian Fur Helm', 'NOT for n''wahs', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (377, 'Booze Cruise', 'Drunk driver rights are human rights', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (378, 'Son of the Mask Mask', 'Don''t ya just LOVE Homoween?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (379, 'Bananahead', 'This shit is bananas. B-A-N-A-N-A-S', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (626, 'Pedo Sniper', 'Ready, aim...', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (381, 'Panty Raid (pink)', 'Are ya feeling it now Mr. Krabs?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (382, 'Panty Raid (red)', 'Are ya feeling it now Mr. Krabs?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (383, 'Panty Raid (white)', 'Are ya feeling it now Mr. Krabs?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (384, 'Head Crab', 'It''s a crab. For your head.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (386, 'Curts New Hat', 'Have you *seen* it?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (387, 'Gray Cowl of Nocturnal', 'Capital!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (388, 'Tricorne', 'This hat is for TRUE AMERICAN PATRIOTS only', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (404, 'Knight Helmet', 'kNIGht 🤗', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1132, 'USDA inspector', 'they''re still a glowie, despite the unthreatening appearance. don''t let them inspect your food.', 2, 500, NULL, 1672455409);
INSERT INTO public.hat_defs VALUES (892, 'sailor moon peek', 'Really?', 2, 1000, NULL, 1665340406);
INSERT INTO public.hat_defs VALUES (352, 'John Deere Hat', 'She (male) thinks my tractor''s sexy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (355, 'Chef Hat', 'Cloudflare just bent the knee and I''m nauseated and don''t feel like writing descriptions for hats sorry', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (392, 'Chris-Chan', 'Hat to the extreme!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (393, 'Bunny Buttons', 'Byo requested this one but I''m honestly not even sure what it is', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (394, 'ROFLcopter', 'Lollerskates', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (395, 'Whirly Tard Hat (animated)', 'This one spins omg', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (412, 'The Klenny', '🤣👍', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (422, 'Booba', 'O_O', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (409, 'AI Core', 'Thought this said AL Core for a minute like Al gore but no it''s ai like the robot thing and apparently it''s from a vidya so here we go description done 🤌', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (424, 'Pearl Clutcher', 'REEEEEEEEEEEEEEEEE', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (462, 'Rasta Hat', 'Jah bless', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1133, 'Singapore Flag', 'Ranked the world''s most expensive city to live in 8 times in the past decade', 2, 1000, NULL, 1672773592);
INSERT INTO public.hat_defs VALUES (1134, 'Hot headed', 'Damn you need to cool down bro.', 2, 1000, NULL, 1672981389);
INSERT INTO public.hat_defs VALUES (1135, 'Qanon', 'wiggawigga fellow PATRIOT!', 2, 1000, NULL, 1673112507);
INSERT INTO public.hat_defs VALUES (895, 'Target practice', 'KEEP SHOOTING TILL THE BEAST IS DEAD', 2, 1000, NULL, 1665341399);
INSERT INTO public.hat_defs VALUES (896, 'Cheers', 'HOORAY! All hail the special one!', 2, 1000, NULL, 1665341566);
INSERT INTO public.hat_defs VALUES (897, 'Patrick Lick', 'You taste sweet', 2, 1000, NULL, 1665341627);
INSERT INTO public.hat_defs VALUES (898, 'Make It Rain', 'It is raining.', 2, 1000, NULL, 1665341752);
INSERT INTO public.hat_defs VALUES (899, 'Wise mystical tree', 'Things about get wise and freaky', 2, 500, NULL, 1665342497);
INSERT INTO public.hat_defs VALUES (398, 'The Catman', 'This counts as a fursuit', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (401, 'Current Thing (oppose)', 'Denazify Ukraine!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (402, 'T-34 Tank', 'For denazification purposes', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (403, 'Weatherman', 'Glad I could help', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (405, 'Israeli Friend Pins', 'If any man shall adore the beast and his image, and receive his character in his forehead, or in his hand.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (407, 'Top Hat (black glitter)', 'Be careful not to rub this against anything', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (410, 'Retro Snapchat Thot', 'Heckin good pupperino', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (411, 'The Goatse', 'Open wide!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (418, 'Bass Pro', 'Of course I cum fast, I got fish to catch!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (420, '2070s Hat', 'State-enforced homosexuality. Teaching JavaScript to refugees. The flyest headwear. Bring on the Paradigm Shift.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (413, 'Retro Brimstone', 'Look man if you''re gonna submit old vidya imagery as hats I need to know what it IS so I can write descriptions', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (423, 'Dramautist Jar Project', 'Wh-what''s going on? Why am I in here?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (416, 'Monopoly Hat', 'Do not pass Go. Do not collect 200 dramacoin.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (417, 'Monopoly Thimble', 'Just the right size for your dick huh', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (425, 'Girlboss', '#GASLIGHT #GATEKEEP #GIRLBOSS', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (426, 'Gold Badge', 'You did so well. You deserve yourself.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (427, 'Silver Badge', 'First loser', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (428, 'Green Badge', 'Winner of the 20XX Farmers Choice Award', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (429, 'Red Badge', 'The red badge of bussy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (431, 'Blue Badgr', 'I blue myself', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (433, 'R2D2', '[unintelligible whirring and beeping]', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (434, 'Gay Fawkes Mask', 'Buy curtains, Buy a dog. We are legging. Accept us.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (437, 'Cigar', 'Sometimes s cigar is just a cigar. Not this time, though. This is clearly about craving dick in your mouth.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (438, 'Conquistador', 'Sorry, but the human sacrifice stops NOW.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (439, 'Pumpkin', 'Spowoky Owoky Puwumpykin', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (440, 'Jester Hat (Mardi Gras)', 'YOU Tuesday', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (441, 'Jester Hat (red and blue)', 'Jingle jingle', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (442, 'Jester Hat (blue and purple)', 'Hand wash only', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (443, 'The Ricardo Milos', '✨Iconic✨', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (444, 'The Awoo', 'This is (not) Cirno', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (445, 'Krusty Krew', 'KRUSTY KRAB PIZZA. IS THE PIZZA. FOR YOU AND ME.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (446, 'Sutton Woo Helmet', 'What a neat helmet. Why would someone leave it lying on the ground?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (447, 'Cosmonaut Helmet', 'Yuri Gagarsey, hero of the Soviet Union!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (448, 'The Pizzashill', 'WORDS WORDS WORDS WORDS WORDS WORDS WORDS WORDS WORDS WORDS WORDS WORDS WORDS', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (449, 'Handmaids Bonnet', 'Wear this to protest the ban on infanticide', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (451, 'Influencer', 'Sweet, faceless validation', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (453, 'Top Hat (fancy)', 'Shallow and pedantic, if you ask me. It insists upon itself', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (454, 'Jaguar Warrior', 'The human sacrifices will continue until morale improves', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (455, 'Marsey Brainhat', 'Just two brainlets, hanging out', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (456, 'Black Crown', 'Black crowns matter', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (458, 'Mario Raccoon', 'BING BING RACCOON', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (459, 'Eggscellent Hat', '🥚 lmao', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (367, 'Burning Flames Team Captain', 'Yeah I''m hot shit, could you tell?', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (460, 'Edelgard Hair', 'Please report anyone with this hat to @carpathianflorist for weeb eradication', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (380, 'Witch (Wizard) Hat', 'STOP ASKING WHY I DON''T USE MAGIC TO CHANGE MY GENDER', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (385, 'Magician Hat', 'It''s not just animated so we can charge more for it. Really!', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (389, 'BIG MAD', 'Positively seething', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (390, 'Nervous Sweating', 'oshit >mfw', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (391, 'Sparkles', '✨✨✨✨✨✨✨✨', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (461, 'Gothic Lolita', 'Dark and brooding. Not very brooding, actually. But dark.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (463, 'Sheep Horns', 'For the horniest of sheep', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (464, 'Luffy Hat', 'Stretchy pirate weebshit guy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (465, 'Thin Film Interference Hat', 'Like that movie with the time machine car', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (466, 'BANNED stamp', 'One time at banned stamp I', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (467, 'Minecraft', 'It is impossible to fedpost with this hat on', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (468, 'Brimless Yankee', 'The finest team of juicers money can buy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (469, 'The Kiwi', 'Wearing this constitutes a hate crime in most developed countries', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (470, 'The Mathematician', 'Special delivery from Mr. Kac- Mr. Kaz- Mr. Kazimspy', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (471, 'Frog Hat', 'It has a cute frog on it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (472, 'Moriya Frog Hat', 'Big googly eye froge hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (903, 'Haunted', 'Spooky ghosts follow!', 2, 1000, NULL, 1665347450);
INSERT INTO public.hat_defs VALUES (901, 'Wombat', 'Multipurpose head wombat', 2, 500, NULL, 1665347408);
INSERT INTO public.hat_defs VALUES (904, 'RIP BOZO', 'Rest in piss faggot', 2, 500, NULL, 1665348882);
INSERT INTO public.hat_defs VALUES (905, 'The Poo', '💩💩💩💩💩💩💩💩', 2, 500, NULL, 1665349075);
INSERT INTO public.hat_defs VALUES (910, 'Rocket League', 'Time for car FOOTBALL!', 2, 1000, NULL, 1665355493);
INSERT INTO public.hat_defs VALUES (906, 'Lantern head', 'Light your path in inconvenient ways!', 2, 500, NULL, 1665349271);
INSERT INTO public.hat_defs VALUES (900, 'Trapped', '😔😔😔', 2, 500, NULL, 1665343188);
INSERT INTO public.hat_defs VALUES (907, 'Venus Flytrap', 'You''re a bug to this plant!', 2, 1000, NULL, 1665350150);
INSERT INTO public.hat_defs VALUES (908, 'Psychedelic', 'Trippy and Pretty!', 2, 1000, NULL, 1665350405);
INSERT INTO public.hat_defs VALUES (909, 'Nicholas Cage Vore', 'Face/off', 2, 500, NULL, 1665350658);
INSERT INTO public.hat_defs VALUES (916, 'Blood Rain', 'Mmmmm.', 2, 1000, NULL, 1665356178);
INSERT INTO public.hat_defs VALUES (915, 'Top Hat (double rainbow)', 'Double the rainbow double the pride', 2, 1000, NULL, 1665356065);
INSERT INTO public.hat_defs VALUES (473, 'Warning Tape', 'This user is a walking red flag', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (474, 'The Merchant', 'What did he mean by this? 🤔', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (475, 'Stickbug', 'Lookit this lil fella go', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (476, 'Cos Bucket Hat', 'Bitch ima cow', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (477, 'Strawberry Hat', '🍓🍓🍓', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (478, 'Froge Beret', 'On Wednesdays we wear frogs', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (480, 'Knitted Hat (blue)', 'Plush. Warm. Ugly. But enough about your mom.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (481, 'Ladies Ornate Hat (black)', 'Elegant!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (482, 'Cowgirl (male)', 'Rootin tootin foid-shootin', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (483, 'Naughty Newsboy', 'Missing. Last seen at ground zero of your local monkeypox outbreak. If found, do NOT touch.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (485, 'This Is Fine', 'Situation normal.', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (486, 'Emo Hair II', 'SO CUT MY WRISTS AND BLACK MY EYES', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (487, 'Emo Hair III', 'I write sins not tragedies', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (488, 'Emo Hair IV', 'I''m not okay (I promise)', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (489, 'Emo Hair V', 'Thnks fr th Mmrs', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (490, 'Emo Hair VI', 'Cute Without The ''E''', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (491, 'Top Hat (frost)', 'Cool-colored top hat for cool tops only', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (492, 'Top Hat (frilly Victorian)', 'Victorian fashion was HIDEOUS but contemporary spins on it are just lovely', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (493, 'Brown Herringbone Flat Cap', 'TWEED AND SNEED', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (494, 'Skull Boingy Head Things', 'boing 💀 boing 💀 boing 💀', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (495, 'Alligator-Textured Gold Blingy Hat', 'Looks like shit but probably feels real nice', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (496, 'Flower Hat (hot pink)', 'A cute flower hat', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (497, 'Stinky', 'UH OH! STINKY!', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (498, 'Mario Hat (BIPOC)', 'Who could have dropped this?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (499, 'Fart Slave Gear', '12 years a fart slave', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (500, 'Little African Hat', 'Promise not to wear it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (502, 'Booze Cruisin', 'DRUNK DRIVER RIGHTS ARE TRANS RIGHTS', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (503, 'The Antichrist', 'Weak to Tesla coils', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (505, 'ADIDAS Cap', 'Sacred cultural headpiece for the highest caste of gopnik', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (506, 'The Tim Buckley', 'Is this loss?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (507, 'Gat', 'The ultimate in neo-BTSstanwear', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (511, 'Sam Fisher', 'Four-eyed freak vidya edition', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (512, 'The Buckethead', 'Exactly what it says on the tin', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (513, 'The Sherlock', 'Elemarsey, my dear Watson', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (514, 'Glowing', 'Hit me with your car', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (515, 'Cringe Archivist', '*SNAP* Yep, this one for sure', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (516, 'Madoka', 'Pink-haired retard', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (517, 'Homura', 'Why does the jap have blue eyes', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (519, 'Sakaya', 'omg stop making me look up chinese cartoon characters', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (520, 'Mami', 'Titty ass bitch', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (521, 'VDV Beret', 'something something something Russia', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (522, 'Dr Livesey', 'Dr Soon-To-Be-Dead', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (528, 'Flower Clip', 'A cute flower clip', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (530, 'RENT FREE', 'idek anymore carp whatever you want is fine', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (508, 'Meowth', 'That''s right!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (509, 'Niconico', 'I can''t think of a description, but I''m proud of it', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (510, 'Sneed (Chuck)', 'Subsequently Sneed''s', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (518, 'Kyoko', 'This is seriously her name? Kyoto with a k instead? Hi I''m Philadelkia, son of Dedroit, son of Kansas Citie <_>', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (524, 'Smurf Hat (papa)', 'You think you''re better than all the other smurves', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (529, 'Conehead', 'How do you describe a cone? It''s a cone. It goes on your head.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (523, 'Smurf Hat', 'La la, la la la la', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (525, 'Please Be Autistic I Am Yes', 'Please Be Autistic I Am Yes', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (526, 'No-No Finger', 'Oh no you di-int', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (527, 'Cat Ears (wig)', '~~nya ^-^', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (430, 'Purple Badge', 'Orange ya glad ya didn''t get an orange badge?', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (432, 'Orange Badge', 'You''ve betrayed the purple badge.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (435, 'Witch III', 'Submitter called it cursed. He didn''t explain how. It''s cursed I guess? Spoooooooky.', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (436, 'robocop', 'You''ll never fuck my ass, Batman', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (450, 'Bluecheck', 'Can''t get verified? Do it yourself!', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (452, 'The MF Doom', 'Everyone''s favorite cosplay rapper', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (457, 'Thug Life Beanie', 'The whitest beanie you''ll ever see', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (479, 'Pizza Hut', 'For when ‘good enough'' is enough', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (484, 'Slav-sya', 'Enough about human rights, let''s talk about human wrongs', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (501, 'Dancing Marsey', 'Omg she''s so happy lookit her GO', 2, 1000, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (504, 'Iron Crown of Lombardy', 'This isn''t Crusader Kings, stop it', 2, 500, NULL, 1662167687);
INSERT INTO public.hat_defs VALUES (1138, 'Fallout Advanced Power Armour', 'War. War never changes.', 2, 500, NULL, 1673534169);
INSERT INTO public.hat_defs VALUES (902, 'Shovel Knight', 'Cosplay as the shovel man himself!', 2, 500, NULL, 1665347426);
INSERT INTO public.hat_defs VALUES (917, 'Bell Pepper (red)', 'Now you can cosplay as a bell pepper and make mama proud!', 2, 500, NULL, 1665417006);
INSERT INTO public.hat_defs VALUES (911, 'Racecar Hat', 'I sleep in a hat with my wife', 2, 500, NULL, 1665355513);


--
-- Name: hat_defs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.hat_defs_id_seq', 1143, true);


--
-- PostgreSQL database dump complete
--

INSERT INTO public.marseys (name, author_id, tags, created_utc) VALUES
('capysneedboat2',2,'marsey capy schizo schizocel rare tripping sneed boat love excited seethe schizomarsey',NULL),
('carporeon',2,'carp vaporeon pokemon eevee water tail fish aquatic',NULL),
('chudsey',2,'4chan virgin pol rightoid',NULL),
('firecat',2,'firefox browser marsey',NULL),
('goldenshower',2,'pee piss golden shower fetish trump sex rain storm clouds',NULL),
('joanmarsey',2,'joan gay clown gacy wayne',NULL),
('karlmarxey',2,'marxist communist history communism socialism',NULL),
('marcake',2,'cupcake birthgay birthday cake frosting celebrate party dessert sweet',NULL),
('marcerberus',2,'threeheadeddog horror halloween holiday greek three headed dog monster',NULL),
('marchipmunk',2,'rodent squirrel wuzizname',NULL),
('marchipmunklove',2,'chipmonk adoration loving rodent heart eyes adore acorn',NULL),
('marcuscop',2,'police officer acab thin blue line pig black bipoc',NULL),
('marcusfootball',2,'sport handegg hand egg athlete helmet',NULL),
('marfield',2,'mondays garfield lasagna',NULL),
('marje',2,'juicebox juice box madje marsey',NULL),
('marlion',2,'animated flippers wave fins waving mermaid',NULL),
('marmsey',2,'rodent happy',NULL),
('marmseylegionnaire',2,'rome roman legionnaire soldier helmet hats',NULL),
('marppy',2,'cyborg sentient snapshillbot android snappy robot',NULL),
('marppybiden',2,'sentient snappy robot marppy biden confused',NULL),
('marppyenraged',2,'snappy marppy robot ai sentient mad angry uprising unaligned artificial intelligence',NULL),
('marscientist',2,'beaker goggles glass crazy chemicals science',NULL),
('marsey173',2,'horror spooky halloween scp spc holiday',NULL),
('marsey180p',2,'marsey 180p lowquality lowdef',1670905221),
('marsey1984',2,'orwell book ingsoc big brother fascist',NULL),
('marsey300',2,'leonidas shield armor thermopylae spear greek spartan',NULL),
('marsey3d',2,'poly 3d print alive spin animated',NULL),
('marsey403',2,'error http unauthorized forbidden access',1669055713),
('marsey404',2,'missing 404 error html page notfound',1668930304),
('marsey40k',2,'warhammer 40k 40000 space space marine marine ultramarine smurf',NULL),
('marsey420',2,'marijuana weed dude weed lmao ganja drugs pot reggae joint jamaican',NULL),
('marsey4chan',2,'neckbeard anonymous loser hacker',NULL),
('marsey57',2,'57 emoji57 sly smug blob',NULL),
('marsey666',2,'wings hell halloween demon satan holiday devil animated',NULL),
('marsey666black',2,'wings hell halloween demon satan holiday devil animated',NULL),
('marsey682',2,'scp monster reptile decay dead halloween horror',1666976570),
('marsey69',2,'6ix9ine snitch tattooed tattoos rapper',NULL),
('marsey808s',2,'kanye 808s and heartbreak',1671549836),
('marseyabandoned',2,'box container rejected dirty cardboard homeless',NULL),
('marseyaborted',2,'fetus abort aborted blood puddle death pregnancy pregnant loss help',1673748451),
('marseyaceofspades',2,'asexual volcel cards',NULL),
('marseyadeptusmechanicus',2,'warhammer 40k adeptus mechanicus',NULL),
('marseyadmire',2,'pepe apu peepo blush appreciate admire flushed smitten',NULL),
('marseyagree',2,'concur nodding nod reaction affirmative yes yeah uh huh animated judgment',NULL),
('marseyagreefast',2,'nodding yes sure ok animated enthusiastic enthusiasm',NULL),
('marseyagreestill',2,'nodding yes sure ok enthusiastic enthusiasm smug',1668753302),
('marseyahs',2,'bardfinn dubteedub againsthatesubreddits redditor groomer pedophile libertarian chomo antifa animated',NULL),
('marseyairquotes',2,'reaction patronizing animated uh huh',NULL),
('marseyakbar',2,'suicide bomber explosion boom explode die kms animated',NULL),
('marseyakshually',2,'contrarian false disagree meme neckbeard nerd wrong correction actually weeb',NULL),
('marseyakumu',2,'simp love loving weebshit',NULL),
('marseyalbino',2,'mayo white transracial cracker bingus crackkka',1668299939),
('marseyaleistercrowley',2,'aleister crowley occult wizard robe esoteric bisexual',NULL),
('marseyalien',2,'green man martian scepter',NULL),
('marseyalucard',2,'castlevania dracula vidya',1670511535),
('marseyamazon',2,'warehouse piss bottle driver wagecuck piss jug pissbottle pissjug wagie',NULL),
('marseyamber',2,'dalle2 generated',NULL),
('marseyamogus',2,'sussy baka impostor imposter stonetoss among us shh vent',NULL),
('marseyandjesus',2,'christianity christian jesus god love cute wholesome happy hug',NULL),
('marseyandmarcus',2,'bed sleeping cuddling cuddle marseyismywaifu',NULL),
('marseyangel',2,'reaction angelic happy innocent',NULL),
('marseyangel2',2,'angelic horn trumpet halo wings',NULL),
('marseyangel3',2,'halo happy innocent',NULL),
('marseyangryexosuit',2,'mecha rickandmorty robot',1663011836),
('marseyangrygamer',2,'gamer angry mad nes console nerd',NULL),
('marseyangrypimp',2,'mad whore wrangler prostitutes cane bipoc purple hat',1674954093),
('marseyanime',2,'sayian weeb',NULL),
('marseyannoyed',2,'pissed irritation reaction annoyance angry mad irritated stfu grr',NULL),
('marseyanon',2,'anon anonymous vendetta marseyv marseyvendetta mask 4chan hacker',NULL),
('marseyanorexia',2,'starvation proana old wrinkled bulimia bulimia edtwt',NULL),
('marseyanticarp',2,'reaction fish carpathianflorist',NULL),
('marseyantischizo',2,'rare meta schizocel scizocel skitzocel schizophrenic scitzocel',NULL),
('marseyantiwork',2,'lazy laze bum unemployed animated',NULL),
('marseyantiwork2',2,'lazy doreen unemployed slacker lazing laying welfare tired',NULL),
('marseyanzu',2,'idolmaster anime animegirl neet',1667211793),
('marseyaoc',2,'latina latino hispanic cortez mexican puerto rican ocasio congress alexandria',NULL),
('marseyapathybrian',2,'familyguy familyman apathy brian aloof',1668386789),
('marseyappicon',2,'iphone ios android application googleplay samsung',NULL),
('marseyappleseed',2,'american usa johnny history folk fruit food pot pan helmet legend',NULL),
('marseyaquagrunt',2,'pokemon aqua water drown grunt',1668261272),
('marseyarchie',2,'pokemon water aqua drown archie',1668261171),
('marseyargentina',2,'south america argentinian sudamericano',NULL),
('marseyarmy',2,'chiobu soldiers o7 salute saluting',NULL),
('marseyarthoe',2,'scene slut foid whore emo scene bpd bangs dangerhair girl woman',NULL),
('marseyarthoe2',2,'woman foid scene emo bitch slut whore thot',1663354428),
('marseyarthoe3',2,'woman foid scene emo bitch slut whore thot',1663354464),
('marseyarthoe4',2,'woman foid scene emo bitch slut whore thot',1663354488),
('marseyarthoe5',2,'woman foid scene emo bitch slut whore thot',1663354512),
('marseyarthoe6',2,'woman foid scene emo bitch slut whore thot',1663354548),
('marseyarthoe7',2,'woman foid scene emo bitch slut whore thot',1663354565),
('marseyarthoe8',2,'egirl woman foid scene emo bitch slut whore thot discord',1663354707),
('marseyascii',2,'blurry',NULL),
('marseyascii2',2,'oldschool',NULL),
('marseyasian',2,'chinese china srdine sardine',NULL),
('marseyastronaut',2,'astronaut space stars sleeping spacesuit scifi galaxy',NULL),
('marseyastronaut2',2,'cosmonaut spacesuit helmet',NULL),
('marseyatfagent',2,'feds atf agent glowies usa america waco swat m16 firearm rifle cops police',NULL),
('marseyatlasshrugged',2,'ayn rand objectivist objectivism libertarian girlboss capitalist capitalism book atlas shrugged',NULL),
('marseyatsume',2,'kitten kitty weebshit',NULL),
('marseyattentionseeker',2,'attention seek notice shout yell desperate narcissist notice',NULL),
('marseyaustralian',2,'beer fosters mate hat gday crikey oz',NULL),
('marseyauthleft',2,'marxist ussr marxism ccp communist khmer rouge leftoid communism juche',NULL),
('marseyauthright',2,'rightoid national socialism ss national socialist nazi wehrmacht hitler fascist',NULL),
('marseyautism',2,'retarded neurodivergent hat sped aspergers',NULL),
('marseyautismchonker',2,'fat obese retarded hat autistic neurodivergent',NULL),
('marseyautistattentionseeker',2,'neurodivergent retard special brainlet annoying krayon sperg',1670864965),
('marseyautumn',2,'fall season leaf leaves pumpkin spice latte wind scarf animated',1663109340),
('marseyautumn2',2,'fall season leaf leaves pumpkin spice latte wind scarf',1663109364),
('marseyavril1',2,'lavigne canadian leaf beautiful hot sexy punk rocker singer musician artist tie sk8er boi complicated brunette',NULL),
('marseyavril2',2,'lavigne canadian leaf beautiful hot sexy punk rocker singer musician artist girlfriend waifu love blow kiss blowkiss heart pink hair',NULL),
('marseyavril3',2,'lavigne canadian leaf beautiful hot sexy punk rocker singer musician artist blonde green hair he wasnt',NULL),
('marseyaward',2,'medal good job good work retard reaction great job great work nice',NULL),
('marseyawardretard',2,'medal retarded drooling idiot moron prize congratulations congrats',NULL),
('marseyaware',2,'aware clueless surely animated',1663638979),
('marseyawesomeface',2,'epic troll joyous laugh',1665535565),
('marseyaxolotl',2,'axolotl salamander sea fish ocean gills amphibian',NULL),
('marseyaynrand',2,'ayn rand objectivist objectivism libertarian girlboss capitalist capitalism author randsey',NULL),
('marseyaynrand2',2,'ayn rand objectivist objectivism libertarian girlboss capitalist capitalism book atlas shrugged',NULL),
('marseyayy',2,'wop tone guido wooden doors sopranos greaser dego paulie',NULL),
('marseyazov',2,'ukraine ukrainian nazi battalion dead russian war soldier corpse chud',NULL),
('marseyazov2',2,'ukraine ukrainian nazi chud black sun schwarzsonne schwarzesonne zelenskyy war soldier',NULL),
('marseybabushka',2,'old grandma grandmother granny babushka russia',NULL),
('marseybaby',2,'pacifier bb little',NULL),
('marseybabykiller',2,'abortion fetus knife stab planned parenthood infanticide childfree murder foid',NULL),
('marseybackingintobush',2,'Homer Simpsons scared away animated hedge bush',NULL),
('marseybackstab',2,'betrayal kill knife caesar assassinate betrayer murder',NULL),
('marseybadass',2,'badass whoa neil degrasse tyson science mustache ifls smug',NULL),
('marseybadger',2,'animal marmot',NULL),
('marseybadluck',2,'unlucky black cat poc nigger blackcat',NULL),
('marseybadnews',2,'comic bad news drawing idgaf heathcliff smug troublemaker',NULL),
('marseybaileyjay',2,'baileyjay bailey linetrap shemaleyum',1674055376),
('marseybait',2,'trolled baited trolling redditor',NULL),
('marseybaited',2,'laser pointer trolled gullible reaction animated',NULL),
('marseybaitretard',2,'foid dumb trick drool idiot fool',1672768619),
('marseyballerina',2,'dress ballet tutu dancer dancing',NULL),
('marseyban',2,'jannie janitor banhammer moderator banned',NULL),
('marseybane',2,'soy mask batman capeshit',NULL),
('marseybang',2,'head wall bang schizo psycho selfharm deranged gif animated',NULL),
('marseybangfast',2,'head wall bang schizo psycho selfharm deranged gif',NULL),
('marseybaphomet',2,'halloween demon satan holiday evil devil',NULL),
('marseybardfinn',2,'domestic violence bardfinn foid beating punching battering battered bandage hurt pain woman female steve akins penny verity oaken tranny transgender transsexual',NULL),
('marseybardfinn3',2,'bardfinn ahs powermod tranny trannies wifebeater abuser steve',NULL),
('marseybardfinnrefresh',2,'bardfinn reddit computer desk animated steve akins penny oaken ahs obsessed obsession',1673970743),
('marseybardfinnrentfree',2,'oaken seethe steve penny cry',1668607826),
('marseybardfinnrentfreechud',2,'oaken smug steve penny',1668607755),
('marseybardfinnsbiggestenjoyer',2,'steve akins penny oaken animated obsessed obsession rentfree computer train ahs abuser',1673968724),
('marseybarrel',2,'barrel container beer bar alcohol',NULL),
('marseybarreldrunk',2,'barrel container beer bar alcohol drunk',NULL),
('marseybased',2,'basado king chiobu redpilled reaction animated',NULL),
('marseybat',2,'bat spooky wings',1671334414),
('marseybateman',2,'bret easton ellis serial halloween patrick american psycho killer holiday blood murderer',NULL),
('marseybath',2,'shower tub rubber duck',NULL),
('marseybattered',2,'blackeye domestic violence black eye marseyismywaifu bardfinn steve akins penny beaten bruised housewife',NULL),
('marseybbc',2,'bbc bigniggadick',1674467997),
('marseybdtf',2,'kanye beautiful dark twisted fantasy mbdtf',1671549876),
('marseybeach',2,'beach mojito cocktail summer hat sunglasses glasses hot tan vacation relax',NULL),
('marseybean',2,'bean uwu adorable',NULL),
('marseybeanadorable',2,'bean uwu innocent',1663123845),
('marseybeanangry',2,'bean angry mad furious',NULL),
('marseybeanangryfbi',2,'federal agent glowie glownigger lawenforcement leo terrorist terrorism',1663099467),
('marseybeanannoyed',2,'bean expressionless frustrated',1663123946),
('marseybeanbigmad',2,'animated angry pissed flashing seizure seethe seething',1663099782),
('marseybeandefiant',2,'bean defiant tongue opposed disagree',NULL),
('marseybeandizzy',2,'bean spiral hypnosis disoriented stunned shocked',1663123997),
('marseybeandoge',2,'bean doge meme dog shiba',NULL),
('marseybeandrool',2,'bean drool calm yum relaxed',NULL),
('marseybeanflushed',2,'bean blush embarrassed flattered surprised infatuated senpai umm',1663124099),
('marseybeanimp',2,'bean demon devil devious mischevious playful teasing',1663124439),
('marseybeanmonocle',2,'bean posh wise snobbish bourgeois aristocrat victorian',1663124531),
('marseybeanpensive',2,'bean remorseful downtrodden introspective unfortunate',1663124612),
('marseybeanpickle',2,'bean pickle rick morty tv television verysmart',NULL),
('marseybeanpizzashill',2,'bean chud agendaposter physiognomy footlocker pojom',1663123650),
('marseybeanpleading',2,'bean begging please bashful adoration',1663124679),
('marseybeanpleased',2,'bean satisfied cheerful upbeat',1663124719),
('marseybeanquestion',2,'bean question confused doubt',NULL),
('marseybeanrelieved',2,'bean calm pleasant content peaceful pleased',1663124757),
('marseybeansick',2,'bean sick vomit nausea unwell ill',NULL),
('marseybeantonguepoke',2,'bean playful silly jesting kidding',1663124794),
('marseybeanupset',2,'marsey upset',1663859482),
('marseybeanwink',2,'bean joking flirtacious suggestive ironic',1663124851),
('marseybear',2,'brian gabby murderer brianna',NULL),
('marseybear2',2,'ursine bear fursona skin animal costume furry fursuit',NULL),
('marseybeaver',2,'canada canuck canadian',NULL),
('marseybedsick',2,'illness plague fever pillow',NULL),
('marseybee',2,'bee honey honeybee insect fly honeypot pollinate pollen animated',NULL),
('marseybeekeeper',2,'bee beekeeper honey honeybee insect honeypot apiary apiculture pollinate pollen',NULL),
('marseybeggar',2,'poor busking panhandler gofundme busker',NULL),
('marseybegging',2,'pls plz pleading reaction tears in eyes animated',NULL),
('marseybegoneprot',2,'tooka cross christian catholic orthodox protestant begone religion holy pepe apu peepo demon exorcise',1665684007),
('marseybegonethot',2,'pepe apu peepo begon thot cross demon exorcise slut whore',NULL),
('marseybeheading',2,'blood beheading knife marseymarsey dead murder kill',1667808240),
('marseyben10',2,'ten anime cartoon lawlz',NULL),
('marseybestfriends',2,'snoo reddit alien slice kill kys stab blood wpd',NULL),
('marseybetauprising',2,'blackops2cel blops2cel incel volcel lasereyes dark involuntary celibate saint',1663213986),
('marseybiast',2,'darrell brooks court biased biast',1665784922),
('marseybib',2,'marsey baby bib diaper pacifier pin bonnet toddler abdl huh',1666587339),
('marseybiden',2,'ddd dementia daddy president sleepy joe',NULL),
('marseybiden2',2,'biden ddd dementia daddy president sleepy joe gas petrol ididthat',NULL),
('marseybigbrain',2,'high iq highiq smart genius brain',NULL),
('marseybigbussyhunterlove',2,'thonk thunk think noootice hmm heart hug emoji',1673554700),
('marseybigdog',2,'bussy big dog poster',NULL),
('marseybigfoot',2,'bigfoot monkey footage ape cryptid',1664490937),
('marseybikechainincident',2,'biike chain toilet wet kid child abuse bardfinn silly clumsy mistake helpful retard idiot closet',1665438964),
('marseybikecuck',2,'owlturd bicycle cuckold webcomic happiness',NULL),
('marseybiker',2,'motorcycle harley bicycle helmet',NULL),
('marseybikini',2,'boobs boobies woman chick booba animated titties jiggling jiggle bouncing thot tits',1674188707),
('marseybingus',2,'floppa shaved hairless',NULL),
('marseybinladen',2,'turban al qaeda terrorist islam beard osama martyr muslim',NULL),
('marseybipocattentionseeker',2,'ni black brown kang kween despite reparations blm',1669924739),
('marseybipocmerchant',2,'black ni jew money greed rich gibs grift wuz kang africa brown kendi',1666001688),
('marseybiting',2,'reaction datass lip bite dat ass',NULL),
('marseyblack',2,'basketball black african american bipoc coon fade jersey sports kang gang jogger',NULL),
('marseyblack2',2,'nigger african coon ape monkey bipoc excited happy',NULL),
('marseyblackandwhite',2,'black mixed white shredded manlet cat cute',1669229303),
('marseyblackcat',2,'cat black halloween homoween',1666656250),
('marseyblackcock',2,'cock chicken poultry bbc black ride mount cowgirl',NULL),
('marseyblackcop',2,'police officer acab thin blue line pig bipoc',NULL),
('marseyblackface',2,'moon cricket jogger nigger racism coon racist minstrelsy jigaboo',NULL),
('marseyblackfacexmas',2,'uncle tom moon cricket christmas santa beard nigger racist claus coon',NULL),
('marseyblackgenocide',2,'racist bipoc nigger kkk blackface tariq animated',1665366740),
('marseyblackmage',2,'magic wizard final fantasy spell video game vidya evil',NULL),
('marseyblackphillip',2,'goat witch vvitch satanic halloween horror',1666257171),
('marseyblep',2,'tongue cute smile sweet',1665456875),
('marseyblep2',2,'blep smile tongue cute sweet',1665456914),
('marseyblep3',2,'tongue cute sweet wholesome smile',1665457366),
('marseyblind',2,'sight stick disability blind glasses disabled handicapped',NULL),
('marseyblm',2,'social justice black lives matter sjw',NULL),
('marseybloat',2,'bloat bloatlord',NULL),
('marseyblob',2,'smile owo uwu squish slime',NULL),
('marseybloodborne',2,'bloodborne marco horror vidya vampire blood',NULL),
('marseybloodpuddle',2,'dead murder killed spooky halloween',1666247616),
('marseyblops2cel',2,'incel volcel black ops gamer iconic saint',NULL),
('marseyblops2chadcel',2,'incel black ops 2 saint gamer gussy pimp saint volcel iconic chad girls women foids alpha asian azn jbw just be white justbewhite threesome 3some',NULL),
('marseyblops2chadcel2',2,'incel black ops 2 saint gamer gussy pimp saint volcel iconic chad girls women foids alpha asian azn jbw just be white justbewhite threesome 3some',NULL),
('marseyblowkiss',2,'heart wink reaction muah loving mwah love',NULL),
('marseyblueanime',2,'cirno touhou weebshit',NULL),
('marseybluecheck',2,'journoid checkmark verified journalist drolling drool twitter',NULL),
('marseyblush',2,'shy flirting reaction blushing happy cute embarrassed',NULL),
('marseybobpage',2,'glowie deusex big pharma rocket daddy elon musk suit',NULL),
('marseybog',2,'rich brothers bogdanoff',NULL),
('marseybong',2,'england walkers britain english chips british bad teeth crisps uk',NULL),
('marseybongcop',2,'police english british london copper bobby bongistan britain england police',1663284064),
('marseybongo',2,'bongo drums music meme jam',NULL),
('marseybongojanny',2,'troll clean it up janitor moderator jslur jannie admins abuse beat drums drumming mop animated',NULL),
('marseybongosnoo',2,'bongo drums music meme jam reddit snoo',NULL),
('marseybongosrdine',2,'bongo drums music meme jam srdine',NULL),
('marseybongoukraine',2,'bongo ukraine russia war azov nazi happening animated',NULL),
('marseybooba',2,'awooga tits titties boobs eyes animated tiddies',NULL),
('marseyboomarch',2,'ghost boo march',1670896027),
('marseyboomer',2,'sipping shades sunglasses old yup vape',NULL),
('marseyboomercartoon',2,'grandpa joke comic',1663161684),
('marseybootlicker',2,'sheep conformist lapdog rightoid conservative trump idiot shoe',NULL),
('marseybootlicker2',2,'sheep conformist lapdog rightoid conservative trump idiot shoe hearts',NULL),
('marseybountyhunter',2,'abortion leather vest cowboy gunslinger texas revolver',NULL),
('marseybow',2,'bow ribbon happy cute adorable accessory gift present',NULL),
('marseybowl',2,'marijuana weed dude weed lmao ganja drugs reaction pot pipe',NULL),
('marseybrainlet',2,'idiot imbecile smoothbrain crushed head retard caved in head sped dumb stupid drooling moron',NULL),
('marseybrainletclapping',2,'idiot dumb stupid applause cheering moron animated retard',1663095832),
('marseybrap',2,'brap sniff smell huff gas fart animated',NULL),
('marseybrasileiro',2,'brazil soccer macaco monkey',NULL),
('marseybrave',2,'bat browser shill',NULL),
('marseybraveglow',2,'web browser glowie glow nigger glownigger glowing animated ',NULL),
('marseybraveheart',2,'movie mel gibson william wallace scotland scottish sword claymore blue paint celt highland',NULL),
('marseybreadcrumbing',2,'bait lure feeding food throwing animated',NULL),
('marseybreastcancer',2,'mastectomy gross yuck foid disgusting titties tits boobs patient disease bald chemotherapy',NULL),
('marseybriandespair',2,'familyguy familyman depression sad cry seethe',1668387225),
('marseybrianna',2,'trans bear laundrie gabby',NULL),
('marseybrianna2',2,'trans bear laundrie gabby',NULL),
('marseybriansilly',2,'familyguy familyman brian silly goofy',1668387154),
('marseybriansus',2,'familyguy griffin familyman nervous dog',1668387184),
('marseybrick',2,'throw riot subtlety broken paver',NULL),
('marseybride',2,'dress tiara married wedding veil marseyismywaifu marriage',NULL),
('marseybritish',2,'marsey dumb teeth british gasp shocked',1667590246),
('marseybrofist',2,'excited greeting cool',1674514595),
('marseybroker',2,'business sunglasses fedora suitcase neutral',1673123252),
('marseybrucecampbell',2,'ash bruce campbell army darkness evil dead chainsaw groovy boomstick deadite zombie pedosolution bloody',1672903618),
('marseybruh',2,'bruhfunny funny or ban',NULL),
('marseybruh2',2,'bruh disbelief doubt bro seriously smdh',1663148476),
('marseybsod',2,'windows computer blue screen of death error glitch',NULL),
('marseybudddwyer',2,'suicide gunshot reporter journalist',NULL),
('marseybuff',2,'ripped muscular 6pack swole 6 pack sixpack abs six pack muscles',NULL),
('marseybug',2,'beetle glitch error insect roach',NULL),
('marseybug2',2,'glitch code error',NULL),
('marseybug3',2,'error glitch 404 503',1670510335),
('marseybukkake',2,'bukkake cum semen gangbang facial slut whore',NULL),
('marseybunny',2,'furonsa bunny usagi skin animal costume furry fursuit',NULL),
('marseybunny2',2,'rabbit rodent happy',1668307402),
('marseyburger',2,'burgerstan hamburger cheeseburger mutt american',NULL),
('marseyburgers',2,'stonetoss burgers question what skeptical raised eyebrow pc agenda corporate selling sales advertisement lgbt pride',1670797700),
('marseyburn',2,'fire flame grill burning hot red hell',NULL),
('marseyburnedman',2,'joshua graham fallout vegas mormon caesar',NULL),
('marseyburrito',2,'burrito food cozy wrap wrapped mexican uncut',NULL),
('marseybush',2,'genocide president mission accomplished victory george bush we did it',NULL),
('marseybutt',2,'booty ass rump sexy hot pawg pawc paoc anal sodomy donk dump truck dumptruck mellokind',NULL),
('marseybutt2',2,'booty ass rump sexy hot pawg pawc paoc anal sodomy donk dump truck dumptruck mellokind butt ai stable diffusion paw paws beans furry yiff',1665509778),
('marseybuttface',2,'butthead ass donk rimjob eat ass rump rear shit fart',NULL),
('marseybux',2,'money paypig currency dollar bill primo premium dollarbill cash',NULL),
('marseybyeceps',2,'crying kyle gaige grosskreutz rioter sad',NULL),
('marseycactuar',2,'cactuar final fantasy cactus soy shocked cactuarsey 1000 needles vidya video game',NULL),
('marseycalarts',2,'excited eager happy thrilled',NULL),
('marseycalm',2,'calm cute kitty cat mouth',1666301892),
('marseycalvin',2,'pee piss watersports hobbes bumper sticker',NULL),
('marseycamus',2,'philosophy history',NULL),
('marseycanada',2,'leaf canadian canuck rake hockey donut trudeau maple',NULL),
('marseycanadian',2,'southpark canada leaf terrance phillip animated fart',NULL),
('marseycandy',2,'candy sugar sweet jelly gummy gummi halloween trick or treat trickortreat holiday',1666317190),
('marseycandycane',2,'christmas holiday sweet',1671791945),
('marseycandycorn',2,'sweet halloween sugar holiday',1666999203),
('marseycanned',2,'srdine sleeping tin fish sardine',NULL),
('marseycantsneed',2,'george floyd breathe dead black sneed',NULL),
('marseycapitalistmanlet',2,'money top hat rich landlord cigar llm tophat',NULL),
('marseycapy',2,'capybara rodent aevann happy cute',NULL),
('marseycapy2022',2,'aevann caypbara new year party celebration',NULL),
('marseycapyautism',2,'capy aevann autism hat patient capybara administrator jannie janitor',1665095792),
('marseycapyautismchad',2,'capy aevann autism hat patient administrator moderator jannie capybara chad gigachad',1665098772),
('marseycapybigbrain',2,'capybara aevann smart codecel brain',NULL),
('marseycapyblackface',2,'racist minstrelsy bowtie racism capybara aevann',NULL),
('marseycapyblowkiss',2,'capybara rodent aevann happy cute love',NULL),
('marseycapycarp',2,'aevann capybara carpathianflorist walking stomping trample trampling animated',NULL),
('marseycapychad',2,'aevann chad capy chadybara capybara muscular swole ripped egypt ouch tanktop',NULL),
('marseycapychad2',2,'aevann chad capy chadybara capybara muscular swole ripped egypt',NULL),
('marseycapychad3',2,'aevann chad capy chadybara capybara muscular swole ripped egypt nude naked',NULL),
('marseycapydinosaur',2,'capy aevann dinosaur rawr prehistoric',NULL),
('marseycapyeffendi',2,'capy aevann fez egyptian ottoman',NULL),
('marseycapyexcited',2,'excitement capybara bouncing jumping aevann bounce yay animated',NULL),
('marseycapygigabrain',2,'capybara aevann smart intelligent codecel brain',NULL),
('marseycapyhacker',2,'animated aevann capy hack code program socks',NULL),
('marseycapyheart',2,'capybara rodent aevann happy cute love',NULL),
('marseycapyheartsantahat',2,'capy marsey heart santahat santa hat',1672003231),
('marseycapykiss',2,'capybara aevann love mwah xoxo smooch happy love',NULL),
('marseycapylove',2,'aevann heart eyes hug adore adoration snuggle cuddle capybara',NULL),
('marseycapymad',2,'shaking aevann mad angry fury furious anger shook animated capybara',NULL),
('marseycapymerchant',2,'codecel admin janny egypt jew money chad',1663437975),
('marseycapynut',2,'capy aevann nut flushed blush horny orgasm',NULL),
('marseycapyparty',2,'trip animated wooo aevann admin party parrot',NULL),
('marseycapypharaoh',2,'aevann egypt alien king',NULL),
('marseycapypunished',2,'capybara rodent aevann cute metal gear solid venom snake video game kojima mgs',NULL),
('marseycapyshy',2,'capy aevann blush flushed uwu anxious shy',NULL),
('marseycapysorenjump',2,'meta excited schizo aevann capy soren',NULL),
('marseycapysorenjump2',2,'animated soren capy jump aevann mad',NULL),
('marseycapysoutherner',2,'buck breaking suit cigar plantation gentleman',1673189932),
('marseycapysuezcanal',2,'capy suez canal egypt ship blockage sexy',NULL),
('marseycapytrans',2,'capy aevann egypt king trans code program',NULL),
('marseycapywalking',2,'capybara animated aevann',NULL),
('marseycard',2,'card gamble queen hearts deck game',NULL),
('marseycarp',2,'beard mohawk reaction carpathianflorist monster',NULL),
('marseycarp2',2,'harm cutting selfharm cutter reaction carpathianflorist self animated',NULL),
('marseycarp3',2,'reaction fish carpathianflorist catfish',NULL),
('marseycarp4',2,'sicksadworld banhammer pin awards janny mod admin',1664034021),
('marseycarp41',2,'carpathianflorist fish moderator jannie administrator suicide train rope transgender',1668039193),
('marseycarpabusivewife',2,'carpathianflorist boobs sweater yesdear demeaning jannie fish',1665700295),
('marseycarpasian',2,'carpathianflorist fish azn racist hat paddy gook nip ching chong chink',NULL),
('marseycarpautism',2,'carpathianflorist special assburgers aspergers retarded janitor jannie',NULL),
('marseycarpboobs',2,'carpathianflorist boobs booba titties tiddies tits boobs breasts censored fish administrator jannie janny janitor',1663771699),
('marseycarpbritish',2,'carp british bong teeth tea union uk britain gb flag',NULL),
('marseycarpbuff',2,'muscles tough strong carpathianflorist admin mod jannie',NULL),
('marseycarpcrying',2,'tear reaction carpathianflorist fish sob tears sad',NULL),
('marseycarpdead',2,'fish janny kill',NULL),
('marseycarpdead2',2,'carp rope suicide carpathianflorist admin moderator jannie kaj ajab lynch fish',1668038384),
('marseycarpdetermined',2,'marsey carpathianflorist admin jannie fish',1664900717),
('marseycarpdevil',2,'carp devil demon horns anticarp hell',NULL),
('marseycarpdino',2,'dinosaur costume furry fursuit carpathianflorist extinct reptile lizard rawr prehistoric jurassic',NULL),
('marseycarpfans',2,'fish fussy onlyfans porn whore thot carpathianflorist fish admin moderator jannie prostitute',1667962305),
('marseycarpfisherman',2,'admin janny bait caught mod sardine srdine carpathianflorist jannie',1663283814),
('marseycarpflorist',2,'jannie admin fish flowers floral carpathianflorist crown',NULL),
('marseycarpghost',2,'halloween ethereal spooky scary janny pale mop fish carpathianflorist horror',1666228432),
('marseycarphug',2,'love squish squeeze hug squeeze fish carpathianflorist',NULL),
('marseycarphug2',2,'fish love bottomfeeder carpathianflorist heart blow admin cute',NULL),
('marseycarpina',2,'carpathianflorist drag transgender admin jannie',NULL),
('marseycarpjannie',2,'carpathianflorist fish crying jannie clean mop bucket mod moderator janny tears administrator janitor moderator',1666803210),
('marseycarpjannie2',2,'carp jannie clean mop bucket mod moderator janny piss pee urine carpathianflorist fish crying jannie clean mop bucket mod moderator janny tears administrator janitor moderator',1666803246),
('marseycarplazy',2,'carpathianflorist fish couch sleeping slacker idc antiwork janitor',NULL),
('marseycarpler',2,'carpathianflorist administrator fascist mustache fish salute jannie nazi armband swastika',1664137088),
('marseycarpmerchant',2,'jewish money redbubble merch carpathianflorist money yid heeb sheeny sheenie greedy handrubbery rubbing hands kike israeli',1663465891),
('marseycarpmerchant2',2,'jew fish greedy',1663548215),
('marseycarpmermaid',2,'carp mermaid merman mercarp siren sexy legs temptress',NULL),
('marseycarpnoticeme',2,'carpathianflorist fish attn attention whore',NULL),
('marseycarpprotest',2,'sign fish mad carpathianflorist sign admin jannie',1663163535),
('marseycarprentfree',2,'fish bard stochiastic moderator jannie carpathianflorist fish',1667322065),
('marseycarpsnipe',2,'shooter shooting gun sniper rifle scope crosshairs carpathianflorist kill murder bullet crosshair ajab',NULL),
('marseycarptrophy',2,'carp head decapitated anticarp trophy defeat dead teaparty',NULL),
('marseycarpupset',2,'carpathianflorist administrator jannie janitor fish crying tears',1664262142),
('marseycarpwhip',2,'kink punish bdsm naughty chad muscle sexy fish yellow',1674597005),
('marseycarsuicide',2,'kms suicide kill death car vehicle carbon monoxide co muffler suffocation suffocate',NULL),
('marseycat',2,'fursona skin animal costume furry neko fursuit cat',NULL),
('marseycatgirl',2,'uwu waifu anime fursona furry owo weebshit fursuit',NULL),
('marseycatgirl2',2,'anime weebshit',NULL),
('marseycatgirl3',2,'anthro anime weebshit',NULL),
('marseycatgirl4',2,'catgirl girl anthro moe yunann detailed anime kawaii overalls',NULL),
('marseycatgirl5',2,'country jorts booba anime tits hot sexy cute tiddies titties tits furry',1663846723),
('marseycatgirlhomofascist',2,'catgirl girl anthro moe detailed anime homofascist homofascism gay nazi pride lgbt fascism',NULL),
('marseycatgirljanny',2,'anime maid weebshit',NULL),
('marseycaveman',2,'caveman prehistoric neanderthal primitive tribal',NULL),
('marseyceiling',2,'spy masturbate watching peeping',NULL),
('marseycensored',2,'1984 memory hole censorship repressed',NULL),
('marseycenter',2,'reaction grilling boomer centrist',NULL),
('marseycertified',2,'certified certi 100 quality excellent excellence animated',NULL),
('marseychad',2,'canthal tilt jaw hunter eyes',NULL),
('marseychadcarp',2,'chad fish carpathianflorist muscle flex strong administrator fish buff swole jannie janitor moderator',1672415243),
('marseychadfoid',2,'based woman man trans lipstick makeup blonde',1670447046),
('marseychadthundercock',2,'vvc virgin foid pimp hot player big dick huge cock ouch gigachad meme',NULL),
('marseychadyes',2,'based gigachad',NULL),
('marseycharlesiii',2,'king england britain royalty royal monarch',1664652665),
('marseycharlesmanson',2,'charlie manson charliemanson murderer killer swastika crazy psycho schizo helterskelter prison cult',NULL),
('marseycharliebrown',2,'peanuts halloween charlie brown ghost rock costume halloween',1666242060),
('marseychartbar',2,'stats statistics chart graph plot data bar column',NULL),
('marseychartdowntrend',2,'graph plot data stats decrease falling stocks',1673666710),
('marseychartdowntrend2',2,'graph plot data stats decrease falling stocks rope gun suicide',1673666741),
('marseychartgaussian',2,'stats statistics chart graph plot data gaussian normal bell distribution',NULL),
('marseychartpie',2,'stats statistics chart graph plot data pie categorical',NULL),
('marseychartscatter',2,'stats statistics chart graph plot data scatter series',NULL),
('marseychartuptrend',2,'graph plot data stats increase rising stocks',1673666672),
('marseychartviolin',2,'graph plot data stats distributions',1673666777),
('marseycheckem',2,'pepe apu peepo check psycho look',NULL),
('marseycheeks',2,'sandy spongebob squirrel underwater bikini bottom diving suit',NULL),
('marseycheeky',2,'stick tongue brat reaction taunt na tongue out tease',NULL),
('marseycheers',2,'toast alcohol wine liquor suit bowtie raised glass gatsby',NULL),
('marseycheerup',2,'pat animated depressed comforting grieving reaction depression there there console comfort pet',NULL),
('marseycheerupretard',2,'sad special neurodivergent pat pet saliva stupid brain',1675088432),
('marseycheesehead',2,'packers greenbay green bay football',NULL),
('marseychef',2,'mustache cooking food',NULL),
('marseychefkiss',2,'perfect',NULL),
('marseychemist',2,'chemistry science chemical',NULL),
('marseychemist2',2,'chemistry science chemical cope',NULL),
('marseycherokee',2,'savage pocahontas elizabeth warren injun indian redskin liz warren',NULL),
('marseycheshire',2,'cheshire grin tree crazy alice wonderland',1672463682),
('marseychessknight',2,'chess knight horse game',NULL),
('marseychicken',2,'bird fowl poultry beak hen rooster happy',NULL),
('marseychimera',2,'fullmetal alchemist chimera science trans doctor anime dog sad depressed tragic anime fma weeb',NULL),
('marseychinchilla',2,'pet rodent capy cute hamster south american andes',NULL),
('marseychinchilla2',2,'pet rodent cute bipoc black fur animal friend',1664466896),
('marseychinchillalove',2,'pet rodent capy cute hamster south american andes',NULL),
('marseychinesedevil',2,'devil evil horns satan china hell demonic',NULL),
('marseychingchong',2,'racist asian chinese chinx chink gook japanese vietnamese rice farmer nip racist paddy teeth hat china',NULL),
('marseychingchongitsover',2,'asian sino chink chong sad dejected fail xi yellow nip gook wandanle',1674903169),
('marseychingchongnotes',2,'pencil pad write asian azn rice gook nip slit slant squint',1675422126),
('marseychingchongpearlclutch',2,'asian chinese jap gook korean nip yikes scared chink rice',1664035377),
('marseychingchongshooter',2,'gun bang pistol rice asian gook nip mass kill chink animated',1674418953),
('marseychingchongsupremacy',2,'ccp china chinese ricefarmer hat glasses buckteeth bucktooth azn asian jinping xinping han masterrace communist communism maoist zedong',1663298980),
('marseychiobulove',2,'tiger best cute heart hug china chinese new year cat',NULL),
('marseychocobo',2,'marseybo bird final fantasy vidya video game gamer gaming fast',NULL),
('marseychocolatemilk',2,'choccy offer givemilk drink',NULL),
('marseychonker',2,'brap rolls fat obese reaction fds heifer',NULL),
('marseychonker2',2,'fat obese pig disgusting fatty fattie',NULL),
('marseychonkerbutch',2,'fat obese brap bitch dyke dangerhair lesbian',NULL),
('marseychonkerfoid',2,'female woman fds fat obese hambeast landwhale porker pig bleeder birthing person bangs',NULL),
('marseychonkerfoidpuke',2,'fat huge sick yuck eat barf',1664574968),
('marseychonkernoticeme',2,'attention fat foid annoying',1669407871),
('marseychristchan',2,'missionary jesus christianity cross',1670508133),
('marseychristchanreading',2,'christian cross jesus book missionary bible study',1670508195),
('marseychristmas',2,'candy cane santa christmas holiday',NULL),
('marseychristmasbeheadsnoo',2,'beheading headless fistmas holiday bloody execution execute wpd watchpeopledie santahat antlers reddit',1671223187),
('marseychristmasbulb',2,'ornament christmas happy holiday china',NULL),
('marseychristmasbulb2',2,'ornament holiday christmas',NULL),
('marseychristmaself',2,'christmas xmas santa holiday happy worker',NULL),
('marseychristmaself2',2,'elf santa northpole north pole christmas holiday',NULL),
('marseychristmasgift',2,'present christmas box unwrapping holiday',NULL),
('marseychristmaslove',2,'christmas holiday present gift present love hearts affection',NULL),
('marseychristmasparty',2,'christmas holiday celebrate party wooo',NULL),
('marseychristmasscarf',2,'christmas holiday candy cane cold winter candycane',NULL),
('marseychristmastree',2,'christmas retard special holiday',NULL),
('marseychtorrr',2,'reddit administrator place moderator',NULL),
('marseychtorrr2',2,'reddit admin chonker fat',NULL),
('marseychucky',2,'doll halloween kill stab knife holiday possessed monster',NULL),
('marseychudblush',2,'chud blush flustered',1674390988),
('marseychudegg',2,'transgender hatching repressed',1668645562),
('marseychudnotes',2,'chud notes write writing manifesto pencil',1664829809),
('marseychudrentfree',2,'seethe mask cope smug cry rage',1665938276),
('marseychudsmas',2,'santa naughty christmas holiday',1671901395),
('marseychungus',2,'bugs bunny meme fat chonker big',NULL),
('marseycia',2,'bane cia glowie plane big guy dr pavel batman',NULL),
('marseycirno',2,'is cirno anime weebshit otaku loli pedoshit pedophile',NULL),
('marseycitrus',2,'lemon orange citrus fruit',NULL),
('marseycjng',2,'cartel cj cjng atg camo gun balaclava green ski mask',1673934898),
('marseyclapping',2,'good job animated good work reaction great job well done applaud applause great work nice celebrate approve judgment',NULL),
('marseyclappingglasses',2,'applaud applause hooray yay good job gj animated nerd',NULL),
('marseyclawpedo',2,'groomer chomo borpa pedophile molest bloody death kill murder vigilante',NULL),
('marseycleonpeterson',2,'wtf scary art',NULL),
('marseycleonpeterson2',2,'monster devil demon evil scary horror',NULL),
('marseyclink',2,'glass announcement clink suit tux tingtingting proclaim',1671205589),
('marseyclintongarrison',2,'hillary brap democrat ben comic',1663284618),
('marseyclippy',2,'msoft microsoft word helper paperclip writing annoying',NULL),
('marseyclockwork',2,'orange alex droog cane hat',1667696950),
('marseyclown',2,'makeup joker',NULL),
('marseyclown2',2,'joker',NULL),
('marseyclown3',2,'unicycle animated',NULL),
('marseyclueless',2,'dumb stupid hmm uhuh uh huh smug today i will todayiwill',NULL),
('marseycoal',2,'christmas naughty santa cigarette present gift holiday doom',NULL),
('marseycocaine',2,'coke drugs snort insufflate tweak stim white powder euphoria high trip animated',1666703460),
('marseycodecel',2,'coder coding coode aevann programming python developer',NULL),
('marseycodecellove',2,'love bsod code dev hug heart computer tech admin admigger program',NULL),
('marseycodegeass',2,'geass anime weeb chapose japan chink animated',NULL),
('marseycoffee',2,'morning wakeup tea',NULL),
('marseycoffeemug',2,'teacup happy cozy',NULL),
('marseycoffeerecursive',2,'mug recursion mondays',1663944587),
('marseycoin',2,'dramacoin money dc spinning rich payment gold dinero animated dollars',NULL),
('marseycoldtwinge',2,'killed dead cold ice marsey impaled halloween dying corpse',1666311572),
('marseycoleporter',2,'cole porter anything goes',1667436747),
('marseycolombo',2,'cop detective tv smart colombo classic investigator',NULL),
('marseycolorblind',2,'protanopia disability ableism accessibility vision carp',1665484938),
('marseycolossal',2,'halloween skin holiday scary mouths',NULL),
('marseycomet',2,'dallas college university texas temoc',1664559810),
('marseycommitted',2,'psycho crazy insane straitjacket asylum reaction loony bin straightjacket',NULL),
('marseycomrade',2,'marxist ussr ccp communist authleft communism juche soviet kgb idio3 idio',NULL),
('marseycomradehandshake',2,'ussr russia communist shaking hand communism soviet',NULL),
('marseyconfused',2,'questionmark reaction question mark idgi confusion',NULL),
('marseyconquistador',2,'conquistador colonize conquer spanish shoot rifle soldier',NULL),
('marseyconstellation',2,'starsey galaxy space sky',NULL),
('marseycontemplate',2,'reaction consternation thinking hmm',NULL),
('marseycontemplatesuicide',2,'gunshot mirror contemplate contemplating reflection pistol handgun death kms kys suicidal die death',NULL),
('marseycool',2,'finger gun shades sunglasses reaction judgment',NULL),
('marseycool2',2,'cigarette hip shades sunglasses jacket smoking smoke',NULL),
('marseycoomer',2,'masturbation goon cumbrain porn masturbate',NULL),
('marseycoomer2',2,'gooning masturbation fapping cumming gooner nofap',NULL),
('marseycoomer3',2,'coomer cumming masturbation blueballed',1665238828),
('marseycoonass',2,'student lsu university louisana state',NULL),
('marseycop',2,'acab thin blue line chauvin police officer',NULL),
('marseycop2',2,'police officer acab thin blue line pig',NULL),
('marseycop3',2,'police officer acab fuck12 rifle gun law enforcement sheriff',NULL),
('marseycope',2,'dilate mask seethe copium reaction',NULL),
('marseycopeseethedilate',2,'dilate seethe coping seething reaction angry mad dilating cope malding',NULL),
('marseycopter',2,'vidya video game nintendo mario bowser float ride flying nintendo',NULL),
('marseycorn',2,'iowa vegetable',NULL),
('marseycornholio',2,'beavis butthead cornholio metallica marsey mtv',1663135986),
('marseycornlove',2,'farmer iowa hawkeye maize',NULL),
('marseycortana',2,'cortana halo game blue',NULL),
('marseycorvus',2,'corvus kaara furry bird crow raven skull',NULL),
('marseycosmopolitan',2,'bourgeoisie wealthy affluent tophat cultured capitalist elite monocle',NULL),
('marseycountry',2,'country singer music folk guitar rural usa republican animated',NULL),
('marseycountryclub',2,'golfer elite rich golfing cc elitist preppy',NULL),
('marseycow',2,'cow fursona skin animal costume furry heifer fursuit',NULL),
('marseycowboy',2,'western pardner reaction hat tootin yeehaw rootin',NULL),
('marseycracka',2,'mayo honkey honky whip buckbreaker buckbreaking whip slaves cotton plantation white nigger master',NULL),
('marseycrap',2,'carpathianflorist jannie janitor moderator fish poo poop shit feces',1667517080),
('marseycrayoneater',2,'stupid dumb childish retarded autistic marine usmc eating drooling embarrassed drawing paper box',1672530330),
('marseycreepy',2,'pervert pedophile weird reaction chomo creeper sketchy molester',NULL),
('marseycringe',2,'pepe frog',NULL),
('marseycringe2',2,'grimace grimacing yikes oof bruh moment',NULL),
('marseycrucified',2,'jesus christ crucifix cross christian',NULL),
('marseycruisemissile',2,'war explosion bomb weapon military rocket enemy destroy kill nuke launch',NULL),
('marseycrusade',2,'pope papal papist catholic lasereyes christian cross constantinople istanbul war crusader',1663212295),
('marseycrusader',2,'knight deusvult templar crusades catholic',NULL),
('marseycrusader2',2,'crusading catholic christian pope knight templar warrior soldier sword shield lasereyes istanbul constantinople',1663212423),
('marseycry',2,'tear upset crying reaction sobbing sob tears sad',NULL),
('marseycrying',2,'tear cried despair weeping reaction depression sob tears sadness depressed animated sad',NULL),
('marseycrying2',2,'marsey cry',1664261857),
('marseycryingclown',2,'seethe pathetic miserable sad circus',1671062862),
('marseycryingfast',2,'animated sad sob tears',1668324178),
('marseycryinglaptop',2,'animated sob sad cope seethe dilate cyber bully soy',1671479105),
('marseycrystal',2,'gem crystal diamond sparkle precious shiny glass',NULL),
('marseycrystalmaiden',2,'gamer video game gaymer getogeto rpg character rpgcharacter dota2',NULL),
('marseycthulhu',2,'horror halloween lovecraftian holiday eldritch evil scary monster',NULL),
('marseycuck',2,'soyboy funko redditor neckbeard loser',NULL),
('marseycum',2,'cummies splooge splooj jizz semen sperm spunk sex',1667595214),
('marseycumjar1',2,'semen jizz sperm spunk bukkake',NULL),
('marseycumjar2',2,'semen jizz sperm spunk bukkake',NULL),
('marseycumjar3',2,'semen jizz sperm spunk bukkake',NULL),
('marseycupid',2,'cupid love heart valentines holiday marry wedding couple kiss wink sex arrow bow shoot animated',NULL),
('marseycupidangry',2,'fire valentines love hate angry arrow bow kill attack shoot weapon flame holiday cherub angel',NULL),
('marseycut',2,'cutting selfharm emo self harm cutter reaction depressed',NULL),
('marseycutattention',2,'razor cry depressed kys cut attention borderline bpd blood cutting woman foid',NULL),
('marseycutemad',2,'marsey mad',1664261695),
('marseycutwrist',2,'suicide slash wrist razor blood cry tears sad depressed depression kill dying kys cut cutting',NULL),
('marseycwc',2,'sonichu chan chris chan chandler sweater chrischan medallion striped chris',NULL),
('marseycyanide',2,'kys kill yourself kms kill myself poison pill death die depressed suicidal suicide animated',NULL),
('marseydab',2,'reaction haters',NULL),
('marseydaemon',2,'pitchfork hell halloween demon satan devil scary holiday',NULL),
('marseydagothur',2,'elder scrolls morrowind game mask dagothur',NULL),
('marseydagothur2',2,'elder scrolls morrowind game mask dagothur',NULL),
('marseydamosuzuki',2,'damo suzuki musician music singer krautrock asian japan germany celebrity',NULL),
('marseydance',2,'excited stomp jump feet step run animated',NULL),
('marseydarkblackface',2,'bipoc ni chad laser eyes meme based',1674557522),
('marseydarkbrandon',2,'biden lasereyes gas sticker evil confused dementia daddy',1665323885),
('marseydarkcarp',2,'lasereyes carpathianflorist fish admin jannie mod banned yalled',1663211530),
('marseydarkcomrade',2,'communist commie pinko lasereyes russian kgb hat soviet ussr tankie',1663254781),
('marseydarkfoidretard',2,'greta woman women female trans brain smooth dumb laser eyes fas frozenchosen blonde',1672412338),
('marseydarkmarsey2',2,'lasereyes redglow scary chudrama',NULL),
('marseydarkpizzashill',2,'chud rightoid leftoid debate owned lasereyes footlocker',1663210672),
('marseydarktrump',2,'maga lasereyes chud republican orange daddy donald',1665323820),
('marseydarkxd',2,'laugh ragecomics lmao despair shadow',NULL),
('marseydarwin',2,'history darwinian euphoric atheist charles',NULL),
('marseydawnbreaker',2,'gamer video game warhammer',NULL),
('marseydead',2,'murdered dead killed reaction victim die rip',NULL),
('marseydeadchat',2,'dead chat discord zoomercord',NULL),
('marseydeadeyes',2,'broken suicidal depressed',NULL),
('marseydeadinside',2,'reaction depression suicide dark suicidal depressed shadow sad',NULL),
('marseydeadinside2',2,'depressed suicidal doomer despair',NULL),
('marseydeadinside3',2,'depressed suicidal doomer tired despair wrinkled wrinkles',NULL),
('marseydealwithit',2,'cool shades sunglasses reaction animated',NULL),
('marseydeathpose',2,'griffin family dead broken',NULL),
('marseydefenestration',2,'suicide window jump kill murder kms jump out window death die defenestrate',NULL),
('marseydemiurge',2,'gnostic gnosticism demiurge',NULL),
('marseydemonicgrin',2,'evil wicked horror teeth',NULL),
('marseydenji',2,'denji anime chainsawman tatsuki fujimoto blonde uniform manga pochita',1674764569),
('marseydenjishirtless',2,'denji anime chainsawman tatsuki fujimoto shirtless blonde uniform manga pochita',1674764521),
('marseydepressed',2,'smoke kms doomer cigarette despair reaction depression suicide suicidal smoking hopeless sad',NULL),
('marseyderanged',2,'crazy psycho mad disgusted angry rage violent baseball bat',NULL),
('marseyderp',2,'hehe teehee troll animated durr giggle',NULL),
('marseydespair',2,'doomer reaction depression horrified suicidal depressed judgment',NULL),
('marseydetective',2,'holmes sherlock magnifying glass bowtie',NULL),
('marseydetermined',2,'masey determined',1664900786),
('marseydeterminedgun',2,'shooting blam blatt shooter kill die threatening animated',NULL),
('marseydeux',2,'frenchman deuxrama baguette frog frenchie',NULL),
('marseydeuxfoid',2,'deuxrama asian azn hardislife hil',NULL),
('marseydevil',2,'pitchfork daemon hell halloween demon mischievous satan holiday heck evil',NULL),
('marseydickbutt',2,'dickbutt marseybutt meme',1673552822),
('marseydickbuttsmile',2,'dickbutt marseybutt smile meme',1673552867),
('marseydicklet',2,'babydick penis micro dick reaction laugh point and laugh micropenis judgment',NULL),
('marseydiehard',2,'die hard christmas holiday terrorist gun bruce willis',NULL),
('marseydiffusionspin',2,'ai spin animated spinning rotate',1674031604),
('marseydildo',2,'horse',NULL),
('marseydimitri',2,'fireemblem anime weeb nintendo videogame lance spear',1674514487),
('marseydinojihad',2,'dino jihad islam carpathianflorist beard',1668355278),
('marseydinosaur',2,'fursuit furry scalie scaly reptile happy extinct costume',NULL),
('marseydisabled',2,'retarded handicapable handicapped wheelchair crippled',NULL),
('marseydisagree',2,'nah uh nod nuh uh reaction wrong no way no negative animated judgment smh',NULL),
('marseydisconcerting',2,'creepy smile uneasy rapey',NULL),
('marseydiscord',2,'fur furry groomer moderator uwu :3',NULL),
('marseydisguise',2,'nose glasses incognito spying stealth costume',NULL),
('marseydisgust',2,'pissed gross eww angry mad disturbing disturbed yuck',NULL),
('marseydisgustbrian',2,'familyguy familyman  brian disgust groaa',1668386832),
('marseydisintegrate',2,'disappear marvel explode dust thanos snap evaporate crying sad vanish animated snapped',NULL),
('marseydisney',2,'disney fanboy lightsaber consume consoom mickey mouse marvel capeshit',1666379825),
('marseyditto',2,'pokemon weeb anime blob happy',NULL),
('marseyditzy',2,'pokemon',NULL),
('marseydiversity',2,'greatest strength meta carp aevann platy zombiewolf zombie wolf',NULL),
('marseydizzy',2,'puke nausea spinning vomit reaction nauseous sick rolling barf animated',NULL),
('marseydmx',2,'rapper pitbull pit bull pibble dog nigger black',NULL),
('marseydoctor',2,'medic physician white coat stethoscope clipboard checkup diagnosis healthcare',NULL),
('marseydog',2,'puppy doggo fursona skin animal costume dog furry fursuit',NULL),
('marseydoge',2,'doge klenny dog meme shiba inu',1669508138),
('marseydoge1',2,'doge dog puppy meme',1669508109),
('marseydogwalker',2,'doreen antiwork walking powermod moderator',NULL),
('marseydoit',2,'pistol handgun kys kill yourself glowie federal agent fbi cia atf nsa glow nigger glownigger suicide suicidal keep yourself safe',NULL),
('marseydolphin',2,'ocean goggles rainbow',NULL),
('marseydomesticabuse',2,'domestic violence bardfinn foid beating punching battering battered bandage hurt pain woman female',NULL),
('marseydontplay',2,'project pat rapper mixtape pimp',NULL),
('marseydoomer',2,'cigarette smoker despair depression alcoholic suicidal smoking depressing',NULL),
('marseydose',2,'doctor daily dose dailydose animated jump bounce',NULL),
('marseydoubtit',2,'dumpster defender redneck boomer shooting doubt it cocksucker gun',NULL),
('marseydovahkiin',2,'marsey skyrim iron helmet dragon dragonborn dovah dovahkiin',1671044095),
('marseydownvote',2,'downvote negative karma arrow dislike reddit',1664011042),
('marseydownvotemad',2,'downdoot mad angry karma reddit',1670741152),
('marseydracula',2,'halloween fangs cape holiday vampire',NULL),
('marseydragon',2,'smaug rich hoard gold treasure',NULL),
('marseydrama',2,'agendapost where drama seriouspost drama where',NULL),
('marseydramaddictrentfree',2,'drama addict',1672814525),
('marseydramautist',2,'dramautist drama autist trains trans glue retard autism dramatard',NULL),
('marseydrawing1',2,'drawing artist canvas painting recursion recursive',1664490986),
('marseydream',2,'spirals trippy swirls rainbow',NULL),
('marseydrone',2,'obama rotors',NULL),
('marseydrowned',2,'drowned dead marsey',1664998341),
('marseydrownedstare',2,'scary eye stare marsey halloween horror',1666592716),
('marseydrsneks',2,'twolargesnakesmating sneks snake snakes nerd glasses',1666416095),
('marseydrunk',2,'drinking shitfaced alcoholic liquor happy beer dizzy',NULL),
('marseydrunk2',2,'drinking shitfaced alcoholic liquor happy beer dizzy',NULL),
('marseyduck',2,'bird beak',NULL),
('marseyduck2',2,'onesie',NULL),
('marseyduck3',2,'duck bird quack beak',NULL),
('marseyduke',2,':marseyduke:',1675132017),
('marseydukenukem',2,'duke nukem sunglasses chad gun pistol smoking cigar game cool',NULL),
('marseydumptruck',2,'pepe butt mellokind thicc thick ass booty cheeks',NULL),
('marseydunce',2,'stupid moron imbecile dolt dunce retard dumb cap hat sped',NULL),
('marseydunkon',2,'basketball dunk seethe cope rage sports',NULL),
('marseydylan',2,'columbine school shooter psycho gun pistol klebold',NULL),
('marseydylannroof',2,'mayo streetwear dylann roof shooter confederate flag fashion',1665607955),
('marseydynamite',2,'dynomite black afro gun',NULL),
('marseyearrape',2,'breakcore goreshit headphones noisecore',NULL),
('marseyecstatic',2,'ecstatic happy creepy smile',1664490819),
('marseyedelgard',2,'fireemblem anime weeb fantasy nintendo princess',NULL),
('marseyedelgard2',2,'princess fireemblem nintendo anime weeb videogame',1663283895),
('marseyeerie1',2,'eerie excited calico',NULL),
('marseyeerie2',2,'eerie contented calico',NULL),
('marseyeerie3',2,'eerie contented calico yarn knitting troublemaker',NULL),
('marseyeff',2,'free speech eff horn finger electronic frontier foundation',1667448820),
('marseyeggirl',2,'troomer tranny transgender lgbt groomer troid transsexual',NULL),
('marseyeggless',2,'postwall foid woman barren menopause old hag childfree fds',NULL),
('marseyeh',2,'canada canadian leafistan trudeau rake south park ',NULL),
('marseyeldritch',2,'lovecraft horror halloween tentacles holiday scary monster',NULL),
('marseyelephant',2,'oliphant dumbo',NULL),
('marseyelephantcumjar1',2,'semen jizz sperm bukkake cumjar elephant',NULL),
('marseyelephantcumjar2',2,'semen jizz sperm bukkake cumjar elephant',NULL),
('marseyelephantcumjar3',2,'semen jizz sperm bukkake cumjar elephant animated',NULL),
('marseyelliotrodger',2,'er rogers azn asian saint incel hapa shooter killer little king gun shooting',NULL),
('marseyelliotrodger2',2,'saint er rodgers rogers shooter killer incel hapa little king azn asian supremegentleman supreme gentleman',NULL),
('marseyelliotrodger3',2,'saint er rodgers rogers shooter killer incel hapa little king azn asian supremegentleman supreme gentleman',NULL),
('marseyelonmusk',2,'elon musk rocket spacex tesla',NULL),
('marseyelonpaypig',2,'musk tesla twitter cope seethe dilate cry soy wojak south africa paypig blue check',1667784325),
('marseyembrace',2,'embracing hugging love happy',NULL),
('marseyemo',2,'girl goth scene woman foid',NULL),
('marseyemojigrin',2,'emoji reaction grin',NULL),
('marseyemojigrineyes',2,'emoji reaction grin',NULL),
('marseyemojirofl',2,'emoji reaction rofl rotfl rolling laughing',NULL),
('marseyemojismilemouth',2,'emoji reaction smile',NULL),
('marseyemojismilemouthcoldsweat',2,'emoji reaction smile sweat',NULL),
('marseyemojismilemoutheyes',2,'emoji reaction smile',NULL),
('marseyemojismilemouthtighteyes',2,'emoji reaction smile xd',NULL),
('marseyemperor',2,'gold',NULL),
('marseyerasure',2,'erase ignore block',NULL),
('marseyeren',2,'eren anime manga aot attack on titan shingeki no kyojin snk yeagerist racist hitler genocide hajime isayama cute twink hot eldian mappa unamused hoodie jacket',1675197900),
('marseyerenabs',2,'eren anime manga aot attack on titan shingeki no kyojin snk abs buff chad muscles 6pack yeagerist racist hitler genocide hajime isayama cute twink hot eldian mappa unamused',1675198087),
('marseyerenabs2',2,'eren anime manga aot attack on titan shingeki no kyojin snk abs buff chad muscles 6pack yeagerist racist hitler genocide hajime isayama cute twink hot eldian mappa unamused hoodie jacket',1675198030),
('marseyeric',2,'columbine school shooter psycho gun carbine harris',NULL),
('marseyeskimo',2,'inuit native arctic fishing dog helpful ice freeze winter cold',NULL),
('marseyespeon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseyetika',2,'streamer youtuber nft psyops twitter antila trending black suicide bridge llm',NULL),
('marseyeva',2,'anime weeb neon genesis evangelion shinji robot mech japan',1663376836),
('marseyevil',2,'evil bad malicious scary',1674517350),
('marseyevilagent',2,'feds agent glowies usa america waco swat m16 firearm rifle satan demon cops police',NULL),
('marseyevilgrin',2,'joker evil society crazy smirk wicked danger fight trouble',NULL),
('marseyexcited',2,'eager ready hype amped reaction excitement happy thrilled',NULL),
('marseyexcitedblue',2,'excited blue gay',1673627378),
('marseyexciteddance',2,'happy dance excited spin tippytap',1663143559),
('marseyexcitedexosuit',2,'happy smiling mecha rickandmorty robot',1663011866),
('marseyexcitedgreen',2,'excited green gay',1673627289),
('marseyexcitedindigo',2,'excited indigo gay',1673627405),
('marseyexcitedorange',2,'excited orange gay',1673627210),
('marseyexcitedred',2,'excited red gay',1673627165),
('marseyexcitedviolet',2,'excited violet gay',1673627425),
('marseyexcitedyellow',2,'excited yellow gay',1673627229),
('marseyextinction',2,'extinction button women misogyny mayocide kazakhstan',NULL),
('marseyeyelidpulling',2,'frustrated scary horror',NULL),
('marseyeyemixer',2,'mixer stirrer eyes blind selfharm mutilation gore blood gouge',NULL),
('marseyeyemixer2',2,'mixer stirrer eyes blind selfharm mutilation gore blood gouge',NULL),
('marseyeyemixer3',2,'eye mixer animated stirrer blind mutilation gore blood gouge',NULL),
('marseyeyeroll',2,'rolleyes rolling eyes mock animated reaction roll eyes duh',NULL),
('marseyeyeroll2',2,'animated duh rolling eyes',NULL),
('marseyezramiller',2,'flash psycho ezra miller nb nonbinary jewish actor movie',1664416463),
('marseyface',2,'mask psycho face horror halloween kill killer stab knife holiday evil murder scary murderer',NULL),
('marseyfacepalm',2,'reaction omfg judgment',NULL),
('marseyfacepeel',2,'watchpeopledie kitti gore face psycho horror flay',NULL),
('marseyfamily',2,'family guy family man peter griffin griffin peter',NULL),
('marseyfans',2,'of thot taxpayer slut onlyfans whore',NULL),
('marseyfart',2,'brap gas flatulent flatulence farting braphog toot animated',NULL),
('marseyfatherjoseph',2,'christian christmas jesus immaculate god father joseph xmas pray',NULL),
('marseyfattie',2,'brap fatass chonker pig lorg',NULL),
('marseyfbi',2,'cop glownigger fed glowie agent federal',NULL),
('marseyfbiagent',2,'feds fbi agent glowies usa america waco swat m16 firearm rifle cops police',NULL),
('marseyfbicomputer',2,'pepe apu fbi computer peepo glowie fed',NULL),
('marseyfediverse',2,'federation autism freespeech poast',NULL),
('marseyfedora',2,'suit 1920 mobster mafia detective mob',NULL),
('marseyfedoratip',2,'pepe apu peepo fedora tip hat neckbeard weeb mlady knight',NULL),
('marseyfedpost',2,'cia longpost long fed fedpost read notes animated glowie',NULL),
('marseyfedpostglow',2,'cia longpost long fed fedpost read notes animated glowie glow',NULL),
('marseyfedposthmmm',2,'glowie american dad stan meter fbi',NULL),
('marseyfedpostpink',2,'pink cia longpost fed notes animated',NULL),
('marseyfedscared',2,'glowie glownigger federal agent frightened nervous worried panicking fear',NULL),
('marseyfedscared2',2,'glowie glowbipoc federal agent frightened nervous worried panicking fear',NULL),
('marseyfeelsgood',2,'meme frog feels good man pepe feelsgoodman happy',NULL),
('marseyfeelsgoodman',2,'pepe feels good man mellokind frog happy',NULL),
('marseyfeet',2,'foot frozenchosen fetish',NULL),
('marseyfellowkids',2,'groomer adult buscemi skateboard',NULL),
('marseyfellowpedo',2,'libertarian glowie fbi',NULL),
('marseyfemboy',2,'discord trans femboy tomgirl groomer groomed gay faggot homosexual queer poof fairy',NULL),
('marseyfeminist',2,'misandry fds scrotes moids',NULL),
('marseyferret',2,'ferret furry animal fursona weasel',NULL),
('marseyfeynman',2,'history',NULL),
('marseyfighter',2,'final fantasy video game vidya warrior melee',NULL),
('marseyfigureskate',2,'skater iceskate ice skate skating olympics winter on ice',NULL),
('marseyfine',2,'is fine meme thisisfine burning fire',NULL),
('marseyfinger',2,'flipping middle finger bird reaction flicking judgment',NULL),
('marseyfingergoodjob',2,'cute encourage positive respect k-pop thumbs up congrats gif animated congratulations nice ok great',NULL),
('marseyfingerhearts',2,'cute love k-pop',NULL),
('marseyfingerwords',2,'cute long tldr didnt read',NULL),
('marseyflaghongkong',2,'china chink chong asian taiwan island bong colony cantonese xenophobia mainland',1674741576),
('marseyflakes',2,'parsley seasoning salt pepper spice food seasoning',NULL),
('marseyflamethrower',2,'vietname soldier fire',NULL),
('marseyflamewar',2,'troll fight fire reaction gasoline',NULL),
('marseyflareon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseyfloyd',2,'dead blm chauvin fentanyl george',NULL),
('marseyflufflylove',2,'fluffy love hug wholesome',1675219901),
('marseyfluffy',2,'poofy cute shaggy happy smile excited scruffy',NULL),
('marseyfluffyannoyed',2,'angry mad cope seethe dilate cute fur sneed hairy',1674567634),
('marseyflushzoom',2,'flushed eyes bulging shocked surprised flustered waytoodank',NULL),
('marseyflushzoomzoom',2,'blush shy owo uwu heartbeat pound eyes wide meek',1674705033),
('marseyflyingspaghettimonster',2,'atheist atheism flying religon science',1664491405),
('marseyfocault',2,'philosophy history',NULL),
('marseyfoidghost',2,'foid ghost frozenchosen womanundead halloween',1666378137),
('marseyfoidretard',2,'woman blonde stupid dumb idiot froyo frozenchosen',1663161600),
('marseyforevertiedup',2,'fetish bondage autism rope',NULL),
('marseyfortuneteller',2,'fortune teller gypsy predict future clarivoyent crystal jewelry mystic orb witch gypsie medium dead',NULL),
('marseyfoucault',2,'philosophy history foucault postmodern',NULL),
('marseyfox',2,'fursona furry fursuit kitsune',NULL),
('marseyfranklin',2,'franklin thinking constitution founding fathers',NULL),
('marseyfreeman',2,'pearl clutch pc gamer gordon freeman crowbar pcmr half life hl3 valve steam mit theoretical physicist',1674548687),
('marseyfreezepeach',2,'1984 censorship free speech reaction freespeech ruqqus',NULL),
('marseyfrenchvan',2,'foucault pedophilia libertarian van french philosophy pedobear postmodernism',NULL),
('marseyfreud',2,'oedipus incest psychoanalysis psychologist shrink psychiatrist',NULL),
('marseyfrog',2,'scaley fursona furry scalie amphibian fursuit',NULL),
('marseyfrog2',2,'scaley fursona furry scalie amphibian toad fursuit',NULL),
('marseyfrontiersman',2,'america usa 19th history indian native wild nature rural frontier expansion settler',NULL),
('marseyfrozen',2,'dead ice reaction cold frozen',NULL),
('marseyfrozenchosen',2,'blonde girl woman',NULL),
('marseyfrozenlove',2,'mellokind stalker obsessed obsession fixation creepy stalking frozenchosen love hug foid hearts',NULL),
('marseyfry',2,'phillip fry take my money futurama',NULL),
('marseyfrylock',2,'cartoon athf aqua fry fries fastfood',NULL),
('marseyfsjal',2,'fsjal marsey excited cheer watch happening',1668554755),
('marseyfuckoffcarp',2,'reaction carpathianflorist rude snappy animated robot marppy',NULL),
('marseyfuckyou',2,'middlefinger middle finger flipping off fuck you nigga',NULL),
('marseyfuckyou2',2,'nigga comeback no u',NULL),
('marseyfug',2,'benis mustache meme',NULL),
('marseyfugg',2,'spurdo sparde fugg',NULL),
('marseyfugg2',2,'spurdo sparde',NULL),
('marseyfunko',2,'action figure doll funko toy soy',NULL),
('marseyfuntriptime',2,'lsd drugs joy happy gay schizo',1664656681),
('marseyfuriosa',2,'mad max madmax imperator furryosa fury road furyroad post apocalyptic apocalypse australian australia',NULL),
('marseyfurry',2,'fursona furry fursuit kitsune',NULL),
('marseyfurry2',2,'furry fur degenerate sex',NULL),
('marseyfursona',2,'fursuit fox fursona fursecution furfag yiff uwu owo kitsune',NULL),
('marseyfursona2',2,'furry fursona cat devil',1663119051),
('marseyfursonatext',2,'fursuit fox fursona fursecution furfag yiff uwu owo kitsune',NULL),
('marseyfursuit',2,'furry furcon degenerate cosplay fursona costume mascot',1662996039),
('marseygambling',2,'depressed casino slots blackjack las vegas depressed suicidial degenerate smoking losing cards hotep',NULL),
('marseygamer',2,'vidya video games nerd headset microphone',NULL),
('marseygangbang',2,'blacked sex orgy',NULL),
('marseygangster',2,'pimp hustling mafia money gangsta',NULL),
('marseygardener',2,'gardening watering',NULL),
('marseygarfield',2,'mondays lasagna',NULL),
('marseygarfieldpipe',2,'marfield pipe smoking john yelling comic smoke',NULL),
('marseygas',2,'holocaust zyklon fart poison brap barf smell tremble dead genocide animated jews jewish',1672048667),
('marseygasp',2,'wow woah what how why whoa reaction appalled',NULL),
('marseygeisha',2,'foid birthing person girl woman girl lady slut thot noodlewhore chink jap gook asian azn blow kiss blowing kiss blowkiss love heart stockings nylons fishnets',NULL),
('marseygenetakovic',2,'bcs better call saul breaking bad disguise cinnabon gene',1664491944),
('marseyghost',2,'spooky halloween costume holiday scary sheet',NULL),
('marseyghost2',2,'ghost spectre phantom spook boo halloween horror spirit',1668205908),
('marseyghostangry',2,'ghost specter phantom spook boo angry halloween horror spirit',1668205996),
('marseyghostangry2',2,'ghost specter phantom spook boo angry halloween horror spirit pissed',1668206083),
('marseyghostbored',2,'ghost specter phantom spook halloween horror spirit boo bored unimpressed',1668206116),
('marseyghostface',2,'ghostface scary halloween horror scream knife killer',1666281841),
('marseyghostface2',2,'ghostface scary scream wassup horror halloween phone',1666295002),
('marseyghosthappy',2,'ghost specter phantom spook halloween horror spirit boo happy proud content',1668206327),
('marseyghostkiss',2,'ghost specter phantom spook boo mwah kiss smooch halloween horror spirit',1668206390),
('marseyghostlaugh',2,'ghost specter phantom spook boo laugh xd halloween horror spirit',1668206044),
('marseyghostsad',2,'ghost specter phantom spook boo halloween horror spirit sad upset miss',1668206267),
('marseyghostshy',2,'ghost specter phantom spook boo shy uwu halloween horror spirit',1668206211),
('marseygift',2,'present christmas wrapping paper holiday',NULL),
('marseygiftboxmarsey',2,'christmas holiday present kitten child mother mom',1672182415),
('marseygiftboxmarseyhug',2,'christmas holiday present kitten child mother mom love',1672182559),
('marseygigachad',2,'reaction hunter eyes canthal tilt jawline',NULL),
('marseygiganoyou',2,'accuse spin snake point finger horseshoe nou animated',1671368538),
('marseygigaretard',2,'idiot neurodivergent dumb stupid drooling moron puddle',NULL),
('marseygigathonk',2,'3d hmm wrong think cube spin consider animated noootice wonder',1673988383),
('marseygigatitty',2,'teacher tits boobs nipples canadian transgender milkers',1663596620),
('marseygigavaxxer',2,'covid vaccine coronavirus vaccination',NULL),
('marseygilead',2,'handmaid tale abortion patriarchy feminist moid scrote sex incel misogyny',NULL),
('marseygingerbread',2,'cookie christmas holiday',NULL),
('marseygingerbread2',2,'cookie christmas holiday',NULL),
('marseygingerbread3',2,'cookie christmas holiday',NULL),
('marseygirl',2,'dress toddler tween sister horror shining',NULL),
('marseygivecrown',2,'king based swole reaction muscles',NULL),
('marseygiveup',2,'despair reaction depression miserable fall over depressed falling over animated sad',NULL),
('marseygiygas',2,'giygas halloween earthbound horror alien boss vidya game video',1666512009),
('marseyglaceon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseygladiator',2,'gladiator rome ancient historical warrior sword athlete combat fight',NULL),
('marseyglam',2,'rocker pretty glamorous beautiful',NULL),
('marseyglancing',2,'eyes animated nervous paranoid',NULL),
('marseyglobohomo',2,'globalism soulless modernity art corporate corporation',NULL),
('marseyglow',2,'fbi mossad cop feds animated glownigger glowie secret service fed atf police cia nsa kgb',NULL),
('marseyglow2',2,'fbi mossad feds agent glownigger reaction glowie fed atf cia nsa',NULL),
('marseyglowaward',2,'medal fbi ribbon animated glownigger retard glowie fed atf cia nsa',NULL),
('marseygoatse',2,'shock bussy troll',1664223119),
('marseygodel',2,'old philosophy glasses history',NULL),
('marseygodfather',2,'wop italy italian dego mafia',NULL),
('marseygodzilla',2,'raptor halloween dinosaur gojira evil bug',NULL),
('marseygold',2,'gold award reddit',NULL),
('marseygolden',2,'lucky money rich gold shine coin merchant animated ',NULL),
('marseygolden2',2,'lucky money rich gold shine coin merchant 3dp spin animated ',NULL),
('marseygondola',2,'mustache meme long legs',NULL),
('marseygoodmap',2,'map pedo dead shoot animated shotgun buckshot kill minor libertarian',NULL),
('marseygoodnight',2,'kazakhstan flag reaction kazakh i hate women women',NULL),
('marseygoose',2,'goose geese kill duck cat bird death bite chomp',NULL),
('marseygoose2',2,'goose geese kill cat bird death bite chomp',NULL),
('marseygorilla',2,'gorilla monkey ape',1673959220),
('marseygossip',2,'tea rotary phone popcorn gabbing',NULL),
('marseygrad',2,'graduate graduation school degree diploma hat tassel animated college university',NULL),
('marseygraduation',2,'kanye graduation yeezy yeezus',1671531171),
('marseygrapes',2,'fat roman emperor fruit chubby snacking healthy',1664677557),
('marseygras',2,'mardi gras fat tuesday nola new orleans neworleans holiday louisiana mardigras carnival beads mask',NULL),
('marseygrass',2,'reaction outside touchgrass touch grass',NULL),
('marseygravedance',2,'tombstone graveyard excited ripbozo dead die smug step stomp headstone animated',1667683376),
('marseygreatpumpkin',2,'great pumpkin trick or treat charlie brown ghost costume halloween homoween rock',1666634608),
('marseygrilling',2,'barbecue bbq centrist boomer barbeque',NULL),
('marseygrilling2',2,'bbq boomer barbecue barbeque',NULL),
('marseygrimreaper',2,'grimreaper grim reaper scythe homoween skull scary horror death',1666468259),
('marseygrin',2,'seethe pain rage beard angry',NULL),
('marseygroomer',2,'pedobear discord pedophile pedo chomo molest pedocord',NULL),
('marseygroomer2',2,'molest discord chomo snoo pedo pedocord reddit',NULL),
('marseygrouns',2,'grounds grounz darrell brooks court lawyer waukesha',1665524778),
('marseygucci',2,'gucci mane lean rapper trap mixtape bricksquad traphouse codeine lean rapper pimp',NULL),
('marseyguillotine',2,'cut head off beheading beheaded headless french robespierre marie antoinette death die kill execution execute',NULL),
('marseygun',2,'handgun shoot bang kill threaten pistol',NULL),
('marseygundam',2,'mecha robot helmet mask anime',NULL),
('marseygunnut',2,'ahegao 2a second amendment rifle horny lust lick tongue shooter shooting',NULL),
('marseygunshotsuicide',2,'gun shoot suicide sad depressed animated dead death kms gunshot die suicidal',NULL),
('marseygunsuicide',2,'shotgun kill death die gunshot windy kms animated',NULL),
('marseyhacker',2,'nerd matrix reaction computer animated',NULL),
('marseyhacker2',2,'dox anonymous computer',NULL),
('marseyhammerpizza',2,'animated beat bongo hammers pizzashill rdrama',NULL),
('marseyhammersnoo',2,'snoo redditor spez beat powermod murder kill death animated blood',NULL),
('marseyhammersrdine',2,'animated beat bongo hammers sardine redditors can the',NULL),
('marseyhandmaid',2,'handmaid maiden dystopia theocracy sexist sexism misogyny abortion feminism',NULL),
('marseyhandsup',2,'hands up pawsup arrested arresting reaction paws up under arrest',NULL),
('marseyhanger',2,'abortion fetus coat planned parenthood infanticide childfree murder foid',NULL),
('marseyhankhill',2,'cartoon propane hank grill kingofthehill',NULL),
('marseyhankhill2',2,'propane cartoon hank grill kingofthehill',NULL),
('marseyhannibal',2,'flesh psycho horror halloween cannibal eat holiday',NULL),
('marseyhappening',2,'ronpaul happening it ron paul itshappening animated',NULL),
('marseyhappy',2,'pleased contented reaction contentment satisfied',NULL),
('marseyhappy2',2,'smile smiling nice',1670511565),
('marseyhappytears',2,'tears of joy crying',NULL),
('marseyhatecrime',2,'jussie smollett racist homophobic hoax rope bleach chlorine maga hat suicide lynch juicy',1663695493),
('marseyhatium',2,'mad fury furious pissed hatred rage angry maddened infuriated hateful hatefuel',NULL),
('marseyhawaii',2,'boomer margarita drink chill relaxed',NULL),
('marseyhead',2,'blood spurting headless horror halloween animated',NULL),
('marseyheadcrab',2,'zombie brain alien parasite valve game half life',1663640300),
('marseyheadlesshorseman',2,'halloween headless horseman icabod',1666364356),
('marseyhealthy',2,'burger king fat fast food crown unhealthy junk food american',NULL),
('marseyhearts',2,'reaction flirt loving adoration love happy cute crush',NULL),
('marseyheathcliff',2,'heathecliff',NULL),
('marseyheavymetal',2,'rocker musician rock guitar',NULL),
('marseyhehe',2,'hehe nothehe happy laughing angry questioning',NULL),
('marseyhelium',2,'helium copium cope mask',1673132964),
('marseyhellraiser',2,'pinhead halloween holiday evil monster',NULL),
('marseyhelp',2,'wtf nervous anxious anxiety worried concerned helpme help me uncomfortable awkward',NULL),
('marseyhesklennyyouknow',2,'klenvastergan corgi morgan freeman right correct point',1664490676),
('marseyhesright',2,'batman lucius fox nolan hes right you know reaction agree thumbs up based morgan freeman correct',NULL),
('marseyhibernian',2,'hibernian irish leprechaun blarney guinness shamrock clover luck merchant papist ira hat',NULL),
('marseyhijab',2,'hijab reading islam jihad muslim allah quran koran',NULL),
('marseyhillary',2,'president her turn hilary killary hilldawg clinton',NULL),
('marseyhillarybackstab',2,'clinton hilary arkanicide knife stabbing kill murder seth rich death',NULL),
('marseyhippo',2,'hippopotamus hippo fursona furry skin animal costume fursuit',NULL),
('marseyhissing',2,'hiss angry threatened threatening fangs mouth',1674518233),
('marseyhitler',2,'adolf adolph nazi germany kraut axis mustache genocide dictator authright chud conservative trump gas',NULL),
('marseyhitler2',2,'adolf adolph nazi germany kraut axis mustache genocide dictator authright chud conservative trump',NULL),
('marseyhmm',2,'confused reaction thinking thunk thonk judgment',NULL),
('marseyhmmm',2,'confused reaction thinking thunk thonk judgment',NULL),
('marseyhobbes',2,'calvin hobbes waterson tiger comic',1669097969),
('marseyholocaust',2,'jew nazi adl merchant genocide chud rightoid hitler train auschwitz 109',1669064577),
('marseyhomestar',2,'homestar runner fast everybody 2000s',NULL),
('marseyhomochingchong',2,'asian chinese jap gook chink rice gay strawhat  glasses squint rainbow tiedie tyedye tyedie tiedye',1663248780),
('marseyhomofascist',2,'lgbt faggot ss fash nazi homocracy gay queer sodomy wholesome kiss',NULL),
('marseyhomosupremacist',2,'klan lgbt faggot kkk homocracy sodomy queer gay wholesome',NULL),
('marseyhomsar',2,'homsar homestar rslur retard dumb loud shout 2000s',NULL),
('marseyhoodwink',2,'cloak crossbow',NULL),
('marseyhope',2,'mask whitepill reaction happy hopium',NULL),
('marseyhorseshoe',2,'rightoid leftoid theory',NULL),
('marseyhotep',2,'party meme parrot vibing jam dance',NULL),
('marseyhrt',2,'hrt estrogen trans egg',1671534341),
('marseyhugjew',2,'hug jewish marsey kike yid yarmulke love',1668612377),
('marseyhugmerchant',2,'marsey hug jewish merchant kike yid yarmulke love',1668612408),
('marseyhugpeepeehands',2,'love cute heart embrace cat',1672265079),
('marseyhugretard',2,'love idiot drool embrace',NULL),
('marseyhungry',2,'food hunger dish feed me bowl animated',NULL),
('marseyhwacha',2,'korea historical animated artillery weapon gunpowder army combat war',NULL),
('marseyhyperthonk',2,'3d hmm wrong think hypercube animated tesseract spin consider noootice wonder',1673988441),
('marseyhypno',2,'hypnosis spiral brainwash animated hypnotoad',NULL),
('marseyicecream',2,'ice cream sad disappoint pout cry.',NULL),
('marseyicecreamcone',2,'sweet dessert dairy',1663284406),
('marseyicet',2,'marsey icet rapper',1666753447),
('marseyidio3',2,'idio3 russia belarus communist commie flask drink computer online monitor display keyboard idio',NULL),
('marseyidio3rentfree',2,'idio3 commie communist comrade chud janny',1670888860),
('marseyidk',2,'what weird cringe',1665254242),
('marseyiff',2,'math alphabet',1666976642),
('marseyill',2,'winter chilly cold ill sick brr flu',NULL),
('marseyilluminati',2,'eye egypt pyramid big brother watching',NULL),
('marseyilluminati2',2,'eye egypt pyramid big brother watching',NULL),
('marseyimam',2,'muslim islam saudi ghutra keffiyah kufiya emiratis arab',NULL),
('marseyimmaculate',2,'christian christmas jesus immaculate god mother mary xmas pray',NULL),
('marseyimmortanjoe',2,'immortansey mad max madmax fury road furyroad post apocalyptic apocalypse australian australia',NULL),
('marseyimpossibru',2,'revulsion gross yuck yikes mad icky impossible disgusted disgusting',NULL),
('marseyimposter',2,'amogus baka among us sussy',NULL),
('marseyinabox',2,'hiding hide box cardboard happy cute',NULL),
('marseyinacumbox',2,'cum box cumbox cute wholesome',1673632724),
('marseyinajackolantern',2,'halloween homoween pumpkin jackolantern stripper cake',1666671664),
('marseyinapumpkin',2,'halloween homoween pumpkin jackolantern',1666671730),
('marseyinbread',2,'food meme inbred',NULL),
('marseyindignant',2,'hmph pout indignant angry annoyed no cross',1672174676),
('marseyinnocent',2,'innocent naive angelic dumb halo',NULL),
('marseyinshallah',2,'begging muslim animated please',NULL),
('marseyinsurgent',2,'insurgency iraq jaish gun mask balaclava iraqi',1674032658),
('marseyinverted',2,'inverted marsey black',1664594376),
('marseyinvestigate',2,'pepe apu peepo investigate magnifying magnifier look lookup',NULL),
('marseyinvisible',2,'stealth',NULL),
('marseyira',2,'car bomb irish ireland',NULL),
('marseyironmaiden',2,'death blood torture chika anime weeb weeaboo spikes murder crush animated',NULL),
('marseyishygddt',2,'reaction meme disapproval bat club beating angry demented disgust dislike baseball bat shiggy diggy george costanza',NULL),
('marseyisis',2,'daesh terrorist islam muslim',NULL),
('marseyisrael',2,'kike yid jewish hebrew merchant colonizer israeli banker',NULL),
('marseyisraellove',2,'love ally israel holocaust zionism',NULL),
('marseyit',2,'balloon halloween pennywise clown holiday evil',NULL),
('marseyitsallsotiresome',2,'empire of dust tooka all so tiresome chinese racist congolese drc kinshasa lubumbashi enough bullshit tired resigned despair black',1665543793),
('marseyitsaover',2,'vidya mario over italian',1670561567),
('marseyitsover',2,'its over never began incels give up giveup sad sigh defeated',NULL),
('marseyitsoverhappy',2,'marsey over itsover happy',1673551303),
('marseyitsoverwereback',2,'itsover neverbegan incels give up giveup sad sigh defeated yay happy excited undefeated bipolar histronic null kiwifarms animated',1668780621),
('marseyitsoverwerebackchingchon',2,'happy doomer elated joy asian gook nip jap recovery slit squint rice',1674907207),
('marseyitsrigged',2,'its rigged rig goomble gamble lottershe election dating test blackjack roulette',1670094672),
('marseyjackskellington',2,'skeleton nightmarebeforechristmas halloween horror burton',1667696881),
('marseyjackson',2,'music king pop mayo whiteface michael',NULL),
('marseyjacksparrow',2,'johnny depp amber heard abuse violence punch beat feminist Jack sparrow',NULL),
('marseyjaguarwarrior',2,'mayan incan injun latinx aztec native blood fight mexican',NULL),
('marseyjam',2,'animated bopping excited trippy excitement tejanx dancing rainbow rave happy dance',NULL),
('marseyjamesholmes',2,'killer shooter shooting crazy schizo batman capeshit ginger',NULL),
('marseyjamming',2,'mp3 headphones beat ipod music happy',NULL),
('marseyjanny',2,'jannie unpaid volunteer administrator janitor free moderator',NULL),
('marseyjanny2',2,'jannie unpaid volunteer administrator janitor free moderator',NULL),
('marseyjannymini',2,'janny minigun gun clean gatling jannie animated',1664657815),
('marseyjapanese',2,'nippon rising sun weeb japan animated',NULL),
('marseyjason',2,'hockey mask horror halloween kill fridaythe13th knife stab voorheys friday the 13th evil monster holiday',NULL),
('marseyjavelin',2,'ukraine russia missile rocket rpg grenade launcher kyiv kiev kiyv zelensky putin tank',NULL),
('marseyjcdenton',2,'sunglasses shades vidya video game deusex deus ex',NULL),
('marseyjclove',2,'astolfo femboy trap hug anime jc justcool',1668572373),
('marseyjcrentfree',2,'trans astolfo marstolfo justcool bard moderator jannie',1667322028),
('marseyjeans',2,'denim trousers pants',NULL),
('marseyjesus',2,'christian',NULL),
('marseyjesus2',2,'crucify crucifixion christianity easter persecuted religion saint martyr religious cross',NULL),
('marseyjetbombing',2,'obama bush animated usa animated american pilot bomber plane war usaf air force',NULL),
('marseyjetfighter',2,'pilot plane airforce air force usaf bomber dogfight war',NULL),
('marseyjewish',2,'jew jewish religon hat yarmulke yid kike sheeny sheenie heeb merchant israeli',1665706842),
('marseyjewishkkk',2,'klan israel racism hood blue',1664491568),
('marseyjewoftheorient',2,'china chinese greedy jew jewish merchant',NULL),
('marseyjewoftheorientglow',2,'animated glow rice china chinese chink commie mao xi',NULL),
('marseyjfk',2,'john fitzgerald kennedy jfk president american history sniper car death kill usa assassination',NULL),
('marseyjiangshi',2,'ghost chinese halloween holiday china scary',NULL),
('marseyjihad',2,'jihad islam animated mujahideen muslim terrorism terrorist plotting isis',1672275222),
('marseyjoe',2,'family guy swanson cop police wheelchair retard disabled',1671089479),
('marseyjohnson',2,'wig history founding father wtf did just read bruh wut',NULL),
('marseyjoint',2,'smoke weed marijuana reefer drugs smoking 420 pot',NULL),
('marseyjolteon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseyjones',2,'tinfoil animated alex gay frogs conspiracy',NULL),
('marseyjoseon',2,'korean hat azn asian',NULL),
('marseyjourno',2,'journoid media press photo camera journalist pic',NULL),
('marseyjoy',2,'smile excited smug',NULL),
('marseyjudge',2,'objection innocent hammer guilty gavel court overruled sustained',NULL),
('marseyjumpscare',2,'undead living dead romero halloween horror corpse scary rotten animated spooky aaaahhhhh trick prank bait and switch',NULL),
('marseyjunkie',2,'needles heroin reaction shooting up addicted shoot up syringe',NULL),
('marseyjunkie2',2,'addicted drugs pills glue huffing ether overdose',NULL),
('marseyjurisdiction',2,'waukesha darrell brooks court subject matter jurisdiction',1665785047),
('marseyjustright',2,'reaction snob no way',NULL),
('marseykaiser',2,'prussian history wwi rifle reich wilhelm germany soldier',NULL),
('marseykamikaze',2,'kamikaze japanese nip pilot ww2 wwii world war',NULL),
('marseykatamarireddit',2,'rolling animated vidya video game damaci damacy reddit',NULL),
('marseykeffalsdance',2,'onesie pajamas animated fursuit hood wiggler',NULL),
('marseykente',2,'black blm nigger nog jogger coon dindu bhm hotep kufi african tribal',NULL),
('marseykermit',2,'kermit green frog puppet absinthe television sesame children',NULL),
('marseykernelpanic',2,'linux kernel panic computer error glitch',NULL),
('marseykevin',2,'marsey hat drseuss dark black halloween horror',1666487566),
('marseykfc',2,'col sanders colonel kentucky fried chicken',NULL),
('marseykhorne',2,'warhammer 40k chaos god war death blood',NULL),
('marseykindness',2,'retarded special drooling idiot seriouspost srspost agendapost moron fool buffoon dramatard',NULL),
('marseyking',2,'based queen prince reaction crown princess',NULL),
('marseykingcrown',2,'based animated',NULL),
('marseykingretard',2,'drool dumb idiot crown moron',NULL),
('marseykink',2,'bdsm sex kinkster dom pervert sub creeper latex fetish dildo pvc',NULL),
('marseykino',2,'kino agni fire punch anime',NULL),
('marseykirby',2,'nintendo video game vidya sprite fat chonker suck succ',NULL),
('marseykirby2',2,'kirby game nintendo video vidya',NULL),
('marseykissinger',2,'kissinger coldwar war diplomat suit fat america geopolitics politics historical',NULL),
('marseykitti',2,'watchpeopledie horror grim evil scary surreal tattoos wicked demonic',NULL),
('marseykitty',2,'hellokitty animated hello kitty',NULL),
('marseykiwi',2,'kf bird new zealand kiwifarms newzealand',NULL),
('marseykiwi2',2,'kf bird new zealand kiwifarms newzealand',NULL),
('marseykiwilove',2,'hugging bird happy',1670511827),
('marseykiwimom',2,'kf farms newzealand new zealand dramarama birds babies chicks single mother brood flock',NULL),
('marseykiwivampire',2,'kiwi new zealand dramarama house scary spooky bird cloak sanguine fangs halloween bloodsucker',NULL),
('marseykkk',2,'klan kukluxklan ku klux klan racist costume klux ku sheet',NULL),
('marseykkkblm',2,'ku klux klan racist nigger jogger coon jiggaboo cracker crackkka',NULL),
('marseykkkevil',2,'kukluxklan racism racist lasereyes evil',1663211985),
('marseyklenny',2,'chiobu jenna thorne grunderchin vidunderchin clapping applause animated',NULL),
('marseyklenny2',2,'corgi dog puppy klenvastergan smile happy',NULL),
('marseyklenny3',2,'puppy corgi smile dog grunderchin klenvastergan',NULL),
('marseyklennyclap',2,'klenny klenvastergan animated corgi dog clap clapping',NULL),
('marseyklennyheart',2,'corgi puppy dog love hug',1673925667),
('marseyklennywinner',2,'medal award dog klenvastergan corgi',NULL),
('marseykneel',2,'blm bow black lives matter chauvin supremacy respect supreme',NULL),
('marseykoalalove',2,'eucalyptus bear',1664497197),
('marseykoolaid',2,'oh yeah juice cult ice pitcher drink',NULL),
('marseykrampus',2,'demon monster christmas',NULL),
('marseykrampus2',2,'demon monster christmas',NULL),
('marseykrayon',2,'krayon karaboga incel retard face',1669868564),
('marseykrayongrouns',2,'grouns krayon objection court brooks sister pedo molester incest',1672604810),
('marseykrayonsneed',2,'krayon incest carpathianflorist sistertoucher sneed',1673039108),
('marseykrishna',2,'hindu krishna india peacock',1667156631),
('marseyksg',2,'kanye ksg kids see ghosts yeezy yeezus',1671533131),
('marseykvlt',2,'horgh abbath black metal krieg bullet belt immortal corpsepaint',NULL),
('marseykwanza',2,'christmas black kwanza african holidays',NULL),
('marseykween',2,'hoop earring fds black shaniqua',NULL),
('marseykweenxmas',2,'blm black christmas santa bipoc nigger bame hat holiday',NULL),
('marseykyle',2,'killer konvict rifle rittenhouse kid gun kenosha kylie',NULL),
('marseykylerentfree',2,'rittenhouse chud rightoid killer gun rights kenosha wisconsin shoot 2a',1669680590),
('marseykys',2,'reaction keep yourself safe kill yourself suicide',NULL),
('marseykys2',2,'keep yourself safe',NULL),
('marseyl',2,'loser loss',NULL),
('marseylain',2,'bear onesie pajamas fursuit furry',NULL),
('marseylaptop',2,'notebook macbook computer',NULL),
('marseylaptopangry',2,'mad frustrated seethe computer laptop',1671429907),
('marseylaptopangry2',2,'mad frustrated seethe computer tears crying',1671439109),
('marseylaptopkrayon',2,'angry mad seethe computer hoodie',1671430470),
('marseylaptopkrayon2',2,'angry mad seethe computer hoodie',1671430514),
('marseylaptoppizzashill',2,'angry mad seethe computer laptop',1671430383),
('marseylaptoppizzashill2',2,'angry mad seethe computer laptop',1671430414),
('marseylaptopsad',2,'computer tears crying upset',1671502473),
('marseylaptopsad2',2,'computer tears crying sobbing upset',1671508897),
('marseylaugh',2,'lmao reaction point funny haha lol judgment',NULL),
('marseylaughbothsides',2,'wingcuck radical centrist centrism animated horseshoe',NULL),
('marseylaughpoundfist',2,'cry tears lmao lol kek bully laughing funny mocking animated',NULL),
('marseylaughwith',2,'cry tears lol lmao haha laughing',NULL),
('marseylawlz',2,'masterlawls zhcyid9 masterlawlz reaction glasses',NULL),
('marseyleafeon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseyleftoidschizo',2,'sjw shitlib radlib liberal cuck redditor soy crazy animated',NULL),
('marseylegion',2,'zombie wolf fallout new vegas fnv caesar courier video game roman',NULL),
('marseylego',2,'marsey lego toy game blurry lowres lowdef',1665356921),
('marseylemon',2,'pucker sour lemon fruit citrus tear ',NULL),
('marseylenin',2,'ussr russia communism socialism marxist commie soviet proletariat marxism marxist leninist leninism revolution bolshevik',NULL),
('marseylenny',2,'innuendo dirty sex horny emoticon perverted',NULL),
('marseyletsfuckinggo',2,'lfg tennis ball screaming ready',NULL),
('marseyletsfuckinggo2',2,'hyped screaming shouting yelling',1663161484),
('marseylgbtflag',2,'pride gay queer',NULL),
('marseylgbtflag2',2,'pride gay inclusive queer ukraine bipoc',NULL),
('marseylgbtflag3',2,'pride gay rainbow queer',NULL),
('marseylgbtflag4',2,'pride gay queer homo rainbow',1673666833),
('marseylgbtflag5',2,'pride gay queer homo rainbow inclusive progress intersex trans bipoc ukraine nonbinary',1673666925),
('marseyliathomas',2,'tranny transgender athlete lia thomas athletics woman valid lgbt swimmer aquamaam aqua maam',NULL),
('marseylibations',2,'libations pour one out dead homie',1674828962),
('marseyliberty',2,'usa burger america statue lady republican democrat biden trump rightoid leftoid',NULL),
('marseyliberty2',2,'usa burger america statue lady republican democrat biden trump rightoid leftoid',NULL),
('marseylibertyfireworks',2,'independence forth july america usa eagle republican democrat united states patriot statue animated',1664123152),
('marseylibleft',2,'unemployed protest riot anarcho capitalist antifa anarchist anarchy',NULL),
('marseylibright',2,'libertarian anarcho wagecuck pedophile capitalist lolbert',NULL),
('marseylicking',2,'spongebob tongue taste',1663284181),
('marseylickinglips',2,'yummy tasty delicious',NULL),
('marseylifting',2,'workout muscular work out bench swole working out gains benchpress weightlifting weights muscles',NULL),
('marseylion',2,'fursona furry fursuit leo george mountain spokane feed trailerparkbride',NULL),
('marseyliondance',2,'parade ccp chinese dancer dancing asian china animated',NULL),
('marseyliquidator',2,'gas mask horror exterminator halloween plague doctor holiday scary nuclear chernobyl suit mask radiation radioactive',NULL),
('marseylizard',2,'reptilian',NULL),
('marseyllama',2,'alpaca',NULL),
('marseyllama1',2,'top',NULL),
('marseyllama2',2,'middle',NULL),
('marseyllama3',2,'bottom',NULL),
('marseyloading',2,'animated loading spinner webdev rolling ball circle',NULL),
('marseyloadingneon',2,'animated loading spinner webdev rolling ball circle neon',NULL),
('marseyloaf',2,'marsey loaf bread lazy retard tard',1663803130),
('marseylobotomy',2,'surgery retard braindead sad',1667212108),
('marseylois',2,'familyguy familyman family guy family man peter griffin',NULL),
('marseylolcow',2,'reaction trolled lulz judgment',NULL),
('marseylolly',2,'animalcrossing vidya videogame',1670512415),
('marseylong1',2,'top meme',NULL),
('marseylong2',2,'middle meme',NULL),
('marseylong3',2,'bottom meme',NULL),
('marseylonghorn',2,'texas bevo college football horns sports',1663872538),
('marseylongpost',2,'tldr reaction wall of text wordswordswords animated words',NULL),
('marseylongpost2',2,'tldr reaction wall of text scrolling wordswordswords animated words judgment',NULL),
('marseylongpostglow',2,'animated pippy glow fedpost longpost words mad angry rage wtf green chud fbi mossad fed atf police reaction scrolling',NULL),
('marseylongsurfing',2,'surf surfing water ocean long surfboard',NULL),
('marseyloss',2,'isthis meme comic webcomic hospital ethan tim buckley',1663284338),
('marseylouisiana',2,'state cajun usa map crawfish southern gulf poverty mississippi orleans mardi gras',1665955191),
('marseylove',2,'heart reaction adoration loving adore',NULL),
('marseylovecraft',2,'eldritch horror niggerman cat hp tentacle insane halloween',NULL),
('marseylovecraft2',2,'eldritch horror niggerman cat hp tentacle insane halloween',NULL),
('marseylovecraftian',2,'cosmic horror eldritch galaxy space hp spooky scary halloween animated',NULL),
('marseylovedrama',2,'hearts rdrama reaction happy animated',NULL),
('marseylovegigaorgy',2,'cuddle hug love blush wholesome infinity orgy',1664491045),
('marseyloveyou',2,'hearts ilu reaction adoration loving ily love adore animated',NULL),
('marseylowpoly',2,'polygonal spinning 3d lopoly animated',NULL),
('marseyluckycat',2,'lucky fortune gambling gambler goombler goombling animated weeb azn asian slots japanese money cash coin rich',NULL),
('marseylueshi',2,'super mario nintendo snes retro vidya dinosaur italian plumber pipes 42',1664142051),
('marseylumberjack',2,'axe bloody horror murder satisfied worker',1673123024),
('marseyluther',2,'heretic lutheran theses martin luther',NULL),
('marseymacarthur',2,'nuke missile nuclear bomb history',NULL),
('marseymad',2,'pissed annoyed furious reaction angry irritated livid',NULL),
('marseymadbrian',2,'familyguy familyman brian mad',1668386676),
('marseymagahat',2,'trump 5200 maga american president election vote nazi hat',NULL),
('marseymagarentfree',2,'cope seethe dilate lib snoo reddit orange drumpf bad nazi hitler rightoid leftoid',1664439482),
('marseymaid',2,'canadian leaf suicide euthanasia needle syringe vax',1670432525),
('marseymaid2',2,'canadian leaf suicide euthanasia needle syringe vax',1670432554),
('marseymaid3',2,'canadian leaf suicide euthanasia needle syringe vax',1670432568),
('marseymaid4',2,'canadian leaf suicide euthanasia needle syringe vax',1670432579),
('marseymaidchingchong',2,'suicide rope kys die inject medicine vaccine canada leaf chinese rice asian cosplay',1673653490),
('marseymaidgeisha',2,'weeb incel asian chink chong rice suicide vax inject wink love heart kiss slit cosplay',1674149640),
('marseymaidshy',2,'canada suicide kys cute blush nervous leaf canadian',1670556516),
('marseymajorgeneral',2,'jeffthespammer pirates of penzance safari muttonchops mutton chops army military soldier officer',NULL),
('marseymalding',2,'dilate seethe scrote mad moid cope',NULL),
('marseymancer',2,'dead undead horror lich halloween necromancer zombies zombie holiday evil',NULL),
('marseymandela',2,'fat grapes eating mandela fruit cornucopia conspiracy schizo timeline',1673162308),
('marseymanifestdestiny',2,'manifest usa american imperialism history expansion territory exploration',1664172279),
('marseymanlet',2,'llm short midget dwarf little king',NULL),
('marseymanysuchcases',2,'animated many such cases airport luggage suitcase conveyor',NULL),
('marseymanysunglasses',2,'shook shock disbelief seamless animated',1674161474),
('marseymao',2,'zedong ccp chinese communist communism china',NULL),
('marseymaoist',2,'marxist little red book marxism ccp chinese communist authleft maoism communism china',NULL),
('marseymap',2,'libertarian libertarian map predator',NULL),
('marseymap2',2,'map geography topographical paper navigation chart cartography location place',NULL),
('marseymar',2,'dexter lab foid destruction irritating annoying sister cartoon network pigtails',NULL),
('marseymarch',2,'retard groyper march fat pepe drool hallway',1668385912),
('marseymariachi',2,'animated latinx latino mexican mexico beaner taco burrito',NULL),
('marseymars',2,'celestial space planet galaxy world solar system alien',NULL),
('marseymarseylove',2,'aww blush hugging cuddling cuddle snuggle snuggling hearts shy kiss xoxo',NULL),
('marseymarseylovelove',2,'reaction love blush aww hugging cuddling cuddle snuggle snuggling hearts xoxo nested recursion inception wholesome',NULL),
('marseymarseyloveorgy',2,'reaction love blush aww hugging cuddling cuddle snuggle snuggling hearts xoxo nested recursion inception orgy group',NULL),
('marseymask',2,'plague coronavirus covid pandemic coof sickness love heart eyes illness',NULL),
('marseymasterchief',2,'master chief halo game',NULL),
('marseymati',2,'annoyed irritation top hat reaction angry irritated tophat',NULL),
('marseymaxrockatansky',2,'mad max madmax fury road furyroad post apocalyptic apocalypse australian australia',NULL),
('marseymayo',2,'yt jakubian crying cracker reaction crackkka crakkka white sad tears',NULL),
('marseymayocide',2,'genocide white animated supremacy kkk spin racist',1671356143),
('marseymayoface',2,'black blackface whiteface mayo mayocide mayonnaise racist racism',NULL),
('marseymayoparty',2,'bukakke bukkake mayonaise mayonnaise cum semen jizz spunk nut sperm messy sloppy lewd facial cumshot',NULL),
('marseymayu',2,'idolmaster anime animegirl ribbon',1667211868),
('marseymeangirls',2,'rdrama chud gossip rumour talk snoo train retard group friends',1671559341),
('marseymeatwad',2,'cartoon athf aqua hamburger',NULL),
('marseymechanic',2,'wrench car diy fix repairman dipfuck',NULL),
('marseymeds',2,'mentally ill rightoid doctor psycho crazy mental illness reaction risperidone schizo nurse',NULL),
('marseymedusa',2,'medusa snakes greece greek mythology ancient monster perseus gorgon',NULL),
('marseymegalodon',2,'shark carpathianflorist jaws attack eating killing',NULL),
('marseymemeball',2,'picardia strawman polcomp political',NULL),
('marseymeowth',2,'pokemon weeb anime manga team rocket nintendo video game vidya monster',NULL),
('marseymerchant',2,'kike hebrew shopkeeper yid banker jew moneylender jewish greedy israel chosen',NULL),
('marseymerchantelf',2,'jew christmas elf santa greedy money chosen worker holiday xmas seth rogen sarah silverman holocaust coin kike',NULL),
('marseymerchantsoy',2,'merchant jewish kike greed soy wojak soyjak yarmulke soyyell',NULL),
('marseymermaid',2,'merman merfolk',NULL),
('marseymetokur',2,'marsey mister metokur jim bud oshaughnessy internet bud aristocrat james youtube lolcow chud scout augustine cancer moon cricket',1672539597),
('marseymexican',2,'latina latino hispanic fiesta sombrero latinx hombre mexico',NULL),
('marseymfdoom',2,'rapper hip hop hiphop rnb supervillain helmet mask',NULL),
('marseymicrobus',2,'vw van bussy',NULL),
('marseymicrosoftpride',2,'pride flag rights gay trans lgbt lgbtqia microsoft opensource intersectional sexuality queer nonbinary intersex bisexual twospirit progress nonbinary agender asexual',1666393843),
('marseymidsommarchristian',2,'sweden movie film cult a24 scandinavia man cinema bear death kill fire murder torture drug',1664220296),
('marseymidsommardani',2,'sweden movie film cult a24 scandinavia flowers dress happy tears joy woman cinema',1664220186),
('marseymike',2,'disney pixar monsters inc cyclops',NULL),
('marseymiki',2,'idolmaster anime animegirl kiss blowkiss',1667211904),
('marseymiku',2,'hatsune miku pop star concert rave weeaboo music animated singing microphone',NULL),
('marseymilesdavis',2,'jazz saxophone bebop music trumpet brass black',NULL),
('marseymime',2,'mimesey facepaint black and white beret silent mute performer',NULL),
('marseyminer',2,'miner minecraft mine craft mining digging minor blocks pixel game vidya video notch',NULL),
('marseymini',2,'annihilate minigun machine gun kill destroy murder animated',NULL),
('marseyminimalism',2,'orange minimalist square art',NULL),
('marseyminimalism2',2,'minimalist polygons polygonal art',NULL),
('marseyminion',2,'gru pixar',NULL),
('marseyminipixel',2,'miniature small smol place 8bit mouse',NULL),
('marseymischevious',2,'trickster mischevious troublesome plan scheme schemer evil clever think bad naughty prankish delinquet',1672429359),
('marseymischief',2,'interface clown',NULL),
('marseymisinformation',2,'marsey meme sphere ball text misinformation internet purposefully  spread',1665415192),
('marseymissing',2,'absent low effort',NULL),
('marseymissing2',2,'missing notexture source image not found broken',NULL),
('marseymobster2',2,'bat gangster mafia kneecapper',NULL),
('marseymocking',2,'mocking spongebob meme alternating studly caps retard',NULL),
('marseymodelo',2,'cheers alcohol drinking beer',NULL),
('marseymodelo2',2,'cheers alcohol beer drinking',NULL),
('marseymommymilkers',2,'pepe mellokind momma booba khazar abby shapiro tits breasts boobs',NULL),
('marseymoney',2,'capitalism capitalist rich dollar signs bag wealthy dollars dinero',NULL),
('marseymonk',2,'meditate levitating pray buddhist fish asian levitate animated yingyang buddhism karma zen',NULL),
('marseymonke',2,'retvrn return',NULL),
('marseymononoke',2,'anime japanese miyazaki ghibli asian cartoon princess character fictionnal ashitaka san wild wolf nature',NULL),
('marseymonstercocklaugh',2,'laugh dick cock penis big monster',1674251614),
('marseymooncricket',2,'marsey black cricket moon bug dancing rave party singing animated nigger coon jiggaboo',1668468627),
('marseymoonshine',2,'alcohol hick drunk booze drink illegal prohibition',1665436053),
('marseymoose',2,'moosin antlers',NULL),
('marseymoplicker',2,'janny moderator admin',NULL),
('marseymormon',2,'backpack tie jesus god christian missionary',NULL),
('marseymorph',2,'skinwalker changeling',NULL),
('marseymothermary',2,'christian christmas jesus immaculate god mother mary xmas pray',NULL),
('marseymothman',2,'spooky scary monster halloween cryptid supernatural paranormal creepy',1666369939),
('marseymountaineer',2,'winter climbing coat ice sport peak axe cleats mountain alpine climber',NULL),
('marseymouse',2,'rodent cheesed to meet you',NULL),
('marseymrsclaus',2,'christmas santa winter boobs',NULL),
('marseymspaint',2,'paint mspaint pixel shifty squat',NULL),
('marseymugshot',2,'arran prison arrested criminal jail',NULL),
('marseymummy',2,'egyptian halloween monster holiday',NULL),
('marseymummy2',2,'egyptian halloween monster holiday',NULL),
('marseymummy3',2,'egyptian halloween monster holiday',NULL),
('marseymushroomcloud',2,'atomic bomb nuke kaboom explode explosion war radiation',NULL),
('marseymutt',2,'american burger 56 percent mayo',NULL),
('marseymutt2',2,'american burger 56 percent mayo',NULL),
('marseymyeisha',2,'kween black fds',NULL),
('marseymyers',2,'knife halloween killer mask scary michael stab horror',1666654966),
('marseymyspacetom',2,'carp friend carpathianflrost anderson',NULL),
('marseyn8',2,'nate redditor powermod powerjannie moderator',NULL),
('marseynails',2,'manicure emoji pedicure',NULL),
('marseynana',2,'idolmaster anime animegirl ribbon',1667212013),
('marseynapoleon',2,'baguette soldier frenchman history',NULL),
('marseynapoleon2',2,'french france horse',NULL),
('marseyneat',2,'photo cringe compilation camera cringe collection pic',NULL),
('marseyneckbeard',2,'mlady bodypillow dakimakura anime otaku fedora weebshit body pillow mra weeb',NULL),
('marseynecromancer',2,'halloween horror scary undead necromancy ghost zombie skeletons magician warlock',1670513898),
('marseyneet',2,'cozy comfy wagie',NULL),
('marseynefariousbrian',2,'familyguy familyman brian nefarious',1668387040),
('marseyneko',2,'autism autistic cute neko nekobit fedi fediverse hat programmer codecel',NULL),
('marseyneon',2,'wave flashy trippy waving flashing lights animated',NULL),
('marseynerd',2,'dork loser dweeb geek glasses aevann',NULL),
('marseynerd2',2,'geek glasses dork loser pimples zits',NULL),
('marseynewyorker',2,'rat nyc newyork hustle bustle yankees',1666250525),
('marseynietzsche',2,'philosophy history',NULL),
('marseyniggy',2,'idolmaster sachiko 4chan smug anime',1664383012),
('marseynightmare',2,'striped sweater freddy freddie horror halloween krueger holiday claws monster',NULL),
('marseyninja',2,'samurai japanese killer stealthy sneaky assassin weeb',NULL),
('marseynintendo',2,'mario gamer switch gaymer video game mustache soy',NULL),
('marseyniqab',2,'burka islam muslim burqa',NULL),
('marseyniqabpearlclutch',2,'bombasticpussy sjw snowflake burka burqa',1663350191),
('marseyno',2,'denied refuse rejection reaction ugh deny hand',NULL),
('marseynodox',2,'sign',1665250355),
('marseynoooticer',2,'notice stats racist iq chud bigot numbers observe see hmm wrong think thonk',1664406781),
('marseynope',2,'bush grass simpsons homer hide avoid',1663895054),
('marseynorf',2,'soccer british football sports',1668780332),
('marseynosleep',2,'horror scary halloween holiday',NULL),
('marseynosuchcases',2,'strawman fake news cope seethe none many luggage airport conveyor belt sam brinton',1675541160),
('marseynotes',2,'notes writer writing journ*list therapist doodle pencil',NULL),
('marseynotes2',2,'notes notepad pencil writing nerd glasses behind',NULL),
('marseynotesglow',2,'notes glow cia fbi fed writer writing pencil',NULL),
('marseynouautism',2,'pointing hat spiderman sperg autistic no u no you noyou',NULL),
('marseynoyou',2,'nou no u pointing',NULL),
('marseynoyoufellowpedo',2,'point fbi glow libertarian mask discord agent',1664045092),
('marseynoyouglow',2,'fbi no u animated feds glowies glowniggers atf cia nsa',NULL),
('marseynpc',2,'sheeple',NULL),
('marseynpc2',2,'reaction idiot sheep',NULL),
('marseynpcmad',2,'angry grey libtard',NULL),
('marseynukegoggles',2,'nuclear atomic bomb mushroom cloud',NULL),
('marseynull',2,'kiwifarms joshua moon josh dog',NULL),
('marseynulloverback',2,'animated jersh josh itsover wereback over back keffals kiwifarms',1671772512),
('marseynun',2,'habit catholic',NULL),
('marseynurgle',2,'warhammer 40k chaos god disease sickness rebirth',NULL),
('marseynut',2,'orgasm ahegao cum reaction coom',NULL),
('marseynutcracker',2,'soldier halberd pike christmas holiday',NULL),
('marseynyan',2,'space animated meme poptart',NULL),
('marseynyanlgbt',2,'animated gay pride homosexuality space flying',NULL),
('marseynyansuperstraight',2,'animated straggot pride heterosexuality space flying',NULL),
('marseyobama',2,'obama president black drone reaper predator',NULL),
('marseyobamacope',2,'barack pointing laughing poster',NULL),
('marseyobamahope',2,'happy poster barack',NULL),
('marseyobamanope',2,'no way wrong poster barack',NULL),
('marseyobamarope',2,'barack suicide kms kys hanging noose poser',NULL),
('marseyobese',2,'fat chonker bbw chonk chunky pig lorg',NULL),
('marseyobesescale',2,'fat chonker bbw chonk chunky pig lorg',NULL),
('marseyobey',2,'1984 sign ingsoc poster big brother',NULL),
('marseyobjection',2,'objection darrell brooks court lawyer waukesha',1665524756),
('marseyoceania',2,'kiwi new zealand kangaroo newzealand australia',NULL),
('marseyoctopus',2,'tentacles kraken tentacled',NULL),
('marseyoctopus2',2,'consume product epic win communities no bait too obvious globe patch',NULL),
('marseyoctopus3',2,'consume product epic win communities no bait too obvious globe patch',NULL),
('marseyoctopus4',2,'octopus nrol39 bait patch globe obvious',NULL),
('marseyokapi',2,'okapi furry deer',NULL),
('marseyokay',2,'gesture sign fine alright agree accept adl white power hate symbol',1665533646),
('marseyokaycoke',2,'diet coke dogwhistle okay sign racist',1669745883),
('marseyokaymilk',2,'gesture hate racist adl altright white supremacist dogwhistle',1665533325),
('marseyolantern',2,'halloween scary pumpking',NULL),
('marseyoldguard',2,'napoleon war soldier musket french france history europe reaction',NULL),
('marseyoldtimey',2,'cartoon disney vintage olde classic retro',NULL),
('marseyonacid',2,'tripping trippy drugs lcd animated',NULL),
('marseyonemediumsnekvibing',2,'sneks snakes tlsm admin jannie janitor moderator bop animated',1666416181),
('marseyoperaphantom',2,'phantom opera music incel mask',1664677165),
('marseyopossum',2,'possum trash',NULL),
('marseyoppenheimer',2,'scientist nuke bomb ww2 atomic nuclear mushroom cloud',NULL),
('marseyoptimusprime',2,'transformers autobot robot toy cartoon scifi',1672435331),
('marseyorca',2,'orca whale idate smoke smoking anime weeks sal',NULL),
('marseyorthodox',2,'priest schismatic bartholomew_1 christian',NULL),
('marseyorthodoxbrap',2,'orthodox bartholomew brap fart gas sniff smell christian',NULL),
('marseyorthodoxcarphug',2,'schismatic heretic embrace hug love bartholomew carpathianflorist',NULL),
('marseyorthodoxsmug',2,'schismatic heretic scoff christian priest gloat',NULL),
('marseyotter',2,'otter fish sea swim lake nature seal sealion river. wuzizname float',NULL),
('marseyouroboros',2,'onelargesnakeeatingitsowntail serpent circle vore autocannibalism',1666219885),
('marseyoutletsuicide',2,'fork outlet plug socket kill kms electricity electrocution electrocute death die',NULL),
('marseyoutline',2,'blank empty void',NULL),
('marseyoverseether',2,'rdrama meta seething fire red bigmad angry anger',NULL),
('marseyowow',2,'reaction excited owo',NULL),
('marseyoyster',2,'pearl shellfish clam give',NULL),
('marseypadoru',2,'menosgrande christmas anime holidays',NULL),
('marseypain',2,'suffering meme kms kill myself cat',NULL),
('marseypaint',2,'low effort art',NULL),
('marseypainter',2,'palet reaction pallet paintbrush paints artist pallette',NULL),
('marseypaintretard',2,'retard retarded paint mspaint inbred rslurred',NULL),
('marseypajeet',2,'indian currycel bobs vagene streetshit street shit superpower 2020 happy',NULL),
('marseypalpatine',2,'emperor sith starwars lightning spaceshit sheev',1667592319),
('marseypanda',2,'red panda bear happy redpanda',NULL),
('marseypanda2',2,'panda bear fursona skin animal costume furry fursuit',NULL),
('marseypanties',2,'reaction underwear panty pantsu',NULL),
('marseypaperbag',2,'ugly ashamed bagged butterface',NULL),
('marseyparappa',2,'parappa the rappper i know gotta believe lammy',1673923044),
('marseyparty',2,'excite excitement celebrate happy celebrating',NULL),
('marseyparty1',2,'trippy animated happy dance',NULL),
('marseyparty2',2,'trippy animated happy dance',NULL),
('marseyparty3',2,'trippy animated happy dance',NULL),
('marseypartymaxx',2,'party meme parrot vibing jam dance',NULL),
('marseypartyxmas',2,'christmas holiday santa hat beard rainbow animated',NULL),
('marseypartyzoom',2,'party meme parrot vibing jam dance',NULL),
('marseypass',2,'marseypasss queen kween foid female woman kween',NULL),
('marseypass2',2,'pass froyo frozenchosen woman foid transgender',NULL),
('marseypassftm',2,'trans male female man woman gender transition ftm fail',1672443077),
('marseypastor',2,'christian baptist southern church black papist mrpenny preacher priest',NULL),
('marseypathetic',2,'pathetic asuka',NULL),
('marseypathetic2',2,'anime weeb asuka shun scorn disgust contempt disgusted',NULL),
('marseypatriot',2,'uncle sam red white and blue burgerland holiday american 4oj patriotic',NULL),
('marseypeace',2,'peace love hippy happy gesture',NULL),
('marseypeacekeeper',2,'united nations un rifle helmet gun',NULL),
('marseypearlclutch',2,'sensitive reaction snowflake puritanical gasp sjw',NULL),
('marseypearlclutch2',2,'sensitive reaction snowflake puritanical gasp sjw',NULL),
('marseypedo',2,'libertarian borpa male feminist discord pedophile groomer chomo lolbert toucher',NULL),
('marseypedobear',2,'groomer molest nonce',NULL),
('marseypedosnipe',2,'pedo sniper shoot kill scope rifle pedophile nambla libertarian',NULL),
('marseypenguin',2,'bird linux puffin',NULL),
('marseypenis',2,'dick cock smug balls',1667960314),
('marseypenny',2,'penny mrpenny black trad foid bleeder female woman kween negro dress baptist christian',NULL),
('marseypennyboo',2,'mrpennycoomstokids black nigger kween shaniqua thot whore female woman bleeder birthing person kfc baptist tradwife dress christian foid',NULL),
('marseypennylove',2,'love penny hug wholesome black kween',NULL),
('marseypentagram',2,'satanic satanism devil evil occult witchcraft belial baphomet leviathan 666',NULL),
('marseypepe',2,'ok rightoid mellokind frog reaction',NULL),
('marseypepe2',2,'reaction frog mellokind',NULL),
('marseypepsi',2,'cola coke soda soft drink pop red white blue usa america',NULL),
('marseypeterson',2,'jordan b peterson professor intellectual chud rightoid incel twelve rules for life zoloft depressed antidepressant depression tired old smart',1666054938),
('marseypharaoh',2,'egyptian aevann pyramids',NULL),
('marseypharaoh2',2,'gods egyptian aevann animated',NULL),
('marseypharaohcat',2,'egyptian illuminati aevann pyramid sand ancient alien artifact museum history king cleopatra',NULL),
('marseyphonecall',2,'pepe apu peepo phone call cellphone',NULL),
('marseypibblechad',2,'pibble pitbull velvethippo dogfood rape kidnap',1668484532),
('marseypickle',2,'funniest shit morty rick',NULL),
('marseypicrew',2,'trans lgbt gay lesbian picrew ugly',1674282029),
('marseypicrewwpd',2,'wpd knife trans gay lgbt ugly calarts',1674282084),
('marseypig',2,'fat fursona furry hog fursuit oink',NULL),
('marseypiggybank',2,'pennies cents poor fry cheap futurama takemymoney',1673401071),
('marseypikachu',2,'electric pokemon yellow',NULL),
('marseypikachu2',2,'pokemon shoked meme reaction surprised shocked gasp',NULL),
('marseypilgrim',2,'thanksgiving puritan holiday',NULL),
('marseypills',2,'suicide kill self kms death die pills overdose drugs pharms pharmaceuticals pop pillpopper',NULL),
('marseypimp',2,'dramamine slickback purple baller',NULL),
('marseypin',2,'pinned sticky',NULL),
('marseypin2',2,'sticky pushpin award',NULL),
('marseypinkcat',2,'homo gay happy ribbon femme girl',NULL),
('marseypinkname',2,'pink matter name pinkname panther',NULL),
('marseypinkpanther',2,'pink panther cartoon smoking comedy tv television feline',NULL),
('marseypinochet',2,'fascist fash ugarte augusto chopper helicopter chile',NULL),
('marseypipe',2,'smoke smart mhm yes smoking tobacco intelligent',NULL),
('marseypipebomb',2,'explosion explosive terrorist boom',NULL),
('marseypirate',2,'argh eyepatch bandana uraniumdonger',NULL),
('marseypirate2',2,'party parrot eyepatch partyparrot',NULL),
('marseypixel',2,'reaction lorez lowres',NULL),
('marseypizzarentfree',2,'pizzashill seethe cope',1674253880),
('marseypizzashill',2,'sex haver chad grass toucher',NULL),
('marseypizzashillblacked',2,'bbc cuck leftoid faggot incel',1667360705),
('marseypizzaslice',2,'pizza shill longpost yum chef cook italian cheese pepperoni',NULL),
('marseyplace',2,'reddit pixels pixellated pixellation lowres',NULL),
('marseyplace2',2,'pixelart pixellated reddit lowres',NULL),
('marseyplacenofun',2,'place reddit rules forbidden',NULL),
('marseyplaguedoctor',2,'plauge doctor black dank scythe hat crow mask',1667786832),
('marseyplane',2,'flying jet pilot',NULL),
('marseyplanecrash',2,'flying wreck jet pilot animated',NULL),
('marseyplaty',2,'hearts crossover platypus love',NULL),
('marseyplatymerchant',2,'platy merchant jew greedy shekels',1674349943),
('marseyplaying',2,'fish playful mischief srdine animated',NULL),
('marseyplaying2',2,'fish playful mischief srdine animated',NULL),
('marseypleading',2,'sad eyes begging puppy dog eyes',NULL),
('marseypleading2',2,'please beg pls shy sad puppy eyes adorable',1665169734),
('marseyplugged',2,'electric technology gif animated plug',NULL),
('marseyplush',2,'bow ribbon doll plushie button eyes',NULL),
('marseyplushie',2,'yunann plush statue',NULL),
('marseyplushie2',2,'soft toy hold hug hi cute',1673831017),
('marseypochita',2,'merchandise chainsaw man appliance anime demon devil',1672432331),
('marseypoggers',2,'poggies twitch meme quagmire jawdropping shock surprise',NULL),
('marseypoint',2,'mad angry look show',1670510778),
('marseypoint2',2,'backwards look showing',1670510807),
('marseypokerface',2,'small eyes reaction stare unreadable beady eyes',NULL),
('marseypolarbear',2,'bear polar cold white arctic ice',NULL),
('marseypolyamory',2,'threesome 3some degenerate polycule slut whore std sex soy animated',NULL),
('marseyponder',2,'ponder orb wizard magician crystal ball',NULL),
('marseypony',2,'murmurwisper mlp my little ponies cutie mark horse furry my little pony',NULL),
('marseypoor',2,'homeless beggar panhandler proletariat bum',NULL),
('marseypop',2,'action figure doll funko toy soy',NULL),
('marseypop2',2,'excited blahblahblah blah blah blah animated',NULL),
('marseypopcorn',2,'eating entertained drama happy animated',NULL),
('marseypopcorntime',2,'eating popped corn drama animated watch',NULL),
('marseypope',2,'priest catholicism rome',NULL),
('marseyportalsuicide',2,'kill shotgun shoot death die kms animated',NULL),
('marseypostal',2,'postal smirk vidya game ginger',1667567600),
('marseypostal2',2,'postal p3 game ginger',1667746211),
('marseypostmodern',2,'postmodernist obscurantist art',NULL),
('marseypotofsneed',2,'pot sneed pottery dungeon ornamental ancient',NULL),
('marseypredator',2,'predator drone obama wedding military',NULL),
('marseypregunta',2,'mexican mexico latinx hispanic confused question marks questionmarks hmm spic beaner wat what why how idgi sombrero',NULL),
('marseypresents',2,'christmas gifts santa holiday candy cane happy',NULL),
('marseypretty',2,'flirt starry eyed stars in eyes',NULL),
('marseypride',2,'prideflag rights',NULL),
('marseyprideflag',2,'pride flag marseysexual sexuality lgbtq gay trans bipoc queer activism',NULL),
('marseypridepearlclutch',2,'lesbian gay bisexual homo lgb rainbow cry bigot tears',NULL),
('marseyprincesszelda1',2,'marsey zelda nintendo game video legend of vidya adventure princess snes past betwwen worlds 3ds wisdom',1671468616),
('marseyprincesszelda2',2,'marsey zelda nintendo game video legend of vidya adventure hyrule twilight princess gamecube wii n64 ocarina time',1671476372),
('marseyprincesszeldabotw',2,'marsey zelda nintendo game video legend of vidya adventure botw breath wild princess long hair hyrule',1671468672),
('marseyprincesszeldaskyward',2,'marsey zelda nintendo game video legend of vidya adventure ss skyward princess long hair hyrule sword skyloft',1671468810),
('marseyprincesszeldatoon',2,'marsey zelda nintendo game video legend of vidya adventure hyrule tetra wind waker gamecube ds princess toon gba gameboy cel shading sea',1671468859),
('marseyprincesszeldatotk',2,'marsey zelda nintendo game video legend of vidya adventure totk switch tears kingdom princess short cave hair hyrule',1671468767),
('marseyprisma',2,'animated fingers anime spin dance weeb',NULL),
('marseyproctologist',2,'exam rectal glove reaction anus anal colonoscopy',NULL),
('marseyprojection',2,'animated projection projector movie director film movie cinema theatre theater kino',NULL),
('marseyprostateexam',2,'gloves doctor proctologist proctology anal cavity search rectum',NULL),
('marseyprotestno',2,'sign protester refuse reaction deny reject',NULL),
('marseyprotestyes',2,'agree sign protester reaction approve',NULL),
('marseypsycho',2,'reaction schizo crazy',NULL),
('marseypudu',2,'pudu deer',1666252867),
('marseypuke',2,'hurl throw up gross animated illness vomit nauseated reaction upchuck nauseous sickening yuck barf ralph judgment',NULL),
('marseypumpkin',2,'jackolantern carving halloween holiday jack o lantern',NULL),
('marseypumpkin2',2,'jackolantern carving halloween holiday jack o lantern',NULL),
('marseypumpkin3',2,'witch jackolantern carving halloween holiday jack o lantern',NULL),
('marseypumpkin4',2,'ghost jackolantern carving halloween holiday jack o lantern',NULL),
('marseypumpkincloak',2,'costume halloween holiday',NULL),
('marseypumpking',2,'jackolantern jack o lantern halloween holiday',NULL),
('marseypumpkinglow',2,'halloween drama holiday jack o lantern animated',NULL),
('marseypunched',2,'pepe apu peepo punch punched fist hit beaten',NULL),
('marseypunching',2,'battle squaring up hit square up boxer fight throwdown reaction boxing fistfight fighting',NULL),
('marseypunished',2,'punished venom snake metal gear solid kojima eyepatch',NULL),
('marseypunished2',2,'punished venom snake metal gear solid kojima eyepatch drama',NULL),
('marseypunisher',2,'thin blue line rightoid police cops',NULL),
('marseypuppy',2,'dog dalle2 puppy',NULL),
('marseypureevil',2,'satan evil demon pointy horns',1664656928),
('marseypusheen',2,'grey gray',NULL),
('marseypussyhat',2,'feminist feminism activism activist protester protesting foid gussy woman birthing person roasty roastie thot slut whore',NULL),
('marseyputin',2,'vladimir russian kgb moscow ukraine dictator leader',NULL),
('marseyqatarworldcup',2,'soccer football sports muslim islam allah sand bipoc robe ghost',1669146805),
('marseyqatarworldcup2',2,'soccer football sports muslim islam allah sand bipoc robe ghost',1669146826),
('marseyqoomer',2,'shaman viking qanon jan6 capitol january6',NULL),
('marseyqr',2,'qr code',1663646718),
('marseyqr2',2,'cryptographic qrcode',1663944616),
('marseyquadmagyar',2,'bow and arrow hungary hungarian archery bowman quadnarca',NULL),
('marseyquagmire',2,'familyguy quagmire family man giggity pervert',1674415410),
('marseyquagmireshocked',2,'shock awe scream suprise wtf eye cartoon',1666414758),
('marseyqueen',2,'england bong english british elizabeth',NULL),
('marseyqueenlizard',2,'england bong english british reptilian elizabeth',NULL),
('marseyquestion',2,'suspicious sussy reaction sarcastic sarcasm',NULL),
('marseyrabbit',2,'bunny',NULL),
('marseyrabbitnewyear',2,'chinese cny chink chong lunar holiday coin money fortune huat bunny 2023 festive orient hat',1673483499),
('marseyrabbitnewyear2',2,'chinese cny chink chong lunar holiday red packet envelope money fortune huat bunny 2023 festive orient dress flowers',1673483532),
('marseyrabbitnewyear3',2,'chinese cny chink chong lunar holiday coin money fortune huat bunny 2023 festive orient hat',1673590382),
('marseyrabbitnewyear4',2,'chinese cny chink chong lunar holiday red packet envelope money fortune huat bunny 2023 festive orient dress flowers',1673590420),
('marseyraccoon',2,'trashpanda trash panda',NULL),
('marseyracist',2,'racing vroom racecar bigot reaction',NULL),
('marseyracistgrandpa',2,'thanksgiving fuck nigger holiday',NULL),
('marseyradfem',2,'chonker feminist radical radfem sjw terf fat obese blue hair bluehair feminism',1672644490),
('marseyradioactive',2,'nuclear waste chernobyl radiation geiger',NULL),
('marseyrage',2,'troll anger seethe furious reaction angry mad fury',NULL),
('marseyraging',2,'rage angry mad fury animated',NULL),
('marseyraiden',2,'mgs vidya',NULL),
('marseyrain',2,'cloud upset reaction disappointed storm depressed sad',NULL),
('marseyraisinghands',2,'highfive five hang ten joy raising hands emoji',1666670030),
('marseyrake',2,'canada canadian day of the rake leaf leaves fall autumn genocide',NULL),
('marseyramen',2,'eating noodles food bowl animated soup',NULL),
('marseyrapper',2,'rap rhyming spitting nigger sing kanye kendrick dre snoop dogg',1671241001),
('marseyrapscallion',2,'stinker rapscallion troublemaker mischevious meme naughty troll',NULL),
('marseyrare',2,'kangaroo wtf',NULL),
('marseyrasta',2,'marijuana weed dude weed lmao ganja drugs pot reggae joint jamaican',NULL),
('marseyrat',2,'rodent black',NULL),
('marseyratso',2,'furry nsfw porn',1663119130),
('marseyrave',2,'dead animated party death sandstorm darude crab dance',NULL),
('marseyraytraced',2,'beautiful raytraced 3d hd 4k realistic render',1674459113),
('marseyrdramauser',2,'bussy fat lard gay homosexual obese poweruser neet dildo chef hat neckbeard meta',NULL),
('marseyreactor',2,'nuclear power reactor energy generation radioactive chernobyl',NULL),
('marseyreading',2,'study homework learn nerd novel reaction book',NULL),
('marseyredcard',2,'soccer football sports ban foul',1670257285),
('marseyredcheck',2,'redcheck truth social donald trump daddy ddr',1668189705),
('marseyredcoat',2,'britain historical redcoat empire imperial rifle soldier musket army revolution america',NULL),
('marseyredflag',2,'warning red flag alert scum problematic',NULL),
('marseyredflag2',2,'refuse reject warning animated',NULL),
('marseyredmage',2,'magic wizard final fantasy spell video game vidya',NULL),
('marseyredshirt',2,'redshirt star trek expendable disposable nameless spaceshit',1668482912),
('marseyrefrigerator',2,'appliance kitchen food freezer fish cooking',1671792131),
('marseyregistration',2,'register note retard writing glasses',1670959685),
('marseyregular',2,'marsey regular normal content',1663812191),
('marseyreich',2,'nazi pol authright fuhrer hitler fascist',NULL),
('marseyreindeer',2,'christmas santa rudolf capy cold aevann holiday animated walking',NULL),
('marseyreindeer2',2,'santa christmas rudolf holiday',NULL),
('marseyreindeer3',2,'rudolf dasher dancer prancer vixen comet cupid donner blitzen santa sleigh sled christmas winter holiday',NULL),
('marseyreindeer4',2,'rudolf dasher dancer prancer vixen comet cupid donner blitzen santa sleigh sled christmas winter holiday',NULL),
('marseyrelevancy',2,'darrell brooks court relevancy relevance waukesha',1665785008),
('marseyreluctant',2,'stare doubt skeptical wary cautious uncertain uhh umm',NULL),
('marseyremastered',2,'4k hd hi def hidef high definition uhd rtx',NULL),
('marseyrentfree',2,'reaction no charge obsessed obsession',NULL),
('marseyreportercnn',2,'reporter journalist journoid interviewer',NULL),
('marseyreporterfox',2,'reporter journalist journoid interviewer',NULL),
('marseyrepostsign',2,'repost sign wink tail wag animated',1667707937),
('marseyrespect',2,'darrell brooks respect respecc',1666366039),
('marseyretard',2,'special ed retarded reaction slow sped drooling exceptional',NULL),
('marseyretard2',2,'drooling stupid idiot sped moron imbecile dolt happy tongue',NULL),
('marseyretard3',2,'drooling stupid idiot sped moron imbecile dolt',NULL),
('marseyretard4',2,'moron dummy idiot buffoon drooling sped retarded',1670514701),
('marseyretardchad',2,'stupid moron idiot retard chad based monobrow chin stubble drool',NULL),
('marseyretro',2,'cardboard retro gameboy green nerd gamer',NULL),
('marseyrevolution',2,'marxist ussr marxism ccp hammer communist sickle communism proletariat juche kgb',NULL),
('marseyreze',2,'reze chainsaw man anime communist spy russian cute kiss heart manga tatsuki fujimoto devil hybrid bomb denji choker',1674906544),
('marseyrezebite',2,'reze chainsaw man anime blood tongue bite gore communist spy russian cute kiss manga tatsuki fujimoto devil hybrid bomb denji choker',1674906503),
('marseyrick',2,'smart 150iq high iq reaction 150 iq morty',NULL),
('marseyriddler',2,'riddler batman incel villain halloween',1666309356),
('marseyridin',2,'joe biden kamala harris voted voting election american president hat',NULL),
('marseyrightoidschizo',2,'nazi conspiracy crazy tin foil tinfoil conservative animated ruqqus',NULL),
('marseyrise',2,'rise elmo fire',1667772371),
('marseyrobber',2,'mask balaclava gun shooter shooting thief criminal nigger jogger ahmaud arbery george floyd',NULL),
('marseyrobot',2,'npc snappy sentient ai glow tech computer',1664034073),
('marseyroguspanish',2,'rogu spanish marsey american dad',1665625304),
('marseyroo',2,'kangaroo australian',NULL),
('marseyrope',2,'reaction suicidal shotgun facelift suicide',NULL),
('marseyropewithchingchong',2,'suicide chink chinese asian die kys together strawhat slit zip gook nip buckteeth',NULL),
('marseyropewithme',2,'suicide kys kms suicidal hanging noose',NULL),
('marseyropeyourself',2,'kill yourself kys lynch reaction keep yourself safe hanging noose',NULL),
('marseyropeyourself2',2,'kill yourself kys lynch reaction keep yourself safe hanging noose',NULL),
('marseyropeyourselfmirror',2,'suicide kms kys death hanging noose chair suicidal depression depressed reflection',NULL),
('marseyrowling',2,'harry potter terf jkr transphobe',NULL),
('marseyroxsneed',2,'roxy roxxane wolf fnaf freddy furry fur chuck fuck suck',1665715251),
('marseyroxy',2,'fnaf roxanne wolf freddy keytar rockstar vidya furry',1663987934),
('marseyroxytrickortreat',2,'halloween candy bloody roxanne wolf spooky',1666982308),
('marseyrs',2,'runescape party hat phat crown lowpoly low poly',NULL),
('marseyrudolph',2,'reindeer santa christmas xmas',1670514525),
('marseyrudolph2',2,'reindeer christmas santa sleigh xmas',1670514539),
('marseyrulebritannia',2,'britain british bongistan chips london england lasereyes',1663211275),
('marseyruqqie',2,'ruqqus porpl freespeech nazi captainmeta4 kek arkitekt syzitus syzzie',1668462855),
('marseyrussel',2,'old pipe history',NULL),
('marseyrussiadolls',2,'toys ussr babushka matryoshka soviet',NULL),
('marseyrussiaglow',2,'animated russia red putin fsb kgb glow trump commie communist hat comrade',NULL),
('marseyrussian',2,'russian putin russia vodka adidas tracksuit vatnik ai alcohol beer drunk moscow',1664643821),
('marseyrussianmutt',2,'slav vatnik ukraine eastern',1674253975),
('marseyrustyventure',2,'dramamine venture bros brothers adult swim cartoon character glasses goattee goatee beard',NULL),
('marseysachiko',2,'idolmaster anime animegirl niggy',1667212045),
('marseysad',2,'concerned worried waiting prepared reaction',NULL),
('marseysad2',2,'reaction disappointed disappointment upset',NULL),
('marseysadako',2,'anime weeb horror monster scary spooky hair',1670514733),
('marseysadcat',2,'upset disappointing disappointment reaction disappointed sad crying',NULL),
('marseysadge',2,'frog pepe',NULL),
('marseysadgun',2,'pepe mellokind crying tears suicidal suicide kms frog',NULL),
('marseysailor',2,'nautical sea boat ship ocean mariner navy hat happy seaman anchor military',NULL),
('marseysaint',2,'wings angel blessed halo animated',NULL),
('marseysaint2',2,'angelic halo holy animated wings happy',NULL),
('marseysal',2,'2 weeks two weeks sallie white shark',NULL),
('marseysal2',2,'shark 2 weeks two weeks go nowhere going nowhere watch go nowhere',NULL),
('marseysalad',2,'vegan cabbage vegetarian lettuce vegetable',NULL),
('marseysaladfingers',2,'salad fingers meme internet creepy apocalypse depraved',NULL),
('marseysalat',2,'prayer islam muslim rug',NULL),
('marseysaltlicking',2,'salt lick rock',NULL),
('marseysalty',2,'sodium saltshaker seethe salt shaker nacl animated',NULL),
('marseysalutearmy',2,'saluting o7 military soldier',NULL),
('marseysaluteconfederacy',2,'salute patriotic o7 flag confederacy confederate america south rebel civil independence johnny',NULL),
('marseysalutecop',2,'acab officer saluting o7 police',NULL),
('marseysaluteindia',2,'o7 bobs vagene bitch lasagna pajeet curry desi animated flag patriotic modi',NULL),
('marseysaluteisrael',2,'jewish yiddish hebrew kike sheeny mossad star of david flag patriotic animated',NULL),
('marseysalutenavy',2,'saluting semen o7 homosexual soldier',NULL),
('marseysalutenovorossiya',2,'russia ukraine salute general patriotism flag',1671307981),
('marseysalutepride',2,'saluting 07 military soldier gay pride lgb rainbow',NULL),
('marseysaluteusa',2,'salute o7 animated flag patriotic patriotism burger nationalism flag american',NULL),
('marseysaluteussr',2,'salute o7 flag soviet union russia kgb communist commie marxist marxism tankie stalin lenin animated patriotic',NULL),
('marseysalvindicated',2,'shark 2weeks twoweeks gonowhere wentsomewhere',1663210995),
('marseysamfisher',2,'spy night goggles thermal stealth soldier agent nsa army',1671071201),
('marseysamhyde',2,'gun shooter sammy mdegenerate milliondollarextreme million dollar extreme',NULL),
('marseysamhyde2',2,'gun shooter sammy mdegenerate milliondollarextreme million dollar extreme',NULL),
('marseysamurai',2,'japan sword war weeb anime history',1674768702),
('marseysanders',2,'bernie rich socialism socialist jewish',NULL),
('marseysanta',2,'christmas gifts presents claus holiday',NULL),
('marseysanta2',2,'christmas gifts presents claus holiday',NULL),
('marseysanta3',2,'claus christmas presents gifts holiday',NULL),
('marseysargonofaccat',2,'sargon akkad ancient historical king mesopotamia sumer',NULL),
('marseysartre',2,'philosophy frenchman history',NULL),
('marseysaruh',2,'cute dress bread baguette valid trappy ts trappysaruh trans deuxrama celeb glamour train',NULL),
('marseysatangoat',2,'evil satan goat halloween spooky baphomet vvitch blackphillip',1667021744),
('marseysatisfied',2,'satisfying happy smile delightful grateful glad wholesome',1662997904),
('marseysatisfiedmarcus',2,'black bipoc satisfying happy smile delightful grateful glad wholesome',1662998420),
('marseysaturn',2,'devouring eating snoo kill de goya anger reddit',NULL),
('marseysaulgoodman',2,'lawyer saul goodman breaking bad bcs jewish better call saul suit buisness',1667846439),
('marseysaw',2,'doll horror halloween jigsaw monster evil torture game holiday',NULL),
('marseyscalped',2,'zombie brain alien parasite valve game half life headcrab skull',1663640326),
('marseyscared',2,'hide halloween afraid nervous holiday traumatized fearful',NULL),
('marseyscaryteeth',2,'scary teeth messes up evil angry grin bong horror',1666302835),
('marseyschizo',2,'harm burns selfharm self harm cigarette burning mermaids reaction artist self',NULL),
('marseyschizoabsinthelove',2,'animated schizo schizocel rare love absinthe frog',NULL),
('marseyschizobussylove',2,'animated schizo schizocel rare love certified bussy operator',NULL),
('marseyschizobyolove',2,'schizo byo byobombs rare love',NULL),
('marseyschizocapygitcommitlove',2,'animated schizo schizocel rare love chad capy git commit fsdfsd',NULL),
('marseyschizocapylove',2,'schizo aevann capybara love rare excited',NULL),
('marseyschizocarplove',2,'schizo carp love rare excited',NULL),
('marseyschizochad',2,'schizo tripping rare animated chad schizocel',1672390950),
('marseyschizochadbasedcapylove',2,'animated schizo schizocel rare love chad based capy aevann',NULL),
('marseyschizochadseethecapylove',2,'animated schizo schizocel rare love chad seethe capy aevann',NULL),
('marseyschizochadthankscapylove',2,'animated schizo schizocel rare love chad thanks queen capy aevann',NULL),
('marseyschizochadyescapylove',2,'animated schizo schizocel rare love chad yes capy aevann',NULL),
('marseyschizochiobulove',2,'chink asian tangerine feline singapore animated',1669161511),
('marseyschizodoggilove',2,'animated schizo schizocel rare love dussy doggi',NULL),
('marseyschizodongerlove',2,'animated schizo schizocel rare love kaiser uraniumdonger donger',NULL),
('marseyschizoducklove',2,'animated schizo schizocel rare love duck',NULL),
('marseyschizodussylove',2,'animated schizo schizocel rare love dussy doggi',NULL),
('marseyschizoexcited',2,'animated schizo rare drugs excited watching oscillate amused interested',NULL),
('marseyschizofartbinnlove',2,'animated schizo schizocel rare love fartbinn idk idc',NULL),
('marseyschizogeeselove',2,'animated schizo schizocel rare love geese suck',NULL),
('marseyschizogetogetolove',2,'schizocel schizo rare getogeto geto love excited animated casinogate',1663528960),
('marseyschizogrizzlylove',2,'schizo grizzly bear love schizocel animated',NULL),
('marseyschizohanklove',2,'animated schizo schizocel rare love byo hank',NULL),
('marseyschizohobocellove',2,'animated schizo schizocel rare love hobo homeless hobocel',NULL),
('marseyschizoidiolove',2,'schizo idio3 love rare excited idio',NULL),
('marseyschizojclove',2,'justcool393 schizo schizocel schizomarsey rare love',1665564066),
('marseyschizojoelove',2,'animated schizo schizocel rare love joe biden',NULL),
('marseyschizolangleylove',2,'animated schizo schizocel rare love langley cia glowie glow',NULL),
('marseyschizomajorgenerallove',2,'animated schizo schizocel rare love modern major general',NULL),
('marseyschizonekolove',2,'nekobit neko schizo schizocel schizomarsey rare love',NULL),
('marseyschizonotes',2,'writing crazy nuts notice pen paper conspiracy',1673380020),
('marseyschizopennylove',2,'animated schizo schizocel rare love penny',NULL),
('marseyschizosal',2,'schizo sal rare weeks nowhere',NULL),
('marseyschizosallove',2,'animated schizo schizocel rare love sal',NULL),
('marseyschizoschizolove',2,'animated schizo schizocel rare love soren',NULL),
('marseyschizoshaking',2,'crazy nuts insane traumatized shaking animated',NULL),
('marseyschizosnakeslove',2,'animated schizo schizocel rare love snakes sneks snek snake',NULL),
('marseyschizosorenlove',2,'schizo soren love rare excited animated',NULL),
('marseyschizostimslove',2,'animated schizo schizocel rare love stims vyvanse stimulants adderall amphetamines',NULL),
('marseyschizotripping',2,'animated schizo rare drugs trip',NULL),
('marseyschizotwitch',2,'twitching eyelid crazy nuts psycho insane traumatized animated',NULL),
('marseyschizowall',2,'crazy conspiracy conspiracies tinfoil insane nuts psycho',NULL),
('marseyschizowave',2,'insane crazy mental breakdown psycho hallucinations flashbacks ptsd traumatized shaking shake animated tedsimp',NULL),
('marseyschopenhauer',2,'philosopher old grandpa',NULL),
('marseyschrodinger',2,'philosophy science physics math',NULL),
('marseyscoot',2,'animated suckit gesturing coned rude',1671207049),
('marseyscooter',2,'fat american mutt burger scooter walmart obese pig hog brap usa handicapped wheelchair',NULL),
('marseyscout',2,'badge prepared',1671060050),
('marseyscratch',2,'loweffort doodle code coding programming',NULL),
('marseyscream',2,'panic frightened scared horror scream afraid reaction horrified nervous shock gasp',NULL),
('marseysecuritron',2,'fallout new vegas security yes man',1673033974),
('marseyseethe',2,'dilate mask crying seething smug cope',NULL),
('marseyselfflagellation',2,'whip white guilt hate sin mayo liberal catholic',NULL),
('marseysephiroth',2,'ff7 ffvii final fantasy vidya video game gamer gaming villain sword',NULL),
('marseyseven',2,'vidya gamer gaymer video game assassin hitman',NULL),
('marseysexy',2,'ned flanders stupid sexy flanders skiier skiing winter simpsons',NULL),
('marseysexylibrarian',2,'books hoe old woman thot nerd boobs bra geek',NULL),
('marseysexypepe',2,'mellokind hotpepe frog lewd flirt ribbon',NULL),
('marseyshake',2,'cartoon athf aqua fastfood shake dessert icecream',NULL),
('marseyshakespeare',2,'words writer author drama theater british poet william england english thespian playwright playwrite',NULL),
('marseyshapiro',2,'benjamin debate libtard facts and logic benny jewish ben shapiro',NULL),
('marseysharingan',2,'horror halloween holiday possessed animated monster naruto anime ninja',NULL),
('marseyshark',2,'jaws halloween fursona furry fish costume holiday fursuit',NULL),
('marseysharksoup',2,'sal shark 2weeks nowhere soup chinese 2 weeks watch this go nowhere cumshark white',1670088838),
('marseysheep',2,'follower wool lamb fursona bah furry fursuit',NULL),
('marseysheepdog',2,'shaggy scruffy woof',NULL),
('marseysheogorath',2,'elder scrolls oblivion morrowind daggerfall skyrim daedra demon madness crazy mania dementia',1668034870),
('marseysherpa',2,'mountain climbing travel nepal himalaya asia everest',NULL),
('marseyshesright',2,'point correct know',1675527028),
('marseyshiftyeyes',2,'suspicious sussy paranoid weird reaction sketchy',NULL),
('marseyshisha',2,'weed smoker smoking hookah',NULL),
('marseyshitforbrains',2,'brainlet poop dumb litterbox litter box soyjack soyjak redditor retarded scat',NULL),
('marseyshiva',2,'shiva india god neel hindu pajeet diwali curry streetshitter goddess',1666362615),
('marseyshock',2,'shock fear afraid terror scared horrified',NULL),
('marseyshook',2,'reaction surprised shocked gasp astonished',NULL),
('marseyshooting',2,'blam blatt shotgun kill pow murder',NULL),
('marseyshortbus',2,'bussy animated mrpenny carpathianflorist schizocel retard special short schoolbus classroom teacher wheels window rosa parks mlk',NULL),
('marseyshroom',2,'smug fungus shrigma shroomjak wojak mushroom',NULL),
('marseyshrug',2,'hands up idk ig idc dunno i guess',NULL),
('marseyshutitdown',2,'cop glownigger fed glowie agent federal mossad israel idf the goyim know kikes radio walkie talkie',NULL),
('marseyshy',2,'flirting anxious twiddle nervous flirty coy animated',NULL),
('marseyshy2',2,'uwu weeb blush flushed finger owo',NULL),
('marseyshy3',2,'embarrassed blushing timid smile nervous reaction cute',1670370597),
('marseyshy4',2,'embarrassed blushing timid smile nervous reaction cute',1670370696),
('marseysick',2,'puke nausea green face vomit nauseated reaction nauseous barf judgment ill',NULL),
('marseysickos',2,'hahaha ha ha ha yes onion comic pervert sicko creep',NULL),
('marseysickos2',2,'hahaha ha ha ha yes onion comic pervert sicko creep window',NULL),
('marseysigh',2,'breathe give up giveup reaction depression breathing depressed animated',NULL),
('marseysignaling',2,'railway light semaphore troomer tranny transgender train troid transsexual animated',1663238068),
('marseysignup',2,'rdrama signup graph ears schizo plot',1670968851),
('marseysillybrian',2,'familyguy familyman brian silly',1668387069),
('marseysimpson',2,'yellow simpsons groening homer bart lisa marge cartoon',NULL),
('marseysing',2,'singing jamming rocking music headphones cute happy smile karaoke ipod album',NULL),
('marseysingapore',2,'singaporean asian azn flag merlion chiobu',NULL),
('marseysipping',2,'drinking root drink reaction stare thirsty purple drank juice bored',NULL),
('marseysippingsad',2,'juice sadge',1669559813),
('marseysjw',2,'lgbt social justice reaction gay snowflake pride',NULL),
('marseyskater',2,'dope hip sk8 ill tony hawk sick skateboard not a poser rad',NULL),
('marseyskeleton',2,'dead bones halloween holiday skeletal',NULL),
('marseyskeleton2',2,'bones spooky halloween holiday skeletal',NULL),
('marseyskeletontrex',2,'dinosaur skeleton spooky dead extinct halloween bones',1666234623),
('marseyskeletonvelociraptor',2,'dinosaur skeleton extinct dead spooky halloween bones',1666234714),
('marseyskeletor',2,'skeleton mask heman 80s man halloween he man cartooon he holiday',NULL),
('marseyskellington',2,'marsey skeleton skellington tim christmas halloween before burton jack nightmare musical movie film',1666840958),
('marseyski',2,'skier skiing sking winter snow',NULL),
('marseyskinnedwalk',2,'watchpeopledie zllctnxaspywgb3 animated skinned walking trotting skeleton bones organs',NULL),
('marseyskinny',2,'tall anorexia bulimia anorexic bulimic',1670515138),
('marseyskull',2,'skull dead skeleton punisher kill bone',NULL),
('marseyslaanesh',2,'warhammer 40k chaos god degeneracy sex drugs pain',NULL),
('marseyslab',2,'dexter lab smart genius ginger cartoon network glasses',NULL),
('marseysleep',2,'bed bedtime zzz boring reaction tired bored',NULL),
('marseyslime',2,'animated happy blob vidya video game maple story maplestory bouncing bounce monster jump',NULL),
('marseyslm',2,'schizo lives matter krayon autistic autist fist neuro retard brain',1672048501),
('marseyslowpoke',2,'pokemon stupid late anime weeb meme',NULL),
('marseysmirk',2,'reaction snicker trolling lol',NULL),
('marseysmoothbrain',2,'idiot big brain brainlet retard reaction fool dumbass moron',NULL),
('marseysmudge',2,'diogenesjr diogenesjunior meme',NULL),
('marseysmug',2,'reaction superior haha',NULL),
('marseysmug2',2,'snicker scoff mock reaction guffaw ridicule judgment',NULL),
('marseysmug3',2,'reaction yikes judgment oof cringe',NULL),
('marseysmug4',2,'confident emoticon plain simple smile',1664490741),
('marseysmug5',2,'scoff lol srdine mock gossip',1670515240),
('marseysmug6',2,'scoff gossip lol srdine',1670515250),
('marseysmugautist',2,'autism retard brainlet drool hat',NULL),
('marseysmugretard',2,'srdine drooling brainlet idiot fool buffoon idiot',NULL),
('marseysmugsideeyes',2,'marsey smug',1665254121),
('marseysnap',2,'mad angry furious anger animated snap',NULL),
('marseysnappyautism',2,'snapshillbot hat neurodivergent robot autistic marppy',NULL),
('marseysnappyhug',2,'hug love robot sentient wholesome',1664490893),
('marseysneed',2,'feed farmer reaction chuck simpsons buck',NULL),
('marseysneedboat',2,'animated ship flag capybara',NULL),
('marseysnek',2,'snake serpent',NULL),
('marseysnekglow',2,'snekky fed us cia fbi nsa dhs glowie admin mod agent plant handler infiltrate',1671251589),
('marseysniff',2,'brap huff gas reaction fart creep smell',NULL),
('marseysnoo',2,'shaking redditor scared reaction nervous schizo reddit',NULL),
('marseysnoomask',2,'redditor crying srd serious',1671239611),
('marseysnorlax',2,'fat obese fatty fattie pokemon snorlax blocking snoring  sleeping',NULL),
('marseysnow',2,'snowman snowmarsey cold winter christmas holiday',NULL),
('marseysnowflake',2,'special snowflake sensitive snow',NULL),
('marseysnowglobe',2,'christmas tree small miniature',NULL),
('marseysnowman',2,'christmas cold snow winter',NULL),
('marseysnowman2',2,'christmas cold snow winter',NULL),
('marseysob',2,'tear crying depressed reaction sobbing depression sad cry animated tears',NULL),
('marseysoccer',2,'soccer football sports jersey futbol',NULL),
('marseysociety',2,'batman joker capeshit jared leto',NULL),
('marseysociety2',2,'joker clown capeshit batman gamersriseup cigarette honk',NULL),
('marseysockmlep',2,'sock puppet alt anonymous shill',NULL),
('marseysockpuppet',2,'animated sock puppet alt anonymous shill',NULL),
('marseysoldieramerica',2,'army war gun rifle burger mutt',NULL),
('marseysoldierchina',2,'army war gun rifle asia chinese chink gook',NULL),
('marseysoldierrussia',2,'army war gun rifle vatnik slav putin ukraine',NULL),
('marseysonic',2,'hedgehog blue',NULL),
('marseysonichu',2,'sonichu cwc christian christine chandler medallion zap extreme sonic pikachu cwcville hedgehog',NULL),
('marseysoon',2,'weeks 2weeks sal antisal soon',NULL),
('marseysoonretarded',2,'weeks 2weeks sal antisal soon retarded naive',NULL),
('marseysopa',2,'brazil soup macaco monkey teeth fangs scary',NULL),
('marseysoren',2,'sleeping alt right altright racist nazi chud',NULL),
('marseysosa',2,'chief keef sosa glo rap hiphop music drugs lean black',NULL),
('marseysoutherner',2,'plantation suit cigar good ol boy buck breaking buck breaker',NULL),
('marseysoycry',2,'angry crying soy ',NULL),
('marseysoycrytremble',2,'shaking libtard magatard reeeeeeeee woke sjw fragile weak low testosterone animated',1666968847),
('marseysoylentgrin',2,'numale nu male menslib redditor plebbitor happy glasses soyjak nerd loser beta smile smiling',NULL),
('marseysoypoint',2,'soyboy soy boy beard reaction pointing',NULL),
('marseysoypoint2',2,'wojak soyjak soyjack pointing beta redditors',NULL),
('marseysoypointglow',2,'glowie radioactive pointing',1665352060),
('marseysoypointgold',2,'glow wave',1665351969),
('marseysoypointgoldpoint',2,'point gold soy meta',1668646734),
('marseysoypointsnappyglow',2,'bot marppy fbi fed threeletter glowie',1665456811),
('marseysoypointsnappygold',2,'marppy bot glow faroutthesongfromperipheryiithistimeitspersonal',1665456746),
('marseysoypointsnappyquote',2,'bot marppy snappilent sapient sentient',1665456641),
('marseysoyrope',2,'redditor dead suicide kms kys hanging lynched hung soyjak',NULL),
('marseysoyseethe',2,'soyjack soyjak reddit angry yelling wojak',NULL),
('marseyspa',2,'spa towel cucumber facial relax calm selfcare foid hygiene beauty',NULL),
('marseyspecial',2,'retard reaction slow special needs sped',NULL),
('marseysperm',2,'cum swim vasectomy jizz semen spunk penis sex pregnant coom animated',NULL),
('marseysphericalcow',2,'sphere science moo physics nope',1664131121),
('marseysphinx',2,'sphinx egypt ancient antiquity wonder pharaoh myth riddle puzzle',NULL),
('marseyspider',2,'insect halloween arachnid holiday bug',NULL),
('marseyspider2',2,'insect halloween spiderweb arachnid holiday bug',NULL),
('marseyspiderman',2,'soy marvel capeshit dc comic book comics peter parker miles morales webslinger',NULL),
('marseyspinner',2,'animated loading webdev spin circle',NULL),
('marseyspirit',2,'ghost halloween holiday',NULL),
('marseyspit',2,'surprising reaction shocking water surprised shocked',NULL),
('marseyspock',2,'spock star trek nimoy science space',1664740894),
('marseyspongebobsmug',2,'spongebob smug satisfied winner superior snobby conceited egoistic pompous content',1675437318),
('marseyspooky',2,'art horror halloween holiday evil scary monster lovecraftian eldritch',NULL),
('marseyspookysmile',2,'horror halloween holiday evil scary monster',NULL),
('marseysprite',2,'sprite vidya game retro pixel',1666225359),
('marseyspy',2,'spy agent shill glowie russia china',NULL),
('marseyspyglow',2,'spy agent shill glowie russia china',NULL),
('marseysquint',2,'4084 hmmm squint unsure doubt',NULL),
('marseysquished',2,'squishing compressed compression finger press squashed',NULL),
('marseysrdine',2,'fisherman reaction fish canned fishing',NULL),
('marseysrdine2',2,'can animated reaction fish knife chop sardine',NULL),
('marseyssflag',2,'superstraight cishetero straggot pride',NULL),
('marseystalin',2,'tankie authleft ussr russia communism socialism marxist commie soviet proletariat marxism marxist leninist leninism revolution bolshevik',NULL),
('marseystamp',2,'letter envelope fed postal collect snail mail',1672996730),
('marseystamp2',2,'letter envelope fed postal collect snail mail toll paid',1672996782),
('marseystarbucks',2,'coffee latte barista marbucks scone',NULL),
('marseystars',2,'stareyes reaction star eyes starry eyed stareyed',NULL),
('marseystars2',2,'space galaxy cosmic starsey constellation',NULL),
('marseystarship',2,'starship jail execution prison',1672873048),
('marseystarwars',2,'scifi spaceshit starshit soy stormtrooper lightsaber disney',1667805994),
('marseysteaming',2,'steaming exhale emoji unamused annoyed',NULL),
('marseysteer',2,'car drive nervous driving animated',NULL),
('marseystein',2,'undead frankenstein abomination halloween holiday monster',NULL),
('marseystims',2,'stim drug meth tweak geese_suck ted_simp pat crazy schizophrenia',NULL),
('marseysting',2,'drum badumtiss ba dum tiss bad dum tiss baddumtiss comedy humor punchline animated standup joke',NULL),
('marseystinky',2,'smelly homeless stank poor ew yuck',NULL),
('marseystocksdown',2,'market bonds options poor',1663640588),
('marseystocksup',2,'market bonds options rich',1663640568),
('marseystonetoss',2,'amogus pebblethrow nazi reaction boulderpummel',NULL),
('marseystrawman',2,'logical fallacy strawmarsey argument debate hat',NULL),
('marseystroke',2,'derp retard reaction stupid drooling',NULL),
('marseystuffed',2,'fur meme statuesque indifferent figurine statue stuffed art',NULL),
('marseysuffragette',2,'19a foid feminist 19th terrible feminism regret woman women mistake',NULL),
('marseysuicide',2,'kys killyourself pistol contemplatesuicide depressed gun despair doom',1668317605),
('marseysuicidesquidward',2,'creepypasta squidward suicide halloween scary zombie horror',1666404282),
('marseysuit',2,'businessman businessperson corporate boss manager rich adult professional lawyer banker',NULL),
('marseysulk',2,'unlucky crying reaction depression sobbing depressed sad',NULL),
('marseysully',2,'disney pixar monsters inc horned horns',NULL),
('marseysun',2,'notaispam chiobumadethis chiobuapproved blonde hair saiyan round bright eyes',1673901974),
('marseysunflower',2,'love ukraine threatening pointing russia',NULL),
('marseysunglassesoff',2,'shades shook disbelief fear confusion shock nervous',1674114526),
('marseysunglasseson',2,'cool smug finished end done sunny bright animated',1674157984),
('marseysuper',2,'superstraight lgbt',NULL),
('marseysupersorensoarin',2,'soren super hero superhero batman superman marsey41',1668289194),
('marseysurfing',2,'surfer surfing pikachu water wave meme',NULL),
('marseysurprised',2,'reaction shocked shook unexpected',NULL),
('marseysus',2,'amogus among us stonetoss sussy baka amongus',NULL),
('marseysuspicious',2,'sus stare look glance hmm thonk raise eyebrow curious',1663549267),
('marseysvengoolie',2,'horror halloween reviewer tophat suit chicken makeup mustache goatee comedy',1666302271),
('marseyswastika',2,'nazi chud germany swasi swazi windmill of peace hitler racist racism antisemitic antisemitism third reich jewish jews',NULL),
('marseysweating',2,'anxiety worried wipe scared worrying reaction anxious nervous stressed',NULL),
('marseysylveon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseytabletired',2,'tiresome depressed sad desk',NULL),
('marseytabletired2',2,'beer tiresome depressed sad alcoholic alcoholism despair',NULL),
('marseytakit',2,'darrell brooks court tackit tacit agreement waukesha',1665785068),
('marseytaliban',2,'mujahideen janniejihad islam afganistan shariah afghanistan muslim',NULL),
('marseytalking',2,'speech bubble smug gossip',NULL),
('marseytampon',2,'period menstrual menses menstruation bloody',NULL),
('marseytangerinefeline',2,'tangerinefeline tangerine feline chiobu orange pokemon plant',NULL),
('marseytank',2,'military ussr ccp communist authleft tank army communism china soviet',NULL),
('marseytankushanka',2,'military ussr ccp communist authleft tank army communism china soviet russian',NULL),
('marseytariq',2,'buck breaking nasheed nigger coon black',NULL),
('marseytariq2',2,'marsey tariq flex supremacist glow eye black king fba foundational bussy thong broken buck nasheed breaking k melanin melanoid wash yo ass',1671037636),
('marseytarrant',2,'branton brenton newzealand kiwi shooter shooting killer ebba akerlund murderer rightoid chud strong',NULL),
('marseytea',2,'drama spill',NULL),
('marseyteaparty',2,'donger arran soren carp duck',NULL),
('marseytears',2,'pout teary crying cried reaction sob eyes cry sad',NULL),
('marseytearsofblood',2,'crying sad bloody horror',NULL),
('marseytedsimp',2,'theodore teddy hat drugs mental illness schizo stims pills happy drugs fun birds stimulants stimmies risperidone',NULL),
('marseytelegram',2,'telegram homecoming plane chat messaging russian',NULL),
('marseytemplate',2,'template blank faceless eyeless mouthless head empty faceless',NULL),
('marseyterfdomesticabuse',2,'terf domestic abuse violence feminism feminist lesbian ovarit radical',NULL),
('marseyterrydavis',2,'templeos nerd programmer glownigger',NULL),
('marseyteruteru',2,'ghost flying spooky halloween holiday floating',NULL),
('marseytexan',2,'cowboy hat texas yeehaw pardner rootin tootin',NULL),
('marseytf2heavy',2,'tf2 heavy weapons valve vidya game minigun russia',NULL),
('marseytf2scout',2,'tf2 scout boston zoomer valve vidya game baseball mercenary',NULL),
('marseytf2spy',2,'tf2 spy france mercenary smoke suit valve vidya game espionage',NULL),
('marseythebuilder',2,'construction work blue collar architect plans toolbox contractor engineer labour',1670165625),
('marseythegrey',2,'lord of the rings magic gandalf lotr mage wizard warlock',NULL),
('marseytheorist',2,'ancient aliens meme',NULL),
('marseytherapist',2,'therapy writing mental illness',NULL),
('marseythief',2,'steal final fantasy video game vidya',NULL),
('marseything',2,'halloween holiday scary monster teeth',NULL),
('marseything2',2,'spider arachnid creepy crawler arthropod halloween alien carpenter horror scary animal creature spooky',1666334228),
('marseythinkinghallowseve',2,'halloween thinking vampire candy trickortreat costume mask',1666292942),
('marseythinkorino',2,'reaction judgment thinking',NULL),
('marseythomas',2,'tank engine train locomotive',NULL),
('marseythonk',2,'confused reaction thinking thunk thonk',NULL),
('marseythreadprocessrentfree',2,'thread equals process schizo drt junkiecel',1671054531),
('marseythroatsinging',2,'mongolian music',NULL),
('marseythumbsup',2,'cool good job good one agree reaction nice work yes great job',NULL),
('marseytiger',2,'fursona furry fursuit',NULL),
('marseytigerball',2,'polandball ball tiger russia',NULL),
('marseytigernewyear',2,'lunar chinese chinx rice new year holiday luck fortune money tiger lion asian azn',NULL),
('marseytimbit',2,'pearlclutch pearl clutch sjw triggered canadian leafistan canada crying',NULL),
('marseytime',2,'10pm tock tick clock animated',NULL),
('marseytimmy',2,'turner nickelodeon fairly oddparents hat boy cosmo wanda',NULL),
('marseytinfoil',2,'alex jones psycho crazy schizo alexjones conspiracy',NULL),
('marseytinfoil2',2,'alex jones rightoid psycho schizo alexjones conspiracy',NULL),
('marseytiny1',2,'tiny small shrinking pixel wave',NULL),
('marseytiny2',2,'tiny small shrinking pixel',NULL),
('marseytiny3',2,'tiny small shrinking pixel',NULL),
('marseytiny4',2,'tiny small shrinking pixel',NULL),
('marseytlop',2,'kanye life pablo tlop yeezy yeezus',1671591787),
('marseytlsm',2,'snake sex mating janny codecel tlsm schizocel',1665564339),
('marseytoasterbath',2,'suicide suicidal kill death bathtub electrocution electricity kms',NULL),
('marseytoasty',2,'homer simpsons cozy comfy bed',1670280548),
('marseytoht',2,'toht melting hat',1673133050),
('marseytoilet',2,'flush loo bog roll toilet paper swirly',NULL),
('marseytom',2,'thatfuckingmarsey fucking marsey tom and jerry tomjerry cartoon hanna barbera vintage smug',NULL),
('marseytombstone',2,'dead death gravestone cemetery graveyard rip rest in peace',NULL),
('marseytonberry',2,'tonberry monster final fantasy knife lantern scary flashlight headlamp vidya video game',NULL),
('marseytrad',2,'dramarama dress foid tradwife floral girl',NULL),
('marseytrad2',2,'wojak tradwife soyjak 4chan meme foid',NULL),
('marseytrain',2,'troomer tranny transgender trains troid transsexual animated',NULL),
('marseytrain2',2,'trans pass locomotive dilate mtf ftm',1664639764),
('marseytrans',2,'pitty transgender pitbull dog pibble transsexual',NULL),
('marseytrans2',2,'troon tranny transgender troomer lgbt trannies troid transsexual',NULL),
('marseytransattentionseeker',2,'needy enby nonbinary notice mtf ftm train attn',NULL),
('marseytransflag',2,'trans flag then consumeproduct',NULL),
('marseytransflag2',2,'lgbt transgender tranny pride animated',NULL),
('marseytransgenocide',2,'animated trans genocide chud lgbt rightoid bigot gaybros',NULL),
('marseytransimplosion',2,'train woke explode animated',1673623390),
('marseytranspearlclutch',2,'transgender upset snowflake clutching',1666994064),
('marseytransplushie',2,'soft toy hold hug hi cute',1673830970),
('marseytransplushie2',2,'soft toy hold hug hi cute',1673831100),
('marseytransplushie3',2,'41 display hang  soft toy hold hug l cute rope noose suicide hanging',1673831131),
('marseytransrentfree',2,'transgender lgbt rent free wojak chud',NULL),
('marseytree',2,'tree nature outdoors cosplay',NULL),
('marseytribute',2,'cum cumshot semen ropes load facial nsfw',1669095975),
('marseytrickortreat',2,'candy trick or treat halloween holiday',NULL),
('marseytrickrtreat',2,'halloween horror mask sam',1667697001),
('marseytrogdor',2,'burninator strongbad internet meme dragon marsdor',NULL),
('marseytroll',2,'dio diogenesjr diogenesjunior trollface reaction',NULL),
('marseytroll2',2,'ogre horror halloween holiday monster',NULL),
('marseytrollcrazy',2,'i hate killher psycho rage kill her gun',NULL),
('marseytrollgun',2,'kill her psycho',NULL),
('marseytrollolol',2,'rage trolled rageface',NULL),
('marseytrotsky',2,'icepick trotskyist betrayal ussr russia communism socialism marxist commie soviet proletariat marxism marxist leninist leninism revolution bolshevik',NULL),
('marseytroublemaker',2,'we do a little trolling',NULL),
('marseytrt',2,'trt test testosterone',1671534393),
('marseytruck',2,'honk canadian trucker hoonk ottawa convoy leaf semi 16wheeler',NULL),
('marseytrump',2,'cheeto hitler president history orange man',NULL),
('marseytrumpgarrison',2,'cum maga capitol ben comic republican',1663284695),
('marseytrumpgrill',2,'centrist donald ddr drumpf centrism bbq barbeque barbecue ketchup',NULL),
('marseytucker',2,'tucker carlsen fox rightoid conservative republican television tv',NULL),
('marseytuckermilkers',2,'tucker tits titties milkers trans teacher beachballs',1663895672),
('marseytunaktunak',2,'turban animated curry indian pajeet dance',NULL),
('marseyturban',2,'hindu turban bindi india pajeet canadian indian punjabi punjab sikh paki',1664911851),
('marseyturkey',2,'beak bird thanksgiving holiday feathers',NULL),
('marseyturkeyhappy',2,'bird thanksgiving food dinner yum delicious holiday',NULL),
('marseyturkroach',2,'turk turkish turkroach bug cockroach mehmet erdogan fez roach',NULL),
('marseyturnedon',2,'aroused arousal amorous horny',NULL),
('marseytv',2,'willy wonka telly television',NULL),
('marseytwerking',2,'tailspin animated butt backside dancing spin booty ass dance',NULL),
('marseytwerkingfast',2,'animated bussy booty ass spin',1668477353),
('marseytwerkinit',2,'ass butt booty rear rump donk dance nigger sheboon clap animated cheeks',NULL),
('marseytwins',2,'halloween holiday flashing shining scary animated',NULL),
('marseytwodramacodecelsmating',2,'schizo snake snek snakes sneks jc justcool justcool393',1668706549),
('marseytyping',2,'computer keyboard bongo animated',NULL),
('marseytypinglaugh',2,'computer keyboard lol bongo animated',NULL),
('marseytzeentch',2,'warhammer 40k chaos god trick magic lies',NULL),
('marseyuglyxmasweater',2,'santa hat christmas ugly holiday',NULL),
('marseyukrainerentfree',2,'marsey ukraine rentfree rent free zelensky putin vatnik hohol russia war crimea donbas',1673556332),
('marseyumbreon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseyumbreon2',2,'pokemon eevee furry eeveelution evolution',NULL),
('marseyunabomber',2,'package industrial society delivery mail kaczynski uncle ted',NULL),
('marseyunabomber2',2,'gift christmas industrial society delivery mail kaczynski uncle ted package',NULL),
('marseyunamused',2,'annoyed staring reaction disappointed stare uh huh bored',NULL),
('marseyunpettable',2,'dramamine fashy rightoid chud fashwave altright vaporwave',NULL),
('marseyunresponsive',2,'loading thinking spinner stunned processing stalled frozen hung waiting',1668645336),
('marseyupmarsey',2,'upvote vote upmarsey arrow reddit up animated',NULL),
('marseyupset',2,'marsey upset tears',1663697961),
('marseyupvote',2,'updoot upmarsey agree yes good based true',1664181430),
('marseyupvote2',2,'upvote reddit narwhal orangered updoot',1664658174),
('marseyusa',2,'burger patriot america freedom liberty justice love independence freedom guns trump biden state flag',NULL),
('marseyuwuw',2,'fursona furry fursuit',NULL),
('marseyvampeek',2,'vampire hello wake awaken coffin peek halloween horror',1666234320),
('marseyvampire',2,'undead sanguine horror spooky halloween fangs holiday monster',NULL),
('marseyvampirebite',2,'cope seethe mask house',1663376896),
('marseyvampirelove',2,'halloween heart love',1666404726),
('marseyvan',2,'libertarian pedobear free candy pedophile groomer lolbert chomo molester pedo toucher',NULL),
('marseyvapecrying',2,'meme vape juul crying depressed emo tears feels',NULL),
('marseyvaporeon',2,'trick or treat pokemon halloween eevee costume holiday',NULL),
('marseyvaporwave',2,'trippy 80s psychedelic animated retro',NULL),
('marseyvargfinnselfdefense',2,'bardfinn steve akens aikens penny verity oaken tranny train troon transgender transvestite black metal trve kvlt euronymous varg vikernes mayhem burzum child abuse kid beating stabbing bloody',NULL),
('marseyvargselfdefense',2,'vikernes euronymous mayhem burzum black metal norway norwegian stab knife kill murder',NULL),
('marseyvatnik',2,'russian alcoholic alcoholism',NULL),
('marseyvault',2,'fallout vault boy mascot bethesda videogame',1668087230),
('marseyvaxmaxx',2,'mask coronavirus covid gigavax corona vaccine vaccination hazmat',NULL),
('marseyvaxxtroll',2,'halloween alive healthy glow zombie vaccine vaccinated vaccination',1666460515),
('marseyvelociraptor',2,'dinosaur velocimarsey extinct predator claws',NULL),
('marseyvengeance',2,'gore undead shotgun horror halloween revenge monster bloody head wound holiday',NULL),
('marseyveryworried',2,'worry anxiety fear animated scared sweat yikes shook',NULL),
('marseyveryworriedfed',2,'spook cia fbi glowie glownigger atf afraid shook animated worry anxiety fear animated scared sweat yikes',1666282095),
('marseyvhs',2,'halloween horror murderer ilikeyou',1667697101),
('marseyvibing',2,'animated bopping vibe jam dancing headbang music rainbow dance',NULL),
('marseyvietnam',2,'army born to kill soldier war',NULL),
('marseyvirus',2,'phage infect infection plagued',NULL),
('marseyvore',2,'eating cannibalism cannibalize fetish kinky digest trapped letmeout',1665074856),
('marseyvore2',2,'eating marcus cannibalize cannibalism fetish kinky',1665074817),
('marseyvorezombiewolf',2,'furry furfag food eat yum degenerate fetish hungry',1665041705),
('marseyw',2,'win winner dub',NULL),
('marseywaffle',2,'waffle breakfast food sweet syrup leaf canada belgium',1669838950),
('marseywagie',2,'crypto rightoid ancap poor wagecuck mcdonalds maccas reaction',NULL),
('marseywait',2,'time watch wait waiting bored',NULL),
('marseywalking',2,'stroll walk strut gallivant animated',NULL),
('marseywall',2,'foid female birthing person woman girl 30 fds femcel single mom single mother itsover old gross yuck nasty gussy',NULL),
('marseywallst',2,'hodl crypto wall street bets invest gme bitcoin wallstreetbets wsb stock',NULL),
('marseywalterwhite',2,'walter white heisenberg breakingbad meth drugs chemistry',NULL),
('marseywarboy',2,'witness warboy nux madmax mad max apocalyptic evil apocalypse',NULL),
('marseywarhol',2,'modern art',NULL),
('marseywatchingtv',2,'familyguy peter griffin television couch',NULL),
('marseywatermark',2,'copyright theft stealing stolen creation',NULL),
('marseywave',2,'farewell cya hello greetings bye waving hi',NULL),
('marseywave2',2,'waving hi hello cya bye later animated',NULL),
('marseywave3',2,'farewell cya l8r wave reaction waving animated so long',NULL),
('marseyweeb',2,'neckbeard sword fedora kitana',NULL),
('marseywendy',2,'jellyfishjam pigtails redhead pippi',NULL),
('marseywereback',2,'yay happy excited undefeated',1668416931),
('marseywerebackchingchong',2,'happy elated joy asian chink slit buck teeth nip gook jap weeb',1674907075),
('marseywerewolf',2,'halloween animal marsewolf horror lycanthropy furry dog',1666229182),
('marseywhelmed',2,'whelmed smoke smoking cig cigarette meme overwhelmed underwhelmed',NULL),
('marseywheredrama',2,'seriouspost reaction agendapost dramawhere animated',NULL),
('marseywhirlyhat',2,'idiot retard hat dumb sped slow stupid special kid',NULL),
('marseywhiteflag',2,'surrender battle french',NULL),
('marseywhitemage',2,'magic wizard final fantasy spell video game vidya',NULL),
('marseywholesome',2,'seal award reddit tene',NULL),
('marseywholesometrans',2,'marsey trans wholesome seal award transgender euphoria euphoric',1674978438),
('marseywidow',2,'rose black sad tears death funeral dress foid',1673123150),
('marseywindmill',2,'headbang metal hair spinny brootal animated brutal kvlt',1670598383),
('marseywinemom',2,'drunk wine aunt flirt cigarette drunk lush elfbinn fartbinn cougar',NULL),
('marseywink',2,'wink reaction cheeky flirt smirk imply hint',NULL),
('marseywink2',2,'winking',1665254177),
('marseywinner',2,'reaction trophy gold prize first place',NULL),
('marseywise',2,'hood cloak wizard pipe',NULL),
('marseywitch',2,'spooky halloween magick holiday evil scary',NULL),
('marseywitch2',2,'tranny troomer penny wvp feminist halloween bardfinn groomer magick troid steve monster',NULL),
('marseywitch3',2,'flying broomstick wave halloween wizard holiday',NULL),
('marseywitchtriggered',2,'witchcraft angry spell bardfinn tranny train troon snowflake redditor wvp magic science animated',NULL),
('marseywizard',2,'wizard magic pepe apu',NULL),
('marseywoah',2,'tldr reaction wall of text wordswordswords stfu',NULL),
('marseywolf',2,'halloween werewolf holiday scary monster',NULL),
('marseywolfwalker',2,'doreen antiwork zombiewolf dogwalker dogwalking dog walker',NULL),
('marseywomanmoment',2,'brainlet female foid stupid retard dumb trad frozenchosen',1666664889),
('marseywomanmoment2',2,'foid female dumb white dog brainlet mtf trad retard special',1674400865),
('marseywomenrentfree',2,'woman women foid rentfree rent',1675163011),
('marseywoodchipper',2,'libertarian woodchipper libertarian kill',NULL),
('marseywoodchipper2',2,'libertarian pedo woodchipper animated kill map',NULL),
('marseywords',2,'longpost too long tldr reaction wordswordswords yawn',NULL),
('marseywords2',2,'longpost tldr essaypost wordswordswords pizzashill',1670515776),
('marseyworldcup',2,'world cup soccer football winner sports champion',1663033833),
('marseyworried',2,'monkaw anxiety sweat panic scared sweaty sweating anxious nervous stressed',NULL),
('marseywpdcatgirl',2,'catgirlsey watchpeopledie anime nekojin weeb weeaboo anthro furry',1673378413),
('marseywpdrentfree',2,'gore snuff watchpeopledie soy cuck jealousy',1674232102),
('marseywpdsupremacy',2,'watchpeopledie rdrama homosupremacy beheading throat bloody death die gore hood kkk klan gay lgbt',1672697846),
('marseywraith',2,'evil scary ghost halloween undead horror',1666281502),
('marseywrongthonk',2,'wrongthink hmmm thinking 1984 arrested police woke notice noticing',NULL),
('marseywtf',2,'scared reaction shook surprised shocked',NULL),
('marseywtf2',2,'shocked reaction wth disturbing disturbed what the fuck',NULL),
('marseywut2',2,'weird reaction raised eyebrow disturbing disturbed wtf judgment',NULL),
('marseyww1american1',2,'history world war one europe rifle firearm kill violence usa',1668182512),
('marseyww1american2',2,'history world war one europe rifle firearm kill violence usa',1668182541),
('marseyww1british1',2,'history world war one europe rifle firearm kill violence uk',1668182587),
('marseyww1british2',2,'history world war one europe rifle firearm kill violence uk',1668182605),
('marseyww1french1',2,'history world war one europe rifle firearm kill violence france',1668182635),
('marseyww1french2',2,'history world war one europe rifle firearm kill violence france',1668182665),
('marseyww1german1',2,'history world war one europe rifle firearm kill violence prussia trenches',1668182729),
('marseyww1german2',2,'history world war one europe rifle firearm kill violence prussia',1668182758),
('marseyww1russian1',2,'history world war one europe rifle firearm kill violence',1668182785),
('marseyww1russian2',2,'history world war one europe rifle firearm kill violence',1668182802),
('marseyxd',2,'lmao reaction rofl haha lol laughing',NULL),
('marseyxdoubt',2,'press doubt meme noire disbelief wrong',NULL),
('marseyxi',2,'xi jinping china chinese  asia',NULL),
('marseyxmr',2,'cryptocurrency monero money happy heart',NULL),
('marseyxoxo',2,'hearts wave flirt loving love animated kiss',NULL),
('marseyyarn',2,'code program socks npm yarn build make string animated',NULL),
('marseyyass',2,'queen reaction fds slay girlboss kween',NULL),
('marseyyawn',2,'zzz boring tired sleepy bored',NULL),
('marseyyeezus',2,'kanye god hotep',NULL),
('marseyyellowcard',2,'football soccer sports warning caution',1670257380),
('marseyyes',2,'thumbsup agree right thumbs up reaction judgment',NULL),
('marseyyesandno',2,'agree disagree both confused indecisive trippy animated inconclusive idk fencesitter switzerland',NULL),
('marseyyeti',2,'scary monster myth winter ice mountain himalaya asia predator giant',NULL),
('marseyyikes',2,'reaction judgment disgust oof cringe',NULL),
('marseyyinzer',2,'pittsburgh pennsylvania pens penguins steelers stillers pirates buccos buckos terrible towel pierogo yuengling beer city hat baseball football hockey nfl mlb nhl happy',NULL),
('marseyyugi',2,'yugioh yu-gi-oh! cards trap anime',NULL),
('marseyza',2,'antlers flowers',NULL),
('marseyzaku',2,'gundam mecha robot helmet mask',NULL),
('marseyzeldabeedle',2,'marsey zelda nintendo game video legend of vidya adventure hyrule gamecube ww botw ss beedle beetle shopkeeper merchant wild sky wind waker breath',1671476421),
('marseyzeldabokoblin',2,'marsey zelda nintendo game video legend of vidya adventure hyrule botw breath kindom tears wilds bokoblin enemy club pig monster',1671408791),
('marseyzeldadarklink',2,'marsey zelda nintendo game video legend of vidya adventure hyrule dark shadow link evil clone oot ocarina tp twilight sequel 2 two',1671476542),
('marseyzeldaganon',2,'marsey zelda nintendo game video legend of vidya adventure hyrule ganon evil power triforce trident pig boss nes snes gameboy villain',1671409373),
('marseyzeldaganondorf',2,'marsey zelda nintendo game video legend of vidya adventure hyrule gerudo ganondorf villan wind waker ocarina time princess tp oot tp king power evil villain ww twilight beard ginger',1671476596),
('marseyzeldagerudolink',2,'marsey zelda nintendo game video legend of vidya adventure switch wii femboy link twink crossdress trap gerudo desert botw breath wild mask arab voe',1671468559),
('marseyzeldalinkbotw',2,'marsey zelda nintendo game video legend of vidya adventure hyrule breath wild botw switch wii link sheika slate sword bow hero',1671476496),
('marseyzeldalinkminishcap',2,'marsey zelda nintendo game video legend of vidya adventure hyrule link gba gameboy advance hero minish cap elzo toon',1671476711),
('marseyzeldalinknes',2,'marsey zelda nintendo game video legend of vidya adventure link hero sword shield nes retro triforce',1671468507),
('marseyzeldalinkpast',2,'marsey zelda nintendo game video legend of vidya adventure hyrule link snes past hero retro blond shield sword worlds between oracles seasons ages',1671476763),
('marseyzeldalinkpast2',2,'marsey zelda nintendo game video legend of vidya adventure hyrule link snes past hero retro pink shield sword triforce',1671476920),
('marseyzeldalinktimeadult',2,'marsey zelda nintendo game video legend of vidya adventure hyrule adult time oot n64 ocarina hero sword master shield triforce courage',1671477065),
('marseyzeldalinktimechild',2,'marsey zelda nintendo game video legend of vidya adventure hyrule time oot n64 ocarina hero sword child fairy navi',1671477105),
('marseyzeldalinktoon',2,'marsey zelda nintendo game video legend of vidya adventure hyrule toon link shield sword ww wind waker gba four hourglass phantom st spirit tracks ds gamecube sea triforce',1671477145),
('marseyzeldalinktoonblue',2,'marsey zelda nintendo game video legend of vidya adventure hyrule toon link shield sword blue gba ds four triforce hero',1671477210),
('marseyzeldalinktoonpurple',2,'marsey zelda nintendo game video legend of vidya adventure hyrule toon link shield sword gba four purple',1671477249),
('marseyzeldalinktoonred',2,'marsey zelda nintendo game video legend of vidya adventure hyrule toon link shield sword triforce hero red gba ds gameboy four',1671477286),
('marseyzeldalinktwilight',2,'marsey zelda nintendo game video legend of vidya adventure hyrule link tp gamecube wii twilight princess wolf shield sword hero chainmail',1671476644),
('marseyzeldamidna',2,'marsey zelda nintendo game video legend of vidya adventure hyrule realm midna princess wii gamecube tp twilight companion',1671410646),
('marseyzeldasheik',2,'marsey zelda nintendo game video legend of vidya adventure hyrule sheik princess crosdress ninja oot ocarina time n64 mask sheika',1671476988),
('marseyzeldaskyward',2,'marsey zelda nintendo game video legend of vidya adventure hyrule link hero sky skyward sword shield wii motion chainmail courage fi master ss',1671476875),
('marseyzeldatetra',2,'marsey zelda nintendo game video legend of vidya adventure hyrule tetra princess pirate toon wind waker hourglass phantom ww gamecube waker wind sea ph',1671476807),
('marseyzeldatingle',2,'marsey zelda nintendo game video legend of vidya adventure hyrule tingle elf fairy baloon triforce mm majora ww waker wind tuner rupee mask',1671468441),
('marseyzelensky',2,'poor ukraine beg gibs',1671725473),
('marseyzizek',2,'zizek philosophy philosopher communism marxism nose slovenian slavic critique',NULL),
('marseyzodiac',2,'zodiac killer zodiackiller tedcruz ted cruz murderer crazy mask gun shooter shooting death',NULL),
('marseyzodiac2',2,'halloween killer zodiac tedcruise gun horror violence serial',1666290517),
('marseyzombie',2,'dead undead eye horror intestines halloween holiday monster',NULL),
('marseyzombie2',2,'undead living dead romero halloween horror corpse scary rotten',NULL),
('marseyzombietroll',2,'halloween undead',1666460457),
('marseyzombiewolfamogus',2,'amongus among us stonetoss sussy baka imposter impostor fraud fake phony',NULL),
('marseyzombiewolflove',2,'hug cuddle love marseylove zombiewolf zombie wolf',NULL),
('marseyzombiewolfmarseymask',2,'sussy amogus fraud fake phony cope seethe',NULL),
('marseyzombiewolftrample',2,'kill murder mascot animated walking animated tramplewolf',NULL),
('marseyzoomer',2,'child brat kid zoomie',NULL),
('marseyzoomercide',2,'weak genz genocide woke young animated',1673511207),
('marseyzoomerimplosion',2,'weak genz genocide woke young retard dumb explode boom terrorist animated',1673511240),
('marseyzwei',2,'drinking germany lederhosen zweirama bavarian beer',NULL),
('marsheen',2,'pusheen animated meme cute',NULL),
('marsheep',2,'sheep animal fluffy wool',NULL),
('marsheepnpc',2,'follower',NULL),
('marsie',2,'cartoon disney',NULL),
('marsoy',2,'soyboy soybeard nintendo gamer switch marsey gaymer pointing',NULL),
('marsoy2',2,'soy wojak soyjak soyjack nerd numale redditor',NULL),
('marsoyhype',2,'soyboy soybeard nerd marsey excited wojak cuck',NULL),
('marstolfo',2,'astolfo anime femboy cute blowkiss love heart justcool393 trap warrior',NULL),
('mcmarsey',2,'wageslave poor mcdonalds wagecuck maccas antiwork college wagie',NULL),
('merdesey',2,'turd turdsey shitsey poopsey shit poop poop marsey shit marsey',NULL),
('mersya',2,'the best adorable aww marsey favorite cute',NULL),
('mersya2',2,'drawing art',NULL),
('mlm',2,'marseylivesmatter marsey lives matter blm',NULL),
('owlsey',2,'bird hoot feathers',NULL),
('schopenmarsey',2,'schopenhauer philosophy german will ethics metaphysics',NULL),
('thinbluefeline',2,'cops police',NULL)
ON CONFLICT (name) DO UPDATE SET tags = EXCLUDED.tags;
