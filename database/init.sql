CREATE DATABASE IF NOT EXISTS employee_db;
USE employee_db;

CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    department VARCHAR(100)
);

CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    employee_id INT,
    task_name VARCHAR(255) NOT NULL,
    status VARCHAR(30) DEFAULT 'Pending',
    FOREIGN KEY (employee_id) REFERENCES employees(id) ON DELETE CASCADE
);

INSERT INTO employees (name, email, department) VALUES
('Newton', 'newton@example.com', 'DevOps'),
('Ravi', 'ravi@example.com', 'Database');

INSERT INTO tasks (employee_id, task_name, status) VALUES
(1, 'Kubernetes deployment', 'Pending'),
(2, 'MariaDB backup', 'Completed');
