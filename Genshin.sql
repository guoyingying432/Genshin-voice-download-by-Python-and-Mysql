#CREATE DATABASE Genshin;# DEFAULT CHARACTER SET UTF8 COLLATE UTF8_GENERAL_CI;
USE genshin;
DROP TABLE IF EXISTS voice_data;
DROP TABLE IF EXISTS charcter;
DROP TABLE IF EXISTS genshin;


CREATE TABLE genshin (
    version CHAR (64),
    key(version)
);
insert into genshin(version) values('2.7');

CREATE TABLE charcter (
    genshin_version CHAR(64),
    char_name varchar(64) unique key,
    voice_actor longtext,
    voice_count int
);
ALTER TABLE charcter ADD CONSTRAINT fok_version 
FOREIGN KEY(genshin_version) REFERENCES genshin(version);
#
CREATE TABLE voice_data (
	voice_id int NOT NULL PRIMARY KEY auto_increment,
    char_name varchar(64),
    voice_position longtext,
    voice_content LONGTEXT,
    voice_title LONGTEXT,
    loudness float check (loudness <= 0 and loudness>=-50),
    key(char_name,loudness)
);
ALTER TABLE voice_data ADD CONSTRAINT fok_char_name 
FOREIGN KEY(char_name) REFERENCES charcter(char_name);
#select * from voice_data where char_name='Yelan'