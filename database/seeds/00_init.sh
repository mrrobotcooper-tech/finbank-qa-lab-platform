#!/bin/bash
set -euo pipefail

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
  DO \$\$
  BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'finbank_qa_reader') THEN
      CREATE ROLE finbank_qa_reader LOGIN PASSWORD '${QA_READER_PASSWORD}';
    END IF;
  END
  \$\$;

  GRANT CONNECT ON DATABASE ${POSTGRES_DB} TO finbank_qa_reader;
  GRANT USAGE ON SCHEMA public TO finbank_qa_reader;
  GRANT SELECT ON ALL TABLES IN SCHEMA public TO finbank_qa_reader;
  GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO finbank_qa_reader;
  ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} IN SCHEMA public
    GRANT SELECT ON TABLES TO finbank_qa_reader;
  ALTER DEFAULT PRIVILEGES FOR ROLE ${POSTGRES_USER} IN SCHEMA public
    GRANT SELECT ON SEQUENCES TO finbank_qa_reader;
EOSQL
