from loguru import logger


def lazy_hook():
    try:
        import app.database.db

        origin_init_db = app.database.db.init_db

        def hijack_all():
            from bizydraft.hijack_nodes import hijack_nodes
            from bizydraft.hijack_routes import hijack_routes

            hijack_nodes()
            hijack_routes()

        def new_init_db():
            hijack_all()
            origin_init_db()

        app.database.db.init_db = new_init_db

    except Exception as e:
        logger.error(f"failed to lazyhook: {e}")
        exit(1)
