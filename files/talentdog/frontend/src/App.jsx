import React, { useState, useEffect } from 'react';
import { 
  Plus, LayoutGrid, Briefcase, Zap, ClipboardList, CheckCircle2, Settings, Database,
  Sparkles, Edit2, Trash2, User, Heart, MoreHorizontal, ArrowLeft, Trophy, Bell,
  ChevronDown, TrendingUp, Users, AlertTriangle, ExternalLink, Globe, Linkedin,
  MapPin, Building2, Send, ChevronRight, Clock, Target, Filter, Search, Upload,
  ScanEye // Nieuw icoon voor de scanner
} from 'lucide-react';

// Importeer je nieuwe component
import SignalIntelligence from './components/SignalIntelligence';

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
        body: JSON.stringify({ title: 'New Position', url: url })
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
    const sectors = ['Technology', 'FinTech', 'E-commerce', 'Healthcare Tech'];
    const signalTypes = ['TENURE EXPIRY', 'CORPORATE SHOCKWAVE', 'LAYOFFS', 'M&A / FUNDING'];
    
    const profiles = [];
    for (let i = 0; i < 100; i++) {
      const name = `${firstNames[i % firstNames.length]} ${lastNames[i % lastNames.length]}`;
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
        signalType: signalTypes[i % signalTypes.length],
        signalDescription: `${name} heeft belangrijke ontwikkelingen.`,
        story: `${name} is klaar voor een nieuwe uitdaging.`,
        background: `Ervaren ${roles[i % roles.length]}.`,
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
  const displayedProfiles = filteredProfiles.slice((currentPage - 1) * profilesPerPage, currentPage * profilesPerPage);

  const handleTalentClick = (talent) => {
    setSelectedTalent(talent);
    setView('talent-detail');
  };

  // ==================== RENDER SECTIONS ====================

  const renderTalentDetail = () => {
    if (!selectedTalent) return null;
    return (
      <div className="animate-in fade-in slide-in-from-right-4 duration-500 pb-20">
        <button onClick={() => setView('overview')} className="flex items-center space-x-2 text-gray-900 font-bold mb-8 hover:opacity-70 transition-opacity">
          <ArrowLeft size={20} /> <span className="text-lg">Back</span>
        </button>
        {/* ... Rest van je bestaande detail view code ... */}
        <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm">
           <h1 className="text-4xl font-black text-gray-900">{selectedTalent.name}</h1>
           <p className="text-gray-500 mt-2">{selectedTalent.role} @ {selectedTalent.currentCompany}</p>
        </div>
      </div>
    );
  };

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
            onClick={() => { setActiveSignalTab(type); setCurrentPage(1); }}
            className={`px-6 py-2.5 rounded-full text-xs font-bold uppercase tracking-wider transition-all ${
              activeSignalTab === type ? 'bg-black text-white' : 'bg-white text-gray-400 border border-gray-200'
            }`}
          >
            {type}
          </button>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-8 mb-12">
        {displayedProfiles.map((candidate, idx) => (
          <div key={candidate.id} onClick={() => handleTalentClick(candidate)} className="group relative bg-white border border-gray-100 rounded-3xl p-8 transition-all hover:shadow-lg cursor-pointer">
            <div className="flex items-center space-x-4">
               <img src={candidate.photo} className="w-16 h-16 rounded-2xl grayscale group-hover:grayscale-0 transition-all" alt="" />
               <div>
                  <h3 className="text-xl font-bold">{candidate.name}</h3>
                  <p className="text-sm text-gray-400 uppercase tracking-widest">{candidate.role}</p>
               </div>
            </div>
            <div className="mt-6 p-4 bg-gray-50 rounded-xl">
               <span className="text-[10px] font-black text-blue-600 uppercase">{candidate.signalType}</span>
               <p className="text-sm text-gray-700 mt-1">{candidate.currentCompany}</p>
            </div>
          </div>
        ))}
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
              ].map((item) => {
                const Icon = item.icon;
                return (
                  <button
                    key={item.name}
                    onClick={() => { setActiveTab(item.name); setView('overview'); }}
                    className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all ${
                      activeTab === item.name ? 'bg-black text-white' : 'text-gray-600 hover:bg-gray-50'
                    }`}
                  >
                    <Icon size={18} />
                    <span className="text-sm font-medium">{item.name}</span>
                  </button>
                );
              })}
            </nav>
          </div>

          {/* NIEUWE SECTIE: Intelligence Scanner */}
          <div className="mb-8">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-[0.15em] mb-4 px-3">Intelligence</h3>
            <nav className="space-y-1">
              <button
                onClick={() => { setActiveTab('Scanner'); setView('overview'); }}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all ${
                  activeTab === 'Scanner' ? 'bg-blue-600 text-white shadow-lg shadow-blue-200' : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                <ScanEye size={18} />
                <span className="text-sm font-medium">Company Scanner</span>
              </button>
            </nav>
          </div>

          <div className="mb-8">
            <h3 className="text-xs font-medium text-gray-400 uppercase tracking-[0.15em] mb-4 px-3">System</h3>
            <button
              onClick={() => { setActiveTab('System Settings'); setView('overview'); }}
              className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg transition-all ${
                activeTab === 'System Settings' ? 'bg-black text-white' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              <Settings size={18} />
              <span className="text-sm font-medium">Settings</span>
            </button>
          </div>
        </div>

        <div className="pt-6 border-t border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-black flex items-center justify-center text-white font-bold text-sm">TD</div>
            <div className="flex-1 min-w-0 text-xs font-bold">demo@talentdog.ai</div>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-7xl mx-auto p-12">
          {/* LOGICA OM HET JUISTE SCHERM TE TONEN */}
          {view === 'talent-detail' ? renderTalentDetail() :
           activeTab === 'Scanner' ? <SignalIntelligence /> : 
           activeTab === 'My Talent Pool' ? renderTalentPool() :
           activeTab === 'My Vacancies' ? (vacancies.length > 0 ? "Vacancies Screen" : "Geen vacatures") :
           "System Settings"}
        </div>
      </main>
    </div>
  );
};

export default App;
