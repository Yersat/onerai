-- Create databases
CREATE DATABASE onerai;
CREATE DATABASE partners_onerai;

-- Create users with passwords
CREATE USER onerai_user WITH PASSWORD 'onerai_password';
CREATE USER partners_onerai_user WITH PASSWORD 'partners_onerai_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE onerai TO onerai_user;
GRANT ALL PRIVILEGES ON DATABASE partners_onerai TO partners_onerai_user;

-- Connect to onerai database and grant schema privileges
\c onerai
GRANT ALL ON SCHEMA public TO onerai_user;

-- Connect to partners_onerai database and grant schema privileges
\c partners_onerai
GRANT ALL ON SCHEMA public TO partners_onerai_user;
