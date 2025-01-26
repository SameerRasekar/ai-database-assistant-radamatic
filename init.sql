-- Switch to the students_information database
\c students_information;

-- Create the students_data table
CREATE TABLE IF NOT EXISTS students_data (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    subject VARCHAR(100),
    marks INT
);
