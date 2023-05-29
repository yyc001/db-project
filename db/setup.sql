/*!40101 SET NAMES utf8 */;
drop database if exists `pub`;
create database `pub`;

create table pub.sc (
    sid varchar(12) not null,
    cid varchar(12) not null,
    score numeric(6,1)
);

insert into pub.sc values ('123456789011', '098765432100', 90);
insert into pub.sc values ('123456789012', '098765432100', 91);
insert into pub.sc values ('123456789013', '098765432100', 92);
insert into pub.sc values ('123456789014', '098765432100', 89);
insert into pub.sc values ('123456789015', '098765432100', 70);
insert into pub.sc values ('123456789016', '098765432100', 60);
insert into pub.sc values ('123456789017', '098765432100', 77);
insert into pub.sc values ('123456789018', '098765432100', 88);
insert into pub.sc values ('123456789019', '098765432100', 99);
insert into pub.sc values ('123456789011', '098765432101', 100);
insert into pub.sc values ('123456789012', '098765432101', 40);
insert into pub.sc values ('123456789013', '098765432101', 59);
insert into pub.sc values ('123456789014', '098765432101', 91);
insert into pub.sc values ('123456789015', '098765432101', 92);
insert into pub.sc values ('123456789016', '098765432101', 93);
insert into pub.sc values ('123456789017', '098765432101', 98);
insert into pub.sc values ('123456789018', '098765432101', 89);
insert into pub.sc values ('123456789019', '098765432101', 78);
insert into pub.sc values ('123456789011', '098765432102', 88);
insert into pub.sc values ('123456789012', '098765432102', 87);
insert into pub.sc values ('123456789013', '098765432102', 86);
insert into pub.sc values ('123456789014', '098765432102', 85);
insert into pub.sc values ('123456789015', '098765432102', 84);
insert into pub.sc values ('123456789016', '098765432102', 83);
insert into pub.sc values ('123456789017', '098765432102', 82);
insert into pub.sc values ('123456789018', '098765432102', 82);
insert into pub.sc values ('123456789019', '098765432102', 80);

create table pub.student (
    sid varchar(12) not null,
    name varchar(12) not null,
    major varchar(12)
);

insert into pub.student values ('123456789011', 'gjc', 'CS');

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
    test_id varchar(12) not null primary key,
    test_name varchar(12) not null,
    test_desc text not null,
    set_id varchar(12) not null,
    expected_time datetime not null,
    score int not null
);

insert into test_table values ('test0_0', '测试题目', '创建一个表test0_0，有两列    sid varchar(12) not null,
    name varchar(12) not null， 插入三条数据("123", "yyc")、("125", "gjc")、("127", "cz")', '0', '2023-06-01 23:59', 1);
insert into test_table values ('test0_1', '测试题目2', '创建一个表test0_1，有两列    sid varchar(12) not null,
    name varchar(12) not null， 插入一条数据("123", "yyc")', '0', '2023-06-01 23:59', 1);


create table student_info(
    sid varchar(12) not null,
    sql_name varchar(20) not null
    -- stu_name varchar(12) not null,
);

create table saved_query(
    sid varchar(12) primary key,
    query text not null
);

create view student_score as
    select sid, sum(score) total_score
    from record
    join test_table tt on record.test_id = tt.test_id
    where result='success'
    group by sid;
