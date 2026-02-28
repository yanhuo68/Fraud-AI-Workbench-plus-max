CREATE TABLE Locations (
    location_id INT PRIMARY KEY,
    city VARCHAR(50),
    state VARCHAR(50),
    country VARCHAR(50),
    risk_level VARCHAR(20),
    timezone VARCHAR(50)
);

-- Sample Data (20 rows)
INSERT INTO Locations (location_id, city, state, country, risk_level, timezone) VALUES
(3001, 'New York', 'NY', 'USA', 'medium', 'America/New_York'),
(3002, 'San Francisco', 'CA', 'USA', 'low', 'America/Los_Angeles'),
(3003, 'Chicago', 'IL', 'USA', 'high', 'America/Chicago'),
(3004, 'Miami', 'FL', 'USA', 'high', 'America/New_York'),
(3005, 'Houston', 'TX', 'USA', 'medium', 'America/Chicago'),
(3006, 'Los Angeles', 'CA', 'USA', 'medium', 'America/Los_Angeles'),
(3007, 'Boston', 'MA', 'USA', 'low', 'America/New_York'),
(3008, 'Seattle', 'WA', 'USA', 'low', 'America/Los_Angeles'),
(3009, 'Atlanta', 'GA', 'USA', 'medium', 'America/New_York'),
(3010, 'Denver', 'CO', 'USA', 'low', 'America/Denver'),
(3011, 'Toronto', 'ON', 'Canada', 'low', 'America/Toronto'),
(3012, 'London', 'England', 'UK', 'medium', 'Europe/London'),
(3013, 'Singapore', 'Singapore', 'Singapore', 'low', 'Asia/Singapore'),
(3014, 'Sydney', 'NSW', 'Australia', 'low', 'Australia/Sydney'),
(3015, 'Berlin', 'Berlin', 'Germany', 'medium', 'Europe/Berlin'),
(3016, 'Paris', 'Île-de-France', 'France', 'medium', 'Europe/Paris'),
(3017, 'Tokyo', 'Tokyo', 'Japan', 'low', 'Asia/Tokyo'),
(3018, 'Mexico City', 'CDMX', 'Mexico', 'high', 'America/Mexico_City'),
(3019, 'Dubai', 'Dubai', 'UAE', 'medium', 'Asia/Dubai'),
(3020, 'Mumbai', 'Maharashtra', 'India', 'high', 'Asia/Kolkata');