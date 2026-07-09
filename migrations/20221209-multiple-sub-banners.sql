UPDATE subactions SET kind = 'upload_banner' WHERE kind = 'change_banner'; -- update mod actions

ALTER TABLE subs RENAME COLUMN bannerurl TO bannerurls;
ALTER TABLE subs ALTER COLUMN bannerurls TYPE VARCHAR(60)[] USING ARRAY[bannerurls];
ALTER TABLE subs ALTER COLUMN bannerurls SET DEFAULT '{}';
ALTER TABLE subs ALTER COLUMN bannerurls SET NOT NULL; -- multiple banners <3

UPDATE subs SET bannerurls = '{}' WHERE bannerurls = '{NULL}'; -- update subs with no banners
