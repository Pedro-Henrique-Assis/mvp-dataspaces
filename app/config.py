import os


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "chave-apenas-para-desenvolvimento")
    MYSQL_CONFIG = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "database": os.getenv("MYSQL_DATABASE", "dataspaces_mvp"),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
    }
    TRUSTED_ISSUER_DID = "did:example:dataspace-authority"
