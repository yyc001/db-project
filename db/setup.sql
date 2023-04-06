drop user if exists 'student1';
drop database `student1`;
create user 'student1'@'%' identified by '123456';
CREATE DATABASE if not exists `student1`;
grant all on student1.* to 'student1' with grant option;

drop user if exists 'student2';
CREATE DATABASE if not exists `student2`;
create user 'student2'@'%' identified by '123456';
drop database `student2`;
grant all on student2.* to 'student2' with grant option;

flush privileges;

create database if not exists `pub`;
create table pub.sc (
    sid varchar(12) not null,
    cid varchar(12) not null,
    score numeric(6,1)
);