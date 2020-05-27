# Network-Programming Lab
Final Lab of Network Programming



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

### Files
```sqlite
CREATE TABLE FILES(
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    FileName TEXT NOT NULL UNIQUE,
    FileType TEXT NOT NULL
);
```



## Run
```shell script
python3 ./TCPserver.py <host> <port> [-v (0-2)]
```
```shell script
python3 ./TCPclient.py <host> <port>
```
or
```shell script
python3 ./UDPserver.py <host> <port> [-v (0-2)]
```
```shell script
python3 ./UDPclient.py <host> <port>
```