/*!40101 SET NAMES utf8 */;
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



drop database if exists `answer`;
create database `answer`;
create table answer.test0_0(
    sid varchar(12) not null,
    name varchar(12) not null
);
insert into answer.test0_0 values('123', 'yyc');
insert into answer.test0_0 values('125', 'gjc');
insert into answer.test0_0 values('127', 'cz');
create table answer.test0_1(
    sid varchar(12) not null,
    name varchar(12) not null
);
insert into answer.test0_1 values('123', 'yyc');

drop database if exists `manage`;
create database `manage`;
use manage;

create table record(
    sid varchar(12) not null,
    submission_time datetime not null,
    test_id varchar(12) not null,
    result varchar(30) not null
);

create table test_table(
    test_id varchar(12) not null,
    test_name varchar(12) not null,
    test_desc text not null,
    set_id varchar(12) not null
);

insert into test_table values ('test0_0', '测试题目', '创建一个表test0_0，有两列    sid varchar(12) not null,
    name varchar(12) not null， 插入三条数据("123", "yyc")、("125", "gjc")、("127", "cz")', '0');
insert into test_table values ('test0_1', '测试题目2', '创建一个表test0_1，有两列    sid varchar(12) not null,
    name varchar(12) not null， 插入一条数据("123", "yyc")', '0');


create table student_info(
    sid varchar(12) not null,
    sql_name varchar(20) not null
    -- stu_name varchar(12) not null,
);

create view student_score as
    select sid, count(*) total_score
    from record
    where result='success'
    group by sid;
