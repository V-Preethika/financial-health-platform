-- Users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    company_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Businesses table
CREATE TABLE businesses (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_name VARCHAR(255) NOT NULL,
    business_type VARCHAR(50),
    industry VARCHAR(100),
    annual_revenue DECIMAL(15, 2),
    employee_count INTEGER,
    gst_number VARCHAR(50),
    pan_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial data table
CREATE TABLE financial_data (
    id SERIAL PRIMARY KEY,
    business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    fiscal_year VARCHAR(10),
    revenue DECIMAL(15, 2),
    expenses DECIMAL(15, 2),
    net_profit DECIMAL(15, 2),
    cash_flow DECIMAL(15, 2),
    accounts_receivable DECIMAL(15, 2),
    accounts_payable DECIMAL(15, 2),
    inventory DECIMAL(15, 2),
    total_assets DECIMAL(15, 2),
    total_liabilities DECIMAL(15, 2),
    equity DECIMAL(15, 2),
    expense_breakdown JSONB,
    revenue_streams JSONB,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Assessments table
CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    business_id INTEGER NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50),
    financial_health_score DECIMAL(5, 2),
    creditworthiness_rating VARCHAR(10),
    risk_level VARCHAR(20),
    key_findings JSONB,
    recommendations JSONB,
    cost_optimization_suggestions JSONB,
    forecasted_metrics JSONB,
    industry_benchmarks JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Financial reports table
CREATE TABLE financial_reports (
    id SERIAL PRIMARY KEY,
    assessment_id INTEGER NOT NULL REFERENCES assessments(id) ON DELETE CASCADE,
    report_type VARCHAR(50),
    language VARCHAR(10),
    report_content TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for performance
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_businesses_user_id ON businesses(user_id);
CREATE INDEX idx_financial_data_business_id ON financial_data(business_id);
CREATE INDEX idx_assessments_business_id ON assessments(business_id);
CREATE INDEX idx_assessments_user_id ON assessments(user_id);
CREATE INDEX idx_reports_assessment_id ON financial_reports(assessment_id);

-- Enable encryption for sensitive columns (PostgreSQL pgcrypto extension)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
