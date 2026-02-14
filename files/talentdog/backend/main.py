from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
import sqlite3
import os
import xml.etree.ElementTree as ET
import uvicorn
from typing import Optional
from datetime import datetime

app = FastAPI(title="TalentDog Enterprise ATS Integrator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = os.path.join(os.getcwd(), "database", "talentdog.db")

# TESTING MODE - Set to True to use mock data without real ATS credentials
TESTING_MODE = os.getenv("TESTING_MODE", "true").lower() == "true"

# Pydantic Models
class ATSConfig(BaseModel):
    system: str
    subdomain: str 
    api_key: Optional[str] = None
    feed_url: Optional[str] = None

class ATSConnectionRequest(BaseModel):
    provider: str
    subdomain: Optional[str] = None
    api_key: Optional[str] = None
    feed_url: Optional[str] = None

# Initialize database
def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ats_configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider TEXT NOT NULL UNIQUE,
            subdomain TEXT,
            api_key TEXT,
            feed_url TEXT,
            is_active INTEGER DEFAULT 1,
            last_sync TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vacancies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT,
            location TEXT,
            department TEXT,
            status TEXT DEFAULT 'Open',
            url TEXT UNIQUE,
            external_id TEXT,
            source_provider TEXT,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

init_db()

class MockATSData:
    """Mock data for testing ATS integrations without real credentials"""
    
    @staticmethod
    def get_mock_jobs(provider: str, company: str = "Demo Company"):
        """Generate realistic mock job data for testing"""
        
        base_jobs = {
            "greenhouse": [
                {
                    "title": "Senior Software Engineer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12345",
                    "id": "gh_12345",
                    "location": "Amsterdam, Netherlands",
                    "department": "Engineering",
                    "description": "We're looking for a Senior Software Engineer to join our team..."
                },
                {
                    "title": "Product Manager",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12346",
                    "id": "gh_12346",
                    "location": "Remote - Europe",
                    "department": "Product",
                    "description": "Join our product team to drive innovation..."
                },
                {
                    "title": "DevOps Engineer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12347",
                    "id": "gh_12347",
                    "location": "Utrecht, Netherlands",
                    "department": "Infrastructure",
                    "description": "Help us scale our infrastructure..."
                },
                {
                    "title": "Full Stack Developer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12348",
                    "id": "gh_12348",
                    "location": "Rotterdam, Netherlands",
                    "department": "Engineering",
                    "description": "Build end-to-end features for our platform..."
                },
                {
                    "title": "UX Designer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12349",
                    "id": "gh_12349",
                    "location": "Amsterdam, Netherlands",
                    "department": "Design",
                    "description": "Create beautiful and intuitive user experiences..."
                },
                {
                    "title": "Data Engineer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12350",
                    "id": "gh_12350",
                    "location": "Eindhoven, Netherlands",
                    "department": "Data",
                    "description": "Build scalable data pipelines..."
                },
                {
                    "title": "Sales Manager",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12351",
                    "id": "gh_12351",
                    "location": "The Hague, Netherlands",
                    "department": "Sales",
                    "description": "Lead our sales team in the Benelux region..."
                },
                {
                    "title": "Marketing Specialist",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12352",
                    "id": "gh_12352",
                    "location": "Amsterdam, Netherlands",
                    "department": "Marketing",
                    "description": "Drive our digital marketing initiatives..."
                },
                {
                    "title": "Technical Lead",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12353",
                    "id": "gh_12353",
                    "location": "Remote - Netherlands",
                    "department": "Engineering",
                    "description": "Lead a team of talented engineers..."
                },
                {
                    "title": "Customer Success Manager",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12354",
                    "id": "gh_12354",
                    "location": "Amsterdam, Netherlands",
                    "department": "Customer Success",
                    "description": "Ensure our customers achieve their goals..."
                },
                {
                    "title": "QA Engineer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12355",
                    "id": "gh_12355",
                    "location": "Utrecht, Netherlands",
                    "department": "Quality Assurance",
                    "description": "Ensure the highest quality of our products..."
                },
                {
                    "title": "Business Analyst",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12356",
                    "id": "gh_12356",
                    "location": "Rotterdam, Netherlands",
                    "department": "Strategy",
                    "description": "Analyze business processes and drive improvements..."
                },
                {
                    "title": "HR Manager",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12357",
                    "id": "gh_12357",
                    "location": "Amsterdam, Netherlands",
                    "department": "Human Resources",
                    "description": "Lead our people operations and culture..."
                },
                {
                    "title": "Security Engineer",
                    "url": f"https://boards.greenhouse.io/democompany/jobs/12358",
                    "id": "gh_12358",
                    "location": "Remote - Europe",
                    "department": "Security",
                    "description": "Protect our infrastructure and data..."
                }
            ],
            "lever": [
                {
                    "title": "Frontend Developer",
                    "url": f"https://{company}.lever.co/jobs/lv_001",
                    "id": "lv_001",
                    "location": "Brussels, Belgium",
                    "department": "Engineering",
                    "description": "Build beautiful user interfaces with React..."
                },
                {
                    "title": "Data Scientist",
                    "url": f"https://{company}.lever.co/jobs/lv_002",
                    "id": "lv_002",
                    "location": "Antwerp, Belgium",
                    "department": "Data",
                    "description": "Apply machine learning to solve business problems..."
                },
                {
                    "title": "Backend Developer",
                    "url": f"https://{company}.lever.co/jobs/lv_003",
                    "id": "lv_003",
                    "location": "Ghent, Belgium",
                    "department": "Engineering",
                    "description": "Build scalable APIs and microservices..."
                },
                {
                    "title": "Product Designer",
                    "url": f"https://{company}.lever.co/jobs/lv_004",
                    "id": "lv_004",
                    "location": "Brussels, Belgium",
                    "department": "Design",
                    "description": "Design innovative product experiences..."
                },
                {
                    "title": "Mobile Developer",
                    "url": f"https://{company}.lever.co/jobs/lv_005",
                    "id": "lv_005",
                    "location": "Leuven, Belgium",
                    "department": "Engineering",
                    "description": "Develop native iOS and Android applications..."
                },
                {
                    "title": "Account Manager",
                    "url": f"https://{company}.lever.co/jobs/lv_006",
                    "id": "lv_006",
                    "location": "Brussels, Belgium",
                    "department": "Sales",
                    "description": "Manage key client relationships..."
                },
                {
                    "title": "Content Writer",
                    "url": f"https://{company}.lever.co/jobs/lv_007",
                    "id": "lv_007",
                    "location": "Remote - Belgium",
                    "department": "Marketing",
                    "description": "Create engaging content for our audience..."
                },
                {
                    "title": "Cloud Architect",
                    "url": f"https://{company}.lever.co/jobs/lv_008",
                    "id": "lv_008",
                    "location": "Antwerp, Belgium",
                    "department": "Infrastructure",
                    "description": "Design cloud-native solutions..."
                },
                {
                    "title": "Financial Analyst",
                    "url": f"https://{company}.lever.co/jobs/lv_009",
                    "id": "lv_009",
                    "location": "Brussels, Belgium",
                    "department": "Finance",
                    "description": "Provide financial insights and reporting..."
                },
                {
                    "title": "Scrum Master",
                    "url": f"https://{company}.lever.co/jobs/lv_010",
                    "id": "lv_010",
                    "location": "Ghent, Belgium",
                    "department": "Engineering",
                    "description": "Facilitate agile processes and team collaboration..."
                },
                {
                    "title": "Legal Counsel",
                    "url": f"https://{company}.lever.co/jobs/lv_011",
                    "id": "lv_011",
                    "location": "Brussels, Belgium",
                    "department": "Legal",
                    "description": "Provide legal guidance on contracts and compliance..."
                },
                {
                    "title": "Data Analyst",
                    "url": f"https://{company}.lever.co/jobs/lv_012",
                    "id": "lv_012",
                    "location": "Antwerp, Belgium",
                    "department": "Data",
                    "description": "Transform data into actionable insights..."
                },
                {
                    "title": "IT Support Specialist",
                    "url": f"https://{company}.lever.co/jobs/lv_013",
                    "id": "lv_013",
                    "location": "Brussels, Belgium",
                    "department": "IT",
                    "description": "Provide technical support to our team..."
                },
                {
                    "title": "Recruitment Manager",
                    "url": f"https://{company}.lever.co/jobs/lv_014",
                    "id": "lv_014",
                    "location": "Brussels, Belgium",
                    "department": "HR",
                    "description": "Lead our talent acquisition efforts..."
                }
            ],
            "jobtoolz": [
                {
                    "title": "Marketing Manager",
                    "url": f"https://jobs.jobtoolz.com/{company}/mk_001",
                    "id": "jt_001",
                    "location": "Ghent, Belgium",
                    "department": "Marketing",
                    "description": "Lead our marketing initiatives across Benelux..."
                },
                {
                    "title": "Sales Representative",
                    "url": f"https://jobs.jobtoolz.com/{company}/sales_001",
                    "id": "jt_002",
                    "location": "Brussels, Belgium",
                    "department": "Sales",
                    "description": "Drive revenue growth in the Belgian market..."
                },
                {
                    "title": "Operations Manager",
                    "url": f"https://jobs.jobtoolz.com/{company}/ops_001",
                    "id": "jt_003",
                    "location": "Antwerp, Belgium",
                    "department": "Operations",
                    "description": "Optimize our operational processes..."
                },
                {
                    "title": "Customer Service Agent",
                    "url": f"https://jobs.jobtoolz.com/{company}/cs_001",
                    "id": "jt_004",
                    "location": "Mechelen, Belgium",
                    "department": "Customer Service",
                    "description": "Provide excellent customer support..."
                },
                {
                    "title": "Supply Chain Coordinator",
                    "url": f"https://jobs.jobtoolz.com/{company}/sc_001",
                    "id": "jt_005",
                    "location": "Liège, Belgium",
                    "department": "Logistics",
                    "description": "Coordinate supply chain activities..."
                },
                {
                    "title": "Accountant",
                    "url": f"https://jobs.jobtoolz.com/{company}/acc_001",
                    "id": "jt_006",
                    "location": "Brussels, Belgium",
                    "department": "Finance",
                    "description": "Manage financial records and reporting..."
                },
                {
                    "title": "Business Development Manager",
                    "url": f"https://jobs.jobtoolz.com/{company}/bd_001",
                    "id": "jt_007",
                    "location": "Ghent, Belgium",
                    "department": "Business Development",
                    "description": "Identify and pursue new business opportunities..."
                },
                {
                    "title": "Project Manager",
                    "url": f"https://jobs.jobtoolz.com/{company}/pm_001",
                    "id": "jt_008",
                    "location": "Brussels, Belgium",
                    "department": "Project Management",
                    "description": "Lead cross-functional projects..."
                },
                {
                    "title": "Graphic Designer",
                    "url": f"https://jobs.jobtoolz.com/{company}/gd_001",
                    "id": "jt_009",
                    "location": "Antwerp, Belgium",
                    "department": "Design",
                    "description": "Create visual content for marketing campaigns..."
                },
                {
                    "title": "HR Coordinator",
                    "url": f"https://jobs.jobtoolz.com/{company}/hr_001",
                    "id": "jt_010",
                    "location": "Brussels, Belgium",
                    "department": "Human Resources",
                    "description": "Support HR operations and employee relations..."
                },
                {
                    "title": "Warehouse Manager",
                    "url": f"https://jobs.jobtoolz.com/{company}/wh_001",
                    "id": "jt_011",
                    "location": "Liège, Belgium",
                    "department": "Logistics",
                    "description": "Oversee warehouse operations and inventory..."
                },
                {
                    "title": "Quality Assurance Specialist",
                    "url": f"https://jobs.jobtoolz.com/{company}/qa_001",
                    "id": "jt_012",
                    "location": "Ghent, Belgium",
                    "department": "Quality",
                    "description": "Ensure product quality standards..."
                },
                {
                    "title": "Social Media Manager",
                    "url": f"https://jobs.jobtoolz.com/{company}/sm_001",
                    "id": "jt_013",
                    "location": "Brussels, Belgium",
                    "department": "Marketing",
                    "description": "Manage our social media presence..."
                },
                {
                    "title": "Procurement Specialist",
                    "url": f"https://jobs.jobtoolz.com/{company}/proc_001",
                    "id": "jt_014",
                    "location": "Antwerp, Belgium",
                    "department": "Procurement",
                    "description": "Source and negotiate with suppliers..."
                }
            ],
            "recruitee": [
                {
                    "title": "UX/UI Designer",
                    "url": f"https://careers.recruitee.com/{company}/ux-designer",
                    "id": "rc_001",
                    "location": "Rotterdam, Netherlands",
                    "department": "Design",
                    "description": "Create delightful user experiences..."
                },
                {
                    "title": "Backend Engineer",
                    "url": f"https://careers.recruitee.com/{company}/backend-engineer",
                    "id": "rc_002",
                    "location": "Amsterdam, Netherlands",
                    "department": "Engineering",
                    "description": "Build scalable backend systems..."
                },
                {
                    "title": "Product Owner",
                    "url": f"https://careers.recruitee.com/{company}/product-owner",
                    "id": "rc_003",
                    "location": "Utrecht, Netherlands",
                    "department": "Product",
                    "description": "Define product roadmap and priorities..."
                },
                {
                    "title": "Machine Learning Engineer",
                    "url": f"https://careers.recruitee.com/{company}/ml-engineer",
                    "id": "rc_004",
                    "location": "Amsterdam, Netherlands",
                    "department": "AI/ML",
                    "description": "Develop ML models and algorithms..."
                },
                {
                    "title": "Solutions Architect",
                    "url": f"https://careers.recruitee.com/{company}/solutions-architect",
                    "id": "rc_005",
                    "location": "Rotterdam, Netherlands",
                    "department": "Engineering",
                    "description": "Design technical solutions for clients..."
                },
                {
                    "title": "Digital Marketing Manager",
                    "url": f"https://careers.recruitee.com/{company}/digital-marketing",
                    "id": "rc_006",
                    "location": "Amsterdam, Netherlands",
                    "department": "Marketing",
                    "description": "Lead digital marketing campaigns..."
                },
                {
                    "title": "Engineering Manager",
                    "url": f"https://careers.recruitee.com/{company}/eng-manager",
                    "id": "rc_007",
                    "location": "Utrecht, Netherlands",
                    "department": "Engineering",
                    "description": "Lead and grow engineering teams..."
                },
                {
                    "title": "Business Intelligence Analyst",
                    "url": f"https://careers.recruitee.com/{company}/bi-analyst",
                    "id": "rc_008",
                    "location": "Amsterdam, Netherlands",
                    "department": "Analytics",
                    "description": "Deliver insights through data analysis..."
                },
                {
                    "title": "Content Strategist",
                    "url": f"https://careers.recruitee.com/{company}/content-strategist",
                    "id": "rc_009",
                    "location": "Remote - Netherlands",
                    "department": "Marketing",
                    "description": "Develop content strategies and guidelines..."
                },
                {
                    "title": "Site Reliability Engineer",
                    "url": f"https://careers.recruitee.com/{company}/sre",
                    "id": "rc_010",
                    "location": "Rotterdam, Netherlands",
                    "department": "Infrastructure",
                    "description": "Ensure system reliability and uptime..."
                },
                {
                    "title": "Partnerships Manager",
                    "url": f"https://careers.recruitee.com/{company}/partnerships",
                    "id": "rc_011",
                    "location": "Amsterdam, Netherlands",
                    "department": "Business Development",
                    "description": "Build strategic partnerships..."
                },
                {
                    "title": "Technical Support Engineer",
                    "url": f"https://careers.recruitee.com/{company}/tech-support",
                    "id": "rc_012",
                    "location": "Utrecht, Netherlands",
                    "department": "Support",
                    "description": "Provide technical assistance to customers..."
                },
                {
                    "title": "Chief of Staff",
                    "url": f"https://careers.recruitee.com/{company}/chief-of-staff",
                    "id": "rc_013",
                    "location": "Amsterdam, Netherlands",
                    "department": "Executive",
                    "description": "Support executive leadership..."
                },
                {
                    "title": "Compliance Officer",
                    "url": f"https://careers.recruitee.com/{company}/compliance",
                    "id": "rc_014",
                    "location": "Amsterdam, Netherlands",
                    "department": "Legal & Compliance",
                    "description": "Ensure regulatory compliance..."
                }
            ],
            "workday": [
                {
                    "title": "HR Business Partner",
                    "url": f"https://{company}.workday.com/jobs/hr_001",
                    "id": "wd_001",
                    "location": "Mechelen, Belgium",
                    "department": "Human Resources",
                    "description": "Partner with business leaders on talent strategy..."
                },
                {
                    "title": "Payroll Specialist",
                    "url": f"https://{company}.workday.com/jobs/pr_001",
                    "id": "wd_002",
                    "location": "Brussels, Belgium",
                    "department": "Finance",
                    "description": "Process payroll and ensure compliance..."
                },
                {
                    "title": "Learning & Development Manager",
                    "url": f"https://{company}.workday.com/jobs/ld_001",
                    "id": "wd_003",
                    "location": "Antwerp, Belgium",
                    "department": "HR",
                    "description": "Design and deliver training programs..."
                },
                {
                    "title": "Talent Acquisition Specialist",
                    "url": f"https://{company}.workday.com/jobs/ta_001",
                    "id": "wd_004",
                    "location": "Brussels, Belgium",
                    "department": "Recruitment",
                    "description": "Source and hire top talent..."
                },
                {
                    "title": "Compensation Analyst",
                    "url": f"https://{company}.workday.com/jobs/comp_001",
                    "id": "wd_005",
                    "location": "Ghent, Belgium",
                    "department": "HR",
                    "description": "Analyze and design compensation structures..."
                },
                {
                    "title": "Employee Relations Manager",
                    "url": f"https://{company}.workday.com/jobs/er_001",
                    "id": "wd_006",
                    "location": "Brussels, Belgium",
                    "department": "HR",
                    "description": "Manage employee relations and workplace issues..."
                },
                {
                    "title": "HR Systems Administrator",
                    "url": f"https://{company}.workday.com/jobs/sys_001",
                    "id": "wd_007",
                    "location": "Mechelen, Belgium",
                    "department": "HR Technology",
                    "description": "Maintain HRIS and related systems..."
                },
                {
                    "title": "Benefits Coordinator",
                    "url": f"https://{company}.workday.com/jobs/ben_001",
                    "id": "wd_008",
                    "location": "Antwerp, Belgium",
                    "department": "HR",
                    "description": "Administer employee benefits programs..."
                },
                {
                    "title": "Organizational Development Consultant",
                    "url": f"https://{company}.workday.com/jobs/od_001",
                    "id": "wd_009",
                    "location": "Brussels, Belgium",
                    "department": "HR",
                    "description": "Drive organizational change initiatives..."
                },
                {
                    "title": "Diversity & Inclusion Manager",
                    "url": f"https://{company}.workday.com/jobs/di_001",
                    "id": "wd_010",
                    "location": "Brussels, Belgium",
                    "department": "HR",
                    "description": "Lead D&I programs and initiatives..."
                },
                {
                    "title": "HR Analytics Manager",
                    "url": f"https://{company}.workday.com/jobs/analytics_001",
                    "id": "wd_011",
                    "location": "Ghent, Belgium",
                    "department": "HR",
                    "description": "Deliver people analytics and insights..."
                },
                {
                    "title": "Onboarding Specialist",
                    "url": f"https://{company}.workday.com/jobs/onb_001",
                    "id": "wd_012",
                    "location": "Mechelen, Belgium",
                    "department": "HR",
                    "description": "Create exceptional onboarding experiences..."
                },
                {
                    "title": "Internal Communications Manager",
                    "url": f"https://{company}.workday.com/jobs/ic_001",
                    "id": "wd_013",
                    "location": "Brussels, Belgium",
                    "department": "Communications",
                    "description": "Drive internal communication strategies..."
                },
                {
                    "title": "Workforce Planning Analyst",
                    "url": f"https://{company}.workday.com/jobs/wfp_001",
                    "id": "wd_014",
                    "location": "Antwerp, Belgium",
                    "department": "HR",
                    "description": "Forecast workforce needs and trends..."
                }
            ],
            "icims": [
                {
                    "title": "Customer Success Manager",
                    "url": f"https://careers.icims.com/{company}/csm_001",
                    "id": "ic_001",
                    "location": "Eindhoven, Netherlands",
                    "department": "Customer Success",
                    "description": "Ensure customer satisfaction and retention..."
                },
                {
                    "title": "Implementation Consultant",
                    "url": f"https://careers.icims.com/{company}/impl_001",
                    "id": "ic_002",
                    "location": "Amsterdam, Netherlands",
                    "department": "Professional Services",
                    "description": "Guide customers through implementation..."
                },
                {
                    "title": "Technical Account Manager",
                    "url": f"https://careers.icims.com/{company}/tam_001",
                    "id": "ic_003",
                    "location": "Rotterdam, Netherlands",
                    "department": "Customer Success",
                    "description": "Provide technical guidance to enterprise clients..."
                },
                {
                    "title": "Solutions Consultant",
                    "url": f"https://careers.icims.com/{company}/sc_001",
                    "id": "ic_004",
                    "location": "Utrecht, Netherlands",
                    "department": "Sales",
                    "description": "Present solutions to prospective customers..."
                },
                {
                    "title": "Customer Support Specialist",
                    "url": f"https://careers.icims.com/{company}/support_001",
                    "id": "ic_005",
                    "location": "Eindhoven, Netherlands",
                    "department": "Support",
                    "description": "Resolve customer inquiries and issues..."
                },
                {
                    "title": "Renewals Manager",
                    "url": f"https://careers.icims.com/{company}/ren_001",
                    "id": "ic_006",
                    "location": "Amsterdam, Netherlands",
                    "department": "Customer Success",
                    "description": "Drive contract renewals and expansion..."
                },
                {
                    "title": "Training Specialist",
                    "url": f"https://careers.icims.com/{company}/train_001",
                    "id": "ic_007",
                    "location": "Rotterdam, Netherlands",
                    "department": "Education",
                    "description": "Deliver training to customers and partners..."
                },
                {
                    "title": "Product Specialist",
                    "url": f"https://careers.icims.com/{company}/ps_001",
                    "id": "ic_008",
                    "location": "Utrecht, Netherlands",
                    "department": "Product",
                    "description": "Support product launches and adoption..."
                },
                {
                    "title": "Customer Experience Manager",
                    "url": f"https://careers.icims.com/{company}/cx_001",
                    "id": "ic_009",
                    "location": "Amsterdam, Netherlands",
                    "department": "Customer Success",
                    "description": "Optimize customer journey and satisfaction..."
                },
                {
                    "title": "Integration Specialist",
                    "url": f"https://careers.icims.com/{company}/int_001",
                    "id": "ic_010",
                    "location": "Eindhoven, Netherlands",
                    "department": "Technical Services",
                    "description": "Configure system integrations..."
                },
                {
                    "title": "Customer Advocate",
                    "url": f"https://careers.icims.com/{company}/adv_001",
                    "id": "ic_011",
                    "location": "Rotterdam, Netherlands",
                    "department": "Customer Success",
                    "description": "Champion customer needs internally..."
                },
                {
                    "title": "Adoption Specialist",
                    "url": f"https://careers.icims.com/{company}/adopt_001",
                    "id": "ic_012",
                    "location": "Utrecht, Netherlands",
                    "department": "Customer Success",
                    "description": "Drive product adoption and usage..."
                },
                {
                    "title": "Customer Operations Analyst",
                    "url": f"https://careers.icims.com/{company}/ops_001",
                    "id": "ic_013",
                    "location": "Amsterdam, Netherlands",
                    "department": "Operations",
                    "description": "Analyze and optimize customer operations..."
                },
                {
                    "title": "Escalation Manager",
                    "url": f"https://careers.icims.com/{company}/esc_001",
                    "id": "ic_014",
                    "location": "Eindhoven, Netherlands",
                    "department": "Support",
                    "description": "Handle escalated customer issues..."
                }
            ],
            "smartrecruiters": [
                {
                    "title": "Technical Writer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/tech-writer",
                    "id": "sr_001",
                    "location": "Remote - Benelux",
                    "department": "Documentation",
                    "description": "Create technical documentation..."
                },
                {
                    "title": "API Developer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/api-dev",
                    "id": "sr_002",
                    "location": "Amsterdam, Netherlands",
                    "department": "Engineering",
                    "description": "Build and maintain APIs..."
                },
                {
                    "title": "Integration Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/int-eng",
                    "id": "sr_003",
                    "location": "Rotterdam, Netherlands",
                    "department": "Engineering",
                    "description": "Develop integration solutions..."
                },
                {
                    "title": "DevSecOps Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/devsecops",
                    "id": "sr_004",
                    "location": "Utrecht, Netherlands",
                    "department": "Security",
                    "description": "Implement security in development pipeline..."
                },
                {
                    "title": "Platform Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/platform",
                    "id": "sr_005",
                    "location": "Amsterdam, Netherlands",
                    "department": "Infrastructure",
                    "description": "Build and maintain platform infrastructure..."
                },
                {
                    "title": "Release Manager",
                    "url": f"https://jobs.smartrecruiters.com/{company}/release",
                    "id": "sr_006",
                    "location": "Remote - Netherlands",
                    "department": "Engineering",
                    "description": "Coordinate software releases..."
                },
                {
                    "title": "Technical Product Manager",
                    "url": f"https://jobs.smartrecruiters.com/{company}/tpm",
                    "id": "sr_007",
                    "location": "Amsterdam, Netherlands",
                    "department": "Product",
                    "description": "Drive technical product strategy..."
                },
                {
                    "title": "Database Administrator",
                    "url": f"https://jobs.smartrecruiters.com/{company}/dba",
                    "id": "sr_008",
                    "location": "Rotterdam, Netherlands",
                    "department": "Infrastructure",
                    "description": "Manage database systems..."
                },
                {
                    "title": "Network Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/network",
                    "id": "sr_009",
                    "location": "Utrecht, Netherlands",
                    "department": "Infrastructure",
                    "description": "Design and maintain network infrastructure..."
                },
                {
                    "title": "System Administrator",
                    "url": f"https://jobs.smartrecruiters.com/{company}/sysadmin",
                    "id": "sr_010",
                    "location": "Amsterdam, Netherlands",
                    "department": "IT",
                    "description": "Manage system infrastructure..."
                },
                {
                    "title": "Performance Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/perf",
                    "id": "sr_011",
                    "location": "Remote - Netherlands",
                    "department": "Engineering",
                    "description": "Optimize application performance..."
                },
                {
                    "title": "Test Automation Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/test-auto",
                    "id": "sr_012",
                    "location": "Rotterdam, Netherlands",
                    "department": "Quality",
                    "description": "Develop automated testing frameworks..."
                },
                {
                    "title": "Build Engineer",
                    "url": f"https://jobs.smartrecruiters.com/{company}/build",
                    "id": "sr_013",
                    "location": "Utrecht, Netherlands",
                    "department": "Engineering",
                    "description": "Maintain build and CI/CD systems..."
                },
                {
                    "title": "Technical Support Lead",
                    "url": f"https://jobs.smartrecruiters.com/{company}/support-lead",
                    "id": "sr_014",
                    "location": "Amsterdam, Netherlands",
                    "department": "Support",
                    "description": "Lead technical support team..."
                }
            ],
            "bamboohr": [
                {
                    "title": "Operations Manager",
                    "url": f"https://{company}.bamboohr.com/jobs/ops_001",
                    "id": "bh_001",
                    "location": "The Hague, Netherlands",
                    "department": "Operations",
                    "description": "Optimize operational efficiency..."
                },
                {
                    "title": "Office Manager",
                    "url": f"https://{company}.bamboohr.com/jobs/office_001",
                    "id": "bh_002",
                    "location": "Amsterdam, Netherlands",
                    "department": "Operations",
                    "description": "Manage office facilities and operations..."
                },
                {
                    "title": "Executive Assistant",
                    "url": f"https://{company}.bamboohr.com/jobs/ea_001",
                    "id": "bh_003",
                    "location": "Rotterdam, Netherlands",
                    "department": "Executive",
                    "description": "Support C-level executives..."
                },
                {
                    "title": "Facilities Coordinator",
                    "url": f"https://{company}.bamboohr.com/jobs/fac_001",
                    "id": "bh_004",
                    "location": "Utrecht, Netherlands",
                    "department": "Facilities",
                    "description": "Coordinate office facilities and services..."
                },
                {
                    "title": "Administrative Assistant",
                    "url": f"https://{company}.bamboohr.com/jobs/admin_001",
                    "id": "bh_005",
                    "location": "The Hague, Netherlands",
                    "department": "Administration",
                    "description": "Provide administrative support..."
                },
                {
                    "title": "Receptionist",
                    "url": f"https://{company}.bamboohr.com/jobs/recep_001",
                    "id": "bh_006",
                    "location": "Amsterdam, Netherlands",
                    "department": "Front Office",
                    "description": "Welcome visitors and manage front desk..."
                },
                {
                    "title": "Event Coordinator",
                    "url": f"https://{company}.bamboohr.com/jobs/event_001",
                    "id": "bh_007",
                    "location": "Rotterdam, Netherlands",
                    "department": "Operations",
                    "description": "Plan and execute company events..."
                },
                {
                    "title": "Travel Coordinator",
                    "url": f"https://{company}.bamboohr.com/jobs/travel_001",
                    "id": "bh_008",
                    "location": "Amsterdam, Netherlands",
                    "department": "Operations",
                    "description": "Manage corporate travel arrangements..."
                },
                {
                    "title": "Operations Analyst",
                    "url": f"https://{company}.bamboohr.com/jobs/ops-analyst_001",
                    "id": "bh_009",
                    "location": "The Hague, Netherlands",
                    "department": "Operations",
                    "description": "Analyze and improve operational processes..."
                },
                {
                    "title": "Vendor Manager",
                    "url": f"https://{company}.bamboohr.com/jobs/vendor_001",
                    "id": "bh_010",
                    "location": "Utrecht, Netherlands",
                    "department": "Procurement",
                    "description": "Manage vendor relationships..."
                },
                {
                    "title": "Process Improvement Specialist",
                    "url": f"https://{company}.bamboohr.com/jobs/process_001",
                    "id": "bh_011",
                    "location": "Rotterdam, Netherlands",
                    "department": "Operations",
                    "description": "Drive process optimization initiatives..."
                },
                {
                    "title": "Business Operations Coordinator",
                    "url": f"https://{company}.bamboohr.com/jobs/bizops_001",
                    "id": "bh_012",
                    "location": "Amsterdam, Netherlands",
                    "department": "Operations",
                    "description": "Support business operations activities..."
                },
                {
                    "title": "Office Assistant",
                    "url": f"https://{company}.bamboohr.com/jobs/assist_001",
                    "id": "bh_013",
                    "location": "The Hague, Netherlands",
                    "department": "Administration",
                    "description": "Provide general office support..."
                },
                {
                    "title": "Chief Operating Officer",
                    "url": f"https://{company}.bamboohr.com/jobs/coo_001",
                    "id": "bh_014",
                    "location": "Amsterdam, Netherlands",
                    "department": "Executive",
                    "description": "Oversee company operations..."
                }
            ]
        }
        
        # Return jobs for the specific provider, or generic jobs if not found
        return base_jobs.get(provider.lower(), [
            {
                "title": f"Test Position - {provider}",
                "url": f"https://example.com/jobs/test_001",
                "id": f"test_001",
                "location": "Amsterdam, Netherlands",
                "department": "Engineering",
                "description": "This is a test position for demonstration purposes."
            }
        ])

class ATSManager:
    @staticmethod
    def fetch_jobs(config: ATSConfig):
        """
        Fetch jobs from various ATS providers
        In TESTING_MODE, returns mock data without calling real APIs
        """
        s = config.system.lower()
        jobs = []
        
        # TESTING MODE: Return mock data
        if TESTING_MODE:
            print(f"🧪 TESTING MODE: Returning mock data for {s}")
            return MockATSData.get_mock_jobs(s, config.subdomain or "demo")
        
        # PRODUCTION MODE: Call real APIs
        try:
            if s == "jobtoolz":
                url = f"https://api.jobtoolz.com/v1/public/jobs/{config.subdomain}"
                headers = {}
                if config.api_key:
                    headers['Authorization'] = f"Bearer {config.api_key}"
                
                res = requests.get(url, headers=headers, timeout=30).json()
                jobs = [{
                    "title": j.get('title', 'Untitled'),
                    "url": j.get('url', ''),
                    "id": str(j.get('id', '')),
                    "location": j.get('location', ''),
                    "department": j.get('department', ''),
                    "description": j.get('description', '')
                } for j in res.get('data', [])]

            elif s == "recruitee":
                url = f"https://api.recruitee.com/c/{config.subdomain}/offers"
                headers = {
                    'Authorization': f"Bearer {config.api_key}"
                }
                
                res = requests.get(url, headers=headers, timeout=30).json()
                jobs = [{
                    "title": j.get('title', 'Untitled'),
                    "url": j.get('careers_url', ''),
                    "id": str(j.get('id', '')),
                    "location": j.get('location', ''),
                    "department": j.get('department', ''),
                    "description": j.get('description', '')
                } for j in res.get('offers', [])]

            elif s == "greenhouse":
                url = f"https://boards-api.greenhouse.io/v1/boards/{config.subdomain}/jobs"
                params = {'content': 'true'}
                
                res = requests.get(url, params=params, timeout=30).json()
                jobs = [{
                    "title": j.get('title', 'Untitled'),
                    "url": j.get('absolute_url', ''),
                    "id": str(j.get('id', '')),
                    "location": j.get('location', {}).get('name', '') if isinstance(j.get('location'), dict) else '',
                    "department": j.get('departments', [{}])[0].get('name', '') if j.get('departments') else '',
                    "description": j.get('content', '')
                } for j in res.get('jobs', [])]

            elif s == "lever":
                url = f"https://api.lever.co/v0/postings/{config.subdomain}"
                params = {'mode': 'json'}
                
                res = requests.get(url, params=params, timeout=30).json()
                jobs = [{
                    "title": j.get('text', 'Untitled'),
                    "url": j.get('hostedUrl', ''),
                    "id": j.get('id', ''),
                    "location": j.get('categories', {}).get('location', ''),
                    "department": j.get('categories', {}).get('team', ''),
                    "description": j.get('description', '')
                } for j in res if isinstance(j, dict)]

            elif s in ["workday", "icims"]:
                target_url = config.feed_url or f"https://{config.subdomain}.{s}.com/wday/cxs/jobs"
                response = requests.get(target_url, timeout=30)
                root = ET.fromstring(response.content)
                
                for item in root.findall('.//item') or root.findall('.//job'):
                    title_elem = item.find('title') or item.find('jobTitle')
                    link_elem = item.find('link') or item.find('jobUrl')
                    guid_elem = item.find('guid') or item.find('jobId')
                    loc_elem = item.find('location') or item.find('jobLocation')
                    dept_elem = item.find('department') or item.find('jobDepartment')
                    desc_elem = item.find('description') or item.find('jobDescription')
                    
                    jobs.append({
                        "title": title_elem.text if title_elem is not None else "Untitled",
                        "url": link_elem.text if link_elem is not None else "",
                        "id": guid_elem.text if guid_elem is not None else "",
                        "location": loc_elem.text if loc_elem is not None else "",
                        "department": dept_elem.text if dept_elem is not None else "",
                        "description": desc_elem.text if desc_elem is not None else ""
                    })

            elif s == "smartrecruiters":
                url = f"https://api.smartrecruiters.com/v1/companies/{config.subdomain}/postings"
                params = {'limit': 100}
                
                res = requests.get(url, params=params, timeout=30).json()
                jobs = [{
                    "title": j.get('name', 'Untitled'),
                    "url": f"https://jobs.smartrecruiters.com/{config.subdomain}/{j.get('id', '')}",
                    "id": str(j.get('id', '')),
                    "location": j.get('location', {}).get('city', '') if isinstance(j.get('location'), dict) else '',
                    "department": j.get('department', {}).get('label', '') if isinstance(j.get('department'), dict) else '',
                    "description": ''
                } for j in res.get('content', [])]

            elif s == "bamboohr":
                url = f"https://{config.subdomain}.bamboohr.com/jobs/embed2.php"
                headers = {
                    'Accept': 'application/json'
                }
                if config.api_key:
                    headers['Authorization'] = f"Basic {config.api_key}"
                
                response = requests.get(url, headers=headers, timeout=30)
                jobs = []

        except Exception as e:
            print(f"Error fetching from {s}: {str(e)}")
            if TESTING_MODE:
                # In testing mode, still return mock data on error
                return MockATSData.get_mock_jobs(s, config.subdomain or "demo")
            raise HTTPException(status_code=500, detail=f"Failed to fetch jobs from {s}: {str(e)}")

        return jobs

# API Endpoints

@app.get("/health")
async def health_check():
    mode = "TESTING (Mock Data)" if TESTING_MODE else "PRODUCTION (Real APIs)"
    return {
        "status": "healthy", 
        "message": "TalentDog ATS API is running",
        "mode": mode,
        "testing_mode": TESTING_MODE
    }

@app.post("/api/ats/connect")
async def connect_ats(request: ATSConnectionRequest):
    """
    Connect to an ATS provider and save configuration
    In TESTING_MODE, accepts any credentials
    """
    try:
        provider_lower = request.provider.lower()
        
        # Store configuration
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM ats_configurations WHERE provider = ?', (provider_lower,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute('''
                UPDATE ats_configurations 
                SET subdomain = ?, api_key = ?, feed_url = ?, is_active = 1, last_sync = ?
                WHERE provider = ?
            ''', (request.subdomain, request.api_key, request.feed_url, datetime.now(), provider_lower))
        else:
            cursor.execute('''
                INSERT INTO ats_configurations (provider, subdomain, api_key, feed_url, is_active)
                VALUES (?, ?, ?, ?, 1)
            ''', (provider_lower, request.subdomain, request.api_key, request.feed_url))
        
        conn.commit()
        conn.close()
        
        message = f"Successfully connected to {request.provider}"
        if TESTING_MODE:
            message += " (TESTING MODE - Using mock data)"
        
        return {
            "success": True,
            "message": message,
            "provider": request.provider,
            "testing_mode": TESTING_MODE
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/ats/disconnect/{provider}")
async def disconnect_ats(provider: str):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE ats_configurations SET is_active = 0 WHERE provider = ?', (provider.lower(),))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": f"Disconnected from {provider}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/ats/status")
async def get_ats_status():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT provider, subdomain, is_active, last_sync 
            FROM ats_configurations
        ''')
        
        configs = cursor.fetchall()
        conn.close()
        
        return [{
            "provider": c[0],
            "subdomain": c[1],
            "is_active": bool(c[2]),
            "last_sync": c[3]
        } for c in configs]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vacancies/sync-ats")
