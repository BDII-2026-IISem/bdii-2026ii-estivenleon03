from django.core.exceptions import ImproperlyConfigured


def database_from_environ(env):
    engine = str(env.get("DB_ENGINE", "mysql")).strip().lower()
    legacy_engines = {
        "django.db.backends.postgresql": "django.db.backends.postgresql",
        "django.db.backends.mysql": "django.db.backends.mysql",
        "django.db.backends.oracle": "django.db.backends.oracle",
    }
    if engine in legacy_engines and env.get("DB_NAME"):
        config = {
            "ENGINE": legacy_engines[engine],
            "NAME": env["DB_NAME"],
            "USER": env.get("DB_USER", ""),
            "PASSWORD": env.get("DB_PASSWORD", ""),
            "HOST": env.get("DB_HOST", ""),
            "PORT": env.get("DB_PORT", ""),
        }
        if engine == "django.db.backends.mysql":
            config["OPTIONS"] = {"charset": "utf8mb4"}
        return {"default": config}

    builders = {
        "postgresql": _postgresql,
        "mysql": _mysql,
        "mssql": _mssql,
        "oracle": _oracle,
        "django.db.backends.postgresql": _postgresql,
        "django.db.backends.mysql": _mysql,
        "django.db.backends.oracle": _oracle,
        "sqlite": _sqlite,
        "sqlite3": _sqlite,
        "django.db.backends.sqlite3": _sqlite,
    }
    builder = builders.get(engine)
    if builder is None:
        raise ImproperlyConfigured(
            f"DB_ENGINE='{engine}' no es válido. "
            "Permitidos: postgresql, mysql, mssql, oracle."
        )
    return {"default": builder(env)}


def _required(env, key):
    value = env.get(key)
    if value is None or str(value).strip() == "":
        raise ImproperlyConfigured(
            f"Falta {key} para DB_ENGINE={env.get('DB_ENGINE')}."
        )
    return str(value).strip()


def _block(env, prefix, engine, options=None):
    config = {
        "ENGINE": engine,
        "NAME": _required(env, f"{prefix}_DB"),
        "USER": _required(env, f"{prefix}_USER"),
        "PASSWORD": _required(env, f"{prefix}_PASSWORD"),
        "HOST": _required(env, f"{prefix}_HOST"),
        "PORT": _required(env, f"{prefix}_PORT"),
    }
    if options:
        config["OPTIONS"] = options
    return config


def _postgresql(env):
    return _block(env, "POSTGRES", "django.db.backends.postgresql")


def _mysql(env):
    return _block(
        env,
        "MYSQL",
        "django.db.backends.mysql",
        {"charset": "utf8mb4"},
    )


def _mssql(env):
    return _block(
        env,
        "MSSQL",
        "mssql",
        {
            "driver": "ODBC Driver 18 for SQL Server",
            "extra_params": "TrustServerCertificate=yes",
        },
    )


def _oracle(env):
    host = _required(env, "ORACLE_HOST")
    port = _required(env, "ORACLE_PORT")
    service = _required(env, "ORACLE_SERVICE_NAME")
    dsn = (
        f"(DESCRIPTION=(ADDRESS=(PROTOCOL=TCP)(HOST={host})(PORT={port}))"
        f"(CONNECT_DATA=(SERVICE_NAME={service})))"
    )
    return {
        "ENGINE": "django.db.backends.oracle",
        "NAME": dsn,
        "USER": _required(env, "ORACLE_USER"),
        "PASSWORD": _required(env, "ORACLE_PASSWORD"),
        "HOST": host,
        "PORT": "",
    }


def _sqlite(env):
    name = env.get("DB_NAME")
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": name or ":memory:",
    }
