DROP DATABASE photoshare;
CREATE DATABASE IF NOT EXISTS photoshare;
USE photoshare;

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
    requester_email VARCHAR(255) NOT NULL,
    responder_email VARCHAR(255) NOT NULL,
    FOREIGN KEY (requester_email) REFERENCES Users(email),
    FOREIGN KEY (responder_email) REFERENCES Users(email)
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
    FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


/*
Photos - Entity:
Have unique photo id as primary key. Each photo needs data (a url to S3 bucket) to upload. They also much belong to exactly one album.
*/
CREATE TABLE Photos( 
    photo_id int4  AUTO_INCREMENT,
    imgdata LONGTEXT,
    likes INT DEFAULT 0, 
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
    FOREIGN KEY (album_id) REFERENCES Albums(album_id) ON DELETE CASCADE,
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE
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
    FOREIGN KEY (photo_id) REFERENCES Photos(photo_id) ON DELETE CASCADE,
    FOREIGN KEY (word) REFERENCES Tags(word)
);

/*
Interaction - Relationship:
Like photo_tag, comments can only be made with a complete tuple of user_id and photo_id. Assuming that comments can only be made on photos. Has a comment_id as primary key to easily differentiate between comments made on the same day.
*/
CREATE TABLE Interactions(
    interaction_id int4 AUTO_INCREMENT,
    user_id int4,
    photo_id int4 NOT NULL,
    comment VARCHAR(255),
    likes INT DEFAULT 0,
    time_created TIMESTAMP,
    CONSTRAINT interaction_pk PRIMARY KEY (interaction_id),
    FOREIGN KEY (user_id) REFERENCES Users (user_id),
    FOREIGN KEY (photo_id) REFERENCES Photos (photo_id) ON DELETE CASCADE
);

INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown) VALUES ('anon@bu.edu', 'test', 'Anon', 'ymous', 'male', '1988-12-01', 'Chicago');

INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown) VALUES ('test1@bu.edu', 'test', 'Testy', 'McTesterson', 'male', '1988-12-01', 'Boston');

INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown) VALUES ('test2@bu.edu', 'test', 'Sir', 'TestAlot', 'female', '1988-11-01', 'Boston');

INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown) VALUES ('foo@bu.edu', 'jk', 'Foo', 'Bar', 'other', '1938-3-02', 'Portland');

INSERT INTO Friends(requester_email, responder_email) VALUES ('test1@bu.edu', 'test2@bu.edu');

INSERT INTO Friends(requester_email, responder_email) VALUES ('foo@bu.edu', 'test1@bu.edu');

INSERT INTO Albums(name) VALUES ('Test1 Album');
INSERT INTO Album_User(album_id, user_id) VALUES (1,2);

/*
RAW QUERY TESTING
*/

-- SELECT *
-- FROM Photos NATURAL JOIN
--     (SELECT DISTINCT photo_id FROM(
--     (SELECT photo_id
--     FROM Photo_Tag
--     WHERE word = 'cat')
--     UNION ALL
--     (SELECT photo_id
--     FROM Photo_Tag
--     WHERE word = 'mouse')
-- ) AS C) AS D;

-- SELECT word, count(word)
-- FROM Photo_Tag NATURAL JOIN(
--     (SELECT photo_id
--     FROM Photo_Tag
--     WHERE word = 'cat')
-- ) AS C
-- GROUP BY word
-- ORDER BY count(word) DESC;

-- SELECT word, count(word)
-- FROM Photo_Tag NATURAL JOIN
-- (SELECT DISTINCT photo_id FROM(
--     (SELECT photo_id
--     FROM Photo_Tag
--     WHERE word = 'cat')
--     UNION
--     (SELECT photo_id
--     FROM Photo_Tag
--     WHERE word = 'mouse')
-- ) AS C) AS D
-- GROUP BY word
-- ORDER BY count(word) DESC;

-- SELECT word, count(word)
-- FROM Photo_Tag NATURAL JOIN (SELECT photo_id
--     FROM Album_Photo NATURAL JOIN (SELECT album_id
--         FROM Album_User
--         WHERE user_id = 2) AS A) AS B
-- GROUP BY word
-- ORDER BY count(word) DESC
-- LIMIT 5;



SELECT *
FROM Photos NATURAL JOIN
(
    SELECT photo_id, count(photo_id)
    FROM Album_User NATURAL JOIN
    (
        SELECT *  
        FROM Album_Photo NATURAL JOIN
        (
            SELECT * FROM
            (
                (SELECT *
                FROM Photo_Tag
                WHERE word = 'cat')
                UNION 
                (SELECT *
                FROM Photo_Tag
                WHERE word = 'farm')
                UNION 
                (SELECT *
                FROM Photo_Tag
                WHERE word = 'nice')
            ) AS C
        ) AS D
    ) AS E
    WHERE user_id != 5
    GROUP BY photo_id
    ORDER BY count(photo_id) DESC
    LIMIT 5
) AS F;  



