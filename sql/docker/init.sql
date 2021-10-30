CREATE DATABASE seedling CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci;
CREATE USER 'seedling' IDENTIFIED WITH mysql_native_password BY 'password';
GRANT ALL PRIVILEGES ON seedling.* TO 'seedling';
-- Need to grant access to test database even though we don't create it until running the tests
GRANT ALL PRIVILEGES ON test_seedling.* TO 'seedling';
