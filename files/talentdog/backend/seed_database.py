"""
Database Seeder for TalentDog
Populate database with 100 realistic talent profiles for testing
"""

import sqlite3
import random
from datetime import datetime, timedelta

# Sample data
FIRST_NAMES = ['Emma', 'Liam', 'Sophie', 'Noah', 'Lisa', 'Lucas', 'Anna', 'Max', 'Julia', 'Tom', 
               'Sarah', 'David', 'Eva', 'Mark', 'Laura', 'Tim', 'Nina', 'Sam', 'Mia', 'Alex',
               'Thomas', 'Elena', 'Jasper', 'Anisa', 'Willem', 'Linda', 'Kevin', 'Charlotte']

LAST_NAMES = ['de Vries', 'Jansen', 'Bakker', 'Visser', 'Smit', 'Meijer', 'de Boer', 'Mulder', 
              'de Groot', 'Bos', 'Vos', 'Peters', 'Hendriks', 'van Dijk', 'Vermeer', 'de Haan',
              'Koster', 'Prins', 'Blom', 'Huisman', 'de Witt', 'Rossi', 'van Dam', 'Farah']

ROLES = [
    'Senior DevOps Engineer', 'Product Lead', 'Frontend Developer', 'Backend Engineer',
    'Data Scientist', 'UX Designer', 'Cloud Architect', 'Security Engineer',
    'Mobile Developer', 'QA Engineer', 'Scrum Master', 'Engineering Manager',
    'ML Engineer', 'Full Stack Developer', 'Platform Engineer', 'Tech Lead',
    'Solutions Architect', 'Site Reliability Engineer', 'Analytics Engineer', 'Growth Hacker'
]

COMPANIES = [
    'ASML', 'Adyen', 'Picnic', 'Bunq', 'Booking.com', 'Just Eat Takeaway',
    'Philips', 'Shell', 'ING', 'Rabobank', 'TomTom', 'Coolblue', 'Bol.com',
    'Uber', 'Spotify', 'Mollie', 'MessageBird', 'Treatwell', 'WeTransfer'
]

CITIES = ['Amsterdam', 'Utrecht', 'Rotterdam', 'Eindhoven', 'Den Haag', 
          'Groningen', 'Tilburg', 'Almere', 'Breda', 'Nijmegen']

SECTORS = [
    'Technology', 'FinTech', 'E-commerce', 'Healthcare Tech', 'Cloud Infrastructure',
    'Artificial Intelligence', 'Cybersecurity', 'SaaS', 'IoT', 'Data Analytics'
]

SIGNAL_TYPES = ['TENURE EXPIRY', 'CORPORATE SHOCKWAVE', 'LAYOFFS', 'M&A / FUNDING', 'LEADERSHIP SHIFT']

# Professional photos from Pexels (free to use)
PHOTOS = [
    'https://images.pexels.com/photos/220453/pexels-photo-220453.jpeg',
    'https://images.pexels.com/photos/415829/pexels-photo-415829.jpeg',
    'https://images.pexels.com/photos/1239291/pexels-photo-1239291.jpeg',
    'https://images.pexels.com/photos/774909/pexels-photo-774909.jpeg',
    'https://images.pexels.com/photos/1222271/pexels-photo-1222271.jpeg',
    'https://images.pexels.com/photos/1065084/pexels-photo-1065084.jpeg',
    'https://images.pexels.com/photos/1080213/pexels-photo-1080213.jpeg',
    'https://images.pexels.com/photos/1043471/pexels-photo-1043471.jpeg',
    'https://images.pexels.com/photos/1181690/pexels-photo-1181690.jpeg',
    'https://images.pexels.com/photos/1037995/pexels-photo-1037995.jpeg',
]

def generate_start_date():
    """Generate random start date between 6 months and 5 years ago"""
    days_ago = random.randint(180, 1825)  # 6 months to 5 years
    return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

def calculate_tenure_months(start_date):
    """Calculate tenure in months from start date"""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    return (datetime.now() - start).days // 30

