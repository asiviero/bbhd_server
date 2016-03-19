drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);

drop table if exists question;
create table question (
  id integer primary key autoincrement,
  title text not null,
  correct_choice int not null,
  time_limit int not null,
  choices text not null
);

drop table if exists user;
create table user (
  id integer primary key autoincrement,
  name text not null,
  picture text not null,
  fbid text not null
);

drop table if exists quiz;
create table quiz (
  id integer primary key autoincrement,
  users text not null,
  questions text not null,
  winner int,
  user_1_right_answers int,
  user_1_indexes text,
  user_2_right_answers int,
  user_2_indexes text
);
