import React, { useState, useEffect } from 'react';
import { 
  Plus, LayoutGrid, Briefcase, Zap, ClipboardList, CheckCircle2, Settings, Database,
  Sparkles, Edit2, Trash2, User, Heart, MoreHorizontal, ArrowLeft, Trophy, Bell,
  ChevronDown, TrendingUp, Users, AlertTriangle, ExternalLink, Globe, Linkedin,
  MapPin, Building2, Send, ChevronRight, Clock, Target, Filter, Search, Upload,
  Eye // ScanEye vervangen door Eye om build-fout op Railway te fixen
} from 'lucide-react';

// Importeer je nieuwe component
import SignalIntelligence from './components/SignalIntelligence';

// ==================== API CONFIGURATION ====================
// Hardcoded URL om build-issues met environment variables te omzeilen
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
  
  // Data states
  const [profiles, setProfiles] = useState([]);
  const [vacancies, setVacancies] = useState([]);
  
  const profilesPerPage = 12;
  const cities = ['Amsterdam', 'Rotterdam', 'Utrecht', 'Eindhoven', 'Den Haag'];

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
      if (!response.ok) throw new Error('Network response was not ok');
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
      if (!response.ok) throw new Error('Network response was not ok');
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
    const companies =
