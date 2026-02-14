import React, { useState, useEffect } from 'react';
import { 
  Plus, 
  LayoutGrid, 
  Briefcase, 
  Zap,
  ClipboardList, 
  CheckCircle2, 
  Settings, 
  Database,
  Sparkles,
  Edit2,
  Trash2,
  User,
  Heart,
  MoreHorizontal,
  ArrowLeft,
  Trophy,
  Bell,
  ChevronDown,
  TrendingUp,
  Users,
  AlertTriangle,
  ExternalLink,
  Globe,
  Linkedin,
  MapPin,
  Building2,
  Send,
  ChevronRight,
  Clock,
  Target,
  X,
  Key,
  Link as LinkIcon
} from 'lucide-react';

// ⚠️ VERANDER DIT NAAR JOUW BACKEND URL!
const API_BASE_URL = 'https://talentdogbackend.up.railway.app';

const TalentDogLogo = () => (
  <div className="flex items-center space-x-3 select-none">
    <div className="w-10 h-10 bg-black rounded-xl flex items-center justify-center shadow-lg shadow-black/10">
      <Zap size={22} className="text-white fill-white" />
    </div>
    <span className="text-2xl font-bold tracking-tight text-[#111827]">TalentDog</span>
  </div>
);

// ATS Connection Modal Component
const ATSConnectionModal = ({ provider, onClose, onConnect }) => {
  const [subdomain, setSubdomain] = useState('');
  const [apiKey, setApiKey] = useState('');
  const [feedUrl, setFeedUrl] = useState('');
  const [loading, setLoading] = useState(false);

  const providerInfo = {
    greenhouse: {
      needsSubdomain: true,
      needsApiKey: false,
      subdomainLabel: 'Board Token',
      subdomainPlaceholder: 'yourcompany',
      helpText: 'Find your board token in Greenhouse under Job Board > Settings'
    },
    lever: {
      needsSubdomain: true,
      needsApiKey: false,
      subdomainLabel: 'Site Name',
      subdomainPlaceholder: 'yourcompany',
      helpText: 'Your Lever site name (e.g., yourcompany from yourcompany.lever.co)'
    },
    jobtoolz: {
      needsSubdomain: true,
      needsApiKey: true,
      subdomainLabel: 'Company ID',
      subdomainPlaceholder: 'your-company-id',
      helpText: 'Find your Company ID and API Key in Jobtoolz Settings'
    },
    recruitee: {
      needsSubdomain: true,
      needsApiKey: true,
      subdomainLabel: 'Company ID',
      subdomainPlaceholder: 'your-company-id',
      helpText: 'Get your API key from Recruitee Settings > API Access'
    },
    workday: {
      needsSubdomain: false,
      needsApiKey: false,
      needsFeedUrl: true,
      helpText: 'Enter your Workday RSS feed URL for job postings'
    },
    icims: {
      needsSubdomain: false,
      needsApiKey: false,
      needsFeedUrl: true,
      helpText: 'Enter your iCIMS RSS feed URL'
    },
    smartrecruiters: {
      needsSubdomain: true,
      needsApiKey: false,
      subdomainLabel: 'Company Identifier',
      subdomainPlaceholder: 'yourcompany',
      helpText: 'Your SmartRecruiters company identifier'
    },
    bamboohr: {
      needsSubdomain: true,
      needsApiKey: true,
      subdomainLabel: 'Subdomain',
      subdomainPlaceholder: 'yourcompany',
      helpText: 'Your BambooHR subdomain and API key'
    }
  };

  const info = providerInfo[provider.toLowerCase()] || providerInfo.greenhouse;

  const handleConnect = async () => {
    setLoading(true);
    try {
      await onConnect(provider, {
        subdomain: subdomain || undefined,
        apiKey: apiKey || undefined,
        feedUrl: feedUrl || undefined
      });
      onClose();
    } catch (error) {
      window.alert('Connection failed: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Connect {provider}</h2>
            <p className="text-sm text-gray-500 mt-1">Enter your {provider} credentials</p>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X size={20} className="text-gray-400" />
          </button>
        </div>

        <div className="space-y-4 mb-6">
          {info.needsSubdomain && (
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                {info.subdomainLabel}
              </label>
              <input
                type="text"
                value={subdomain}
                onChange={(e) => setSubdomain(e.target.value)}
                placeholder={info.subdomainPlaceholder}
                className="w-full px-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black/10"
              />
            </div>
          )}

          {info.needsApiKey && (
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                API Key
              </label>
              <div className="relative">
                <Key size={18} className="absolute left-3 top-3 text-gray-400" />
                <input
                  type="password"
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  placeholder="Enter your API key"
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black/10"
                />
              </div>
            </div>
          )}

          {info.needsFeedUrl && (
            <div>
              <label className="block text-sm font-bold text-gray-700 mb-2">
                RSS Feed URL
              </label>
              <div className="relative">
                <LinkIcon size={18} className="absolute left-3 top-3 text-gray-400" />
                <input
                  type="url"
                  value={feedUrl}
                  onChange={(e) => setFeedUrl(e.target.value)}
                  placeholder="https://..."
                  className="w-full pl-10 pr-4 py-2.5 bg-gray-50 border border-gray-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black/10"
                />
              </div>
            </div>
          )}
        </div>

        <div className="bg-blue-50 border border-blue-100 rounded-xl p-4 mb-6">
          <div className="flex items-start space-x-2">
            <AlertTriangle size={16} className="text-blue-600 flex-shrink-0 mt-0.5" />
            <p className="text-xs text-blue-700">{info.helpText}</p>
          </div>
        </div>

        <div className="flex space-x-3">
          <button
            onClick={onClose}
            className="flex-1 py-2.5 border border-gray-200 rounded-xl text-sm font-bold text-gray-700 hover:bg-gray-50 transition-all"
          >
            Cancel
          </button>
          <button
            onClick={handleConnect}
            disabled={loading || (!subdomain && info.needsSubdomain) || (!feedUrl && info.needsFeedUrl)}
            className="flex-1 py-2.5 bg-black text-white rounded-xl text-sm font-bold hover:bg-gray-800 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Connecting...' : 'Connect'}
          </button>
        </div>
      </div>
    </div>
  );
};

const App = () => {
  const [activeTab, setActiveTab] = useState('My Vacancies');
  const [view, setView] = useState('overview');
  const [selectedTalent, setSelectedTalent] = useState(null);
  const [selectedVacancy, setSelectedVacancy] = useState(null);
  const [loading, setLoading] = useState(false);
  const [apiProfiles, setApiProfiles] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  const [vacancyMatches, setVacancyMatches] = useState({});
  const [atsConnections, setAtsConnections] = useState([]);
  const [showATSModal, setShowATSModal] = useState(false);
  const [selectedATSProvider, setSelectedATSProvider] = useState(null);

  useEffect(() => {
    loadTalentFromAPI();
    loadVacanciesFromAPI();
    loadATSStatus();
  }, []);

  const loadTalentFromAPI = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/talent-pool?limit=100`);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setApiProfiles(data);
    } catch (error) {
      console.error('Failed to load talent pool:', error);
      setApiProfiles([]);
    } finally {
      setLoading(false);
    }
  };

  const loadVacanciesFromAPI = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies`);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setVacancies(data);
      
      // Load matches for each vacancy
      data.forEach(vacancy => {
        loadVacancyMatches(vacancy.id);
      });
    } catch (error) {
      console.error('Failed to load vacancies:', error);
      setVacancies([]);
    }
  };

  const loadVacancyMatches = async (vacancyId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies/${vacancyId}/matches`);
      if (!response.ok) throw new Error('Failed to load matches');
      const data = await response.json();
      
      setVacancyMatches(prev => ({
        ...prev,
        [vacancyId]: data
      }));
    } catch (error) {
      console.error(`Failed to load matches for vacancy ${vacancyId}:`, error);
    }
  };

  const loadATSStatus = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/ats/status`);
      if (!response.ok) throw new Error('Network response was not ok');
      const data = await response.json();
      setAtsConnections(data);
    } catch (error) {
      console.error('Failed to load ATS status:', error);
      setAtsConnections([]);
    }
  };

  const handleConnectATS = async (provider, config) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/ats/connect`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          provider: provider,
          ...config
        })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to connect');
      }

      window.alert(`Successfully connected to ${provider}!`);
      
      await handleSyncATS(provider, config);
      await loadATSStatus();
      await loadVacanciesFromAPI();
      
    } catch (error) {
      console.error('ATS connection error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const handleSyncATS = async (provider, config) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies/sync-ats`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system: provider,
          ...config
        })
      });

      if (!response.ok) throw new Error('Sync failed');
      const result = await response.json();
      console.log('Sync result:', result);
    } catch (error) {
      console.error('Sync error:', error);
    }
  };

  const handleDisconnectATS = async (provider) => {
    if (!window.confirm(`Verbreek verbinding met ${provider}?`)) return;

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/ats/disconnect/${provider}`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Failed to disconnect');

      window.alert(`Verbinding met ${provider} verbroken`);
      await loadATSStatus();
      
    } catch (error) {
      window.alert('Fout: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSyncAllATS = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies/sync-all`, {
        method: 'POST'
      });

      if (!response.ok) throw new Error('Sync failed');

      const result = await response.json();
      window.alert(`Gesynchroniseerd!\nNieuw: ${result.total_new}, Geüpdatet: ${result.total_updated}`);
      await loadVacanciesFromAPI();
      
    } catch (error) {
      window.alert('Sync mislukt: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTalentClick = (talent) => {
    setSelectedTalent(talent);
    setView('talent-detail');
  };

  const handleVacancyClick = (vacancy) => {
    setSelectedVacancy(vacancy);
    setView('vacancy-detail');
  };

  const isATSConnected = (provider) => {
    return atsConnections.some(conn => 
      conn.provider.toLowerCase() === provider.toLowerCase() && conn.is_active
    );
  };

  const getConnectedATS = () => {
    return atsConnections.filter(conn => conn.is_active);
  };

  // RENDER FUNCTIONS (abbreviated for space - include full implementations)
  
  const renderVacancyDetail = () => {
    if (!selectedVacancy) return null;
    
    const matches = vacancyMatches[selectedVacancy.id] || [];
    
    return (
      <div className="animate-in fade-in slide-in-from-right-4 duration-500">
        <button 
          onClick={() => setView('overview')}
          className="flex items-center space-x-2 text-gray-400 hover:text-black transition-colors mb-8 group"
        >
          <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <span className="text-sm font-bold">Terug naar Vacatures</span>
        </button>

        <div className="bg-white border border-gray-100 rounded-[2.5rem] shadow-sm overflow-hidden">
          <div className="p-8 border-b border-gray-50 bg-[#F9FAFB]/30">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
              <div className="flex items-start space-x-5">
                <div className="w-14 h-14 bg-white border border-gray-100 rounded-2xl flex items-center justify-center shadow-sm text-gray-400">
                  <Target size={28} />
                </div>
                <div>
                  <h2 className="text-2xl font-black text-gray-900 tracking-tight">{selectedVacancy.title}</h2>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400 font-bold">
                    <span className="flex items-center space-x-1.5"><Building2 size={14} /> <span>{selectedVacancy.department}</span></span>
                    <span className="flex items-center space-x-1.5"><MapPin size={14} /> <span>{selectedVacancy.location}</span></span>
                    {selectedVacancy.source && (
                      <span className="flex items-center space-x-1.5 text-emerald-600"><Database size={14} /> <span>via {selectedVacancy.source}</span></span>
                    )}
                  </div>
                </div>
              </div>
              <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ${
                matches.length > 5 ? 'bg-green-50 text-green-600' : 
                matches.length > 0 ? 'bg-amber-50 text-amber-600' : 
                'bg-gray-50 text-gray-400'
              }`}>
                {matches.length} Matches
              </span>
            </div>
          </div>

          <div className="p-8">
            <div className="flex items-center justify-between mb-8 px-2">
              <h3 className="text-[10px] font-black text-gray-400 tracking-[0.2em] uppercase">Matchend Talent</h3>
              <span className="text-xs font-bold text-gray-400">{matches.length} Kandidaten</span>
            </div>
            
            {matches.length === 0 ? (
              <div className="text-center py-12 border-2 border-dashed border-gray-100 rounded-2xl">
                <Users size={48} className="mx-auto text-gray-200 mb-4" />
                <p className="text-sm font-bold text-gray-400">Nog geen matches</p>
                <p className="text-xs text-gray-300 mt-1">De AI scant de talent pool</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {matches.map((match) => (
                  <div 
                    key={match.id}
                    onClick={() => handleTalentClick(match)}
                    className="group flex items-center p-5 border border-gray-100 rounded-[2rem] hover:border-gray-900 hover:shadow-xl transition-all cursor-pointer bg-white"
                  >
                    <div className="w-16 h-16 rounded-2xl overflow-hidden border border-gray-50 flex-shrink-0 transition-transform duration-500 group-hover:scale-105">
                      <img src={match.photo} className="w-full h-full object-cover" alt={match.name} />
                    </div>
                    <div className="ml-5 flex-1">
                      <h4 className="text-lg font-black text-gray-900">{match.name}</h4>
                      <p className="text-sm text-gray-500 font-medium">{match.role}</p>
                      <div className="flex items-center space-x-2 mt-1">
                        {match.signalType && (
                          <span className="text-[10px] font-black text-orange-600 bg-orange-50 px-2 py-0.5 rounded-md uppercase">
                            {match.signalType}
                          </span>
                        )}
                        <span className="text-xs font-bold text-gray-400">Score: {match.matchScore || match.points}</span>
                      </div>
                    </div>
                    <ChevronRight size={24} className="text-gray-200 group-hover:text-black transition-colors" />
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    );
  };

  const renderVacancies = () => {
    return (
      <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
        <header className="flex items-center justify-between mb-12">
          <div>
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">My Vacancies</h1>
            <p className="text-sm text-gray-400 font-medium mt-1">Monitor talent matches</p>
          </div>
          <button 
            onClick={() => { setActiveTab('System Settings'); setView('manage-vacancies'); }}
            className="group flex items-center space-x-2 bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition-all"
          >
            <Settings size={16} strokeWidth={2.5} />
            <span className="text-[11px] font-bold uppercase">Manage ATS</span>
          </button>
        </header>

        {vacancies.length === 0 ? (
          <div className="text-center py-20 bg-white border border-gray-100 rounded-2xl">
            <Briefcase size={48} className="mx-auto text-gray-200 mb-4" />
            <p className="text-lg font-bold text-gray-400 mb-2">Geen vacatures</p>
            <p className="text-sm text-gray-300 mb-6">Verbind je ATS om te starten</p>
            <button
              onClick={() => { setActiveTab('System Settings'); setView('manage-vacancies'); }}
              className="bg-black text-white px-6 py-3 rounded-xl text-sm font-bold hover:bg-gray-800"
            >
              Connect ATS
            </button>
          </div>
        ) : (
          <div className="space-y-6">
            {vacancies.map((vacancy) => {
              const matches = vacancyMatches[vacancy.id] || [];
              
              return (
                <div 
                  key={vacancy.id} 
                  onClick={() => handleVacancyClick(vacancy)}
                  className="bg-white border border-gray-100 rounded-2xl p-6 hover:border-gray-300 hover:shadow-lg transition-all cursor-pointer group"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center space-x-3 mb-2">
                        <h3 className="text-xl font-black text-gray-900">{vacancy.title}</h3>
                        {vacancy.source && (
                          <span className="text-xs font-bold text-emerald-600 bg-emerald-50 px-2 py-1 rounded-full">
                            {vacancy.source}
                          </span>
                        )}
                      </div>
                      <div className="flex items-center space-x-4 text-sm text-gray-400 font-bold">
                        <span className="flex items-center space-x-1.5"><Building2 size={14} /> {vacancy.company}</span>
                        <span className="flex items-center space-x-1.5"><MapPin size={14} /> {vacancy.location}</span>
                        <span className="flex items-center space-x-1.5"><Target size={14} /> {vacancy.department}</span>
                      </div>
                    </div>
                    <div className="flex items-center space-x-4">
                      <div className="text-right">
                        <div className="text-2xl font-black text-gray-900">{matches.length}</div>
                        <div className="text-[10px] font-bold text-gray-400 uppercase">Matches</div>
                      </div>
                      <ChevronRight size={24} className="text-gray-300 group-hover:text-black transition-colors" />
                    </div>
                  </div>

                  {matches.length > 0 && (
                    <div className="flex items-center space-x-3 mt-4 pt-4 border-t border-gray-50">
                      <div className="flex -space-x-2">
                        {matches.slice(0, 4).map((match, idx) => (
                          <img key={idx} src={match.photo} alt={match.name} className="w-8 h-8 rounded-full border-2 border-white" />
                        ))}
                      </div>
                      <span className="text-xs text-gray-500 font-medium">
                        {matches.slice(0, 3).map(m => m.name.split(' ')[0]).join(', ')}
                        {matches.length > 3 && ` +${matches.length - 3} meer`}
                      </span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>
    );
  };

  // Continue with other render functions...
  const renderManageVacancies = () => {
    const atsProviders = [
      { name: 'Greenhouse' }, { name: 'Lever' }, { name: 'Workday' }, { name: 'BambooHR' },
      { name: 'SmartRecruiters' }, { name: 'iCIMS' }, { name: 'Jobtoolz' }, { name: 'Recruitee' }
    ];

    return (
      <div className="animate-in fade-in slide-in-from-right-4 duration-500">
        <button onClick={() => setView('overview')} className="flex items-center space-x-2 text-gray-400 hover:text-black mb-6 group">
          <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <div className="text-left">
            <h2 className="text-sm font-bold text-black">Vacancies</h2>
            <p className="text-[11px] font-medium text-gray-400">Connect your ATS</p>
          </div>
        </button>

        <div className="space-y-6">
          <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-black text-gray-900">Connect ATS System</h3>
                <p className="text-xs text-gray-500 mt-1">Synchroniseer vacatures automatisch</p>
              </div>
              {getConnectedATS().length > 0 && (
                <button onClick={handleSyncAllATS} disabled={loading} className="flex items-center space-x-2 bg-emerald-500 text-white px-4 py-2 rounded-xl text-xs font-bold hover:bg-emerald-600">
                  <Sparkles size={14} /> <span>Sync All</span>
                </button>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {atsProviders.map((provider) => {
                const connected = isATSConnected(provider.name);
                return (
                  <button
                    key={provider.name}
                    onClick={() => {
                      if (connected) {
                        handleDisconnectATS(provider.name);
                      } else {
                        setSelectedATSProvider(provider.name);
                        setShowATSModal(true);
                      }
                    }}
                    disabled={loading}
                    className={`group relative p-5 border rounded-xl transition-all ${
                      connected ? 'border-emerald-500 bg-emerald-50/50' : 'border-gray-200 hover:border-gray-900 hover:shadow-md bg-white'
                    } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${connected ? 'bg-emerald-100' : 'bg-gray-100'}`}>
                        <Database size={16} className={connected ? 'text-emerald-600' : 'text-gray-400'} />
                      </div>
                      {connected && <CheckCircle2 size={18} className="text-emerald-600" />}
                    </div>
                    <div className="text-sm font-bold text-gray-900 text-left">{provider.name}</div>
                    <div className="text-xs text-gray-400 text-left mt-0.5">{connected ? 'Verbonden' : 'Klik om te verbinden'}</div>
                  </button>
                );
              })}
            </div>

            {getConnectedATS().length > 0 && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-xl">
                <div className="flex items-start space-x-3">
                  <Bell size={18} className="text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-bold text-blue-900 mb-1">{getConnectedATS().length} ATS Verbonden</p>
                    <p className="text-xs text-blue-700">{getConnectedATS().map(c => c.provider).join(', ')}</p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {vacancies.length > 0 && (
            <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-black text-gray-900">Huidige Vacatures</h3>
                <span className="text-xs font-bold text-gray-400">{vacancies.length} Actief</span>
              </div>
              <div className="space-y-2">
                {vacancies.slice(0, 10).map((vacancy, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100">
                    <div className="flex items-center space-x-3 flex-1">
                      <Target size={16} className="text-gray-400" />
                      <div className="flex-1">
                        <span className="text-sm font-bold text-gray-900">{vacancy.title}</span>
                        {vacancy.source && <span className="ml-2 text-xs text-emerald-600 font-semibold">via {vacancy.source}</span>}
                      </div>
                    </div>
                    <div className="flex items-center space-x-3">
                      <span className="text-xs text-gray-400">{vacancy.location}</span>
                      <span className="text-xs font-bold text-gray-600">{vacancyMatches[vacancy.id]?.length || 0} matches</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderSystemSettings = () => (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
      {view === 'overview' ? (
        <>
          <header className="mb-12">
            <h1 className="text-3xl font-extrabold text-gray-900 mb-2">System Setup</h1>
            <p className="text-[15px] text-gray-500 font-medium">Manage settings</p>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
              <div className="flex justify-between items-start mb-8">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Briefcase size={24} /></div>
                  <div>
                    <h3 className="text-[15px] font-bold text-gray-900">Vacancies</h3>
                    <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">
                      {getConnectedATS().length > 0 ? `${getConnectedATS().length} ATS` : 'NIET VERBONDEN'}
                    </p>
                  </div>
                </div>
                <div className={`w-2.5 h-2.5 rounded-full ${getConnectedATS().length > 0 ? 'bg-emerald-400' : 'bg-amber-400'}`}></div>
              </div>
              <div className="mb-10">
                <span className="text-5xl font-black text-gray-900">{vacancies.length}</span>
                <p className="text-sm font-medium text-gray-400 mt-2">Actieve Vacatures</p>
              </div>
              <button onClick={() => setView('manage-vacancies')} className="w-full py-3.5 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 hover:bg-gray-50">
                Beheer Vacatures
              </button>
            </div>
          </div>
        </>
      ) : view === 'manage-vacancies' ? renderManageVacancies() : null}
    </div>
  );

  return (
    <div className="flex h-screen w-full bg-[#FCFCFD] text-[#111827] font-sans overflow-hidden">
      {showATSModal && (
        <ATSConnectionModal
          provider={selectedATSProvider}
          onClose={() => { setShowATSModal(false); setSelectedATSProvider(null); }}
          onConnect={handleConnectATS}
        />
      )}

      <aside className="w-72 bg-white border-r border-gray-100 flex flex-col shrink-0">
        <div className="p-8 flex-1">
          <div className="mb-12 px-2"><TalentDogLogo /></div>
          <nav className="space-y-10">
            <div>
              <p className="text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-6 px-4">My Account</p>
              <div className="space-y-2">
                <button 
                  onClick={() => { setActiveTab('My Vacancies'); setView('overview'); }} 
                  className={`w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-[15px] font-bold transition-all ${
                    activeTab === 'My Vacancies' ? 'bg-[#F8FAFC] text-black shadow-sm border border-gray-100' : 'text-gray-500 hover:bg-gray-50'
                  }`}
                >
                  <Briefcase size={22} strokeWidth={activeTab === 'My Vacancies' ? 2.5 : 2} />
                  <span>My Vacancies</span>
                  {vacancies.length > 0 && (
                    <span className="ml-auto bg-emerald-500 text-white text-xs font-bold px-2 py-0.5 rounded-full">{vacancies.length}</span>
                  )}
                </button>
                <button onClick={() => { setActiveTab('System Settings'); setView('overview'); }} className={`w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-[15px] font-bold transition-all ${
                  activeTab === 'System Settings' ? 'bg-[#F8FAFC] text-black shadow-sm border border-gray-100' : 'text-gray-500 hover:bg-gray-50'
                }`}>
                  <Settings size={22} strokeWidth={activeTab === 'System Settings' ? 2.5 : 2} />
                  <span>System Settings</span>
                </button>
              </div>
            </div>
          </nav>
        </div>
        <div className="p-6 border-t border-gray-50">
          <div className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-2xl cursor-pointer">
            <div className="w-10 h-10 rounded-full bg-indigo-50 flex items-center justify-center text-indigo-600 font-bold border border-indigo-100">NJ</div>
            <div className="flex-1 overflow-hidden">
              <p className="text-sm font-bold truncate">Noah Jacobs</p>
              <p className="text-xs text-gray-400 truncate">noah@talentdog.ai</p>
            </div>
          </div>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <div className="max-w-6xl mx-auto p-12">
          {activeTab === 'My Vacancies' && (
            view === 'overview' ? renderVacancies() : 
            view === 'vacancy-detail' ? renderVacancyDetail() : null
          )}
          {activeTab === 'System Settings' && renderSystemSettings()}
        </div>
      </main>
    </div>
  );
};

export default App;
