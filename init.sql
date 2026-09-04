CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    first_name VARCHAR(50),
    last_name VARCHAR(50),
    email VARCHAR(100),
    registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(100),
    category VARCHAR(50),
    price DECIMAL(10, 2)
);

CREATE TABLE orders (
    order_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    product_id INT REFERENCES products(product_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    quantity INT,
    total_amount DECIMAL(10, 2)
);

-- Insert dummy data
INSERT INTO users (first_name, last_name, email) VALUES 
('Alice', 'Smith', 'alice@example.com'),
('Bob', 'Jones', 'bob@example.com'),
('Charlie', 'Brown', 'charlie@example.com');

INSERT INTO products (product_name, category, price) VALUES 
('Wireless Mouse', 'Electronics', 25.99),
('Mechanical Keyboard', 'Electronics', 85.50),
('Desk Mat', 'Accessories', 15.00);

INSERT INTO orders (user_id, product_id, quantity, total_amount) VALUES 
(1, 1, 2, 51.98),
(2, 2, 1, 85.50),
(1, 3, 1, 15.00),
(3, 1, 1, 25.99);