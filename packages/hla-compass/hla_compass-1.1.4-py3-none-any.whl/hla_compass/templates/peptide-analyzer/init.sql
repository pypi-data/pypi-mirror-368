-- Initialize HLA-Compass database for peptide analyzer module

-- Create scientific schema
CREATE SCHEMA IF NOT EXISTS scientific;
CREATE SCHEMA IF NOT EXISTS platform;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create peptides table
CREATE TABLE IF NOT EXISTS scientific.peptides (
    id SERIAL PRIMARY KEY,
    sequence VARCHAR(50) NOT NULL,
    length INTEGER,
    molecular_weight DECIMAL(10,2),
    source VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create index for better performance
CREATE INDEX IF NOT EXISTS idx_peptides_sequence ON scientific.peptides(sequence);
CREATE INDEX IF NOT EXISTS idx_peptides_length ON scientific.peptides(length);

-- Insert real immunogenic peptides
INSERT INTO scientific.peptides (sequence, length, molecular_weight, source) VALUES
('SIINFEKL', 8, 963.12, 'OVA protein'),
('GILGFVFTL', 9, 966.18, 'Influenza M1'),
('YLQPRTFLL', 9, 1150.37, 'HBV core'),
('FLPSDFFPSV', 10, 1155.30, 'HBV pol'),
('GLCTLVAML', 9, 920.18, 'BMLF1'),
('NLVPMVATV', 9, 958.20, 'pp65 CMV'),
('LLWNGPMAV', 9, 1013.24, 'Yellow fever'),
('KVLEYVIKV', 9, 1090.37, 'MAG-1'),
('FLLTRILTI', 9, 1088.39, 'HCV'),
('YMLDLQPETT', 10, 1225.38, 'NY-ESO-1'),
('KVAELVHFL', 9, 1025.26, 'MAGE-A3'),
('SLLMWITQC', 9, 1080.33, 'NY-ESO-1'),
('LLDFVRFMGV', 10, 1211.48, 'EBNA3A'),
('TPRVTGGGAM', 10, 960.15, 'pp65 CMV'),
('CINGVCWTV', 9, 995.21, 'Survivin'),
('ELAGIGILTV', 10, 1000.20, 'MART-1'),
('YMNGTMSQV', 9, 1018.19, 'Tyrosinase'),
('FLWGPRALV', 9, 1043.26, 'MAGE-A3'),
('KLGEFYNQMM', 10, 1274.51, 'HIV gag'),
('RMFPNAPYL', 9, 1108.33, 'WT1'),
('ILKEPVHGV', 9, 993.18, 'HIV RT'),
('SLYNTVATL', 9, 995.13, 'HIV gag'),
('VLYRYGSFSV', 10, 1206.38, 'HBV pol'),
('GLYSSTVPV', 9, 923.05, 'HBV sAg'),
('IPSINVHHY', 9, 1089.25, 'HBV pol')
ON CONFLICT DO NOTHING;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA scientific TO postgres;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA scientific TO postgres;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA scientific TO postgres;