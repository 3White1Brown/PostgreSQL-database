CREATE TABLE IF NOT EXISTS Vaccine (
  id char(4) PRIMARY KEY,
  name varchar(20),
  dosage INT check (dosage >= 1 and dosage <= 2),
  tempmin int, 
  tempmax int
);

CREATE TABLE IF NOT EXISTS Manufacturer (
  id char(3) PRIMARY KEY,
  phone VARCHAR(20),
  country VARCHAR(20),
  vaccineid char(4),
  FOREIGN KEY (vaccineID) REFERENCES Vaccine(id)
);

CREATE TABLE IF NOT EXISTS HealthcareFacility (
  name VARCHAR(255) PRIMARY KEY,
  address VARCHAR(100),
  phone VARCHAR(20)
);

CREATE TABLE IF NOT EXISTS Batch (
  id char(4) PRIMARY KEY,
  numberofvaccines INTEGER,
  manufacturerid char(3),
  manufactureddate DATE,
  healthcarefacilityname VARCHAR(255),
  expiryDate DATE,
  FOREIGN KEY (manufacturerid) REFERENCES Manufacturer(id),
  FOREIGN KEY (healthcarefacilityname) REFERENCES HealthcareFacility(name)
);

CREATE TABLE IF NOT EXISTS Staff (
  ssno VARCHAR(20) PRIMARY KEY,
  name VARCHAR(255),
  birthday DATE,
  phone VARCHAR(255),
  role VARCHAR(255),
  vaccinationstatus INT check (vaccinationStatus >= 0 and vaccinationStatus <= 1), 
  healthcarefacilityname VARCHAR(255),
  FOREIGN KEY (healthcarefacilityname) REFERENCES HealthcareFacility(name)
);

CREATE TABLE IF NOT EXISTS Shift (
  workday integer check (workday = 1 or workday = 2 or workday = 3 or workday = 4 or workday = 5 or workday = 6 or workday = 7),
  ssno VARCHAR(20),
  PRIMARY KEY (workday, ssNo),
  FOREIGN KEY (ssno) REFERENCES Staff(ssno)
);

CREATE TABLE IF NOT EXISTS TransportationLog (
  batchid char(4),
  fromlocation VARCHAR(255),
  tolocation VARCHAR(255),
  departuredate DATE,
  arrivaldate DATE,
  PRIMARY KEY (fromlocation, batchid, departuredate),
  FOREIGN KEY (batchid) REFERENCES Batch(id),
  foreign key (fromlocation) references HealthcareFacility(name),
  foreign key (tolocation) references HealthcareFacility(name)
);

CREATE TABLE IF NOT EXISTS Patient (
  ssNo VARCHAR(20) PRIMARY KEY,
  name VARCHAR(255),
  birthday DATE,
  gender CHAR(1),
  vaccinationstatus INT check (vaccinationStatus = 0 or vaccinationStatus = 1 or vaccinationStatus = 2)
);

CREATE TABLE IF NOT EXISTS Vaccination (
  date DATE,
  healthcareFacilityName VARCHAR(255),
  batchid char(4),
  primary key (date, HealthcareFacilityName),
  FOREIGN KEY (healthcareFacilityName) REFERENCES HealthcareFacility(name),
  FOREIGN KEY (batchID) REFERENCES Batch(id)
);

CREATE TABLE IF NOT EXISTS Attends (
  date date, 
  healthcarefacilityname varchar(255),
  ssno VARCHAR(20),
  PRIMARY KEY (date, healthcareFacilityName, ssNo),
  FOREIGN KEY (ssNo) REFERENCES Patient(ssNo),
  foreign key (date, healthcareFacilityName) references Vaccination(date, healthcareFacilityName)
);

CREATE TABLE IF NOT EXISTS Symptoms (
  name varchar(100) NOT NULL UNIQUE,
  criticality int check (criticality >= 0 and criticality <= 1),
  primary key (name)
);

CREATE TABLE IF NOT EXISTS Diagnosis (
  ssNo VARCHAR(20),
  symptom VARCHAR(100),
  date DATE,
  PRIMARY KEY (ssNo, symptom, Date),
  FOREIGN KEY (ssNo) REFERENCES Patient(ssNo),
  FOREIGN KEY (symptom) REFERENCES Symptoms(name)
);
