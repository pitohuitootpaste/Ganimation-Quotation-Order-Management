import hashlib
import os


def get_connection():
    try:
        import psycopg
    except ModuleNotFoundError as error:
        raise RuntimeError("Install the project requirements first.") from error

    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not configured.")

    return psycopg.connect(database_url)


def create_tables():
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS customer_response_links (
                client_id TEXT NOT NULL,
                quotation_id BIGINT NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                decision TEXT CHECK (decision IN ('accepted', 'declined')),
                created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                responded_at TIMESTAMPTZ,
                PRIMARY KEY (client_id, quotation_id)
            )
            """
        )


def save_response_link(quotation, token):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    with get_connection() as connection:
        existing = connection.execute(
            """SELECT decision FROM customer_response_links
            WHERE client_id = %s AND quotation_id = %s""",
            (quotation["client_id"], quotation["quotation_id"])
        ).fetchone()

        if existing and existing[0]:
            raise ValueError("This quotation already has a customer response.")

        connection.execute(
            """
            INSERT INTO customer_response_links (
                client_id, quotation_id, token_hash, decision, created_at, responded_at
            )
            VALUES (%s, %s, %s, NULL, NOW(), NULL)
            ON CONFLICT (client_id, quotation_id) DO UPDATE SET
                token_hash = EXCLUDED.token_hash,
                created_at = NOW()
            """,
            (
                quotation["client_id"],
                quotation["quotation_id"],
                token_hash
            )
        )


def record_decision(token, decision):
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()

    with get_connection() as connection:
        row = connection.execute(
            """
            UPDATE customer_response_links
            SET decision = %s, responded_at = NOW()
            WHERE token_hash = %s AND decision IS NULL
            RETURNING quotation_id
            """,
            (decision, token_hash)
        ).fetchone()

        if row:
            return True

        exists = connection.execute(
            "SELECT decision FROM customer_response_links WHERE token_hash = %s",
            (token_hash,)
        ).fetchone()

        if exists:
            raise ValueError("A response has already been submitted for this quotation.")

        raise LookupError("This response link is invalid or has expired.")


def get_customer_responses():
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT client_id, quotation_id, decision
            FROM customer_response_links
            WHERE decision IS NOT NULL
            ORDER BY responded_at
            """
        ).fetchall()

    return [
        {"client_id": row[0], "quotation_id": row[1], "decision": row[2]}
        for row in rows
    ]
