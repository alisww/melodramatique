-- create main table
CREATE TABLE documents (
    doc_id uuid PRIMARY KEY,
    object jsonb
);

CREATE TABLE users (
	username text PRIMARY KEY,
	hash text
);

-- creates index on documents for faster JSONPATH matching
CREATE INDEX doc_idx ON documents USING gin (object jsonb_path_ops);

-- creates full text search index
CREATE INDEX fts_summary_idx ON documents USING gin (to_tsvector('portuguese', (object ->> 'summary'::text)));
CREATE INDEX fts_ocr_idx ON documents USING gin (to_tsvector('portuguese', (object ->> 'ocr'::text)));
