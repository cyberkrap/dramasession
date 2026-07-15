#!/bin/sh
set -eu

: "${SITE:?SITE is required}"
: "${SITE_NAME:?SITE_NAME is required}"
: "${SECRET_KEY:?SECRET_KEY is required}"
: "${DATABASE_URL:?DATABASE_URL is required}"
: "${REDIS_URL:?REDIS_URL is required}"

export PORT="${PORT:-8080}"
export LOG_DIRECTORY="${LOG_DIRECTORY:-/data/logs}"
export SETTINGS_FILENAME="${SETTINGS_FILENAME:-/data/site_settings.json}"
export DEFAULT_ASSETS_FILE="${DEFAULT_ASSETS_FILE:-/data/default_assets.json}"
export DEFAULT_ASSET_DIR="${DEFAULT_ASSET_DIR:-/data/default_assets}"
export ASSET_SUBMISSIONS_ROOT="${ASSET_SUBMISSIONS_ROOT:-/data/asset_submissions}"
export COMMUNITY_ASSET_ROOT="${COMMUNITY_ASSET_ROOT:-/data/community_assets}"
case "${DATABASE_URL}" in
	postgres://*) export DATABASE_URL="postgresql://${DATABASE_URL#postgres://}" ;;
esac

mkdir -p "$LOG_DIRECTORY" "$ASSET_SUBMISSIONS_ROOT" "$COMMUNITY_ASSET_ROOT" \
	/data/images /data/audio /data/videos /data/songs /data/chat_images /data/dm_images \
	/data/assets/images/emojis /data/assets/images/hats /data/default_assets \
	"$COMMUNITY_ASSET_ROOT/banners" "$COMMUNITY_ASSET_ROOT/sidebar" \
	"$ASSET_SUBMISSIONS_ROOT/banner_submissions" "$ASSET_SUBMISSIONS_ROOT/sidebar_submissions"

link_data_dir() {
	name="$1"
	if [ -e "/$name" ] && [ ! -L "/$name" ]; then
		cp -a "/$name/." "/data/$name/" 2>/dev/null || true
		rm -rf "/$name"
	fi
	ln -sfn "/data/$name" "/$name"
}

for directory in images audio videos songs chat_images dm_images; do
	link_data_dir "$directory"
done

copy_and_link() {
	source="$1"
	target="$2"
	mkdir -p "$target"
	if [ -d "$source" ] && [ ! -L "$source" ]; then
		cp -a "$source/." "$target/" 2>/dev/null || true
		rm -rf "$source"
	fi
	ln -sfn "$target" "$source"
}

copy_and_link /app/files/assets/images/emojis /data/assets/images/emojis
copy_and_link /app/files/assets/images/hats /data/assets/images/hats
copy_and_link /app/files/assets/images/Obsession/banners "$COMMUNITY_ASSET_ROOT/banners"
copy_and_link /app/files/assets/images/Obsession/sidebar "$COMMUNITY_ASSET_ROOT/sidebar"
copy_and_link /app/files/assets/images/Obsession/defaults /data/default_assets
copy_and_link /app/asset_submissions "$ASSET_SUBMISSIONS_ROOT"

if [ ! -f "$DEFAULT_ASSETS_FILE" ]; then
	cp /app/files/assets/default_assets.json "$DEFAULT_ASSETS_FILE"
fi
if [ ! -f "$SETTINGS_FILENAME" ]; then
	cp /app/production_settings.json "$SETTINGS_FILENAME"
fi

envsubst '${PORT}' < /app/nginx.production.conf.template > /etc/nginx/nginx.conf
python /app/production_init.py
exec /usr/bin/supervisord -c /app/supervisord.production.conf -n
