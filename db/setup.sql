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



drop database if exists 'answer';
create database 'answer';
create table answer.0_0(
    sid varchar(12) not null,
    name varchar(12) not null
)
insert into answer.0_0 values('123', 'yyc')
insert into answer.0_0 values('125', 'gjc')
insert into answer.0_0 values('127', 'cz')

drop database if exists 'admin';
create database 'admin';
create table admin.record(
    sid varchar(12) not null,
    submission_time datetime not null,
    test_id varchar(12) not null,
    result varchar(30) not null
)

create table admin.test_table(
    test_id varchar(12) not null,
    test_name varchar(12) not null,
    test_desc varchar(100) not null 
)

