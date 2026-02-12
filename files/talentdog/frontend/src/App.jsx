import React, { useState, useEffect } from 'react';
import { 
  Plus, LayoutGrid, Briefcase, Zap, ClipboardList, CheckCircle2, Settings, Database,
  Sparkles, Edit2, Trash2, User, Heart, MoreHorizontal, ArrowLeft, Trophy, Bell,
  ChevronDown, TrendingUp, Users, AlertTriangle, ExternalLink, Globe, Linkedin,
  MapPin, Building2, Send, ChevronRight, Clock, Target, Filter, Search, Upload
} from 'lucide-react';

// API Configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const TalentDogLogo = () => (
  <div className="flex items-center space-x-3 select-none">
    <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center shadow-lg shadow-black/10">
      <Zap size={22} className="text-white fill-white" />
    </div>
    <span className="text-2xl font-bold tracking-tight text-[#111827]">TalentDog</span>
  </div>
);

const App = () => {
  const [activeTab, setActiveTab] = useState('My Talent Pool');
  const [activeSignalTab, setActiveSignalTab] = useState('All Signals');
  const [view, setView] = useState('overview');
  const [selectedTalent, setSelectedTalent] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(false);
  
  // Data states
  const [profiles, setProfiles] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  
  const profilesPerPage = 12;

  const signalTypes = [
    'All Signals', 
    'Tenure Expiry', 
    'Layoffs',
    'M&A / Funding', 
    'Leadership Shift',
    'Corporate Shockwave'
  ];

  // ==================== API CALLS ====================
  
  useEffect(() => {
    loadTalentPool();
    loadVacancies();
  }, []);

  const loadTalentPool = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/talent-pool?limit=100`);
      const data = await response.json();
      setProfiles(data);
    } catch (error) {
      console.error('Failed to load talent pool:', error);
      // Use mock data as fallback
      setProfiles(generateMockProfiles());
    } finally {
      setLoading(false);
    }
  };

  const loadVacancies = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies`);
      const data = await response.json();
      setVacancies(data);
    } catch (error) {
      console.error('Failed to load vacancies:', error);
      setVacancies([]);
    }
  };

  const syncVacancy = async (url) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          title: 'New Position',
          url: url 
        })
      });
      
      if (response.ok) {
        alert('✅ Vacature succesvol gesynchroniseerd!');
        loadVacancies();
      }
    } catch (error) {
      alert('❌ Fout bij synchroniseren: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const shareWithTeam = async (talent, channel) => {
    try {
      await fetch(`${API_BASE_URL}/api/signals/share`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          talentId: talent.id,
          signalType: talent.signalType,
          channel: channel
        })
      });
      alert(`✅ Gedeeld via ${channel}!`);
    } catch (error) {
      alert('❌ Fout bij delen: ' + error.message);
    }
  };

  // ==================== MOCK DATA GENERATOR ====================
  
  const generateMockProfiles = () => {
    const firstNames = ['Emma', 'Liam', 'Sophie', 'Noah', 'Lisa', 'Lucas', 'Anna', 'Max', 'Julia', 'Tom'];
    const lastNames = ['de Vries', 'Jansen', 'Bakker', 'Visser', 'Smit', 'Meijer', 'de Boer', 'Mulder'];
    const roles = ['Senior DevOps Engineer', 'Product Lead', 'Data Scientist', 'Cloud Architect'];
    const companies = ['ASML', 'Adyen', 'Picnic', 'Bunq', 'Booking.com', 'Philips', 'Shell'];
    const cities = ['Utrecht', 'Amsterdam', 'Rotterdam', 'Eindhoven'];
    const sectors = ['Technology', 'FinTech', 'E-commerce', 'Healthcare Tech'];
    const signalTypes = ['TENURE EXPIRY', 'CORPORATE SHOCKWAVE', 'LAYOFFS', 'M&A / FUNDING'];
    
    const profiles = [];
    for (let i = 0; i < 100; i++) {
      const name = `${firstNames[i % firstNames.length]} ${lastNames[i % lastNames.length]}`;
      const signalType = signalTypes[i % signalTypes.length];
      
      profiles.push({
        id: i + 1,
        rank: `#${i + 1}`,
        name,
        role: roles[i % roles.length],
        currentCompany: companies[i % companies.length],
        location: `${cities[i % cities.length]}, NL`,
        sector: sectors[i % sectors.length],
        points: Math.floor(Math.random() * 50) + 50,
        photo: `https://images.pexels.com/photos/${220453 + (i % 10)}/pexels-photo.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop`,
        signalType,
        signalDescription: `${name} heeft belangrijke ontwikkelingen bij ${companies[i % companies.length]}. Perfect moment voor contact.`,
        matchedVacancy: '',
        story: `${name} is klaar voor een nieuwe uitdaging na sterke prestaties.`,
        background: `Ervaren ${roles[i % roles.length]} met bewezen track record.`,
        email: `${name.toLowerCase().replace(' ', '.')}@example.com`
      });
    }
    return profiles;
  };

  // ==================== FILTERING & PAGINATION ====================
  
  const filteredProfiles = profiles.filter(profile => {
    const matchesSearch = profile.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         profile.role.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         profile.currentCompany.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesSignal = activeSignalTab === 'All Signals' || 
                         profile.signalType.toLowerCase().includes(activeSignalTab.toLowerCase());
    return matchesSearch && matchesSignal;
  });

  const totalPages = Math.ceil(filteredProfiles.length / profilesPerPage);
  const displayedProfiles = filteredProfiles.slice(
    (currentPage - 1) * profilesPerPage,
    currentPage * profilesPerPage
  );

  const handleTalentClick = (talent) => {
    setSelectedTalent(talent);
    setView('talent-detail');
  };

  // ==================== RENDER FUNCTIONS ====================

  const renderTalentDetail = () => {
    if (!selectedTalent) return null;

    return (
      <div className="animate-in fade-in slide-in-from-right-4 duration-500 pb-20">
        <div className="flex justify-between items-center mb-8">
          <button 
            onClick={() => setView('overview')}
            className="flex items-center space-x-2 text-gray-900 font-bold hover:opacity-70 transition-opacity"
          >
            <ArrowLeft size={20} />
            <span className="text-lg">Back</span>
          </button>
          <div className="flex items-center space-x-3">
            <button className="flex items-center space-x-2 px-4 py-2 border border-gray-200 rounded-lg text-sm font-bold text-gray-700 hover:bg-gray-50">
              <Briefcase size={16} />
              <span>VIEW IN CRM</span>
            </button>
          </div>
        </div>

        <div className="flex items-start justify-between mb-10">
          <div className="flex items-center space-x-6">
            <div className="relative">
              <div className="w-24 h-24 rounded-2xl overflow-hidden border-2 border-white shadow-xl">
                <img src={selectedTalent.photo} className="w-full h-full object-cover" alt={selectedTalent.name} />
              </div>
              <div className="absolute -top-3 -left-3 bg-[#4ADE80] text-white text-[10px] font-black px-2 py-1 rounded shadow-sm uppercase tracking-tighter">
                New Info
              </div>
            </div>
            <div>
              <h1 className="text-4xl font-black text-gray-900 tracking-tight">{selectedTalent.name}</h1>
              <div className="flex items-center space-x-4 mt-3 text-gray-500 font-semibold text-sm">
                <div className="flex items-center space-x-1.5">
                  <Building2 size={16} className="text-gray-300" />
                  <span>{selectedTalent.sector}</span>
                </div>
                <span>|</span>
                <div className="flex items-center space-x-1.5">
                  <User size={16} className="text-gray-300" />
                  <span>{selectedTalent.email}</span>
                </div>
                <span>|</span>
                <div className="flex items-center space-x-1.5">
                  <MapPin size={16} className="text-gray-300" />
                  <span>{selectedTalent.location}</span>
                </div>
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-[54px] font-black text-gray-900 leading-none">{selectedTalent.points}</div>
            <div className="text-sm font-black text-gray-400 uppercase tracking-widest mt-1">Points</div>
          </div>
        </div>

        <div className="grid grid-cols-12 gap-8">
          <div className="col-span-8 space-y-8">
            <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm">
              <div className="flex items-center space-x-2 mb-6 text-gray-400">
                <ClipboardList size={18} />
                <span className="text-xs font-black uppercase tracking-widest">Talent Story</span>
              </div>
              <div className="relative z-10">
                <h2 className="text-3xl font-black text-gray-900 mb-6 leading-tight">
                  {selectedTalent.name}'s {selectedTalent.signalType === 'TENURE EXPIRY' ? 'Strategic Exit Window' : 'Career Shift Opportunity'}
                </h2>
                <p className="text-lg text-gray-600 leading-relaxed font-medium">{selectedTalent.story}</p>
              </div>
            </div>

            <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm">
              <div className="flex items-center space-x-2 mb-6 text-gray-400">
                <Zap size={18} />
                <span className="text-xs font-black uppercase tracking-widest">Verified Signals</span>
              </div>
              <div className="flex items-center justify-between p-5 bg-[#F9FAFB] rounded-2xl border border-gray-50">
                <div className="flex items-center space-x-4">
                  <div className="p-2 bg-orange-100 rounded-lg">
                    <AlertTriangle size={20} className="text-orange-600" />
                  </div>
                  <div>
                    <p className="text-sm font-bold text-gray-900 uppercase tracking-tight">{selectedTalent.signalType}</p>
                    <p className="text-xs text-gray-500 font-medium">Verified via LinkedIn & Corporate Filings</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="col-span-4 space-y-8">
            <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm">
              <div className="flex items-center space-x-2 mb-6 text-gray-400">
                <Building2 size={18} />
                <span className="text-xs font-black uppercase tracking-widest">Career Background</span>
              </div>
              <p className="text-sm text-gray-500 leading-relaxed font-medium mb-8">{selectedTalent.background}</p>
              <div className="flex flex-wrap gap-2">
                <div className="flex items-center space-x-2 text-[11px] font-black text-gray-400 uppercase bg-gray-50 p-2.5 rounded-lg border border-gray-100 w-fit">
                   <Linkedin size={12} />
                   <span>LINKEDIN</span>
                </div>
              </div>
            </div>

            <div className="space-y-3">
              <button 
                onClick={() => shareWithTeam(selectedTalent, 'slack')}
                className="w-full bg-black text-white py-4 rounded-[2rem] flex items-center justify-center space-x-3 text-lg font-black hover:opacity-90 transition-all shadow-xl shadow-black/10"
              >
                <Send size={20} />
                <span>Share via Slack</span>
              </button>
              <button 
                onClick={() => shareWithTeam(selectedTalent, 'teams')}
                className="w-full bg-blue-600 text-white py-4 rounded-[2rem] flex items-center justify-center space-x-3 text-lg font-black hover:opacity-90 transition-all"
              >
                <Send size={20} />
                <span>Share via Teams</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderVacancies = () => (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
      <header className="flex items-center justify-between mb-12">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">My Vacancies</h1>
          <p className="text-sm text-gray-400 font-normal mt-2">Monitor talent matches across {vacancies.length} active roles.</p>
        </div>
        <div className="flex items-center space-x-3">
          <input 
            type="text" 
            placeholder="Paste vacancy URL..." 
            className="px-4 py-2 border border-gray-200 rounded-lg text-sm w-96"
            id="vacancy-url-input"
          />
          <button 
            onClick={() => {
              const url = document.getElementById('vacancy-url-input').value;
              if (url) syncVacancy(url);
            }}
            className="flex items-center space-x-2 bg-black text-white px-4 py-2 rounded-lg hover:opacity-90"
            disabled={loading}
          >
            <Upload size={16} />
            <span className="text-sm font-bold">{loading ? 'Syncing...' : 'Sync Vacancy'}</span>
          </button>
        </div>
      </header>

      {vacancies.length === 0 ? (
        <div className="text-center py-20">
          <Target size={64} className="mx-auto text-gray-300 mb-4" />
          <h3 className="text-2xl font-bold text-gray-900 mb-2">No vacancies yet</h3>
          <p className="text-gray-500">Add a vacancy URL above to start matching talent</p>
        </div>
      ) : (
        <div className="space-y-8">
          {vacancies.map((vacancy) => (
            <div key={vacancy.id} className="bg-white border border-gray-100 rounded-[2.5rem] shadow-sm overflow-hidden">
              <div className="p-8 border-b border-gray-50 bg-[#F9FAFB]/30">
                <div className="flex items-center justify-between">
                  <div className="flex items-start space-x-5">
                    <div className="w-14 h-14 bg-white border border-gray-100 rounded-2xl flex items-center justify-center shadow-sm text-gray-400">
                      <Target size={28} />
                    </div>
                    <div>
                      <h2 className="text-2xl font-black text-gray-900 tracking-tight">{vacancy.title}</h2>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400 font-bold">
                        <span className="flex items-center space-x-1.5"><Building2 size={14} /> <span>{vacancy.department || 'Unknown Dept'}</span></span>
                        <span className="flex items-center space-x-1.5"><MapPin size={14} /> <span>{vacancy.location || 'Unknown'}</span></span>
                      </div>
                    </div>
                  </div>
                  <span className="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest bg-green-50 text-green-600">
                    {vacancy.status}
                  </span>
                </div>
              </div>

              <div className="p-8">
                <div className="flex items-center justify-between mb-8 px-2">
                  <h3 className="text-[10px] font-black text-gray-400 tracking-[0.2em] uppercase">Matching Talent</h3>
                  <span className="text-xs font-bold text-gray-400">{vacancy.matches?.length || 0} Candidates</span>
                </div>
                
                <div className="grid grid-cols-3 gap-6">
                  {(vacancy.matches || []).slice(0, 6).map((match) => (
                    <div 
                      key={match.id}
                      onClick={() => handleTalentClick(match)}
                      className="group flex items-center p-5 border border-gray-100 rounded-[2rem] hover:border-gray-900 hover:shadow-xl transition-all cursor-pointer"
                    >
                      <div className="w-16 h-16 rounded-2xl overflow-hidden border border-gray-50 flex-shrink-0">
                        <img src={match.photo} className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all" alt={match.name} />
                      </div>
                      <div className="ml-5 flex-1">
                        <h4 className="text-base font-black text-gray-900">{match.name}</h4>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-[9px] font-black text-orange-600 bg-orange-50 px-2 py-0.5 rounded-md uppercase">{match.signalType}</span>
                          <span className="text-xs font-bold text-gray-400">{match.points}</span>
                        </div>
                      </div>
                      <ChevronRight size={20} className="text-gray-200 group-hover:text-black" />
                    </div>
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderTalentPool = () => (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
      <header className="flex items-center justify-between mb-10">
        <div>
          <h1 className="text-4xl font-bold text-gray-900">My Talent Pool</h1>
          <p className="text-sm text-gray-400 font-normal mt-2">Real-time signals across {profiles.length} profiles</p>
        </div>
      </header>

      <div className="flex flex-wrap gap-3 mb-12">
        {signalTypes.map((type) => (
          <button
            key={type}
            onClick={() => {
              setActiveSignalTab(type);
              setCurrentPage(1);
            }}
            className={`px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${
              activeSignalTab === type 
              ? 'bg-black text-white' 
              : 'bg-white text-gray-400 hover:text-gray-700 border border-gray-200'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="text-center py-20">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="text-gray-500 mt-4">Loading talent pool...</p>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-8 mb-12">
            {displayedProfiles.map((candidate, idx) => (
              <div 
                key={candidate.id} 
                onClick={() => handleTalentClick(candidate)}
                className="group relative bg-white border border-gray-100 rounded-3xl flex flex-col transition-all hover:shadow-lg cursor-pointer overflow-hidden"
              >
                <div className="absolute -top-3 left-8 z-20">
                  <div className="bg-white px-5 py-1 rounded-full shadow-sm border border-gray-100">
                    <span className="text-sm font-bold text-gray-400">#{idx + 1 + (currentPage - 1) * profilesPerPage}</span>
                  </div>
                </div>

                <div className="p-8 pt-12">
                  <div className="flex items-center space-x-4 mb-8">
                    <div className="w-16 h-16 rounded-2xl overflow-hidden flex-shrink-0">
                      <img src={candidate.photo} alt={candidate.name} className="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-700" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold text-gray-900">{candidate.name}</h3>
                      <p className="text-sm text-gray-400 uppercase tracking-wide font-medium mt-0.5">{candidate.role}</p>
                    </div>
                  </div>

                  <div className="mb-8 p-5 bg-gray-50 rounded-2xl">
                    <div className="flex items-center space-x-2 mb-3">
                      <Zap size={12} className="text-gray-400" />
                      <h4 className="text-[10px] font-bold text-gray-900 uppercase tracking-[0.1em]">{candidate.signalType}</h4>
                    </div>
                    <p className="text-sm text-gray-700 leading-relaxed">{candidate.signalDescription}</p>
                  </div>

                  <div className="flex items-center space-x-3 text-sm">
                    <Heart size={16} className="text-gray-300" />
                    <span className="text-xs text-gray-400 uppercase tracking-wider font-bold">Score</span>
                    <span className="text-sm text-gray-900 font-medium">{candidate.points} points</span>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex justify-center items-center space-x-2 mt-12">
              <button
                onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                disabled={currentPage === 1}
                className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium disabled:opacity-50"
              >
                Previous
              </button>
              <div className="text-sm font-medium text-gray-600">
                Page {currentPage} of {totalPages}
              </div>
              <button
                onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                disabled={currentPage === totalPages}
                className="px-4 py-2 border border-gray-200 rounded-lg text-sm font-medium disabled:opacity-50"
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );

  const renderSystemSettings = () => (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
      <header className="mb-12">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">System Settings</h1>
        <p className="text-sm text-gray-400 font-normal mt-2">Configure TalentDog intelligence engine</p>
      </header>

      <div className="grid grid-cols-3 gap-8">
        <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
          <div className="flex justify-between items-start mb-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Users size={24} /></div>
              <div>
                <h3 className="text-[15px] font-bold text-gray-900">Talent Pool</h3>
                <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">OPERATIONAL</p>
              </div>
            </div>
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400"></div>
          </div>
          <div className="mb-10">
            <span className="text-5xl font-black text-gray-900 tracking-tight">{profiles.length}</span>
            <p className="text-sm font-medium text-gray-400 mt-2">Active Profiles</p>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
          <div className="flex justify-between items-start mb-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Target size={24} /></div>
              <div>
                <h3 className="text-[15px] font-bold text-gray-900">Vacancies</h3>
                <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">OPERATIONAL</p>
              </div>
            </div>
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400"></div>
          </div>
          <div className="mb-10">
            <span className="text-5xl font-black text-gray-900 tracking-tight">{vacancies.length}</span>
            <p className="text-sm font-medium text-gray-400 mt-2">Active Roles</p>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
          <div className="flex justify-between items-start mb-8">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Sparkles size={24} /></div>
              <div>
                <h3 className="text-[15px] font-bold text-gray-900">AI Matching</h3>
                <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">POWERED BY GEMINI</p>
              </div>
            </div>
            <div className="w-2.5 h-2.5 rounded-full bg-emerald-400"></div>
          </div>
          <div className="mb-10">
            <span className="text-5xl font-black text-gray-900 tracking-tight">AI</span>
            <p className="text-sm font-medium text-gray-400 mt-2">Intelligence Engine</p>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-100 rounded-2xl p-8 mt-8">
        <h3 className="text-lg font-bold text-blue-900 mb-4">🚀 API Configuration</h3>
        <p className="text-sm text-blue-700 mb-4">
          Configure your environment variables in <code className="bg-white px-2 py-1 rounded">.env</code> file:
        </p>
        <ul className="text-sm text-blue-700 space-y-2">
          <li>• <strong>GEMINI_API_KEY</strong> - For AI matching & briefings</li>
          <li>• <strong>SERPER_API_KEY</strong> - For company signal detection</li>
          <li>• <strong>SCRAPINGDOG_KEY</strong> - For LinkedIn profile scraping</li>
          <li>• <strong>SLACK_WEBHOOK_URL</strong> - For Slack notifications</li>
          <li>• <strong>TEAMS_WEBHOOK_URL</strong> - For Microsoft Teams alerts</li>
        </ul>
      </div>
    </div>
  );

  // ==================== MAIN RENDER ====================

  return (
    <div className="flex h-screen w-full bg-[#FCFCFD] text-[#111827] font-sans overflow-hidden">
      <aside className="w-64 bg-white border-r border-gray-100 flex flex-col justify-between py-10 px-6">
        <div>
          <div className="mb-16">
            <TalentDogLogo />
          </div>
          
          <div className="mb-8">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-[0.15em] mb-4 px-3">Main</h3>
            <nav className="space-y-1">
              {[
                { name: 'My Talent Pool', icon: LayoutGrid },
                { name: 'My Vacancies', icon: Briefcase },
                { name: 'System Settings', icon: Settings }
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.name}
                    onClick={() => {
                      setActiveTab(item.name);
                      setView('overview');
                    }}
                    className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all ${
                      activeTab === item.name
                        ? 'bg-black text-white'
                        : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon size={18} strokeWidth={2} />
                    <span className="text-sm font-medium">{item.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
              TD
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">TalentDog User</p>
              <p className="text-xs text-gray-400 truncate">demo@talentdog.ai</p>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-12">
          {view === 'talent-detail' ? renderTalentDetail() :
           activeTab === 'My Talent Pool' ? renderTalentPool() :
           activeTab === 'My Vacancies' ? renderVacancies() :
           renderSystemSettings()}
        </div>
      </main>
    </div>
  );
};

export default App;
