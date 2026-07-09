CREATE TYPE casino_game_kind AS ENUM ('blackjack', 'slots');

CREATE TYPE casino_game_currency AS ENUM ('coins', 'procoins');

CREATE TABLE casino_games (
    id SERIAL PRIMARY KEY,
    user_id integer NOT NULL REFERENCES users(id),
    created_utc integer NOT NULL,
    active boolean NOT NULL DEFAULT true,
    currency casino_game_currency NOT NULL,
    wager integer NOT NULL,
    winnings integer NOT NULL,
    kind casino_game_kind NOT NULL,
    game_state jsonb NOT NULL
);
