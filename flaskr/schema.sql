drop table if exists domains;
create table domains (
  id integer primary key autoincrement,
  name text not null,
  parent_category integer not null
);

drop table if exists categories;
create table categories (
  id integer primary key autoincrement,
  name text not null,
  parent_categories text not null,
  child_categories text not null
);
