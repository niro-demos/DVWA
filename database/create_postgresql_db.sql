CREATE TABLE users (user_id INT PRIMARY KEY,first_name VARCHAR(15),last_name VARCHAR(15), "user" VARCHAR(15), password VARCHAR(255),avatar VARCHAR(70), last_login timestamp, failed_login INT);

INSERT INTO users VALUES ('1','admin','admin','admin','$argon2id$v=19$m=65536,t=4,p=1$eEJHY3c3SUlqTEh4MWIvVA$XE01dl2mhsiLMfotTi1zzZlaAnsfxCvYZmpwJsDoPis','admin.jpg', CURRENT_TIMESTAMP, '0'),('2','Gordon','Brown','gordonb','$argon2id$v=19$m=65536,t=4,p=1$d0Rob0s4VEF3cDExM0dUQg$qtKk2Ekk2qtCCfwTgdO33vRs9pNGDwM9W3QbXB6074k','gordonb.jpg', CURRENT_TIMESTAMP, '0'), ('3','Hack','Me','1337','$argon2id$v=19$m=65536,t=4,p=1$OFlTWTMvdzlNa0NiTkVDeg$PzzkmfNOD6ODDdrm8fYUxu6PdV38YQ9wwIL713kILOo','1337.jpg', CURRENT_TIMESTAMP, '0'), ('4','Pablo','Picasso','pablo','$argon2id$v=19$m=65536,t=4,p=1$LzRCdldNSjE0blFBOHZDWg$3rs3KH0aunZTx1+/w7jakPHjxoTieMficibqkpIV9AM','pablo.jpg', CURRENT_TIMESTAMP, '0'), ('5', 'Bob','Smith','smithy','$argon2id$v=19$m=65536,t=4,p=1$Y3NJdU9Rb2l5NGVHSzFKSg$g0cj3hwMkyuLd723acnN+N2JG91a3MEB4UJSk3WyZxI','smithy.jpg', CURRENT_TIMESTAMP, '0');

CREATE TABLE guestbook (comment_id serial PRIMARY KEY, comment VARCHAR(300), name VARCHAR(100));

INSERT INTO guestbook (comment, name) VALUES ('This is a test comment.','test');
