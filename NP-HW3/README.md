# Network-Programming HW3
HW3 of Network Programming



## Tables
### Users
```sqlite
CREATE TABLE USERS(
    UID INTEGER PRIMARY KEY AUTOINCREMENT,
    Username TEXT NOT NULL UNIQUE,
    BucketName TEXT NOT NULL UNIQUE,
    Email TEXT NOT NULL,
    Password TEXT NOT NULL,
);
```

### Boards
```sqlite
CREATE TABLE BOARDS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BoardName TEXT NOT NULL UNIQUE,
    Moderator TEXT NOT NULL,
    FOREIGN KEY(Moderator) REFERENCES USERS(Username)
);
```

### Posts
Contents are stored on S3 for each author
```sqlite
CREATE TABLE POSTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BoardName TEXT NOT NULL,
    ObjectName TEXT NOT NULL,
    Title TEXT NOT NULL,
    Author TEXT NOT NULL,
    PostDate TEXT NOT NULL,
    FOREIGN KEY(BoardName) REFERENCES BOARDS(BoardName),
    FOREIGN KEY(Author) REFERENCES USERS(Username)
);
```

### Comments
Comments for a post are stored in the post object on S3

### Mails
```sqlite
CREATE TABLE MAILS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ObjectName TEXT NOT NULL,
    Recipient TEXT NOT NULL,
    Subject TEXT NOT NULL,
    Sender TEXT NOT NULL,
    MailDate TEXT NOT NULL,
    FOREIGN KEY(Recipient) REFERENCES USERS(Username),
    FOREIGN KEY(Sender) REFERENCES USERS(Username)
);
```

## Run
```shell script
python3 ./server.py <host> <port> [-v (0-2)]
```
```shell script
python3 ./client.py <host> <port>
```