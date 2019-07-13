CREATE TABLE raw_data (
    group_name VARCHAR(32),
    student VARCHAR(32),
    student_id INT,
    subject VARCHAR(32),
    score DOUBLE,
    file_url VARCHAR(512),
    feedback VARCHAR(4096),
    submit_time INT,
    submit_date INT
);

CREATE TABLE student (
    id INT primary key,
    name VARCHAR(64)
);