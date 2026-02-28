CREATE TABLE Devices (
    device_id INT PRIMARY KEY,
    device_type VARCHAR(50),
    os_version VARCHAR(50),
    last_seen DATETIME,
    is_trusted BOOLEAN,
    user_agent TEXT
);

-- Sample Data (20 rows)
INSERT INTO Devices (device_id, device_type, os_version, last_seen, is_trusted, user_agent) VALUES
(2001, 'iPhone 13', 'iOS 17.2', '2024-01-28 14:30:00', TRUE, 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X)'),
(2002, 'Samsung Galaxy S23', 'Android 14', '2024-01-28 10:15:00', TRUE, 'Mozilla/5.0 (Linux; Android 14; S23)'),
(2003, 'iPad Pro', 'iOS 16.6', '2024-01-27 22:45:00', TRUE, 'Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X)'),
(2004, 'Windows Laptop', 'Windows 11', '2024-01-28 09:00:00', TRUE, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
(2005, 'MacBook Pro', 'macOS 14.2', '2024-01-28 16:20:00', TRUE, 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'),
(2006, 'Unknown Device', 'Unknown', '2024-01-28 03:45:00', FALSE, 'Unknown/1.0'),
(2007, 'Google Pixel 7', 'Android 13', '2024-01-28 12:10:00', TRUE, 'Mozilla/5.0 (Linux; Android 13; Pixel 7)'),
(2008, 'iPhone XR', 'iOS 15.7', '2024-01-27 19:30:00', FALSE, 'Mozilla/5.0 (iPhone; CPU iPhone OS 15_7 like Mac OS X)'),
(2009, 'Android Tablet', 'Android 12', '2024-01-28 08:45:00', TRUE, 'Mozilla/5.0 (Linux; Android 12; Tablet)'),
(2010, 'Desktop PC', 'Windows 10', '2024-01-28 11:30:00', TRUE, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
(2011, 'iPhone 15', 'iOS 17.3', '2024-01-28 15:45:00', TRUE, 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X)'),
(2012, 'Samsung A54', 'Android 13', '2024-01-28 02:20:00', FALSE, 'Mozilla/5.0 (Linux; Android 13; A54)'),
(2013, 'MacBook Air', 'macOS 13.5', '2024-01-28 13:15:00', TRUE, 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'),
(2014, 'Windows Tablet', 'Windows 11', '2024-01-27 23:10:00', FALSE, 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'),
(2015, 'OnePlus 11', 'Android 14', '2024-01-28 07:30:00', TRUE, 'Mozilla/5.0 (Linux; Android 14; OnePlus11)'),
(2016, 'iPad Air', 'iOS 17.1', '2024-01-28 18:40:00', TRUE, 'Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X)'),
(2017, 'Linux Desktop', 'Ubuntu 22.04', '2024-01-28 14:00:00', TRUE, 'Mozilla/5.0 (X11; Linux x86_64)'),
(2018, 'iPhone SE', 'iOS 16.4', '2024-01-28 01:15:00', FALSE, 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_4 like Mac OS X)'),
(2019, 'Android TV Box', 'Android 11', '2024-01-28 20:30:00', FALSE, 'Mozilla/5.0 (Linux; Android 11; TV)'),
(2020, 'ChromeBook', 'ChromeOS 120', '2024-01-28 10:50:00', TRUE, 'Mozilla/5.0 (X11; CrOS x86_64 14541.0.0)');