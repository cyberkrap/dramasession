from flask_caching import Cache


# Shared cache instance. Keep this outside files.__main__ so helper modules can
# import cache decorators without bootstrapping the Flask application.
cache = Cache()
