drop database if exists `pub`;
create database `pub`;
create table pub.sc (
    sid varchar(12) not null,
    cid varchar(12) not null,
    score numeric(6,1)
);

insert into pub.sc values ('123456789011', '098765432100', 90);


drop user if exists 'student1';
drop database if exists `student1`;
create user 'student1'@'%' identified by '123456';
create database `student1`;
grant all on student1.* to 'student1' with grant option;
grant select on pub.* to 'student1';

drop user if exists 'student2';
drop database if exists `student2`;
create user 'student2'@'%' identified by '123456';
create database `student2`;
grant all on student2.* to 'student2' with grant option;
grant select on pub.* to 'student2';

flush privileges;