async def sync_ats(config: ATSConfig):
    try:
        jobs = ATSManager.fetch_jobs(config)
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        new_count = 0
        updated_count = 0

        for job in jobs:
            cursor.execute(
                'SELECT id FROM vacancies WHERE external_id = ? OR url = ?', 
                (job['id'], job['url'])
            )
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute('''
                    UPDATE vacancies 
                    SET title = ?, location = ?, department = ?, 
                        description = ?, updated_at = ?, source_provider = ?
                    WHERE id = ?
                ''', (
                    job['title'], 
                    job.get('location', ''), 
                    job.get('department', ''),
                    job.get('description', ''),
                    datetime.now(),
                    config.system,
                    existing[0]
                ))
                updated_count += 1
            else:
                cursor.execute('''
                    INSERT INTO vacancies 
                    (title, company, location, department, description, status, url, external_id, source_provider) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    job['title'], 
                    config.subdomain, 
                    job.get('location', ''),
                    job.get('department', ''),
                    job.get('description', ''),
                    "Open", 
                    job['url'], 
                    job['id'],
                    config.system
                ))
                new_count += 1
        
        cursor.execute('''
            UPDATE ats_configurations 
            SET last_sync = ? 
            WHERE provider = ?
        ''', (datetime.now(), config.system.lower()))
        
        conn.commit()
        conn.close()
        
        return {
            "success": True, 
            "total": len(jobs), 
            "new": new_count,
            "updated": updated_count,
            "provider": config.system,
            "testing_mode": TESTING_MODE
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/vacancies/sync-all")
async def sync_all_ats():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT provider, subdomain, api_key, feed_url 
            FROM ats_configurations 
            WHERE is_active = 1
        ''')
        
        configs = cursor.fetchall()
        conn.close()
        
        results = []
        total_new = 0
        total_updated = 0
        
        for config_row in configs:
            config = ATSConfig(
                system=config_row[0],
                subdomain=config_row[1] or "",
                api_key=config_row[2],
                feed_url=config_row[3]
            )
            
            try:
                result = await sync_ats(config)
                results.append({
                    "provider": config.system,
                    "success": True,
                    "new": result["new"],
                    "updated": result["updated"]
                })
                total_new += result["new"]
                total_updated += result["updated"]
            except Exception as e:
                results.append({
                    "provider": config.system,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "success": True,
            "results": results,
            "total_new": total_new,
            "total_updated": total_updated,
            "testing_mode": TESTING_MODE
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/vacancies")
async def get_vacancies(limit: int = 100, status: str = None):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        query = 'SELECT id, title, company, location, department, status, url, source_provider FROM vacancies'
        params = []
        
        if status:
            query += ' WHERE status = ?'
            params.append(status)
        
        query += ' ORDER BY created_at DESC LIMIT ?'
        params.append(limit)
        
        cursor.execute(query, params)
        
        vacancies = [{
            "id": row[0],
            "title": row[1],
            "company": row[2],
            "location": row[3],
            "department": row[4],
            "status": row[5],
            "url": row[6],
            "source": row[7]
        } for row in cursor.fetchall()]
        
        conn.close()
        
        return vacancies
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/vacancies/{vacancy_id}")
async def delete_vacancy(vacancy_id: int):
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM vacancies WHERE id = ?', (vacancy_id,))
        
        conn.commit()
        conn.close()
        
        return {"success": True, "message": "Vacancy deleted"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/talent-pool")
async def get_talent_pool(limit: int = 100):
    return []

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
