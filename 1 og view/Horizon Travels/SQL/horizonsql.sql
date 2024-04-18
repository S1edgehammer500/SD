-- Active: 1681406752661@@127.0.0.1@3306@horizontravels
CREATE DATABASE HORIZONTRAVELS;     
USE HORIZONTRAVELS;
CREATE TABLE USER (
UserID INTEGER(10) NOT NULL AUTO_INCREMENT,
UserEmail VARCHAR(30) NOT NULL UNIQUE,
UserPassword VARCHAR(100) NOT NULL,
UserFname VARCHAR(30) NOT NULL,
UserLname VARCHAR(30) NOT NULL,
UserType VARCHAR(8) NOT NULL DEFAULT 'standard',
PRIMARY KEY (UserID)
);

CREATE TABLE JOURNEY
(
JourneyID INTEGER(10) NOT NULL AUTO_INCREMENT,
DepartureCity VARCHAR(30) NOT NULL,
DepartureTime TIME NOT NULL,
ArrivalCity VARCHAR(30) NOT NULL,
ArrivalTime TIME NOT NULL,
PRICE INT(4) NOT NULL DEFAULT '75',
PRIMARY KEY (JourneyID)
);

CREATE TABLE BOOKING
(
BookingID INTEGER(10) NOT NULL AUTO_INCREMENT,
JourneyID INTEGER(10),
FOREIGN KEY (JourneyID) 
REFERENCES JOURNEY(JourneyID)
  ON DELETE CASCADE
  ON UPDATE CASCADE,

PurchaseDate DATETIME NOT NULL,
JourneyDate DATE NOT NULL,
SeatID INTEGER(10) NOT NULL,

UserID INTEGER(10) NOT NULL,
FOREIGN KEY (UserID) REFERENCES USER(UserID)
  ON DELETE CASCADE
  ON UPDATE CASCADE,

PRIMARY KEY (BookingID)
);


CREATE TABLE DISCOUNT
(
DiscountID INTEGER(10) NOT NULL AUTO_INCREMENT,
DaysToJourney INTEGER(10) NOT NULL,
DiscountPercentage INTEGER(3) NOT NULL,
PRIMARY KEY (DiscountID)
);

CREATE TABLE CANCELLATION
(
CancellationID INTEGER(10) NOT NULL AUTO_INCREMENT,
DaysToJourney INTEGER(10) NOT NULL,
CancellationPercantage INTEGER(3) NOT NULL,
PRIMARY KEY (CancellationID)
);

    
INSERT INTO  JOURNEY  VALUES 
  (1,'Newcastle', '16:45','Bristol', '18:00', 80),
  (2,'Bristol', '08:00','Newcastle', '09:15', 80),
  (3,'Cardiff', '06:00','Edinburgh', '07:30', 80),
  (4,'Bristol', '11:30','Manchester', '12:30', 60),
  (5,'Manchester', '12:20','Bristol', '13:20', 60),
  (6,'Bristol', '07:40','London', '08:20', 60),
  (7,'London', '11:00','Manchester', '12:20', 75),
  (8,'Manchester', '12:20','Glasgow', '13:30', 75),
  (9,'Bristol', '07:40','Glasgow', '08:45', 90),
  (10,'Glasgow', '14:30','Newcastle', '15:45', 75),
  (11,'Newcastle', '16:15','Manchester', '17:05', 75),
  (12,'Manchester', '18:25','Bristol', '19:30', 60),
  (13,'Bristol', '06:20','Manchester', '07:20', 60),
  (14,'Portsmouth', '12:00','Dundee', '14:00', 100),
  (15,'Dundee', '10:00','Portsmouth', '12:00', 100),
  (16,'Edinburgh', '18:30','Cardiff', '20:00', 75),
  (17,'Southampton', '12:00','Manchester', '13:30', 75),
  (18,'Manchester', '19:00','Southampton', '20:30', 70),
  (19,'Birmingham', '16:00','Newcastle', '17:30', 75),
  (20,'Newcastle', '06:00','Birmingham', '07:30', 75),
  (21,'Abderdeen', '07:00','Portsmouth', '09:00', 75)
; 

INSERT INTO DISCOUNT VALUES
  (1, 80, 20),
  (2, 60, 10),
  (3, 45, 5)
;

INSERT INTO CANCELLATION VALUES
  (1, 60, 0),
  (2, 30, 50)
;

;

INSERT INTO BOOKING(JourneyID, PurchaseDate, JourneyDate, SeatID, UserID) VALUES

  (4,'2023/06/28','2023/09/01', 106, 8),
  (4,'2023/06/14','2023/09/01', 63, 19),
  (13,'2023/06/07','2023/09/01', 103, 22),
  (7,'2023/06/22','2023/09/01', 20, 17),
  (7,'2023/06/24','2023/09/01', 101, 6),
  (9,'2023/06/05','2023/09/01', 1, 4),
  (7,'2023/06/04','2023/09/01', 4, 18),
  (20,'2023/07/12','2023/09/01', 21, 1),
  (1,'2023/07/17','2023/09/01', 65, 3),
  (2,'2023/07/06','2023/09/01', 45, 15),
  (15,'2023/07/29','2023/09/01', 99, 16),
  (10,'2023/07/18','2023/09/01', 87, 12),
  (5,'2023/07/25','2023/09/01', 119, 7),
  (4,'2023/07/16','2023/09/01', 76, 20),
  (13,'2023/08/18','2023/09/01', 15, 10),
  (3,'2023/08/31','2023/09/01', 48, 11),
  (4,'2023/08/21','2023/09/01', 81, 14),
  (1,'2023/08/02','2023/09/01', 82, 5),
  (18,'2023/08/19','2023/09/01', 70, 21),
  (20,'2023/08/28','2023/09/01', 119, 13),
  (11,'2023/08/25','2023/09/01', 61, 2),
  (13,'2023/08/02','2023/09/01', 116, 8),
  (2,'2023/08/10','2023/09/01', 5, 19)

;
/*
Commit;
*/

    -- Andre Barnett - 22025153