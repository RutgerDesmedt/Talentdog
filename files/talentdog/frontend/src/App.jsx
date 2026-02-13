import React, { useState, useEffect } from 'react';
import { 
  Plus, LayoutGrid, Briefcase, Zap, ClipboardList, CheckCircle2, 
  Settings, Database, Sparkles, Edit2, Trash2, User, Heart, 
  MoreHorizontal, ArrowLeft, Trophy, Bell, ChevronDown, TrendingUp, 
  Users, AlertTriangle, ExternalLink, Globe, Linkedin, MapPin, 
  Building2, Send, ChevronRight, Clock, Target, Loader2
} from 'lucide-react';

const API_BASE_URL = 'https://talentdogbackend.up.railway.app';

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
  const [loading, setLoading] = useState(false);
  const [apiProfiles, setApiProfiles] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  const [vacancyUrl, setVacancyUrl] = useState('');
  const [atsSubdomain, setAtsSubdomain] = useState('');

  const signalTypes = ['All Signals', 'Tenure Expiry', 'Layoffs', 'M&A / Funding', 'Leadership Shift', 'Failing Vacancies'];
  
  const atsProviders = [
    { id: 'jobtoolz', name: 'Jobtoolz' },
    { id: 'greenhouse', name: 'Greenhouse' },
    { id: 'lever', name: 'Lever' },
    { id: 'workday', name: 'Workday' },
    { id: 'smartrecruiters', name: 'SmartRecruiters' },
    { id: 'icims', name: 'iCIMS' }
  ];

  useEffect(() => {
    loadTalentFromAPI();
    loadVacanciesFromAPI();
  }, []);

  const loadTalentFromAPI = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/talent-pool?limit=100`);
      const data = await response.json();
      setApiProfiles(data);
    } catch (error) { console.error('Talent load error:', error); }
    finally { setLoading(false); }
  };

  const loadVacanciesFromAPI = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies`);
      const data = await response.json();
      setVacancies(data);
    } catch (error) { console.error('Vacancy load error:', error); }
  };

  const handleConnectATS = async (providerId) => {
    if (!atsSubdomain) return alert('Vul een subdomein in (bijv. conxion)');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/vacancies/sync-ats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ system: providerId, subdomain: atsSubdomain })
      });
      const data = await res.json();
      if (data.success) {
        alert(`Gekoppeld! ${data.total} vacatures gevonden.`);
        loadVacanciesFromAPI();
        setView('overview');
      }
    } catch (e) { alert('ATS Connectie mislukt'); }
    finally { setLoading(false); }
  };

  const handleDeleteVacancy = async (id) => {
    if (!window.confirm("Verwijder vacature?")) return;
    await fetch(`${API_BASE_URL}/api/vacancies/${id}`, { method: 'DELETE' });
    loadVacanciesFromAPI();
  };

  // --- VIEWS ---

  const renderTalentDetail = () => (
    <div className="animate-in fade-in slide-in-from-right-4 duration-500">
      <button onClick={() => setView('overview')} className="flex items-center space-x-2 text-gray-900 font-bold mb-8 hover:opacity-70">
        <ArrowLeft size={20} /> <span className="text-lg">Back</span>
      </button>
      <div className="flex items-start justify-between mb-10">
        <div className="flex items-center space-x-6">
          <div className="w-24 h-24 rounded-2xl overflow-hidden border-2 border-white shadow-xl">
            <img src={selectedTalent.photo || 'https://via.placeholder.com/150'} className="w-full h-full object-cover" alt="" />
          </div>
          <div>
            <h1 className="text-4xl font-black text-gray-900">{selectedTalent.name}</h1>
            <p className="text-gray-500 font-semibold">{selectedTalent.role} @ {selectedTalent.currentCompany || selectedTalent.company}</p>
          </div>
        </div>
        <div className="text-right">
          <div className="text-5xl font-black text-gray-900">{selectedTalent.points || 88}</div>
          <div className="text-xs font-black text-gray-400 uppercase tracking-widest">Score</div>
        </div>
      </div>
      <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm">
        <h3 className="flex items-center space-x-2 text-xs font-black uppercase tracking-widest text-gray-400 mb-4">
          <ClipboardList size={16} /> <span>Talent Story</span>
        </h3>
        <p className="text-lg text-gray-600 leading-relaxed font-medium">
          {selectedTalent.story || "Deze kandidaat vertoont sterke signalen voor een overstap op basis van recente bedrijfsveranderingen en loopbaanhistorie."}
        </p>
      </div>
    </div>
  );

  const renderManageSources = () => (
    <div className="max-w-4xl">
      <button onClick={() => setView('overview')} className="flex items-center space-x-2 text-gray-400 hover:text-black mb-8">
        <ArrowLeft size={18} /> <span className="font-bold">Dashboard</span>
      </button>
      <div className="bg-white border border-gray-100 rounded-[2.5rem] p-10 shadow-sm">
        <h2 className="text-2xl font-black mb-2">Connect Recruitment Source</h2>
        <p className="text-gray-400 mb-8 font-medium">Koppel je ATS om automatisch vacatures te synchroniseren.</p>
        
        <input 
          type="text" placeholder="Subdomein (bijv: conxion)" 
          className="w-full px-6 py-4 bg-gray-50 border border-gray-100 rounded-2xl mb-8 focus:outline-none"
          value={atsSubdomain} onChange={(e) => setAtsSubdomain(e.target.value)}
        />

        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {atsProviders.map((p) => (
            <button key={p.id} onClick={() => handleConnectATS(p.id)} disabled={loading}
              className="p-6 border border-gray-100 rounded-2xl hover:border
