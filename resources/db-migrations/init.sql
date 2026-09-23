CREATE TABLE customer(
customer_id INT AUTO_INCREMENT,
first_name VARCHAR(20) NOT NULL,
last_name VARCHAR(20) NOT NULL,
email VARCHAR(50) UNIQUE NOT NULL,
status VARCHAR(20) NOT NULL DEFAULT 'REGULAR',
PRIMARY KEY(customer_id)
);


CREATE TABLE orders(
order_id INT AUTO_INCREMENT,
customer_id INT NOT NULL,
item_name VARCHAR(50) NOT NULL,
price DECIMAL(5,2) NOT NULL DEFAULT 0.00,
PRIMARY KEY(order_id),
FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);


INSERT INTO customer (first_name, last_name, email)
VALUES
('John', 'Smith', 'john.smith@example.com'),
('Sarah', 'Johnson', 'sarah.johnson@example.com'),
('Michael', 'Brown', 'michael.brown@example.com'),
('Emily', 'Davis', 'emily.davis@example.com'),
('David', 'Wilson', 'david.wilson@example.com');


INSERT INTO orders (customer_id, item_name, price)
VALUES
(1, 'Laptop', 899.99),
(2, 'Wireless Mouse', 29.99),
(3, 'Keyboard', 79.50),
(4, 'USB-C Cable', 14.99),
(5, 'Monitor', 249.99);
