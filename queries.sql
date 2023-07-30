-- 1
SELECT DISTINCT Staff.ssNo, Staff.name, Staff.phone, Staff.role, Staff.vaccinationStatus, healthcarefacility.name 
FROM
vaccination
JOIN healthcarefacility ON healthcarefacility.name = Vaccination.healthcareFacilityName 
JOIN Staff ON healthcarefacility.name = Staff.healthcareFacilityName 
JOIN Shift ON Shift.ssNo = Staff.ssNo
WHERE vaccination.date = '2021-05-10' AND 1 = shift.workday;

-- 2
SELECT DISTINCT shift.ssNo, name FROM Staff 
JOIN Shift ON Staff.ssNo = Shift.ssNo 
WHERE Shift.workday = 3 AND Staff.role = 'doctor' 
AND (Staff.healthcareFacilityName = 'Messukeskus' OR Staff.healthcareFacilityName = 'Malmi');

-- 3
SELECT B.id AS batchID, B.healthcarefacilityname AS currentLocation, TL.tolocation AS lastLocation,
  CASE WHEN B.healthcarefacilityname = TL.tolocation THEN '' ELSE HF.phone END AS phone
FROM Batch AS B
JOIN TransportationLog AS TL ON B.id = TL.batchid
JOIN HealthcareFacility AS HF ON B.healthcarefacilityname = HF.name
WHERE TL.arrivaldate = (
  SELECT MAX(arrivaldate)
  FROM TransportationLog
  WHERE batchid = B.id
)
AND B.healthcarefacilityname != TL.tolocation

UNION

SELECT B.id AS batchID, B.healthcarefacilityname AS currentLocation, TL.tolocation AS lastLocation, ''
FROM Batch AS B
JOIN TransportationLog AS TL ON B.id = TL.batchid
JOIN HealthcareFacility AS HF ON B.healthcarefacilityname = HF.name
WHERE TL.arrivaldate = (
  SELECT MAX(arrivaldate)
  FROM TransportationLog
  WHERE batchid = B.id
)
AND B.healthcarefacilityname = TL.tolocation;

-- 4
SELECT *
FROM Patient p
JOIN Diagnosis d ON p.ssNo = d.ssNo
JOIN Symptoms s ON d.symptom = s.name
WHERE s.criticality = 1 AND d.date > '2021-05-10';

-- 5 
CREATE VIEW vaccination_status_view AS
SELECT P.ssno, P.name, P.birthday, P.gender,
       CASE
           WHEN COUNT(A.*) >= vc.dosage THEN 1
           ELSE 0
       END AS vaccinationStatus
FROM Patient P
LEFT JOIN Attends A ON P.ssNo = A.ssNo
LEFT JOIN Vaccination V ON V.date = A.date AND V.healthcarefacilityname = A.healthcarefacilityname
LEFT JOIN Batch B ON B.id = V.batchid
LEFT JOIN Manufacturer M ON M.id = B.manufacturerid
LEFT JOIN Vaccine VC ON VC.id = M.vaccineid
GROUP BY P.ssNo, VC.dosage;

-- 6
SELECT hf.name AS facility_name, 
       SUM(b.numberOfVaccines) AS total_vaccines,
       COUNT(DISTINCT v.id) AS different_types
FROM HealthcareFacility hf
LEFT JOIN Batch b ON hf.name = b.healthcareFacilityName
LEFT JOIN Manufacturer m ON b.manufacturerID = m.id
LEFT JOIN Vaccine v ON m.vaccineID = v.id
GROUP BY hf.name;


-- 7
SELECT Vaccine.id, Symptoms.name, COUNT(*) as frequency,
       COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY Vaccine.id) as relative_frequency
FROM Diagnosis
JOIN (Attends NATURAL JOIN Vaccination) ON Diagnosis.ssNo = Attends.ssNo
JOIN Batch ON Batch.ID = Vaccination.batchID
JOIN Manufacturer ON Manufacturer.id = Batch.manufacturerID
JOIN Vaccine ON Vaccine.id = Manufacturer.vaccineID
JOIN Symptoms ON Symptoms.name = Diagnosis.symptom
WHERE Diagnosis.date >= Attends.date
GROUP BY Vaccine.id, Symptoms.name;

-- test