# Network-Programming HW1
HW1 of Network Programming



## Tables
### Users
```sqlite
CREATE TABLE USERS(
    UID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL,
    Password TEXT NOT NULL
);
```