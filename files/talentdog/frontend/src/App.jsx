import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  Briefcase, 
  Zap,
  CheckCircle2, 
  Settings, 
  Database,
  Trash2,
  Users,
  MapPin,
  Building2,
  ArrowLeft,
  Target,
  Loader2
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
  const [view, setView] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [apiProfiles, setApiProfiles] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  const [vacancyUrl, setVacancyUrl] = useState('');
  const [atsSubdomain, setAtsSubdomain] = useState('');
  const [atsConnected, setAtsConnected] = useState(false);
  const [atsProvider, setAtsProvider] = useState('');

  const atsProviders = [
    { id: 'jobtoolz', name: 'Jobtoolz' },
    { id: 'greenhouse', name: 'Greenhouse' },
    { id: 'lever', name: 'Lever' },
    { id: 'workday', name: 'Workday' },
    { id: 'bamboohr', name: 'BambooHR' },
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
    } catch (error) {
      console.error('Failed to load talent pool:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadVacanciesFromAPI = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies`);
      const data = await response.json();
      setVacancies(data);
    } catch (error) {
      console.error('Failed to load vacancies:', error);
    }
  };

  const handleSyncVacancyUrl = async () => {
    if (!vacancyUrl.trim()) return alert('Voer een geldige URL in');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/vacancies/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: vacancyUrl })
      });
      if (res.ok) {
        alert('Synchronisatie voltooid!');
        loadVacanciesFromAPI();
        setVacancyUrl('');
      }
    } catch (e) { 
      alert('Sync fout: ' + e.message); 
    } finally { 
      setLoading(false); 
    }
  };

  const handleConnectATS = async (providerId, providerName) => {
    if (!atsSubdomain) return alert('Vul eerst de bedrijfsnaam/subdomein in.');
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/api/vacancies/sync-ats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          system: providerId, 
          subdomain: atsSubdomain 
        })
      });
      const data = await res.json();
      if (data.success) {
        setAtsProvider(providerName);
        setAtsConnected(true);
        alert(`Gekoppeld! ${data.total} vacatures gevonden.`);
        loadVacanciesFromAPI();
      }
    } catch (e) { 
      alert('ATS Connectie mislukt'); 
    } finally { 
      setLoading(false); 
    }
  };

  const handleDeleteVacancy = async (id) => {
    if (!window.confirm("Verwijder deze vacature uit de lijst?")) return;
    try {
      const res = await fetch(`${API_BASE_URL}/api/vacancies/${id}`, { method: 'DELETE' });
      if (res.ok) loadVacanciesFromAPI();
    } catch (e) { 
      console.error(e); 
    }
  };

  const renderManageVacancies = () => (
    <div className="max-w-4xl mx-auto">
      <button onClick={() => setView('overview')} className="flex items-center space-x-2 text-gray-400 hover:text-black mb-8 group">
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        <span className="font-bold">Terug naar Dashboard</span>
      </button>

      <div className="grid gap-8">
        <section className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
          <div className="mb-6">
            <h3 className="text-xl font-black text-gray-900">1. Koppel ATS Systemen</h3>
            <p className="text-sm text-gray-500">Voer de naam in van je klant (subdomein).</p>
          </div>

          <input 
            type="text" 
            placeholder="Bijv: 'conxion' of 'asml'" 
            className="w-full px-6 py-4 bg-gray-50 border border-gray-100 rounded-2xl mb-6 focus:outline-none"
            value={atsSubdomain}
            onChange={(e) => setAtsSubdomain(e.target.value)}
          />

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {atsProviders.map((p) => (
              <button
                key={p.id}
                onClick={() => handleConnectATS(p.id, p.name)}
                disabled={loading}
                className="p-4 border border-gray-100 rounded-2xl hover:border-black transition-all bg-white group text-center"
              >
                <Database size={20} className="mx-auto mb-2 text-gray-300 group-hover:text-black" />
                <span className="text-xs font-black uppercase">{p.name}</span>
              </button>
            ))}
          </div>
        </section>

        <section className="bg-white border border-gray-100 rounded-[2rem] p-8 shadow-sm">
          <h3 className="text-xl font-black text-gray-900 mb-6">2. Of Sync via URL</h3>
          <div className="flex gap-4">
            <input 
              type="url" 
              placeholder="https://jobs.bedrijf.be" 
              className="flex-1 px-6 py-4 bg-gray-50 border border-gray-100 rounded-2xl"
              value={vacancyUrl}
              onChange={(e) => setVacancyUrl(e.target.value)}
            />
            <button onClick={handleSyncVacancyUrl} className="bg-black text-white px-8 rounded-2xl font-black text-xs uppercase tracking-widest">
              {loading ? <Loader2 className="animate-spin" size={16} /> : 'Sync Now'}
            </button>
          </div>
        </section>
      </div>
    </div>
  );

  const renderVacanciesList = () => (
    <div className="space-y-6">
      <header className="flex justify-between items-end mb-8">
        <div>
          <h1 className="text-3xl font-black text-gray-900">Active Roles</h1>
          <p className="text-gray-400 font-medium">Beheer je vacatures en bekijk AI matches.</p>
        </div>
        <button onClick={() => setView('manage-vacancies')} className="bg-black text-white px-6 py-3 rounded-full font-bold text-xs uppercase tracking-widest">
          Manage Sources
        </button>
      </header>

      <div className="grid gap-4">
        {vacancies.map((v) => (
          <div key={v.id} className="bg-white border border-gray-100 rounded-3xl p-6 shadow-sm flex items-center justify-between group">
            <div className="flex items-center space-x-5">
              <div className="w-12 h-12 bg-gray-50 rounded-xl flex items-center justify-center text-gray-400"><Target /></div>
              <div>
                <h4 className="font-black text-gray-900">{v.title}</h4>
                <p className="text-xs text-gray-400 font-bold">{v.company} • {v.location || 'Remote'}</p>
              </div>
            </div>
            <button onClick={() => handleDeleteVacancy(v.id)} className="p-3 text-gray-200 hover:text-red-500 transition-colors">
              <Trash2 size={20} />
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#FCFCFD] flex">
      <aside className="w-72 h-screen border-r border-gray-100 p-8 flex flex-col bg-white sticky top-0">
        <TalentDogLogo />
        <nav className="mt-12 space-y-2 flex-1">
          <button onClick={() => { setActiveTab('My Talent Pool'); setView('overview'); }} className={`w-full flex items-center space-x-3 px-4 py-3.5 rounded-2xl text-sm font-bold ${activeTab === 'My Talent Pool' ? 'bg-black text-white' : 'text-gray-400'}`}><Users size={18} /> <span>Talent Pool</span></button>
          <button onClick={() => { setActiveTab('Vacancies'); setView('overview'); }} className={`w-full flex items-center space-x-3 px-4 py-3.5 rounded-2xl text-sm font-bold ${activeTab === 'Vacancies' ? 'bg-black text-white' : 'text-gray-400'}`}><Briefcase size={18} /> <span>Vacancies</span></button>
        </nav>
      </aside>
      <main className="flex-1 p-12">
        {view === 'manage-vacancies' ? renderManageVacancies() : (activeTab === 'Vacancies' ? renderVacanciesList() : <div className="text-center py-20 text-gray-300 font-black uppercase tracking-widest">Selecteer een tab om te beginnen</div>)}
      </main>
    </div>
  );
};

export default App;
