# Network-Programming HW4
HW4 of Network Programming



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
```sqlite
CREATE TABLE POSTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    BoardName TEXT NOT NULL,
    Title TEXT NOT NULL,
    Content TEXT NOT NULL,
    Author TEXT NOT NULL,
    PostDate TEXT NOT NULL,
    FOREIGN KEY(BoardName) REFERENCES BOARDS(BoardName),
    FOREIGN KEY(Author) REFERENCES USERS(Username)
);
```

### Comments
```sqlite
CREATE TABLE COMMENTS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    PostID INTEGER NOT NULL,
    Username TEXT NOT NULL,
    Comment TEXT NOT NULL,
    FOREIGN KEY(PostID) REFERENCES POSTS(ID),
    FOREIGN KEY(Username) REFERENCES USERS(Username)
);
```

### Mails
```sqlite
CREATE TABLE MAILS(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    Recipient TEXT NOT NULL,
    Subject TEXT NOT NULL,
    Sender TEXT NOT NULL,
    MailDate TEXT NOT NULL,
    Content TEXT NOT NULL,
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