import psycopg2, json, uuid
from psycopg2.extras import Json
psycopg2.extras.register_uuid()

with open("out.json") as f:
    conn = psycopg2.connect('dbname=melodramatique-dev')
    cur = conn.cursor()
    for doc in json.load(f):
        id = uuid.uuid4()
        doc['id'] = str(id)
        doc['authors'] = [doc.pop('author')]
        doc['newspaper'] = [doc.pop('newspaper')]
        doc['mentioned_orgs'] = list(map(lambda x: x.lstrip(), doc['mentioned_orgs']))
        doc['mentioned_works'] = list(map(lambda x: x.lstrip(), doc['mentioned_works']))
        doc['mentioned_authors'] = list(map(lambda x: x.lstrip(), doc['mentioned_authors']))
        cur.execute("INSERT INTO documents (doc_id,object) VALUES (%s,%s)", [id,Json(doc)])
    conn.commit()
    cur.close()
    conn.close()
