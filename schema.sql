DROP TABLE IF EXISTS Checklist;

CREATE TABLE Checklist (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  tf INTEGER UNIQUE NOT NULL,
  arg1 TEXT NOT NULL,
  arg2 TEXT NOT NULL,
  arg3 TEXT NOT NULL,
  arg4 TEXT NOT NULL,
  arg5 TEXT NOT NULL,
  arg6 TEXT NOT NULL,
  arg7 TEXT NOT NULL,
  arg8 TEXT NOT NULL,
  arg9 TEXT NOT NULL,
  pts FLOAT NOT NULL,
  percent INTEGER NOT NULL
);

INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (1,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (3,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (15,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (60,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (240,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (1440,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (10080,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);
INSERT INTO Checklist (tf,arg1,arg2,arg3,arg4,arg5,arg6,arg7,arg8,arg9,pts,percent) VALUES (40320,"YES","YES","YES","YES","YES","YES","YES","YES","YES",0,0);