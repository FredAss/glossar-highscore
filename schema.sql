drop table if exists highscore;
create table highscore (
  id integer primary key autoincrement,
  datetime datetime not null,
  name text not null,
  score int not null,
  time float not null
);
