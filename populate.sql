-- Populates the clinica table
\copy clinica FROM '~/data/clinica.csv' DELIMITER ',' CSV HEADER

-- Populates the enfermeiro table
\copy enfermeiro FROM '~/data/enfermeiro.csv' DELIMITER ',' CSV HEADER

-- Populates the medico table
\copy medico FROM '~/data/medico.csv' DELIMITER ',' CSV HEADER

-- Populates the trabalha table
\copy trabalha FROM '~/data/trabalha.csv' DELIMITER ',' CSV HEADER

-- Populates the paciente table
\copy paciente FROM '~/data/paciente.csv' DELIMITER ',' CSV HEADER