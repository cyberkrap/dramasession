from collections import OrderedDict

DEFAULT_USERNAME_EFFECT_PRICE = 75_000
FLAG_USERNAME_EFFECT_PRICE = 100_000
PARTY_USERNAME_EFFECT_PRICE = 250_000
FLAG_EFFECT_KEYS = frozenset({'china', 'israel', 'japan', 'uk', 'ukraine', 'usa'})

_EFFECT_ROWS = [
    ('acid', 'Acid', 'One Wish Willow said this was a normal Tuesday.', 'Neon'),
    ('aurora', 'Aurora', 'Pretty lights for people with ugly posting habits.', 'Atmospheric'),
    ('barbershop', 'Barbershop', 'A quarter for the cut; the obsession is free.', 'Pattern'),
    ('barrage', 'Barrage', "You're the bomb.", 'Energy'),
    ('bee', 'Bee', 'Caution: bees at work ahead!', 'Pattern'),
    ('blood', 'Blood', 'For when your Nikki obsession stops being metaphorical.', 'Dark'),
    ('blossom', 'Blossom', 'Makes your heart flutter.', 'Nature'),
    ('bubbles', 'Bubbles', "Don't let anyone burst your bubble.", 'Pattern'),
    ('bux', 'Bux', 'Here come the Wishbux.', 'Luxury'),
    ('candycane', 'Candy Cane', 'Festive stripes for your annual parasocial relapse.', 'Seasonal'),
    ('candycorn_darker', 'Candy Corn', 'The candy nobody wanted, now attached to your identity.', 'Seasonal'),
    ('china', 'China', 'Made in China.', 'Flags'),
    ('coins', 'Coins', "It's just common cents.", 'Luxury'),
    ('diamond', 'Diamond', "For your engagement ring to Nikki's comment section.", 'Luxury'),
    ('disco', 'Disco', 'The afterparty you were not invited to.', 'Neon'),
    ('effeminate', 'Effeminate', 'Serving more wrist than a freaky Nikki reaction gif.', 'Neon'),
    ('error', 'ERROR', 'Missing texture. Nikki.exe has stopped responding.', 'Texture'),
    ('explosive', 'Explosive', 'KA-BOOM!', 'Energy'),
    ('fire_dark', 'Dark Fire', "Now you're really playing with fire!", 'Dark'),
    ('fishy', 'Fishy', 'What a load of carp!', 'Nature'),
    ('fur', 'Fur', 'Fur is murder. Your posting streak is attempted manslaughter.', 'Texture'),
    ('galaxy', 'Galaxy', "There's plenty of space. None of it is between you and Nikki.", 'Atmospheric'),
    ('glitched', 'Glitched', 'VHS found footage from the MySpace era.', 'Texture'),
    ('gold_dark', 'Dark Gold', 'A prestigious golden shimmer for the truly obsessed.', 'Luxury'),
    ('heavenly', 'Heavenly', 'A little divine lighting.', 'Atmospheric'),
    ('hellish', 'Hellish', 'Better to reign in Hell than wait for a reply.', 'Dark'),
    ('holographic', 'Holographic', 'A fake light show for a very real obsession.', 'Luxury'),
    ('incandescent', 'Incandescent', 'Nikki walked in and the whole frame lit up.', 'Atmospheric'),
    ('interference', 'Interference', 'The signal is bad. The obsession is crystal clear.', 'Texture'),
    ('israel', 'Israel', 'This effect was promised to you 3000 years ago.', 'Flags'),
    ('japan', 'Japan', 'Imported from the folder you swear is just fan art.', 'Flags'),
    ('lasers', 'Lasers', 'Remain focused. Nikki posted again.', 'Neon'),
    ('lemonparty', 'Lemon Party', 'A citrus-themed mistake you cannot unsee.', 'Psychedelic'),
    ('lightning', 'Lightning', 'One Wish Willow touched the router again.', 'Energy'),
    ('lsd', 'LSD', 'The effect is working. Your monitor is innocent.', 'Psychedelic'),
    ('milkyway', 'Milky Way', 'Lost in space, still online.', 'Atmospheric'),
    ('nether', 'Nether', 'Proudly display your nether regions.', 'Dark'),
    ('party', 'Party', 'Every colour at once because restraint is for lurkers.', 'Psychedelic'),
    ('radioactive', 'Radioactive', 'Your obsession has reached unsafe levels.', 'Energy'),
    ('rainbow', 'Rainbow', 'A dazzling rainbow for every flavour of obsession.', 'Psychedelic'),
    ('rome', 'Rome', 'All roads lead back to Nikki.', 'Atmospheric'),
    ('siren', 'Siren', 'WeeWoo WeeWoo WeeWoo!', 'Energy'),
    ('spill', 'Spill', 'A happy little accident.', 'Texture'),
    ('splash', 'Splash', 'Splish splash.', 'Nature'),
    ('splatter', 'Splatter', 'Repaint your sins.', 'Texture'),
    ('stargate', 'Stargate', 'Go through this and you might enter another timeline.', 'Psychedelic'),
    ('stars', 'Stars', 'Reach for the stars. Settle for another refresh.', 'Atmospheric'),
    ('static', 'Static', 'Is something wrong with your screen?', 'Texture'),
    ('steel', 'Steel', 'For fans of heavy metal and heavier attachment issues.', 'Luxury'),
    ('submerge', 'Submerge', 'Going under. Still refreshing.', 'Nature'),
    ('sunbeams', 'Sunbeams', "You've got flare. Nikki has the restraining order.", 'Atmospheric'),
    ('swirly', 'Swirly', 'Photoreceptors beware.', 'Psychedelic'),
    ('synthwave', 'Synthwave', 'Go back to the 80s. 🎵', 'Neon'),
    ('tartan', 'Tartan', 'Scotland forever.', 'Pattern'),
    ('tiedye', 'Tie-Dye', 'Groovy.', 'Psychedelic'),
    ('uk', 'UK', 'This is Pound (£) Town.', 'Flags'),
    ('ukraine', 'Ukraine', 'Blue, gold, and better organised than your saved edits.', 'Flags'),
    ('usa', 'USA', 'Many Constitutional Calories.', 'Flags'),
    ('valid', 'Valid', 'Let everyone know your obsession has been peer reviewed.', 'Pattern'),
    ('vaporwave', 'Vaporwave', '[ v a p o r w a v e ]', 'Neon'),
    ('water', 'Water', 'Remember to stay hydrated between refreshes.', 'Nature'),
    ('weed', 'Weed', 'Dude weed lmao!', 'Nature'),
    ('yoonseul', 'Yoonseul', "A little shimmer for Nikki's MySpace era.", 'Atmospheric'),
]


def _price_for(key):
    if key == 'party':
        return PARTY_USERNAME_EFFECT_PRICE
    if key in FLAG_EFFECT_KEYS:
        return FLAG_USERNAME_EFFECT_PRICE
    return DEFAULT_USERNAME_EFFECT_PRICE


USERNAME_EFFECTS = OrderedDict(
    (
        key,
        {
            'key': key,
            'title': title,
            'description': description,
            'category': category,
            'price': _price_for(key),
            'asset_url': f'/assets/images/username_effects/{key}.webp?v=8',
        },
    )
    for key, title, description, category in _EFFECT_ROWS
)

USERNAME_EFFECT_KEYS = frozenset(USERNAME_EFFECTS)
USERNAME_EFFECT_CATEGORIES = tuple(
    dict.fromkeys(effect['category'] for effect in USERNAME_EFFECTS.values())
)
