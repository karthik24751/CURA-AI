-- Add new tables for CuraLink Platform Upgrade
-- Run this after the initial setup_database.sql

-- User Activity Tracking Table
CREATE TABLE IF NOT EXISTS user_activities (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    activity_type VARCHAR(50) NOT NULL,
    item_type VARCHAR(50) NOT NULL,
    item_id VARCHAR(255) NOT NULL,
    item_data TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_activity (user_id, created_at),
    INDEX idx_activity_type (activity_type, created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Disease Categories Table
CREATE TABLE IF NOT EXISTS disease_categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    keywords TEXT,
    related_diseases TEXT,
    popularity_score INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_popularity (popularity_score DESC),
    INDEX idx_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default disease categories
INSERT IGNORE INTO disease_categories (name, keywords, related_diseases) VALUES
('Parkinson''s Disease', 'tremor,rigidity,bradykinesia,deep brain stimulation', '["Multiple System Atrophy","Lewy Body Dementia","Progressive Supranuclear Palsy"]'),
('Alzheimer''s Disease', 'memory loss,dementia,cognitive decline,amyloid', '["Vascular Dementia","Frontotemporal Dementia","Mild Cognitive Impairment"]'),
('Cancer', 'tumor,oncology,chemotherapy,radiation', '["Breast Cancer","Lung Cancer","Prostate Cancer","Colorectal Cancer"]'),
('Diabetes', 'insulin,glucose,blood sugar,hyperglycemia', '["Type 1 Diabetes","Type 2 Diabetes","Gestational Diabetes"]'),
('ADHD', 'attention,hyperactivity,focus,concentration', '["ADD","Executive Function Disorder","Learning Disabilities"]'),
('Heart Disease', 'cardiac,cardiovascular,blood pressure,cholesterol', '["Coronary Artery Disease","Heart Failure","Arrhythmia"]'),
('Depression', 'mood,mental health,antidepressant,therapy', '["Major Depressive Disorder","Bipolar Disorder","Seasonal Affective Disorder"]'),
('Multiple Sclerosis', 'demyelination,autoimmune,neurological,myelin', '["Relapsing-Remitting MS","Primary Progressive MS","Neuromyelitis Optica"]'),
('Asthma', 'respiratory,breathing,wheezing,bronchial', '["COPD","Chronic Bronchitis","Allergic Rhinitis"]'),
('Stroke', 'cerebral,brain attack,thrombosis,embolism', '["Ischemic Stroke","Hemorrhagic Stroke","TIA"]');

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON curalink.* TO 'your_user'@'localhost';
-- FLUSH PRIVILEGES;

-- Display confirmation
SELECT 'New tables created successfully!' AS status;
SELECT COUNT(*) AS disease_categories_count FROM disease_categories;
