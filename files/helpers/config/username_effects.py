from collections import OrderedDict

USERNAME_EFFECT_PRICE = 100_000

_EFFECT_ROWS = [
    ('acid', 'Acid', 'Liquid neon shifts through every letter.', 'Neon'),
    ('aurora', 'Aurora', 'Slow polar light rolls across your name.', 'Atmospheric'),
    ('bee', 'Bee', 'Honey-gold stripes with a sharp black contrast.', 'Pattern'),
    ('blood', 'Blood', 'A deep crimson flow for a darker nameplate.', 'Dark'),
    ('candycane', 'Candy Cane', 'Animated red and white candy stripes.', 'Seasonal'),
    ('candycorn_darker', 'Candy Corn', 'Warm orange, gold, and cream bands.', 'Seasonal'),
    ('china', 'China', 'A vivid red flag texture with gold highlights.', 'Flags'),
    ('diamond', 'Diamond', 'Cold crystalline light flashes through the text.', 'Luxury'),
    ('effeminate', 'Effeminate', 'A soft prismatic shimmer with playful color.', 'Neon'),
    ('fire_dark', 'Dark Fire', 'Hot embers and flame moving through a dark base.', 'Dark'),
    ('fishy', 'Fishy', 'An aquatic scale texture that keeps moving.', 'Nature'),
    ('fur', 'Fur', 'A tactile animated fur pattern for heavier lettering.', 'Texture'),
    ('galaxy', 'Galaxy', 'Deep-space color clouds drift behind the username.', 'Atmospheric'),
    ('gold_dark', 'Dark Gold', 'Muted metallic gold with a rich shadowed finish.', 'Luxury'),
    ('israel', 'Israel', 'A blue and white flag texture clipped to the name.', 'Flags'),
    ('japan', 'Japan', 'A clean red and white flag-inspired treatment.', 'Flags'),
    ('lasers', 'Lasers', 'Fast neon beams cut across the username.', 'Neon'),
    ('lightning', 'Lightning', 'Electric flashes crackle through each letter.', 'Energy'),
    ('lsd', 'LSD', 'Aggressive psychedelic color motion.', 'Psychedelic'),
    ('nether', 'Nether', 'A molten underworld texture with dark red depth.', 'Dark'),
    ('party', 'Party', 'Rapid color changes for a constantly moving name.', 'Psychedelic'),
    ('rainbow', 'Rainbow', 'A full-spectrum animated gradient.', 'Psychedelic'),
    ('siren', 'Siren', 'Alternating emergency-light color pulses.', 'Energy'),
    ('splatter', 'Splatter', 'Paint-like bursts move through the text.', 'Texture'),
    ('stars', 'Stars', 'A moving star field with a crisp nighttime glow.', 'Atmospheric'),
    ('static', 'Static', 'Television noise flickers across the username.', 'Texture'),
    ('steel', 'Steel', 'Brushed metal motion with a cool silver finish.', 'Luxury'),
    ('sunbeams', 'Sunbeams', 'Warm rays sweep across the lettering.', 'Atmospheric'),
    ('synthwave', 'Synthwave', 'Retro magenta and blue motion inspired by neon nights.', 'Neon'),
    ('uk', 'United Kingdom', 'The Union Jack rendered as an animated text texture.', 'Flags'),
    ('ukraine', 'Ukraine', 'Blue and gold flag colors move through the name.', 'Flags'),
    ('usa', 'United States', 'A stars-and-stripes texture clipped to the username.', 'Flags'),
    ('valid', 'Valid', 'A sharp high-contrast verification-style pattern.', 'Pattern'),
    ('vaporwave', 'Vaporwave', 'Pastel retro color motion with a dreamy finish.', 'Neon'),
    ('water', 'Water', 'Clear blue ripples flow across the text.', 'Nature'),
    ('weed', 'Weed', 'A dense animated botanical texture.', 'Nature'),
]

USERNAME_EFFECTS = OrderedDict(
    (
        key,
        {
            "key": key,
            "title": title,
            "description": description,
            "category": category,
            "price": USERNAME_EFFECT_PRICE,
            "asset_url": f"/assets/images/username_effects/{key}.webp?v=1",
        },
    )
    for key, title, description, category in _EFFECT_ROWS
)

USERNAME_EFFECT_KEYS = frozenset(USERNAME_EFFECTS)
USERNAME_EFFECT_CATEGORIES = tuple(
    dict.fromkeys(effect["category"] for effect in USERNAME_EFFECTS.values())
)
