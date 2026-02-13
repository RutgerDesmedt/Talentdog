def is_genuine_job_title(title):
    """
    Controleert of de tekst een echte functietitel is.
    """
    title_clean = title.lower()
    
    # Specifieke markers gebaseerd op jouw lijst van Conxion
    job_markers = [
        'engineer', 'developer', 'manager', 'consultant', 'advisor', 
        'specialist', 'partner', 'ciso', 'lead', 'sales', 'account', 
        'support', 'project manager', 'business central', 'cloud', 'data'
    ]
    
    # Woorden die vaak op knoppen staan maar GEEN vacaturetitel zijn
    blacklist = ['klik hier', 'solliciteer', 'spontaan', 'lees meer', 'onze', 'vacatures', 'over']

    # 1. Mag geen blacklist woorden bevatten
    if any(word in title_clean for word in blacklist):
        return False
    
    # 2. Moet minstens één job marker bevatten
    # 3. Moet een realistische lengte hebben (bijv. tussen 5 en 60 tekens)
    has_marker = any(marker in title_clean for marker in job_markers)
    is_correct_length = 5 < len(title) < 60
    
    return has_marker and is_correct_length

@app.post("/api/vacancies/sync")
async def sync_vacancies(data: VacancySync):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        res = requests.get(data.url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        found_count = 0
        # We kijken naar alle links op de pagina
        for link in soup.find_all('a', href=True):
            href = link['href']
            
            # Stap 1: Pak de tekst. Soms zit de titel in een <h3> of <span> binnen de <a>
            inner_tag = link.find(['h2', 'h3', 'h4', 'span', 'p'])
            raw_text = inner_tag.get_text().strip() if inner_tag else link.get_text().strip()
            
            # Stap 2: Validatie
            if is_genuine_job_title(raw_text):
                full_url = urllib.parse.urljoin(data.url, href)
                
                # Voorkom dat we dubbele of onlogische links pakken
                if "vacature" in full_url.lower() or "/p/" in full_url.lower() or "jobs" in full_url.lower():
                    clean_title = clean_job_title(raw_text)
                    
                    # Deep scan voor requirements (keywords)
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
        raise HTTPException(status_code=500, detail=str(e))
