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
	"$ASSET_SUBMISSIONS_ROOT/banner_submissions" "$ASSET_SUBMISSIONS_ROOT/sidebar_submissions" \
	"$ASSET_SUBMISSIONS_ROOT/marseys/pending" "$ASSET_SUBMISSIONS_ROOT/marseys/approved" \
	"$ASSET_SUBMISSIONS_ROOT/marseys/original" "$ASSET_SUBMISSIONS_ROOT/hats"

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
mkdir -p /data/default_assets
if [ ! -e /data/default_assets/profile.webp ] && [ -f /app/files/assets/images/Obsession/defaults/profile.webp ]; then
	cp /app/files/assets/images/Obsession/defaults/profile.webp /data/default_assets/profile.webp
fi
if [ -d /app/files/assets/images/Obsession/defaults ] && [ ! -L /app/files/assets/images/Obsession/defaults ]; then
	for default_file in /app/files/assets/images/Obsession/defaults/*; do
		[ -f "$default_file" ] || continue
		default_name="${default_file##*/}"
		if [ ! -e "/data/default_assets/$default_name" ]; then
			cp -a "$default_file" "/data/default_assets/$default_name"
		fi
	done
	rm -rf /app/files/assets/images/Obsession/defaults
fi
ln -sfn /data/default_assets /app/files/assets/images/Obsession/defaults
copy_and_link /app/asset_submissions "$ASSET_SUBMISSIONS_ROOT"

# Legacy emote/hat routes still address /asset_submissions directly. Point that
# path at the Railway volume too, so approved custom assets survive redeploys.
if [ -e /asset_submissions ] && [ ! -L /asset_submissions ]; then
	cp -a /asset_submissions/. "$ASSET_SUBMISSIONS_ROOT/" 2>/dev/null || true
	rm -rf /asset_submissions
fi
ln -sfn "$ASSET_SUBMISSIONS_ROOT" /asset_submissions

if [ ! -f "$DEFAULT_ASSETS_FILE" ]; then
	cp /app/files/assets/default_assets.json "$DEFAULT_ASSETS_FILE"
fi
if [ ! -f "$SETTINGS_FILENAME" ]; then
	cp /app/production_settings.json "$SETTINGS_FILENAME"
fi

envsubst '${PORT}' < /app/nginx.production.conf.template > /etc/nginx/nginx.conf
python /app/production_init.py
exec /usr/bin/supervisord -c /app/supervisord.production.conf -n
