ALTER SESSION SET CONTAINER=FREEPDB1;
ALTER SESSION SET CURRENT_SCHEMA=scott;

CREATE TABLE class (
  name VARCHAR2(32 CHAR),
  height NUMBER
);

INSERT INTO class(name, height) VALUES('Peter', 143.5);
INSERT INTO class(name, height) VALUES('Paul', 102.13);
INSERT INTO class(name, height) VALUES('Mary', 122.25);
