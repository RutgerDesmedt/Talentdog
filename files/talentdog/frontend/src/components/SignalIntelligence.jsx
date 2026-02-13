import React, { useState } from 'react';
import { 
  TrendingDown, 
  Users, 
  Briefcase, 
  AlertCircle, 
  MessageSquare, 
  Search, 
  Loader2, 
  ExternalLink 
} from 'lucide-react';

const SignalIntelligence = () => {
  const [company, setCompany] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const fetchSignals = async () => {
    if (!company) return;
    setLoading(true);
    try {
      // De URL naar jouw specifieke Railway backend
      const response = await fetch(`https://talentdogbackend.up.railway.app/api/detect-signals/${company}`);
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error("Fout bij ophalen signalen:", error);
    } finally {
      setLoading(false);
    }
  };

  const getSignalIcon = (id) => {
    switch (id) {
      case 'layoffs': return <TrendingDown className="text-red-500" />;
      case 'tenure': return <Users className="text-green-500" />;
      case 'ma_activity': return <Briefcase className="text-blue-500" />;
      case 'leadership': return <AlertCircle className="text-purple-500" />;
      case 'sentiment': return <MessageSquare className="text-orange-500" />;
      default: return <Search className="text-gray-400" />;
    }
  };

  return (
    <div className="p-6 max-w-7xl mx-auto font-sans">
      {/* Zoekbalk Sectie */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-8 mb-8 animate-in">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Talent Intelligence Scanner</h1>
        <p className="text-gray-500 mb-6">Scan real-time signalen bij concurrenten om poaching kansen te vinden.</p>
        
        <div className="flex gap-3">
          <input 
            type="text" 
            placeholder="Bijv. Philips, ASML of Google..." 
            className="flex-1 px-4 py-3 rounded-xl border border-gray-200 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition-all"
            value={company}
            onChange={(e) => setCompany(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && fetchSignals()}
          />
          <button 
            onClick={fetchSignals}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-xl font-semibold flex items-center gap-2 transition-all disabled:opacity-50"
          >
            {loading ? <Loader2 className="animate-spin w-5 h-5" /> : <Search className="w-5 h-5" />}
            {loading ? 'Scanning AI...' : 'Scan Signalen'}
          </button>
        </div>
      </div>

      {/* Resultaten Grid */}
      {results && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in">
          {results.signals.map((signal) => (
            <div key={signal.signal_id} className="flex flex-col gap-4">
              <div className="flex items-center gap-2 px-1">
                {getSignalIcon(signal.signal_id)}
                <h3 className="font-bold text-gray-700 uppercase tracking-wider text-sm">
                  {signal.signal_label}
                </h3>
              </div>
              
              {signal.found_items.map((item, idx) => (
                <div key={idx} className="bg-white border border-gray-100 rounded-2xl p-5 shadow-sm hover:shadow-md transition-all group">
                  <h4 className="font-bold text-gray-900 mb-2 leading-snug group-hover:text-blue-600 transition-colors">
                    {item.title}
                  </h4>
                  <p className="text-sm text-gray-600 mb-4 line-clamp-3 leading-relaxed italic">
                    "{item.snippet}"
                  </p>
                  <div className="flex justify-between items-center pt-4 border-t border-gray-50">
                    <span className="text-xs text-gray-400 font-medium">{item.date || 'Recent ontdekt'}</span>
                    <a 
                      href={item.link} 
                      target="_blank" 
                      rel="noreferrer"
                      className="text-blue-500 hover:bg-blue-50 p-2 rounded-lg transition-colors flex items-center gap-1 text-xs font-bold"
                    >
                      BRON <ExternalLink size={14} />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SignalIntelligence;
