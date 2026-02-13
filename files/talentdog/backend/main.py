def is_genuine_job_title(title):
    """
    Controleert of de tekst een echte functietitel is.
    """
    # Verwijder overtollige spaties en witregels voor de check
    title_clean = " ".join(title.lower().split())
    
    # Uitgebreide markers gebaseerd op de Conxion lijst
    job_markers = [
        'engineer', 'developer', 'manager', 'consultant', 'advisor', 
        'specialist', 'partner', 'ciso', 'lead', 'sales', 'account', 
        'support', 'project', 'central', 'cloud', 'data', 'software', 'architect'
    ]
    
    # Woorden die we absoluut NIET willen
    blacklist = ['klik hier', 'solliciteer', 'spontaan', 'lees meer', 'onze vacatures', 'cookies', 'privacy']

    if any(word in title_clean for word in blacklist):
        return False
    
    # Check of een van de markers in de tekst voorkomt
    has_marker = any(marker in title_clean for marker in job_markers)
    
    # Iets ruimere lengte check voor titels als "Freelance HR Business Partner (2 dagen/week)"
    is_correct_length = 5 < len(title_clean) < 100
    
    return has_marker and is_correct_length

@app.post("/api/vacancies/sync")
async def sync_vacancies(data: VacancySync):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(data.url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found_count = 0
        # Gebruik een set om dubbele URL's in één run te voorkomen
        processed_urls = set()

        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Stap 1: Pak ALLE tekst binnen de link (ook als het in meerdere spans/divs staat)
            raw_text = link.get_text(" ", strip=True)
            
            # Stap 2: Validatie van de functietitel
            if is_genuine_job_title(raw_text):
                full_url = urllib.parse.urljoin(data.url, href)
                
                # Voorkom dubbele verwerking
                if full_url in processed_urls:
                    continue
                
                # VERSOEPELDE URL CHECK: 
                # Op jobs.conxion.be bevatten de echte job-links vaak 'jobs' of eindigen ze op een unieke slug
                # We laten de restrictie op 'vacature' vallen als de titel sterk genoeg is
                is_likely_job_link = any(k in full_url.lower() for k in ['job', 'vacature', '/p/', 'career']) or len(href.split('/')) > 2

                if is_likely_job_link:
                    processed_urls.add(full_url)
                    clean_title = clean_job_title(raw_text)
                    
                    # Deep scan voor requirements
                    try:
                        detail_res = requests.get(full_url, headers=headers, timeout=5)
                        reqs = extract_requirements(detail_res.text)
                    except:
                        reqs = ""

                    # Opslaan in de database
                    conn = sqlite3.connect(DB_PATH)
                    cursor = conn.cursor()
                    cursor.execute('SELECT id FROM vacancies WHERE url = ?', (full_url,))
                    
                    if not cursor.fetchone():
                        cursor.execute('''INSERT INTO vacancies (title, company, requirements, status, url) 
                                         VALUES (?, ?, ?, ?, ?)''', 
                                      (clean_title, "Conxion", reqs, "Open", full_url))
                        found_count += 1
                    conn.commit()
                    conn.close()
        
        return {"success": True, "new_vacancies": found_count}
    except Exception as e:
        print(f"Error during sync: {e}")
        raise HTTPException(status_code=500, detail=str(e))
