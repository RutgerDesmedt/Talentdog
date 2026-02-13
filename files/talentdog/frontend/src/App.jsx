import React, { useState, useEffect } from 'react';
import { 
  Plus, LayoutGrid, Briefcase, Zap, ClipboardList, CheckCircle2, Settings, Database,
  Sparkles, Edit2, Trash2, User, Heart, MoreHorizontal, ArrowLeft, Trophy, Bell,
  ChevronDown, TrendingUp, Users, AlertTriangle, ExternalLink, Globe, Linkedin,
  MapPin, Building2, Send, ChevronRight, Clock, Target, Filter, Search, Upload,
  Eye 
} from 'lucide-react';

// Importeer je nieuwe component
import SignalIntelligence from './components/SignalIntelligence';

// ==================== API CONFIGURATION ====================
const API_BASE_URL = 'https://talentdogbackend.up.railway.app';
// ===========================================================

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
  const [profiles, setProfiles] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  
  const profilesPerPage = 12;
  const cities = ['Amsterdam', 'Rotterdam', 'Utrecht', 'Eindhoven', 'Den Haag'];
  const signalTypes = ['All Signals', 'Tenure Expiry', 'Layoffs', 'M&A / Funding', 'Leadership Shift', 'Corporate Shockwave'];

  useEffect(() => {
    loadTalentPool();
    loadVacancies();
  }, []);

  const loadTalentPool = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/talent-pool?limit=100`);
      if (!response.ok) throw new Error('Network error');
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

  const generateMockProfiles = () => {
    const firstNames = ['Emma', 'Liam', 'Sophie', 'Noah', 'Lisa'];
    const lastNames = ['de Vries', 'Jansen', 'Bakker'];
    const roles = ['Senior DevOps Engineer', 'Product Lead'];
    const companies = ['ASML', 'Adyen', 'Picnic'];
    const sTypes = ['TENURE EXPIRY', 'LAYOFFS', 'M&A / FUNDING'];
    
    return Array.from({ length: 20 }, (_, i) => ({
      id: i + 1,
      name: `${firstNames[i % firstNames.length]} ${lastNames[i % lastNames.length]}`,
      role: roles[i % roles.length],
      currentCompany: companies[i % companies.length],
      location: `${cities[i % cities.length]}, NL`,
      photo: `https://images.pexels.com/photos/${220453 + (i % 5)}/pexels-photo.jpeg?auto=compress&cs=tinysrgb&w=150&h=150&fit=crop`,
      signalType: sTypes[i % sTypes.length],
      signalDescription: "Klaar voor een nieuwe uitdaging."
    }));
  };

  const filteredProfiles = profiles.filter(p => 
    (p.name.toLowerCase().includes(searchTerm.toLowerCase())) &&
    (activeSignalTab === 'All Signals' || p.signalType.toLowerCase().includes(activeSignalTab.toLowerCase()))
  );

  const displayedProfiles = filteredProfiles.slice((currentPage - 1) * profilesPerPage, currentPage * profilesPerPage);

  const renderTalentDetail = () => (
    <div className="p-10 bg-white rounded-[2rem] border border-gray-100 shadow-sm">
      <button onClick={() => setView('overview')} className="flex items-center space-x-2 font-bold mb-8">
        <ArrowLeft size={20} /> <span>Back</span>
      </button>
      <h1 className="text-4xl font-black">{selectedTalent?.name}</h1>
      <p className="text-gray-500">{selectedTalent?.role} @ {selectedTalent?.currentCompany}</p>
    </div>
  );

  const renderTalentPool = () => (
    <div className="animate-in fade-in duration-500">
      <header className="mb-10">
        <h1 className="text-4xl font-bold">My Talent Pool</h1>
        <p className="text-sm text-gray-400 mt-2">Real-time signals across {profiles.length} profiles</p>
      </header>
      <div className="flex gap-3 mb-12 flex-wrap">
        {signalTypes.map(type => (
          <button key={type} onClick={() => setActiveSignalTab(type)} className={`px-6 py-2 rounded-full text-xs font-bold uppercase ${activeSignalTab === type ? 'bg-black text-white' : 'bg-white text-gray-400 border border-gray-200'}`}>
            {type}
          </button>
        ))}
      </div>
      <div className="grid grid-cols-2 gap-8">
        {displayedProfiles.map(candidate => (
          <div key={candidate.id} onClick={() => { setSelectedTalent(candidate); setView('talent-detail'); }} className="bg-white border border-gray-100 rounded-3xl p-8 hover:shadow-lg cursor-pointer transition-all">
            <div className="flex items-center space-x-4">
              <img src={candidate.photo} className="w-16 h-16 rounded-2xl grayscale hover:grayscale-0" alt="" />
              <div>
                <h3 className="text-xl font-bold">{candidate.name}</h3>
                <p className="text-sm text-gray-400 uppercase">{candidate.role}</p>
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

  return (
    <div className="flex h-screen w-full bg-[#FCFCFD] text-[#111827] overflow-hidden">
      <aside className="w-64 bg-white border-r p-10 flex flex-col">
        <div className="mb-16"><TalentDogLogo /></div>
        <nav className="space-y-8">
          <div>
            <h3 className="text-xs font-medium text-gray-400 uppercase mb-4 px-3">Main</h3>
            <div className="space-y-1">
              <button onClick={() => {setActiveTab('My Talent Pool'); setView('overview');}} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg ${activeTab === 'My Talent Pool' ? 'bg-black text-white' : 'text-gray-600'}`}><LayoutGrid size={18} /><span className="text-sm font-medium">Talent Pool</span></button>
              <button onClick={() => {setActiveTab('Scanner'); setView('overview');}} className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg ${activeTab === 'Scanner' ? 'bg-blue-600 text-white' : 'text-gray-600'}`}><Eye size={18} /><span className="text-sm font-medium">Company Scanner</span></button>
            </div>
          </div>
        </nav>
      </aside>
      <main className="flex-1 overflow-y-auto p-12">
        {view === 'talent-detail' ? renderTalentDetail() : activeTab === 'Scanner' ? <SignalIntelligence /> : renderTalentPool()}
      </main>
    </div>
  );
};

export default App;
