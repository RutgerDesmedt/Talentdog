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
  Target
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
  const [companies, setCompanies] = useState(['ASML', 'Adyen', 'Picnic', 'Bunq', 'Booking.com', 'Philips', 'Shell']);
  const [companyInput, setCompanyInput] = useState('');
  const [vacancyUrl, setVacancyUrl] = useState('');
  const [atsProvider, setAtsProvider] = useState('');
  const [atsConnected, setAtsConnected] = useState(false);

  const signalTypes = [
    'All Signals', 
    'Tenure Expiry', 
    'Layoffs',
    'M&A / Funding', 
    'Leadership Shift', 
    'Failing Vacancies'
  ];

  useEffect(() => {
    loadTalentFromAPI();
    loadVacanciesFromAPI();
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
    } catch (error) {
      console.error('Failed to load vacancies:', error);
      setVacancies([]);
    }
  };

  const handleAddCompanies = () => {
    if (!companyInput.trim()) return;
    
    const newCompanies = companyInput
      .split(',')
      .map(c => c.trim())
      .filter(c => c.length > 0 && !companies.includes(c));
    
    if (newCompanies.length > 0) {
      setCompanies([...companies, ...newCompanies]);
      setCompanyInput('');
      alert(`${newCompanies.length} bedrijven toegevoegd!`);
    }
  };

  const handleRemoveCompany = (companyToRemove) => {
    setCompanies(companies.filter(c => c !== companyToRemove));
  };

  const handleSyncVacancyUrl = async () => {
    if (!vacancyUrl.trim()) {
      alert('Voer een geldige URL in');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/vacancies/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url: vacancyUrl })
      });
      
      if (response.ok) {
        alert('Vacatures succesvol gesynchroniseerd!');
        loadVacanciesFromAPI();
        setVacancyUrl('');
        setView('overview');
      } else {
        alert('Fout bij synchroniseren van vacatures');
      }
    } catch (error) {
      console.error('Sync error:', error);
      alert('Fout bij synchroniseren: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnectATS = async (provider) => {
    setLoading(true);
    try {
      // Simulate ATS connection
      await new Promise(resolve => setTimeout(resolve, 1500));
      setAtsProvider(provider);
      setAtsConnected(true);
      alert(`Succesvol verbonden met ${provider}!`);
      loadVacanciesFromAPI();
      setView('overview');
    } catch (error) {
      alert('Fout bij verbinden met ATS');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnectATS = () => {
    setAtsProvider('');
    setAtsConnected(false);
    alert('ATS verbinding verbroken');
  };

  const candidateSignals = [
    {
      id: 1,
      rank: '#1',
      name: 'Mark Janssen',
      role: 'Senior DevOps Engineer',
      currentCompany: 'CloudScale BV',
      location: 'Utrecht, Netherlands',
      sector: 'Cloud Infrastructure',
      points: 26,
      photo: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?q=80&w=150&h=150&auto=format&fit=crop',
      signalType: 'TENURE EXPIRY',
      signalDescription: 'Mark has passed the 25-month threshold. Average tenure at CloudScale is 2y 1m. Window of Opportunity is NOW open.',
      matchedVacancy: 'Lead Infrastructure Engineer',
      story: "Mark has spent the last 2.1 years at CloudScale BV, where he spearheaded the transition to a serverless architecture. Having surpassed the median tenure of his peers, he is statistically likely to be open to new challenges that offer leadership responsibilities. His recent work with Kubernetes and Terraform aligns perfectly with your open Lead Infrastructure role.",
      background: "Mark Janssen is a seasoned DevOps specialist with over 8 years of experience in scaling high-traffic platforms. He has a proven track record of reducing deployment times by 40% and implementing robust CI/CD pipelines. Mark is highly regarded for his ability to bridge the gap between development and operations teams.",
      email: 'm.janssen@cloudscale.io'
    },
    {
      id: 2,
      rank: '#2',
      name: 'Sarah Chen',
      role: 'Product Lead',
      currentCompany: 'Aura AI',
      location: 'London, UK',
      sector: 'Artificial Intelligence',
      points: 42,
      photo: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=150&h=150&auto=format&fit=crop',
      signalType: 'CORPORATE SHOCKWAVE',
      signalDescription: 'Aura AI was acquired 48 hours ago. Historical attrition after M&A in this sector is 20%. Rapid action required.',
      matchedVacancy: 'Senior Product Manager',
      story: "Sarah's current employer, Aura AI, was acquired by Meta just 48 hours ago. This 'shockwave' signal suggests a high probability of cultural misalignment or role redundancy in the coming quarter. Sarah's background in early-stage AI product development makes her a prime target for high-growth startups before her equity packages are fully re-aligned.",
      background: "Sarah is a visionary Product Lead with a deep focus on LLM applications and user experience. She joined Aura AI as one of the first 10 employees and was instrumental in their growth to acquisition. Her expertise lies in product strategy, cross-functional team leadership, and rapid prototyping.",
      email: 'sarah.c@aura-ai.com'
    }
  ];

  const defaultVacancies = [
    {
      id: 'v1',
      title: 'Lead Infrastructure Engineer',
      department: 'Platform Ops',
      location: 'Hybrid / Utrecht',
      status: 'High Priority',
      posted: '4 days ago',
      matches: [candidateSignals[0]]
    },
    {
      id: 'v2',
      title: 'Senior Product Manager',
      department: 'Product Strategy',
      location: 'Remote / London',
      status: 'Active',
      posted: '1 week ago',
      matches: [candidateSignals[1]]
    }
  ];

  const orgSignals = [
    { id: 1, tag: 'LAYOFFS', tagColor: 'text-orange-600 bg-orange-50', text: 'Has {company} announced layoffs in the last 30 days?', alpha: '96', priority: 'Immediate', count: '8' },
    { id: 2, tag: 'CORPORATE SHOCKWAVE', tagColor: 'text-red-500 bg-red-50', text: 'Has {company} been involved in a merger or acquisition?', alpha: '92', priority: 'High', count: '12' },
    { id: 3, tag: 'TENURE EXPIRY', tagColor: 'text-amber-500 bg-amber-50', text: 'Has {talent} exceeded the median tenure at {company}?', alpha: '88', priority: 'High', count: '45' }
  ];

  const handleTalentClick = (talent) => {
    setSelectedTalent(talent);
    setView('talent-detail');
  };

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
            <button className="p-2 border border-gray-200 rounded-lg text-gray-400 hover:text-black">
              <MoreHorizontal size={20} />
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
              <h1 className="text-4xl font-black text-gray-900 tracking-tight flex items-center">
                {selectedTalent.name}
              </h1>
              <div className="flex items-center space-x-4 mt-3 text-gray-500 font-semibold text-sm">
                <div className="flex items-center space-x-1.5">
                  <Building2 size={16} className="text-gray-300" />
                  <span>{selectedTalent.sector || selectedTalent.currentCompany}</span>
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
            <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm relative overflow-hidden">
              <div className="flex items-center space-x-2 mb-6 text-gray-400">
                <ClipboardList size={18} />
                <span className="text-xs font-black uppercase tracking-widest">Talent Story</span>
              </div>
              <div className="relative z-10">
                <h2 className="text-3xl font-black text-gray-900 mb-6 leading-tight">
                  {selectedTalent.name}'s {selectedTalent.signalType === 'TENURE EXPIRY' ? 'Strategic Exit Window' : 'Career Shift Opportunity'}
                </h2>
                <p className="text-lg text-gray-600 leading-relaxed font-medium">
                  {selectedTalent.story || selectedTalent.signalDescription}
                </p>
              </div>
            </div>

            <div className="bg-white border border-gray-100 rounded-[2rem] p-10 shadow-sm">
              <div className="flex items-center space-x-2 mb-6 text-gray-400">
                <Zap size={18} />
                <span className="text-xs font-black uppercase tracking-widest">Verified Signals</span>
              </div>
              <div className="space-y-4">
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
                  <button className="text-[11px] font-black text-blue-600 bg-blue-50 px-3 py-1.5 rounded-full uppercase">Review Logic</button>
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
              <p className="text-sm text-gray-500 leading-relaxed font-medium mb-8">
                {selectedTalent.background || `${selectedTalent.name} is an experienced ${selectedTalent.role} at ${selectedTalent.currentCompany}.`}
              </p>
              <div className="flex flex-wrap gap-2">
                <div className="flex items-center space-x-2 text-[11px] font-black text-gray-400 uppercase bg-gray-50 p-2.5 rounded-lg border border-gray-100 w-fit">
                   <Globe size={12} />
                   <span>PERSONAL.IO</span>
                </div>
                <div className="flex items-center space-x-2 text-[11px] font-black text-gray-400 uppercase bg-gray-50 p-2.5 rounded-lg border border-gray-100 w-fit">
                   <Linkedin size={12} />
                   <span>LINKEDIN</span>
                </div>
              </div>
            </div>

            <button className="w-full bg-black text-white py-5 rounded-[2rem] flex items-center justify-center space-x-3 text-lg font-black hover:opacity-90 transition-all shadow-xl shadow-black/10">
              <Send size={20} className="text-white" />
              <span>Share with Team</span>
            </button>
          </div>
        </div>
      </div>
    );
  };

  const renderVacancies = () => {
    const vacancyList = vacancies.length > 0 ? vacancies.map(v => ({
      ...v,
      id: v.id || `v${v.id}`,
      department: v.department || 'General',
      status: v.status || 'Active',
      posted: '1 week ago',
      matches: candidateSignals.slice(0, 1)
    })) : defaultVacancies;

    return (
      <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
        <header className="flex items-center justify-between mb-12">
          <div>
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">My Vacancies</h1>
            <p className="text-sm text-gray-400 font-medium mt-1">Monitor talent matches across active roles.</p>
          </div>
          <button className="group flex items-center space-x-2 bg-black text-white px-6 py-3 rounded-full hover:bg-gray-800 transition-all active:scale-95 shadow-lg shadow-black/10">
            <Plus size={16} className="text-white" strokeWidth={2.5} />
            <span className="text-[11px] font-bold uppercase tracking-[0.1em]">New Vacancy</span>
          </button>
        </header>

        <div className="space-y-12">
          {vacancyList.map((vacancy) => (
            <div key={vacancy.id} className="bg-white border border-gray-100 rounded-[2.5rem] shadow-sm overflow-hidden">
              <div className="p-8 border-b border-gray-50 bg-[#F9FAFB]/30">
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
                  <div className="flex items-start space-x-5">
                    <div className="w-14 h-14 bg-white border border-gray-100 rounded-2xl flex items-center justify-center shadow-sm text-gray-400">
                      <Target size={28} />
                    </div>
                    <div>
                      <h2 className="text-2xl font-black text-gray-900 tracking-tight">{vacancy.title}</h2>
                      <div className="flex items-center space-x-4 mt-2 text-sm text-gray-400 font-bold">
                        <span className="flex items-center space-x-1.5 uppercase tracking-wider"><Building2 size={14} /> <span>{vacancy.department}</span></span>
                        <span className="flex items-center space-x-1.5 uppercase tracking-wider"><MapPin size={14} /> <span>{vacancy.location}</span></span>
                        <span className="flex items-center space-x-1.5 uppercase tracking-wider"><Clock size={14} /> <span>{vacancy.posted}</span></span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4 self-end md:self-auto">
                    <span className={`px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest ${vacancy.status === 'High Priority' ? 'bg-red-50 text-red-600' : 'bg-green-50 text-green-600'}`}>
                      {vacancy.status}
                    </span>
                    <button className="p-2.5 text-gray-400 hover:text-black border border-gray-100 rounded-xl hover:bg-white transition-all">
                      <Settings size={18} />
                    </button>
                  </div>
                </div>
              </div>

              <div className="p-8">
                <div className="flex items-center justify-between mb-8 px-2">
                  <h3 className="text-[10px] font-black text-gray-400 tracking-[0.2em] uppercase">Matching Talent (α High Signal)</h3>
                  <span className="text-xs font-bold text-gray-400">{vacancy.matches ? vacancy.matches.length : 0} Candidates Found</span>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {vacancy.matches && vacancy.matches.map((match) => (
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
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-[10px] font-black text-orange-600 bg-orange-50 px-2 py-0.5 rounded-md uppercase tracking-tighter">{match.signalType}</span>
                          <span className="text-xs font-bold text-gray-400">Score: {match.points}</span>
                        </div>
                      </div>
                      <div className="p-3 text-gray-200 group-hover:text-black transition-colors">
                        <ChevronRight size={24} />
                      </div>
                    </div>
                  ))}
                  
                  <div className="flex items-center justify-center p-5 border-2 border-dashed border-gray-100 rounded-[2rem] opacity-50">
                    <p className="text-xs font-black text-gray-300 uppercase tracking-widest">Searching for more matches...</p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTalentPool = () => {
    const displayProfiles = apiProfiles.length > 0 ? apiProfiles.slice(0, 10).map((p, idx) => ({
      ...p,
      rank: `#${idx + 1}`,
      story: p.story || `${p.name} is ready for a new challenge.`,
      background: p.background || `Experienced ${p.role}.`,
      matchedVacancy: 'Open Position'
    })) : candidateSignals;

    return (
      <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
        <header className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-black text-gray-900 tracking-tight">My Talent Pool</h1>
            <p className="text-sm text-gray-400 font-medium mt-1">Real-time signals and matching opportunities</p>
          </div>
          <button className="group flex items-center space-x-2 bg-transparent text-gray-500 border border-gray-200 px-5 py-2.5 rounded-full hover:border-gray-900 hover:text-gray-900 transition-all active:scale-95">
            <Plus size={14} className="text-gray-400 group-hover:text-gray-900 transition-colors" strokeWidth={2.5} />
            <span className="text-[10px] font-bold uppercase tracking-[0.1em]">Add Talent</span>
          </button>
        </header>

        {loading && (
          <div className="flex justify-center items-center py-20">
            <div className="animate-spin">
              <Zap size={32} className="text-blue-600" />
            </div>
          </div>
        )}

        <div className="flex flex-wrap gap-2 mb-10">
          {signalTypes.map((type) => (
            <button
              key={type}
              onClick={() => setActiveSignalTab(type)}
              className={`px-5 py-2 rounded-full text-[10px] font-black tracking-widest uppercase transition-all border ${
                activeSignalTab === type 
                ? 'bg-black text-white border-black shadow-lg shadow-black/10' 
                : 'bg-white text-gray-400 border-gray-100 hover:border-gray-300'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

        <div className="flex items-center justify-between mb-8">
          <h2 className="text-[10px] font-black text-gray-400 tracking-[0.2em] uppercase">Top Talent</h2>
          <button className="p-1 hover:bg-gray-50 rounded-md transition-colors">
            <MoreHorizontal size={18} className="text-gray-400" />
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
          {displayProfiles.map((candidate) => (
            <div 
              key={candidate.id} 
              onClick={() => handleTalentClick(candidate)}
              className="group relative bg-white border border-gray-100 rounded-[2.5rem] flex flex-col transition-all hover:border-gray-200 hover:shadow-2xl cursor-pointer"
            >
              <div className="absolute -top-4 left-1/2 -translate-x-1/2 z-20">
                  <div className="bg-white px-6 py-1.5 rounded-full border border-gray-100 shadow-sm flex items-center justify-center min-w-[64px]">
                      <span className="text-xs font-black tracking-tighter text-gray-400 uppercase">
                          {candidate.rank}
                      </span>
                  </div>
              </div>

              <div className="p-8 pb-10">
                <div className="flex items-center space-x-5 mb-10 mt-4">
                  <div className="w-16 h-16 rounded-2xl overflow-hidden flex-shrink-0 border border-gray-50 shadow-sm transition-all duration-700 filter grayscale group-hover:grayscale-0 group-hover:scale-105">
                    <img src={candidate.photo} alt={candidate.name} className="w-full h-full object-cover" />
                  </div>
                  <div>
                    <h4 className="text-xl font-black text-gray-900 tracking-tight">{candidate.name}</h4>
                    <p className="text-[10px] font-bold text-gray-400 uppercase tracking-[0.15em]">{candidate.role}</p>
                  </div>
                </div>

                <div className="mb-8 p-6 bg-gray-50 rounded-2xl border border-gray-50 group-hover:bg-white group-hover:border-gray-100 transition-colors">
                  <div className="flex items-center space-x-1.5 mb-3 text-gray-500">
                    <Sparkles size={10} className="fill-gray-500/10" />
                    <h5 className="text-[9px] font-black text-black uppercase tracking-[0.25em]">
                      {candidate.signalType}
                    </h5>
                  </div>
                  <p className="text-sm text-gray-800 leading-relaxed font-semibold">
                    {candidate.signalDescription}
                  </p>
                </div>

                <div className="space-y-4 px-2">
                  <div className="flex items-center space-x-4">
                    <div className="p-2 border border-gray-100 rounded-lg bg-white transition-colors">
                      <Heart size={14} className="text-gray-300 transition-colors group-hover:text-red-400" />
                    </div>
                    <p className="text-[11px] leading-relaxed">
                      <span className="font-black text-gray-300 uppercase mr-2 tracking-widest">Matching</span>
                      <span className="font-medium text-gray-900">{candidate.matchedVacancy}</span>
                    </p>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderManageVacancies = () => {
    const atsProviders = [
      { name: 'Greenhouse', connected: atsProvider === 'Greenhouse' },
      { name: 'Lever', connected: atsProvider === 'Lever' },
      { name: 'Workday', connected: atsProvider === 'Workday' },
      { name: 'BambooHR', connected: atsProvider === 'BambooHR' },
      { name: 'SmartRecruiters', connected: atsProvider === 'SmartRecruiters' },
      { name: 'iCIMS', connected: atsProvider === 'iCIMS' }
    ];

    return (
      <div className="animate-in fade-in slide-in-from-right-4 duration-500">
        <button 
          onClick={() => setView('overview')}
          className="flex items-center space-x-2 text-gray-400 hover:text-black transition-colors mb-6 group"
        >
          <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
          <div className="text-left">
            <h2 className="text-sm font-bold text-black">Vacancies</h2>
            <p className="text-[11px] font-medium text-gray-400">Connect your ATS or sync vacancy page URL.</p>
          </div>
        </button>

        <div className="space-y-6">
          {/* ATS Connection Section */}
          <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h3 className="text-sm font-black text-gray-900 tracking-tight">Connect ATS System</h3>
                <p className="text-xs text-gray-500 mt-1">Automatically sync vacancies from your recruitment platform</p>
              </div>
              {atsConnected && (
                <div className="flex items-center space-x-2 bg-emerald-50 text-emerald-700 px-3 py-1.5 rounded-full">
                  <div className="w-2 h-2 rounded-full bg-emerald-500"></div>
                  <span className="text-xs font-bold">Connected to {atsProvider}</span>
                </div>
              )}
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              {atsProviders.map((provider) => (
                <button
                  key={provider.name}
                  onClick={() => provider.connected ? handleDisconnectATS() : handleConnectATS(provider.name)}
                  disabled={loading}
                  className={`group relative p-5 border rounded-xl transition-all ${
                    provider.connected 
                      ? 'border-emerald-500 bg-emerald-50/50' 
                      : 'border-gray-200 hover:border-gray-900 hover:shadow-md bg-white'
                  } ${loading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                      provider.connected ? 'bg-emerald-100' : 'bg-gray-100'
                    }`}>
                      <Database size={16} className={provider.connected ? 'text-emerald-600' : 'text-gray-400'} />
                    </div>
                    {provider.connected && (
                      <CheckCircle2 size={18} className="text-emerald-600" />
                    )}
                  </div>
                  <div className="text-sm font-bold text-gray-900 text-left">{provider.name}</div>
                  <div className="text-xs text-gray-400 text-left mt-0.5">
                    {provider.connected ? 'Connected' : 'Click to connect'}
                  </div>
                </button>
              ))}
            </div>

            {atsConnected && (
              <div className="mt-6 p-4 bg-blue-50 border border-blue-100 rounded-xl">
                <div className="flex items-start space-x-3">
                  <Bell size={18} className="text-blue-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-xs font-bold text-blue-900 mb-1">Auto-sync enabled</p>
                    <p className="text-xs text-blue-700">
                      Vacancies sync automatically every 4 hours. Last sync: Just now
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-xs">
              <span className="bg-[#FCFCFD] px-4 text-gray-400 font-bold uppercase tracking-widest">OR</span>
            </div>
          </div>

          {/* URL Sync Section */}
          <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
            <h3 className="text-sm font-black text-gray-900 mb-4 tracking-tight">Sync from Vacancy Page</h3>
            <p className="text-xs text-gray-500 mb-4">Enter the URL of your careers page to automatically extract vacancies</p>
            
            <div className="flex space-x-3">
              <input 
                type="url" 
                placeholder="https://yourcompany.com/careers" 
                className="flex-1 px-4 py-2.5 bg-[#F9FAFB] border border-gray-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black/10" 
                value={vacancyUrl}
                onChange={(e) => setVacancyUrl(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSyncVacancyUrl()}
              />
              <button 
                onClick={handleSyncVacancyUrl}
                disabled={loading}
                className={`bg-black text-white px-6 py-2.5 rounded-lg flex items-center space-x-2 text-sm font-bold hover:bg-gray-800 transition-all ${
                  loading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    <span>Syncing...</span>
                  </>
                ) : (
                  <>
                    <ExternalLink size={16} />
                    <span>Sync Vacancies</span>
                  </>
                )}
              </button>
            </div>

            <div className="mt-4 p-4 bg-gray-50 rounded-xl">
              <div className="flex items-start space-x-3">
                <Sparkles size={16} className="text-gray-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-bold text-gray-700 mb-1">AI-Powered Extraction</p>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    Our AI automatically detects job titles, locations, departments, and requirements from your careers page.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Current Vacancies Overview */}
          {vacancies.length > 0 && (
            <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-black text-gray-900">Current Vacancies</h3>
                <span className="text-xs font-bold text-gray-400">{vacancies.length} Active</span>
              </div>
              <div className="space-y-2">
                {vacancies.slice(0, 5).map((vacancy, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-3">
                      <Target size={16} className="text-gray-400" />
                      <span className="text-sm font-bold text-gray-900">{vacancy.title}</span>
                    </div>
                    <span className="text-xs text-gray-400">{vacancy.location || 'Remote'}</span>
                  </div>
                ))}
                {vacancies.length > 5 && (
                  <p className="text-xs text-gray-400 text-center pt-2">
                    +{vacancies.length - 5} more vacancies
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Help Section */}
          <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6">
            <div className="flex items-start space-x-3">
              <AlertTriangle size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
              <div>
                <h4 className="text-sm font-bold text-blue-900 mb-2">How vacancy matching works</h4>
                <ul className="text-xs text-blue-700 leading-relaxed space-y-1">
                  <li>• Synced vacancies appear under "My Vacancies"</li>
                  <li>• AI automatically matches talent based on skills, experience, and signals</li>
                  <li>• Matching candidates are prioritized by relevance score</li>
                  <li>• You can manually adjust matches and add notes</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  const renderManageTalentPool = () => (
    <div className="animate-in fade-in slide-in-from-right-4 duration-500">
      <button 
        onClick={() => setView('overview')}
        className="flex items-center space-x-2 text-gray-400 hover:text-black transition-colors mb-6 group"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        <div className="text-left">
          <h2 className="text-sm font-bold text-black">Talent Pool</h2>
          <p className="text-[11px] font-medium text-gray-400">Manage companies to track for talent signals.</p>
        </div>
      </button>

      <div className="space-y-6">
        <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <h3 className="text-xs font-black text-gray-900 mb-4 tracking-tight">Add Companies</h3>
          <p className="text-xs text-gray-500 mb-4">Enter company names separated by commas (e.g., Google, Microsoft, Apple)</p>
          <div className="flex space-x-3">
            <input 
              type="text" 
              placeholder="ASML, Adyen, Picnic..." 
              className="flex-1 px-4 py-2.5 bg-[#F9FAFB] border border-gray-100 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-black/10" 
              value={companyInput}
              onChange={(e) => setCompanyInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleAddCompanies()}
            />
            <button 
              onClick={handleAddCompanies}
              className="bg-black text-white px-6 py-2.5 rounded-lg flex items-center space-x-2 text-sm font-bold hover:bg-gray-800 transition-all"
            >
              <Plus size={16} strokeWidth={3} />
              <span>Add Companies</span>
            </button>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
          <div className="p-6 border-b border-gray-50 flex justify-between items-center">
            <h3 className="text-sm font-bold text-gray-900">Tracked Companies</h3>
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">{companies.length} Companies</span>
          </div>
          
          <div className="p-6">
            {companies.length === 0 ? (
              <div className="text-center py-12">
                <Database size={48} className="mx-auto text-gray-200 mb-4" />
                <p className="text-sm font-bold text-gray-400">No companies added yet</p>
                <p className="text-xs text-gray-300 mt-1">Add companies above to start tracking talent signals</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {companies.map((company, idx) => (
                  <div 
                    key={idx}
                    className="group flex items-center justify-between p-4 border border-gray-100 rounded-xl hover:border-gray-300 hover:shadow-md transition-all bg-white"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="w-10 h-10 bg-gray-50 rounded-lg flex items-center justify-center">
                        <Building2 size={18} className="text-gray-400" />
                      </div>
                      <span className="text-sm font-bold text-gray-900">{company}</span>
                    </div>
                    <button 
                      onClick={() => handleRemoveCompany(company)}
                      className="opacity-0 group-hover:opacity-100 p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-all"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="bg-blue-50 border border-blue-100 rounded-2xl p-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle size={20} className="text-blue-600 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="text-sm font-bold text-blue-900 mb-1">How it works</h4>
              <p className="text-xs text-blue-700 leading-relaxed">
                TalentDog continuously monitors these companies for signals like layoffs, M&A activity, tenure milestones, and leadership changes. 
                Candidates from these companies will appear in your talent pool when relevant signals are detected.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderConfigureSignals = () => (
    <div className="animate-in fade-in slide-in-from-right-4 duration-500">
      <button 
        onClick={() => setView('overview')}
        className="flex items-center space-x-2 text-gray-400 hover:text-black transition-colors mb-6 group"
      >
        <ArrowLeft size={18} className="group-hover:-translate-x-1 transition-transform" />
        <div className="text-left">
          <h2 className="text-sm font-bold text-black">Signals</h2>
          <p className="text-[11px] font-medium text-gray-400">Configure which events trigger an opportunity.</p>
        </div>
      </button>

      <div className="space-y-6">
        <div className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm">
          <h3 className="text-xs font-black text-gray-900 mb-4 tracking-tight">Add Signals</h3>
          <div className="flex space-x-3">
            <input type="text" placeholder="Does {talent} mention..." className="flex-1 px-4 py-2.5 bg-[#F9FAFB] border border-gray-100 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-black/5" />
            <input type="text" placeholder="Enter Title" className="w-48 px-4 py-2.5 bg-[#F9FAFB] border border-gray-100 rounded-lg text-sm focus:outline-none focus:ring-1 focus:ring-black/5" />
            <button className="bg-black text-white px-4 py-2.5 rounded-lg flex items-center space-x-2 text-sm font-bold hover:bg-gray-800 transition-all">
              <Plus size={16} strokeWidth={3} />
              <span>Add</span>
            </button>
          </div>
        </div>

        <div className="bg-white border border-gray-100 rounded-2xl overflow-hidden shadow-sm">
          <div className="p-6 border-b border-gray-50 flex justify-between items-center">
            <h3 className="text-sm font-bold text-gray-900">Organization Signals</h3>
            <span className="text-[11px] font-bold text-gray-400 uppercase tracking-widest">10 Signals Remaining</span>
          </div>
          
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="text-[11px] font-bold text-gray-400 uppercase tracking-widest border-b border-gray-50">
                  <th className="px-6 py-4">Signal</th>
                  <th className="px-6 py-4 text-center">Alpha (α)</th>
                  <th className="px-6 py-4 text-center">Count</th>
                  <th className="px-6 py-4 text-center">Mute</th>
                  <th className="px-6 py-4">Signal Priority</th>
                  <th className="px-6 py-4 text-right">Options</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-50">
                {orgSignals.map((signal) => (
                  <tr key={signal.id} className="hover:bg-gray-50/50 transition-colors">
                    <td className="px-6 py-6">
                      <div className="space-y-1">
                        <span className={`text-[9px] font-black px-2 py-0.5 rounded uppercase tracking-wider ${signal.tagColor}`}>
                          {signal.tag}
                        </span>
                        <p className="text-sm font-bold text-gray-800">{signal.text}</p>
                      </div>
                    </td>
                    <td className="px-6 py-6 text-center text-sm font-bold text-gray-900">{signal.alpha}</td>
                    <td className="px-6 py-6 text-center text-sm font-bold text-gray-900">{signal.count}</td>
                    <td className="px-6 py-6 text-center text-gray-400 hover:text-black transition-colors cursor-pointer"><Bell size={18} /></td>
                    <td className="px-6 py-6">
                      <div className="flex items-center justify-between w-full px-3 py-2 bg-[#F9FAFB] border border-gray-100 rounded-lg text-sm font-bold">
                        <span>{signal.priority}</span>
                        <ChevronDown size={14} className="text-gray-400" />
                      </div>
                    </td>
                    <td className="px-6 py-6 text-right">
                      <button className="text-gray-400 hover:text-black transition-colors"><MoreHorizontal size={18} /></button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );

  const renderSystemSettings = () => (
    <div className="animate-in fade-in slide-in-from-bottom-2 duration-500">
      {view === 'overview' ? (
        <>
          <header className="mb-12 flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight mb-2">System Setup</h1>
              <p className="text-[15px] text-gray-500 font-medium">Manage territory, signals, and team capacity.</p>
            </div>
            <div className="text-right text-xs font-semibold text-gray-400 tracking-wide bg-gray-50 px-3 py-1.5 rounded-full border border-gray-100">
                 Renewal Date: January 23, 2026
            </div>
          </header>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-10">
            <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
              <div className="flex justify-between items-start mb-8">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Database size={24} /></div>
                  <div>
                    <h3 className="text-[15px] font-bold text-gray-900">Talent Pool List</h3>
                    <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">OPERATIONAL</p>
                  </div>
                </div>
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400"></div>
              </div>
              <div className="mb-10">
                <span className="text-5xl font-black text-gray-900 tracking-tight">{companies.length}</span>
                <p className="text-sm font-medium text-gray-400 mt-2">Companies Tracked / 100 Capacity</p>
              </div>
              <button 
                onClick={() => setView('manage-talent-pool')}
                className="w-full py-3.5 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 hover:bg-gray-50 transition-all"
              >
                Manage Talent Pool
              </button>
            </div>

            <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
              <div className="flex justify-between items-start mb-8">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Briefcase size={24} /></div>
                  <div>
                    <h3 className="text-[15px] font-bold text-gray-900">Vacancies</h3>
                    <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">
                      {atsConnected ? `CONNECTED - ${atsProvider}` : 'MANUAL SYNC'}
                    </p>
                  </div>
                </div>
                <div className={`w-2.5 h-2.5 rounded-full ${atsConnected ? 'bg-emerald-400' : 'bg-amber-400'}`}></div>
              </div>
              <div className="mb-10">
                <span className="text-5xl font-black text-gray-900 tracking-tight">{vacancies.length}</span>
                <p className="text-sm font-medium text-gray-400 mt-2">Active Vacancies</p>
              </div>
              <button 
                onClick={() => setView('manage-vacancies')}
                className="w-full py-3.5 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 hover:bg-gray-50 transition-all"
              >
                Manage Vacancies
              </button>
            </div>

            <div className="bg-white border border-gray-100 rounded-[28px] p-8 shadow-sm">
              <div className="flex justify-between items-start mb-8">
                <div className="flex items-center space-x-4">
                  <div className="p-3 bg-gray-50 rounded-2xl text-gray-600"><Sparkles size={24} /></div>
                  <div>
                    <h3 className="text-[15px] font-bold text-gray-900">Signals</h3>
                    <p className="text-[11px] font-bold text-emerald-500 uppercase tracking-widest mt-0.5">OPERATIONAL</p>
                  </div>
                </div>
                <div className="w-2.5 h-2.5 rounded-full bg-emerald-400"></div>
              </div>
              <div className="mb-10">
                <span className="text-5xl font-black text-gray-900 tracking-tight">20</span>
                <p className="text-sm font-medium text-gray-400 mt-2">Active Signals (5 High Priority)</p>
              </div>
              <button onClick={() => setView('configure-signals')} className="w-full py-3.5 border border-gray-200 rounded-xl text-sm font-bold text-gray-900 hover:bg-gray-50 transition-all">Configure Signals</button>
            </div>
          </div>

          <div className="bg-white border border-gray-100 rounded-[28px] overflow-hidden shadow-sm">
            <div className="p-8 border-b border-gray-50 flex justify-between items-center">
              <div>
                <h3 className="text-[17px] font-bold text-gray-900">Active Users</h3>
                <p className="text-sm font-medium text-gray-400 mt-1">All the users in your organization.</p>
              </div>
              <button className="flex items-center space-x-2 bg-black text-white px-5 py-2.5 rounded-xl text-sm font-bold hover:bg-gray-800 transition-all">
                <Plus size={16} strokeWidth={3} />
                <span>Add User</span>
              </button>
            </div>
            <div className="divide-y divide-gray-50">
              {['noah+t6@getbirddog.ai', 'noah+t20@getbirddog.ai', 'Jack Porter', 'Noah Jacobs'].map((user, idx) => (
                <div key={idx} className="flex items-center justify-between p-6 hover:bg-gray-50/50 transition-colors px-10">
                  <div className="flex items-center space-x-5">
                    <div className="w-10 h-10 rounded-xl flex items-center justify-center bg-gray-100 text-gray-500">
                      <User size={18} />
                    </div>
                    <span className="text-[15px] font-semibold text-gray-700">{user}</span>
                  </div>
                  <div className="flex items-center space-x-12">
                    <span className="text-sm font-bold text-gray-400 min-w-[120px] text-right">{idx < 2 ? 'Super Admin' : 'Normal + Admin'}</span>
                    <div className="flex items-center space-x-4 text-gray-400">
                      <button className="hover:text-black"><Edit2 size={18} /></button>
                      <button className="hover:text-red-500"><Trash2 size={18} /></button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      ) : view === 'configure-signals' ? renderConfigureSignals() : 
          view === 'manage-talent-pool' ? renderManageTalentPool() : 
          renderManageVacancies()}
    </div>
  );

  return (
    <div className="flex h-screen w-full bg-[#FCFCFD] text-[#111827] font-sans overflow-hidden">
      <aside className="w-72 bg-white border-r border-gray-100 flex flex-col shrink-0">
        <div className="p-8 flex-1">
          <div className="mb-12 px-2">
            <TalentDogLogo />
          </div>

          <nav className="space-y-10">
            <div>
              <p className="text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-6 px-4">My Account</p>
              <div className="space-y-2">
                <button 
                  onClick={() => { setActiveTab('My Talent Pool'); setView('overview'); }} 
                  className={`w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-[15px] font-bold transition-all ${activeTab === 'My Talent Pool' ? 'bg-[#F8FAFC] text-black shadow-sm border border-gray-100' : 'text-gray-500 hover:bg-gray-50'}`}
                >
                  <LayoutGrid size={22} strokeWidth={activeTab === 'My Talent Pool' ? 2.5 : 2} />
                  <span>My Talent Pool</span>
                </button>
                <button 
                  onClick={() => { setActiveTab('My Vacancies'); setView('overview'); }} 
                  className={`w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-[15px] font-bold transition-all ${activeTab === 'My Vacancies' ? 'bg-[#F8FAFC] text-black shadow-sm border border-gray-100' : 'text-gray-500 hover:bg-gray-50'}`}
                >
                  <Briefcase size={22} strokeWidth={activeTab === 'My Vacancies' ? 2.5 : 2} />
                  <span>My Vacancies</span>
                </button>
                <button className="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-gray-500 hover:bg-gray-50 font-bold text-[15px] transition-all"><Zap size={22} /><span>Signals</span></button>
              </div>
            </div>

            <div>
              <p className="text-[11px] font-bold text-gray-400 uppercase tracking-[0.2em] mb-6 px-4">Talent Manager</p>
              <div className="space-y-2">
                <button className="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-gray-500 hover:bg-gray-50 font-bold text-[15px] transition-all"><ClipboardList size={22} /><span>Assignment Desk</span></button>
                <button className="w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-gray-500 hover:bg-gray-50 font-bold text-[15px] transition-all"><CheckCircle2 size={22} /><span>Progress</span></button>
                <button onClick={() => { setActiveTab('System Settings'); setView('overview'); }} className={`w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-[15px] font-bold transition-all ${activeTab === 'System Settings' ? 'bg-[#F8FAFC] text-black shadow-sm border border-gray-100' : 'text-gray-500 hover:bg-gray-50'}`}>
                  <Settings size={22} strokeWidth={activeTab === 'System Settings' ? 2.5 : 2} />
                  <span>System Settings</span>
                </button>
              </div>
            </div>
          </nav>
        </div>

        <div className="p-6 border-t border-gray-50">
          <div className="flex items-center space-x-3 p-3 hover:bg-gray-50 rounded-2xl transition-colors cursor-pointer">
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
          {activeTab === 'My Talent Pool' && (view === 'overview' ? renderTalentPool() : renderTalentDetail())}
          {activeTab === 'My Vacancies' && (view === 'overview' ? renderVacancies() : renderTalentDetail())}
          {activeTab === 'System Settings' && renderSystemSettings()}
        </div>
      </main>
    </div>
  );
};

export default App;
