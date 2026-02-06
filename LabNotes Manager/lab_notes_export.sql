BEGIN TRANSACTION;
CREATE TABLE lab_notes (
    id INTEGER PRIMARY KEY ,
    date TEXT NOT NULL,
    subject TEXT NOT NULL,
    notes TEXT NOT NULL
);
INSERT INTO lab_notes VALUES(1,'[1-1-1111]','Seditrujn0shgvt','ethetk');
INSERT INTO lab_notes VALUES(2,'[1-1-1111]','Shvbf','wfgeijvh9dsjvos');


COMMIT;
select * from lab_notes