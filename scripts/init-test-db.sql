DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'reason_test') THEN
        CREATE DATABASE reason_test;
    END IF;
END $$;
