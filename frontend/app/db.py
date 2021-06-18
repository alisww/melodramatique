import asyncpg, json, uuid
from werkzeug.security import check_password_hash
from quart import Quart


class MelodramatiqueDB:
    def __init__(self, app: Quart, uri: str) -> None:
        self.init_app(app)
        self._pool = None
        self.uri = uri

    def init_app(self, app: Quart) -> None:
        app.before_serving(self._before_serving)
        app.after_serving(self._after_serving)

    async def _before_serving(self) -> None:
        self._pool = await asyncpg.create_pool(self.uri)

    async def _after_serving(self) -> None:
        await self._pool.close()

    async def check_user(self, user, password) -> bool:
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM users WHERE username = $1", user)
            if not row:
                return False

            return check_password_hash(row["hash"], password)

    async def add_doc(self, doc, doc_id=uuid.uuid4()):
        async with self._pool.acquire() as conn:
            doc["id"] = str(doc_id)
            await conn.execute(
                """
                INSERT INTO documents (doc_id, object)
                VALUES ($1, $2)
                ON CONFLICT (doc_id) DO UPDATE SET object = $2
            """,
                doc_id,
                json.dumps(doc),
            )

    async def get_tags(self, field):
        async with self._pool.acquire() as conn:
            res = await conn.fetch(
                """SELECT DISTINCT trim('"' FROM jsonb_array_elements(object->$1)::text) AS tag FROM documents""",
                field,
            )
            return list(filter(lambda x: x != "", map(lambda x: x["tag"], res)))

    async def get_by_id(self,doc_id):
        async with self._pool.acquire() as conn:
            res = await conn.fetchrow(
                """SELECT object FROM documents WHERE doc_id = $1""",
                doc_id
            )
            return json.loads(res["object"])
