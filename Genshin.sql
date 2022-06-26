#CREATE DATABASE Genshin;# DEFAULT CHARACTER SET UTF8 COLLATE UTF8_GENERAL_CI;
USE genshin;/*
CREATE TABLE genshin (
    version CHAR (64),
    key(version)
);#
insert into genshin(version) values('2.7');*/
CREATE TABLE charcter (
    genshin_version CHAR(64),
    char_name varchar(64),
    voice_actor longtext,
    voice_count int,
    key(char_name)
);
#
CREATE TABLE voice_data (
    char_name varchar(64),
    voice_position longtext,
    voice_content LONGTEXT,
    voice_title LONGTEXT,
    loudness float,
    key(char_name,loudness)
);

#select * from voice_data where char_name='Yelan'