def generate_signal_description(signal_type, name, company, tenure_months):
    """Generate realistic signal description"""
    descriptions = {
        'TENURE EXPIRY': f"{name} heeft de {tenure_months}-maanden drempel bereikt bij {company}. Benchmark voor deze sector is {random.randint(18, 36)} maanden. Window of Opportunity staat NU open.",
        'CORPORATE SHOCKWAVE': f"{company} heeft {random.randint(10, 60)} dagen geleden een grote reorganisatie aangekondigd. Historische attrition rate na deze events is {random.randint(15, 35)}%.",
        'LAYOFFS': f"{company} heeft recent {random.randint(50, 300)} medewerkers laten gaan. {name} behoort tot de overgebleven {random.randint(60, 90)}% en zoekt mogelijk stabiliteit.",
        'M&A / FUNDING': f"{company} werd {random.randint(10, 90)} dagen geleden overgenomen. {name}'s huidige rol kan veranderen door integratie. Prime timing voor benadering.",
        'LEADERSHIP SHIFT': f"{company} heeft een nieuwe {random.choice(['CTO', 'CEO', 'CPO'])} aangesteld. {name} staat mogelijk open voor nieuwe uitdagingen onder de nieuwe koers."
    }
    return descriptions[signal_type]

def generate_story(name, company, tenure_years, signal_type):
    """Generate AI-style talent story"""
    stories = [
        f"{name} heeft de afgelopen {tenure_years} jaar bij {company} gewerkt aan schaalbare cloud platformen. Met het huidige {signal_type.lower()} signaal is dit het perfecte moment voor een nieuwe uitdaging die meer verantwoordelijkheid biedt.",
        f"Na {tenure_years} jaar bij {company} heeft {name} bewezen ervaring in het leiden van complexe technische projecten. De recente {signal_type.lower()} situatie maakt dit een strategisch moment voor outreach.",
        f"{name} is een key contributor bij {company} met {tenure_years} jaar aan impact. Het {signal_type.lower()} signaal wijst erop dat ze openstaan voor rollen met meer autonomie en technische ownership."
    ]
    return random.choice(stories)

def generate_background(name, role, sector, years):
    """Generate professional background"""
    return f"{name} is een ervaren {role.lower()} met {years}+ jaar ervaring in {sector.lower()}. Bekend om excellente teamwork, technische diepgang en strategisch denken. Track record van het leveren van innovatieve oplossingen en snelle delivery."

def seed_database():
    """Populate database with 100 realistic profiles"""
    
    print("🌱 Starting database seed...")
    
    # Connect to database
    conn = sqlite3.connect('/home/claude/talentdog/database/talentdog.db')
    cursor = conn.cursor()
    
    # Clear existing data
    cursor.execute('DELETE FROM talent_profiles')
    
    profiles_added = 0
    
    for i in range(100):
        # Generate profile data
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        name = f"{first_name} {last_name}"
        
        role = random.choice(ROLES)
        company = random.choice(COMPANIES)
        city = random.choice(CITIES)
        sector = random.choice(SECTORS)
        signal_type = random.choice(SIGNAL_TYPES)
        
        start_date = generate_start_date()
        tenure_months = calculate_tenure_months(start_date)
        tenure_years = round(tenure_months / 12, 1)
        
        email = f"{first_name.lower()}.{last_name.lower()}@{company.lower().replace(' ', '')}.com"
        photo = PHOTOS[i % len(PHOTOS)] + f"?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop&v={i}"
        
        signal_description = generate_signal_description(signal_type, first_name, company, tenure_months)
        story = generate_story(first_name, company, tenure_years, signal_type)
        background = generate_background(name, role, sector, random.randint(3, 10))
        
        points = random.randint(50, 100)
        
        # Insert into database
        cursor.execute('''
            INSERT INTO talent_profiles 
            (name, role, current_company, location, sector, linkedin_url, email, 
             start_date, tenure_months, signal_type, signal_description, 
             points, photo_url, story, background)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            role,
            company,
            f"{city}, Netherlands",
            sector,
            f"https://linkedin.com/in/{first_name.lower()}-{last_name.lower()}",
            email,
            start_date,
            tenure_months,
            signal_type,
            signal_description,
            points,
            photo,
            story,
            background
        ))
        
        profiles_added += 1
        
        if (i + 1) % 20 == 0:
            print(f"  ✅ Added {i + 1} profiles...")
    
    # Also add companies to company monitoring table
    for company in COMPANIES:
        cursor.execute('''
            INSERT OR IGNORE INTO companies (name, last_news_check)
            VALUES (?, ?)
        ''', (company, datetime.now().isoformat()))
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Successfully seeded database with {profiles_added} talent profiles!")
    print(f"✅ Added {len(COMPANIES)} companies to monitoring")
    print(f"\n🚀 Ready to use! Start the backend and frontend to see the data.")

if __name__ == "__main__":
    seed_database()
