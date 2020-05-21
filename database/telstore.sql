create database telstore;

USE telstore;
create TABLE admin(
srno int primary key auto_increment,
name varchar(40),
username varchar(40),
email varchar(40),
password varchar(40),
security_key varchar(6),
comments varchar(100)
);

CREATE TABLE directory(
status varchar(10) DEFAULT 'active',
srno int primary key auto_increment,
name varchar(30),
title varchar(30),
company varchar(40),
phone1 varchar(14),
phone2 varchar(14),
address varchar(90),
groups varchar(25),
email varchar(40),
website varchar(40)
);