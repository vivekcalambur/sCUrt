CREATE TABLE Users (
    user_id int NOT NULL AUTO_INCREMENT,
    email varchar(255) NOT NULL UNIQUE,
    password varchar(255) NOT NULL,
    first_name varchar(255) NOT NULL,
    last_name varchar(255) NOT NULL,
    age int,
    address varchar(255),
    phone varchar(255),
    PRIMARY KEY (user_id)
);
