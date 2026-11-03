-- Lectura de evidencia para el rol de QA. Idempotente.
GRANT CONNECT ON DATABASE finbank TO finbank_qa_reader;
GRANT USAGE ON SCHEMA public TO finbank_qa_reader;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO finbank_qa_reader;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA public TO finbank_qa_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE finbank IN SCHEMA public
  GRANT SELECT ON TABLES TO finbank_qa_reader;
ALTER DEFAULT PRIVILEGES FOR ROLE finbank IN SCHEMA public
  GRANT SELECT ON SEQUENCES TO finbank_qa_reader;
