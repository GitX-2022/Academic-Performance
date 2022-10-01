create database if not exists Academic_evaluation;

use Academic_evaluation;

create table if not exists students(
		id int(11) not null auto_increment,
        name varchar(50) not null,
        password varchar (50) not null ,
        email varchar(50) not null,
        roll_no varchar(10) not null,
        primary key(id));

create table if not exists admin(
		id int(11) not null auto_increment,
        username varchar(50) not null,
        password varchar (50) not null ,
        email varchar(50) not null,
        primary key(id));
        
create table if not exists marks(
		id int(11) not null auto_increment,
        roll_no varchar(50) not null,
        subject varchar (50) not null ,
        internal_mark varchar(50) not null,
        external_mark varchar(50) not null,
        attendance varchar(50) not null,
        primary key(id));

insert into admin values (NULL,'admin','admin123','admin@gmail.com');



