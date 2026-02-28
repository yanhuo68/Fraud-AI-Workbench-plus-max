CREATE TABLE Users (
    user_id INT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100),
    phone VARCHAR(20),
    account_age INT,  -- in days
    risk_score DECIMAL(3,2),
    registration_date DATE,
    status VARCHAR(20)
);

-- Sample Data (25 rows)
INSERT INTO Users (user_id, name, email, phone, account_age, risk_score, registration_date, status) VALUES
(101, 'Alice Johnson', 'alice.j@email.com', '+1-555-0101', 365, 1.2, '2023-01-15', 'active'),
(102, 'Bob Smith', 'bob.smith@email.com', '+1-555-0102', 120, 4.8, '2023-09-15', 'under_review'),
(103, 'Carol Davis', 'carol.d@email.com', '+1-555-0103', 45, 2.1, '2023-12-10', 'active'),
(104, 'David Wilson', 'david.w@email.com', '+1-555-0104', 600, 1.0, '2022-06-20', 'active'),
(105, 'Eva Brown', 'eva.b@email.com', '+1-555-0105', 30, 7.5, '2024-01-05', 'suspended'),
(106, 'Frank Miller', 'frank.m@email.com', '+1-555-0106', 200, 3.2, '2023-06-15', 'active'),
(107, 'Grace Lee', 'grace.l@email.com', '+1-555-0107', 90, 5.1, '2023-10-25', 'under_review'),
(108, 'Henry Chen', 'henry.c@email.com', '+1-555-0108', 720, 0.8, '2022-02-14', 'active'),
(109, 'Ivy Garcia', 'ivy.g@email.com', '+1-555-0109', 180, 2.5, '2023-07-20', 'active'),
(110, 'Jack Taylor', 'jack.t@email.com', '+1-555-0110', 15, 8.9, '2024-01-20', 'suspended'),
(111, 'Karen Martinez', 'karen.m@email.com', '+1-555-0111', 400, 1.8, '2022-12-01', 'active'),
(112, 'Leo Anderson', 'leo.a@email.com', '+1-555-0112', 60, 6.3, '2023-11-15', 'under_review'),
(113, 'Mia Thomas', 'mia.t@email.com', '+1-555-0113', 300, 2.0, '2023-03-10', 'active'),
(114, 'Noah Jackson', 'noah.j@email.com', '+1-555-0114', 150, 4.1, '2023-08-25', 'under_review'),
(115, 'Olivia White', 'olivia.w@email.com', '+1-555-0115', 500, 1.5, '2022-09-10', 'active'),
(116, 'Paul Harris', 'paul.h@email.com', '+1-555-0116', 80, 7.2, '2023-11-05', 'suspended'),
(117, 'Quinn Clark', 'quinn.c@email.com', '+1-555-0117', 250, 2.9, '2023-05-20', 'active'),
(118, 'Rachel Lewis', 'rachel.l@email.com', '+1-555-0118', 100, 5.5, '2023-10-15', 'under_review'),
(119, 'Sam Walker', 'sam.w@email.com', '+1-555-0119', 650, 1.1, '2022-04-30', 'active'),
(120, 'Tina Hall', 'tina.h@email.com', '+1-555-0120', 35, 8.2, '2024-01-01', 'suspended'),
(121, 'Uma Allen', 'uma.a@email.com', '+1-555-0121', 420, 1.9, '2022-11-15', 'active'),
(122, 'Victor Young', 'victor.y@email.com', '+1-555-0122', 75, 6.8, '2023-10-30', 'suspended'),
(123, 'Wendy King', 'wendy.k@email.com', '+1-555-0123', 280, 2.4, '2023-04-05', 'active'),
(124, 'Xander Scott', 'xander.s@email.com', '+1-555-0124', 190, 3.8, '2023-07-05', 'under_review'),
(125, 'Yvonne Wright', 'yvonne.w@email.com', '+1-555-0125', 320, 2.1, '2023-02-28', 'active');