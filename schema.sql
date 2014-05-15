drop table if exists highscore;
create table highscore (
  id integer primary key autoincrement,
  name text not null,
  score int not null,
  time float not null
);
