# Obsession Forum

Obsession Forum is a movie-related community website for discussion, profiles, badges, public chat, moderation, and shared discoveries.

## Features

- Forum posts and threaded comments
- User profiles and account pages
- Badges and community identity features
- Public chat for live community discussion
- Voting and ranking mechanics
- Moderation and admin tools
- Docker-based local setup

## Tech Stack

- Python / Flask
- PostgreSQL
- Redis
- Docker / Docker Compose
- JavaScript, CSS, and server-rendered templates

## Local Installation

1. Install Docker and Docker Compose.

2. Copy the environment template:

```sh
cp env_template .env
```

On Windows PowerShell:

```powershell
Copy-Item env_template .env
```

3. Start the application:

```sh
docker-compose up
```

4. Open the site in your browser:

```text
http://localhost
```

The first account created locally receives full admin access.

## Environment Setup

The `.env` file is required for local development. Start from `env_template`, then adjust values for your local environment as needed.

Never commit secrets, keys, tokens, passwords, or local credentials. Keep `.env` and other private configuration files out of version control.

## Development Workflow

1. Run the project locally with Docker Compose.
2. Make source, template, or asset changes.
3. Test changes in the browser at `http://localhost`.
4. Commit and push the finished work.

## License

This project is licensed under AGPL-3.0. See [LICENSE](LICENSE).