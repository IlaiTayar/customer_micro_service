DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customer_favorite_item;
DROP TABLE IF EXISTS customer;


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
item_id INT NOT NULL,
item_name VARCHAR(50) NOT NULL,
price DECIMAL(10,2) NOT NULL DEFAULT 0.00,
image_url VARCHAR(500),
PRIMARY KEY(order_id),
FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);



CREATE TABLE customer_favorite_item(
favorite_item_id INT AUTO_INCREMENT,
customer_id INT NOT NULL,
item_id INT NOT NULL,
PRIMARY KEY(favorite_item_id),
UNIQUE KEY uq_customer_favorite_item (customer_id, item_id),
FOREIGN KEY(customer_id) REFERENCES customer(customer_id)
);


INSERT INTO customer (first_name, last_name, email)
VALUES
('John', 'Smith', 'john.smith@example.com'),
('Sarah', 'Johnson', 'sarah.johnson@example.com'),
('Michael', 'Brown', 'michael.brown@example.com'),
('Emily', 'Davis', 'emily.davis@example.com'),
('David', 'Wilson', 'david.wilson@example.com');

INSERT INTO customer (customer_id, first_name, last_name, email, status)
VALUES
(100, 'Admin', 'User', 'admin@admin', 'REGULAR');


INSERT INTO orders (customer_id, item_id, item_name, price, image_url)
VALUES
(1, 1, 'Laptop', 999.99, 'https://images.unsplash.com/photo-1496181133206-80ce9b88a853'),
(2, 5, 'Mouse', 29.99, 'https://images.unsplash.com/photo-1527814050087-3793815479db'),
(3, 6, 'Keyboard', 49.99, 'https://images.unsplash.com/photo-1587829741301-dc798b83add3'),
(4, 13, 'USB Cable', 9.99, 'https://images.unsplash.com/photo-1625842268584-8f3296236761'),
(5, 4, 'Monitor', 199.99, 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf');
