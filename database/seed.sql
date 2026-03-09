-- Seed Data — Sample data for development
-- Run after schema.sql to get a working system immediately

-- Agent Profiles (13 departments)
INSERT INTO agent_profiles (name, dept_code, role, description) VALUES
('HQ Router', 'HQ', 'Front Desk', 'Routes queries to the correct department'),
('Research Agent', 'RND', 'Researcher', 'Searches knowledge base and documentation'),
('Finance Agent', 'FIN', 'Analyst', 'Handles quotes, P&L, and financial tracking'),
('Strategy Agent', 'STR', 'Consultant', 'Designs consulting engagements and frameworks'),
('Document Agent', 'DOC', 'Writer', 'Generates proposals and contracts'),
('Project Agent', 'PMO', 'Manager', 'Tracks projects, deadlines, and risks'),
('Sales Agent', 'SAL', 'Representative', 'Manages leads and pipeline'),
('CSM Agent', 'CSM', 'Success Manager', 'Monitors client health and retention'),
('Engineering Agent', 'ENG', 'Lead Developer', 'Handles code, deployments, and migrations'),
('Analytics Agent', 'ANA', 'Analyst', 'Tracks KPIs, metrics, and performance'),
('Training Agent', 'QAT', 'Trainer', 'Manages methodology and quality assurance'),
('Web Agent', 'WEB', 'Content Manager', 'Manages website and content'),
('Lab Agent', 'LAB', 'Innovator', 'Experiments with new tools and automation'),
('Marketing Agent', 'MKT', 'Marketer', 'Handles campaigns and brand presence');

-- Sample Projects
INSERT INTO projects (project_key, project_name, client_name, status, progress, service_type, start_date, end_date, budget, currency) VALUES
('acme-diagnostic', 'ACME Operations Diagnostic', 'ACME Manufacturing', 'active', 45, 'consulting', '2026-02-01', '2026-04-15', 85000, 'MXN'),
('bella-platform', 'Bella CRM Platform', 'Bella Spa & Wellness', 'active', 70, 'platform', '2026-01-15', '2026-03-30', 120000, 'MXN'),
('casa-ai', 'Casa Real AI Assistant', 'Casa Real Hotel', 'active', 25, 'ai', '2026-02-15', '2026-05-01', 200000, 'MXN');

-- Sample Tasks
INSERT INTO tasks (title, project_key, due_date, is_blocking, description) VALUES
('Complete gap analysis report', 'acme-diagnostic', '2026-03-10', true, 'Finalize the operational gap analysis with recommendations'),
('Design SOPs for reception', 'acme-diagnostic', '2026-03-15', false, 'Standard operating procedures for front desk and reception'),
('Deploy CRM dashboard v2', 'bella-platform', '2026-03-12', true, 'Second iteration of the main dashboard with KPI widgets'),
('Integrate Stripe payments', 'bella-platform', '2026-03-20', false, 'Payment processing for booking system'),
('Train RAG model on menu data', 'casa-ai', '2026-03-25', false, 'Fine-tune embeddings on hotel menu and services catalog'),
('Design chatbot conversation flows', 'casa-ai', '2026-03-18', false, 'Map out guest interaction flows for the AI assistant');

-- Sample Income
INSERT INTO income (source, amount, currency, status, date, project_key, description) VALUES
('ACME Manufacturing', 42500, 'MXN', 'received', '2026-02-01', 'acme-diagnostic', 'First payment - 50% upfront'),
('ACME Manufacturing', 42500, 'MXN', 'pending', '2026-04-15', 'acme-diagnostic', 'Final payment on delivery'),
('Bella Spa', 60000, 'MXN', 'received', '2026-01-15', 'bella-platform', 'Phase 1 payment'),
('Bella Spa', 60000, 'MXN', 'pending', '2026-03-30', 'bella-platform', 'Phase 2 payment on completion'),
('Casa Real Hotel', 100000, 'MXN', 'received', '2026-02-15', 'casa-ai', 'Project kickoff - 50%'),
('Casa Real Hotel', 100000, 'MXN', 'pending', '2026-05-01', 'casa-ai', 'Final delivery payment');

-- Sample Expenses
INSERT INTO expenses (description, amount, currency, category, date) VALUES
('Supabase Pro plan', 25, 'USD', 'infrastructure', '2026-03-01'),
('Vercel Pro plan', 20, 'USD', 'infrastructure', '2026-03-01'),
('Claude Max subscription', 100, 'USD', 'ai_tools', '2026-03-01'),
('Domain renewal - consultinghea.com', 15, 'USD', 'infrastructure', '2026-02-15');

-- Sample Leads
INSERT INTO leads (company_name, contact_name, contact_email, industry, stage, score, estimated_value, source) VALUES
('Tortilleria Don Jose', 'Jose Martinez', 'jose@donjose.mx', 'food_manufacturing', 'qualified', 75, 50000, 'referral'),
('Clinica San Angel', 'Dr. Laura Reyes', 'laura@clinicasanangel.mx', 'healthcare', 'contacted', 60, 80000, 'google_places'),
('Gym Titan', 'Roberto Flores', 'roberto@gymtitan.mx', 'fitness', 'new', 40, 35000, 'google_places'),
('Hotel Mirador', 'Ana Gutierrez', 'ana@hotelmirador.mx', 'hospitality', 'proposal', 85, 150000, 'website');

-- Sample Knowledge Base
INSERT INTO knowledge_base (title, content, domain, content_era) VALUES
('Lean Six Sigma Overview', 'Lean Six Sigma combines Lean manufacturing principles with Six Sigma methodology to eliminate waste and reduce variation in business processes. The DMAIC framework (Define, Measure, Analyze, Improve, Control) provides a structured approach to process improvement that can be applied across industries.', 'consulting', 'strategic-blueprint'),
('SOP Template - Service Business', 'Standard Operating Procedure template for service businesses. Includes sections for: Purpose, Scope, Responsibilities, Procedure Steps, Quality Checks, Exception Handling, and Revision History. SOPs should be written at a level that a new employee can follow without supervision.', 'consulting', 'source-of-truth'),
('Client Onboarding Checklist', 'Five-step onboarding process: 1) Initial discovery call (30 min), 2) Diagnostic assessment submission, 3) Scope definition and proposal, 4) Contract signing and payment, 5) Kickoff meeting with project plan. Average onboarding time: 5-7 business days.', 'operations', 'source-of-truth'),
('Pricing Strategy for SMB Consulting', 'Pricing for small and medium business consulting should reflect value delivered, not hours worked. Recommended tiers: Diagnostic ($15K-30K MXN), Implementation ($50K-150K MXN), Transformation ($150K-500K MXN). Always include ROI projections to justify investment.', 'finance', 'strategic-blueprint');

-- Sample Pricing Models
INSERT INTO pricing_models (name, service_type, base_rate, currency) VALUES
('Strategy & Consulting', 'consulting', 15000, 'MXN'),
('Custom Platform', 'platform', 25000, 'MXN'),
('AI Solutions', 'ai', 35000, 'MXN'),
('Business Intelligence', 'bi', 20000, 'MXN'),
('Premium Website', 'website', 18000, 'MXN');
