-- Checking Table films' correct creation
USE recommendation;
DESC films;
SELECT * FROM films;

SELECT * FROM users;

-- Creation of Table users
CREATE TABLE users (
    id BINARY(16) DEFAULT (UUID()) NOT NULL PRIMARY KEY,
    username VARCHAR(10),
    password VARCHAR(20)
) DEFAULT CHARSET=utf8 COMMENT '';
-- Testing insertion
INSERT INTO users (username, password) VALUES ('admin', 'admin');