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
