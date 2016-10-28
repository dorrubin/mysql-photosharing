DROP DATABASE photoshare;
CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;
-- DROP TABLE IF EXISTS Users CASCADE;
-- DROP TABLE IF EXISTS Friends CASCADE;
-- DROP TABLE IF EXISTS Albums CASCADE;
-- DROP TABLE IF EXISTS Album_User CASCADE;
-- DROP TABLE IF EXISTS Photos CASCADE;
-- DROP TABLE IF EXISTS Album_Photo CASCADE;
-- DROP TABLE IF EXISTS Tags CASCADE;
-- DROP TABLE IF EXISTS Photo_Tag CASCADE;
-- DROP TABLE IF EXISTS Comments CASCADE;

/*
Users - Entity:
Have unique user id as primary key. They also have a unique email address to avoid duplicate accounts from the same email. Only email and password are needed to facilitate registrations. Other fields are optional and can be added at a later time.
*/
CREATE TABLE Users (
    user_id int4  AUTO_INCREMENT,
    email VARCHAR(255) UNIQUE,
    password VARCHAR(255),
    first_name CHAR(200),
    last_name CHAR(200),
    gender CHAR(10),
    dob DATE,
    hometown CHAR(20),
    CONSTRAINT users_pk PRIMARY KEY (user_id)
);

/*
Friends - Relationship:
Both requester_id and responder_id are entities in User.They are differentiated by the user who initiated the friend request (requester) and the one who responded AND accepted (responder). Both ids are needed to create an entry.
*/
CREATE TABLE Friends( 
    requester_id int4 NOT NULL,
    responder_id int4 NOT NULL,
    FOREIGN KEY (requester_id) REFERENCES Users(user_id),
    FOREIGN KEY (responder_id) REFERENCES Users(user_id)
);


/*
Albums - Entity:
Have unique album id as primary key. Each album is required to have a name and an owner ( a user_id) to be created since each album has at exactly one owner.
*/
CREATE TABLE Albums( 
    album_id int4 AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    creation TIMESTAMP,
    CONSTRAINT album_pk PRIMARY KEY (album_id)
);

/*
Album_User - Relationship:
Keeps track of the owners of each album. Each Album can only owned by exactly 1 user so the album is made the primary key
*/
CREATE TABLE Album_User( 
    album_id int4,
    user_id int4,
    PRIMARY KEY (user_id, album_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


/*
Photos - Entity:
Have unique photo id as primary key. Each photo needs data (a url to S3 bucket) to upload. They also much belong to exactly one album.
*/
CREATE TABLE Photos( 
    photo_id int4  AUTO_INCREMENT,
    imgdata blob,
    -- INDEX upid_idx (user_id),
    caption VARCHAR(255),
    CONSTRAINT photo_pk PRIMARY KEY (photo_id)
);


/*
Album_Photo - Relationship:
Keeps track of the owners of each album. Each Album can only owned by exactly 1 user so the album is made the primary key
*/
CREATE TABLE Album_Photo( 
    album_id int4,
    photo_id int4,
    CONSTRAINT album_photo_pk PRIMARY KEY (album_id, photo_id),
    FOREIGN KEY (album_id) REFERENCES Albums(album_id),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id)
);

/*
Tags - Entity:
Have unique word as primary key. This single column table is to avoid duplication and track existing.
*/
CREATE TABLE Tags( 
    word VARCHAR(255),
    CONSTRAINT tags_pk PRIMARY KEY (word)
);

/*
Photo_Tag - Relationship:
Keeps track of tags on photos. There can be many tags on many photos but each entry must contain the tuple.
*/
CREATE TABLE Photo_Tag( 
    photo_id int4,
    word VARCHAR(255),
    CONSTRAINT photo_tag_pk PRIMARY KEY (photo_id, word),
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id),
    FOREIGN KEY (word) REFERENCES Tags(word)
);

/*
Comments - Relationship:
Like photo_tag, comments can only be made with a complete tuple of user_id and photo_id. Assuming that comments can only be made on photos. Has a comment_id as primary key to easily differentiate between comments made on the same day.
*/
CREATE TABLE Comments(
    comment_id int4,
    user_id int4 NOT NULL,
    photo_id int4 NOT NULL,
    text VARCHAR(255) NOT NULL,
    time_created TIMESTAMP,
    CONSTRAINT comment_pk PRIMARY KEY (comment_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id),
    FOREIGN KEY (photo_id) REFERENCES Photos (photo_id)
);


INSERT INTO Users (email, password) VALUES ('test@bu.edu', 'test');
INSERT INTO Users (email, password) VALUES ('test1@bu.edu', 'test');
