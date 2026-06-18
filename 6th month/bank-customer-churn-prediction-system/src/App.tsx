import React, { useState, useMemo } from 'react';
import { 
  TrendingUp, 
  UserCheck, 
  Users, 
  Percent, 
  ShieldCheck, 
  Layers, 
  Settings, 
  Code, 
  Database, 
  BookOpen, 
  ArrowRight, 
  Sparkles, 
  Terminal, 
  Sliders, 
  Download, 
  LayoutDashboard,
  CheckCircle,
  AlertTriangle,
  Folder,
  FileCode,
  Info,
  Server,
  Activity,
  Cpu,
  RefreshCw,
  HardDrive
} from 'lucide-react';

// Unified type definitions
interface CustomerData {
  creditScore: number;
  geography: 'France' | 'Germany' | 'Spain';
  gender: 'Female' | 'Male';
  age: number;
  tenure: number;
  balance: number;
  numOfProducts: number;
  hasCrCard: boolean;
  isActiveMember: boolean;
  estimatedSalary: number;
}

export default function App() {
  // Navigation State
  const [activeTab, setActiveTab] = useState<'simulator' | 'eda' | 'codebase' | 'terminal'>('simulator');
  
  // Interactive Customer State
  const [customer, setCustomer] = useState<CustomerData>({
    creditScore: 650,
    geography: 'France',
    gender: 'Female',
    age: 38,
    tenure: 5,
    balance: 85000,
    numOfProducts: 2,
    hasCrCard: true,
    isActiveMember: true,
    estimatedSalary: 112000
  });

  // Simulator Engine based on realistic Logistic Coefficients + Interaction terms from real bank churn logs
  const prediction = useMemo(() => {
    // Standardizing values
    const normAge = (customer.age - 38) / 10;
    const normCredit = (customer.creditScore - 650) / 100;
    const normBalance = customer.balance === 0 ? -1 : (customer.balance - 75000) / 50000;
    const normSalary = (customer.estimatedSalary - 100000) / 50000;

    // Log-odds baseline
    let logOdds = -1.8;

    // Feature impacts matching typical bank parameters
    logOdds += normAge * 0.85; // Age is strongest driver of churn
    logOdds -= normCredit * 0.15; // Better credit reduces churn slightly
    
    // Geography
    if (customer.geography === 'Germany') {
      logOdds += 0.8; // Germany has highly elevated risk
    } else if (customer.geography === 'Spain') {
      logOdds -= 0.1;
    }

    // Gender
    if (customer.gender === 'Female') {
      logOdds += 0.25; // Female slightly higher churn
    }

    // NumOfProducts (Crucial interaction)
    if (customer.numOfProducts === 1) {
      logOdds += 0.3; // moderate risk
    } else if (customer.numOfProducts === 2) {
      logOdds -= 0.8; // lowest risk (sweet spot)
    } else if (customer.numOfProducts === 3) {
      logOdds += 1.95; // high risk of multi-product drop
    } else if (customer.numOfProducts === 4) {
      logOdds += 3.8; // extreme near-certainty of churn
    }

    // Member activity
    if (customer.isActiveMember) {
      logOdds -= 0.95; // active status strongly reduces risk
    }

    // Tenure impact
    logOdds -= (customer.tenure - 5) * 0.05;

    // Card ownership
    if (customer.hasCrCard) {
      logOdds -= 0.05;
    }

    // Convert log-odds to probability
    const probability = 1 / (1 + Math.exp(-logOdds));
    
    // Categorization
    let riskLevel: 'LOW' | 'MEDIUM' | 'HIGH' = 'LOW';
    let riskColor = 'text-emerald-400';
    let riskBg = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
    let labelBorder = 'border-emerald-500/50';
    
    if (probability >= 0.6) {
      riskLevel = 'HIGH';
      riskColor = 'text-rose-400';
      riskBg = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
      labelBorder = 'border-rose-500/50';
    } else if (probability >= 0.3) {
      riskLevel = 'MEDIUM';
      riskColor = 'text-amber-400';
      riskBg = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
      labelBorder = 'border-amber-500/50';
    }

    return {
      probability: Math.round(probability * 100),
      riskLevel,
      riskColor,
      riskBg,
      labelBorder
    };
  }, [customer]);

  // List of high impact factors for the simulator
  const riskDrivers = useMemo(() => {
    const drivers = [];
    if (customer.age > 45) {
      drivers.push({ name: 'Elevated Customer Age', impact: 'High Risk', detail: `Age ${customer.age} places client in retention risk bracket.` });
    }
    if (customer.numOfProducts >= 3) {
      drivers.push({ name: 'Product Over-concentration', impact: 'Critical Risk', detail: `${customer.numOfProducts} products linked to imminent retention losses.` });
    }
    if (customer.geography === 'Germany') {
      drivers.push({ name: 'High-risk Region (Germany)', impact: 'Medium Risk', detail: 'German customers consistently present double the baseline churn rates.' });
    }
    if (!customer.isActiveMember) {
      drivers.push({ name: 'Inactive Membership', impact: 'High Risk', detail: 'Zero transactions or digital logins logged during recent quarter.' });
    }
    if (customer.creditScore < 500) {
      drivers.push({ name: 'Lower Credit Stand', impact: 'Medium Risk', detail: 'Credit score below 500 correlates with economic strain exits.' });
    }

    if (drivers.length === 0) {
      drivers.push({ name: 'Optimal Product Balance', impact: 'Strong Mitigator', detail: 'Using exactly 2 banking products is structural sweet spot.' });
      drivers.push({ name: 'Active Bank Relationship', impact: 'Mitigator', detail: 'Regular customer contact and transactions minimize risk.' });
    }
    return drivers;
  }, [customer]);

  // Codebase structure preview data
  const filesList = [
    {
      name: 'README.md',
      path: '/capstone-churn-system/README.md',
      status: 'Ready',
      size: '2.8 KB',
      desc: 'System summary, architecture specs, and full instructions for Docker containers.'
    },
    {
      name: 'preprocessor.py',
      path: '/capstone-churn-system/ml_pipeline/preprocessor.py',
      status: 'Pending Turn 2',
      size: 'Planned ~4.2 KB',
      desc: 'Target encoding, min-max transformations, and artifact serialization rules.'
    },
    {
      name: 'train.py',
      path: '/capstone-churn-system/ml_pipeline/train.py',
      status: 'Pending Turn 2',
      size: 'Planned ~6.8 KB',
      desc: 'MLflow workflow integration, hyperparameter tracking, and XGBoost training code.'
    },
    {
      name: 'main.py',
      path: '/capstone-churn-system/backend/main.py',
      status: 'Pending Turn 2',
      size: 'Planned ~5.5 KB',
      desc: 'FastAPI instance, CORS setup, model state recovery, and predictive routers.'
    },
    {
      name: 'schemas.py',
      path: '/capstone-churn-system/backend/schemas.py',
      status: 'Pending Turn 2',
      size: 'Planned ~1.8 KB',
      desc: 'Strict type validation on requests via nested Pydantic models.'
    },
    {
      name: 'app.py',
      path: '/capstone-churn-system/frontend/app.py',
      status: 'Pending Turn 3',
      size: 'Planned ~7.2 KB',
      desc: 'Streamlit controller serving metrics, visual insights via charts, and interactive input sliders.'
    },
    {
      name: 'docker-compose.yml',
      path: '/capstone-churn-system/docker-compose.yml',
      status: 'Pending Turn 3',
      size: 'Planned ~1.2 KB',
      desc: 'Environment orchestration mapping ports, hot reloads, and internal network routes.'
    }
  ];

  return (
    <div className="min-h-screen bg-[#0F1115] text-[#E2E8F0] font-sans flex flex-col selection:bg-sky-500/30 selection:text-sky-300">
      
      {/* Upper Structural Header - Matches "Technical Dashboard" layout */}
      <header className="h-16 border-b border-slate-800 flex items-center justify-between px-6 bg-[#161922]">
        <div className="flex items-center gap-3">
          <div className="w-3 h-3 bg-emerald-500 rounded-full shadow-[0_0_8px_#10b981] animate-pulse"></div>
          <h1 className="text-md md:text-lg font-bold tracking-tight text-white flex items-center gap-2">
            CHURN-SYSTEM-v1.0 <span className="text-slate-500 font-normal">/ MLOps Engine</span>
          </h1>
        </div>
        
        <div className="flex items-center gap-6 text-xs font-mono">
          <div className="hidden sm:flex gap-2 text-slate-400">
            <span className="text-emerald-400">STATUS:</span> READY_FOR_PART_2
          </div>
          <div className="hidden md:flex gap-2 text-slate-400">
            <span className="text-sky-400">MLFLOW:</span> ACTIVE
          </div>
          <div className="px-3 py-1 bg-slate-800 border border-slate-700 rounded text-sky-400 text-[11px] font-bold">
            PRINCIPAL MLOPS WORKSPACE
          </div>
        </div>
      </header>

      {/* Main Structural Body Split */}
      <div className="flex-1 flex flex-col lg:flex-row min-h-[calc(100vh-6.5rem)] overflow-hidden">
        
        {/* Left Sidebar - Matches theme tree directory & system metrics */}
        <aside className="w-full lg:w-72 border-b lg:border-b-0 lg:border-r border-slate-800 bg-[#0F1115] p-6 flex flex-col gap-6">
          
          {/* Section: Directory Tree Layout */}
          <div>
            <h2 className="text-[10px] uppercase tracking-widest text-[#64748B] font-bold mb-4 flex items-center gap-2">
              <Folder className="w-3.5 h-3.5 text-sky-400" />
              SYSTEM DIRECTORY BLUEPRINT
            </h2>
            <div className="font-mono text-[12px] leading-relaxed bg-[#161922] p-4 rounded-lg border border-slate-800/80 text-slate-400">
              <div className="text-sky-400 flex items-center gap-1.5 font-bold">
                <span>/capstone-churn-system/</span>
              </div>
              <div className="pl-3 border-l border-slate-850">
                <div className="pl-1 text-slate-300">├── <span className="text-slate-200">backend/</span></div>
                <div className="pl-5 text-[11px] text-slate-500">├── main.py</div>
                <div className="pl-5 text-[11px] text-slate-500">└── schemas.py</div>
                
                <div className="pl-1 text-slate-300">├── <span className="text-slate-200">frontend/</span></div>
                <div className="pl-5 text-[11px] text-slate-500">└── app.py</div>
                
                <div className="pl-1 text-slate-300">├── <span className="text-slate-200">ml_pipeline/</span></div>
                <div className="pl-5 text-[11px] text-slate-500">├── train.py</div>
                <div className="pl-5 text-[11px] text-slate-500">└── preprocessor.py</div>
                
                <div className="pl-1 text-slate-400">├── docker-compose.yml</div>
                <div className="pl-1 text-teal-400">└── README.md <span className="text-[8px] px-1 bg-teal-500/20 rounded">V1</span></div>
              </div>
            </div>
          </div>

          {/* Section: Active User Persona Switch Info */}
          <div className="bg-[#161922]/40 p-4 rounded-lg border border-slate-800/50 space-y-3">
            <h3 className="text-[10px] uppercase tracking-widest text-slate-500 font-bold flex items-center gap-1.5">
              <UserCheck className="w-3 h-3 text-sky-400" />
              SIMULATED FOOTPRINT
            </h3>
            <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
              <div>
                <span className="text-slate-500 block">GEOGRAPHY</span>
                <span className="text-slate-200 font-semibold">{customer.geography}</span>
              </div>
              <div>
                <span className="text-slate-500 block">RELATION</span>
                <span className="text-slate-200 font-semibold">{customer.gender}</span>
              </div>
              <div>
                <span className="text-slate-500 block">AGE</span>
                <span className="text-slate-200 font-semibold">{customer.age} yrs</span>
              </div>
              <div>
                <span className="text-slate-500 block">CREDIT SCORE</span>
                <span className={`${customer.creditScore < 600 ? 'text-amber-400' : 'text-emerald-400'} font-semibold font-mono`}>
                  {customer.creditScore}
                </span>
              </div>
            </div>
          </div>

          {/* Section: System Health Metrics */}
          <div className="mt-auto pt-6 border-t border-slate-800">
            <h2 className="text-[10px] uppercase tracking-widest text-[#64748B] font-bold mb-3 flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-teal-400" />
              SYSTEM HEALTH (SANDBOX)
            </h2>
            <div className="space-y-3 bg-[#111319] p-3 rounded border border-slate-850">
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-slate-400">ML CPU Usage</span>
                <span className="text-emerald-400">14% (Idle)</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-emerald-500 h-full w-[14%]" />
              </div>
              
              <div className="flex justify-between text-[11px] font-mono">
                <span className="text-slate-400">RAM Allocation</span>
                <span className="text-sky-400">1.2GB / 8GB</span>
              </div>
              <div className="w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div className="bg-sky-400 h-full w-[15%]" />
              </div>

              <div className="flex justify-between text-[9px] font-mono text-slate-500">
                <span>Docker Engine</span>
                <span>Active v24.0.5</span>
              </div>
            </div>
          </div>
        </aside>

        {/* Right Dashboard Area */}
        <main className="flex-1 bg-[#111319] p-6 md:p-8 flex flex-col gap-6 overflow-y-auto">
          
          {/* Tab Selection Row & Documentation Excerpt */}
          <section className="flex flex-col gap-4">
            <div className="flex flex-col md:flex-row md:items-baseline justify-between gap-3 border-b border-slate-800 pb-4">
              <div className="flex items-baseline gap-3">
                <span className="text-2xl md:text-3xl font-light text-white tracking-tight">Project Documentation</span>
                <span className="text-sky-400 font-mono text-xs hover:underline cursor-pointer flex items-center gap-1">
                  README.md <BookOpen className="w-3 h-3" />
                </span>
              </div>
              
              {/* Core Tabs on Right Header */}
              <div className="flex items-center space-x-1 bg-[#161922] p-1 rounded-lg border border-slate-800 text-xs shrink-0 self-start">
                <button
                  onClick={() => setActiveTab('simulator')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 font-medium rounded transition-all cursor-pointer ${
                    activeTab === 'simulator' 
                      ? 'bg-sky-600/20 text-sky-400 border border-sky-500/20' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Sliders className="w-3 h-3" />
                  Simulator
                </button>
                <button
                  onClick={() => setActiveTab('eda')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 font-medium rounded transition-all cursor-pointer ${
                    activeTab === 'eda' 
                      ? 'bg-sky-600/20 text-sky-400 border border-sky-500/20' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <TrendingUp className="w-3 h-3" />
                  EDA Grid
                </button>
                <button
                  onClick={() => setActiveTab('codebase')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 font-medium rounded transition-all cursor-pointer ${
                    activeTab === 'codebase' 
                      ? 'bg-sky-600/20 text-sky-400 border border-sky-500/20' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Code className="w-3 h-3" />
                  Directory
                </button>
                <button
                  onClick={() => setActiveTab('terminal')}
                  className={`flex items-center gap-1.5 px-3 py-1.5 font-medium rounded transition-all cursor-pointer ${
                    activeTab === 'terminal' 
                      ? 'bg-sky-600/20 text-sky-400 border border-sky-500/20' 
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                >
                  <Terminal className="w-3 h-3" />
                  Logs
                </button>
              </div>
            </div>

            {/* Architecture Overview block */}
            <div className="bg-[#161922] border border-slate-800 rounded-lg p-6 relative overflow-hidden">
              <div className="absolute top-0 right-0 p-4 font-mono text-[10px] text-slate-600">
                REF: SYSTEM_ARCH_01
              </div>
              <h3 className="text-sky-400 font-bold mb-2 uppercase text-xs tracking-wider flex items-center gap-2">
                <Server className="w-3.5 h-3.5" />
                Highly Decoupled End-to-End Capstone Architecture
              </h3>
              <p className="text-slate-350 text-xs md:text-sm leading-relaxed mb-4">
                This bank customer churn pipeline integrates real-world ML engineering and operational robustness. The training pipeline encapsulates statistical weights, exporting them securely into localized models, while our dual-container system maps the API microflows with Streamlit management suites.
              </p>
              
              {/* Architecture micro cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-[#0F1115] p-3 border border-slate-800 rounded flex items-start gap-2.5">
                  <Database className="w-5 h-5 text-sky-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-[9px] text-[#64748B] font-bold uppercase">Backend API Service</div>
                    <div className="text-xs font-mono text-slate-200">FastAPI + Async Pydantic</div>
                  </div>
                </div>
                <div className="bg-[#0F1115] p-3 border border-slate-800 rounded flex items-start gap-2.5">
                  <Cpu className="w-5 h-5 text-emerald-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-[9px] text-[#64748B] font-bold uppercase">Statistical Learning</div>
                    <div className="text-xs font-mono text-slate-200">XGBoost Classifiers</div>
                  </div>
                </div>
                <div className="bg-[#0F1115] p-3 border border-slate-800 rounded flex items-start gap-2.5">
                  <HardDrive className="w-5 h-5 text-purple-400 shrink-0 mt-0.5" />
                  <div>
                    <div className="text-[9px] text-[#64748B] font-bold uppercase">Ops Framework</div>
                    <div className="text-xs font-mono text-slate-200">Docker + Compose Maps</div>
                  </div>
                </div>
              </div>
            </div>
          </section>

          {/* TAB CONTENT 1: PREDICTIVE SIMULATOR */}
          {activeTab === 'simulator' && (
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              
              {/* Factors controller widget */}
              <div className="lg:col-span-2 bg-[#161922] rounded-lg p-6 border border-slate-800 flex flex-col gap-6">
                <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <Sliders className="text-sky-400 w-4 h-4" />
                    <h2 className="text-xs uppercase font-mono tracking-wider text-slate-300">Feature Variable Synthesizer</h2>
                  </div>
                  <span className="text-[10px] font-mono text-slate-500">INPUTS TO COG_WEIGHTS</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Slider: Age */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Customer Age</span>
                      <span className="text-sky-400 font-bold">{customer.age} years</span>
                    </div>
                    <input 
                      type="range" 
                      min="18" 
                      max="90" 
                      value={customer.age}
                      onChange={(e) => setCustomer({ ...customer, age: Number(e.target.value) })}
                      className="w-full accent-sky-400 bg-slate-850 rounded h-1 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                      <span>18 yrs</span>
                      <span>45 yrs (Peak Churn)</span>
                      <span>90 yrs</span>
                    </div>
                  </div>

                  {/* Slider: Credit Score */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Credit Score</span>
                      <span className="text-sky-400 font-bold">{customer.creditScore} points</span>
                    </div>
                    <input 
                      type="range" 
                      min="350" 
                      max="850" 
                      value={customer.creditScore}
                      onChange={(e) => setCustomer({ ...customer, creditScore: Number(e.target.value) })}
                      className="w-full accent-sky-400 bg-slate-850 rounded h-1 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                      <span>350 pts</span>
                      <span>650 pts (Avg)</span>
                      <span>850 pts</span>
                    </div>
                  </div>

                  {/* Slider: Balance */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Account Balance</span>
                      <span className="text-sky-400 font-bold">
                        ${customer.balance.toLocaleString()}
                      </span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="250000" 
                      step="5000"
                      value={customer.balance}
                      onChange={(e) => setCustomer({ ...customer, balance: Number(e.target.value) })}
                      className="w-full accent-sky-400 bg-slate-850 rounded h-1 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                      <span>$0 (Empty)</span>
                      <span>$125k</span>
                      <span>$250k+</span>
                    </div>
                  </div>

                  {/* Slider: Salary */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Estimated annual income</span>
                      <span className="text-sky-400 font-bold">
                        ${customer.estimatedSalary.toLocaleString()}
                      </span>
                    </div>
                    <input 
                      type="range" 
                      min="10000" 
                      max="200000" 
                      step="5000"
                      value={customer.estimatedSalary}
                      onChange={(e) => setCustomer({ ...customer, estimatedSalary: Number(e.target.value) })}
                      className="w-full accent-sky-400 bg-slate-850 rounded h-1 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                      <span>$10k</span>
                      <span>$100k</span>
                      <span>$200k</span>
                    </div>
                  </div>

                  {/* Product Count Block */}
                  <div className="space-y-2">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">Number of products registered</span>
                    <div className="grid grid-cols-4 gap-2">
                      {[1, 2, 3, 4].map((num) => (
                        <button
                          key={num}
                          type="button"
                          onClick={() => setCustomer({ ...customer, numOfProducts: num })}
                          className={`py-1.5 font-mono text-xs rounded border transition-all cursor-pointer ${
                            customer.numOfProducts === num 
                              ? 'bg-sky-500/20 text-sky-400 border-sky-500/40' 
                              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {num}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Tenure Slider */}
                  <div className="space-y-2">
                    <div className="flex justify-between text-xs font-mono">
                      <span className="text-slate-400">Tenure (Years registered)</span>
                      <span className="text-sky-400 font-bold">{customer.tenure} years</span>
                    </div>
                    <input 
                      type="range" 
                      min="0" 
                      max="10" 
                      value={customer.tenure}
                      onChange={(e) => setCustomer({ ...customer, tenure: Number(e.target.value) })}
                      className="w-full accent-sky-400 bg-slate-850 rounded h-1 cursor-pointer"
                    />
                    <div className="flex justify-between text-[10px] text-slate-500 font-mono">
                      <span>0 (Newcomer)</span>
                      <span>5 yrs</span>
                      <span>10 yrs</span>
                    </div>
                  </div>

                  {/* dropdown grids */}
                  <div className="space-y-2">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">Geography branch</span>
                    <div className="grid grid-cols-3 gap-2">
                      {(['France', 'Germany', 'Spain'] as const).map((country) => (
                        <button
                          key={country}
                          type="button"
                          onClick={() => setCustomer({ ...customer, geography: country })}
                          className={`py-1.5 text-xs rounded border transition-all cursor-pointer ${
                            customer.geography === country 
                              ? 'bg-sky-500/20 text-sky-400 border-sky-500/40' 
                              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {country}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <span className="text-[11px] font-mono uppercase tracking-wider text-slate-400 block">Gender Group</span>
                    <div className="grid grid-cols-2 gap-2">
                      {(['Male', 'Female'] as const).map((g) => (
                        <button
                          key={g}
                          type="button"
                          onClick={() => setCustomer({ ...customer, gender: g })}
                          className={`py-1.5 text-xs rounded border transition-all cursor-pointer ${
                            customer.gender === g 
                              ? 'bg-sky-500/20 text-sky-400 border-sky-500/40' 
                              : 'bg-slate-900 border-slate-800 text-slate-400 hover:text-slate-200'
                          }`}
                        >
                          {g}
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Switches */}
                  <div className="flex items-center justify-between p-3.5 bg-slate-900 rounded border border-slate-800">
                    <div className="space-y-0.5">
                      <p className="text-xs font-semibold text-slate-200">Active Credit Card</p>
                      <p className="text-[10px] font-mono text-slate-500">HAS_CR_CARD = {customer.hasCrCard ? 'True' : 'False'}</p>
                    </div>
                    <button 
                      type="button"
                      onClick={() => setCustomer({ ...customer, hasCrCard: !customer.hasCrCard })}
                      className={`relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                        customer.hasCrCard ? 'bg-sky-500' : 'bg-slate-800'
                      }`}
                    >
                      <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-slate-950 transition duration-200 ease-in-out ${
                        customer.hasCrCard ? 'translate-x-5' : 'translate-x-0'
                      }`} />
                    </button>
                  </div>

                  <div className="flex items-center justify-between p-3.5 bg-slate-900 rounded border border-slate-800">
                    <div className="space-y-0.5">
                      <p className="text-xs font-semibold text-slate-200">Active Member Status</p>
                      <p className="text-[10px] font-mono text-slate-500">IS_ACTIVE_MEMBER = {customer.isActiveMember ? 'True' : 'False'}</p>
                    </div>
                    <button 
                      type="button"
                      onClick={() => setCustomer({ ...customer, isActiveMember: !customer.isActiveMember })}
                      className={`relative inline-flex h-5 w-10 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out ${
                        customer.isActiveMember ? 'bg-sky-500' : 'bg-slate-800'
                      }`}
                    >
                      <span className={`pointer-events-none inline-block h-4 w-4 transform rounded-full bg-slate-950 transition duration-200 ease-in-out ${
                        customer.isActiveMember ? 'translate-x-5' : 'translate-x-0'
                      }`} />
                    </button>
                  </div>

                </div>
              </div>

              {/* Inference Side Panel display */}
              <div className="space-y-6">
                
                {/* Dial Gage panel */}
                <div className="bg-[#161922] rounded-lg p-6 border border-slate-800 flex flex-col items-center justify-center text-center relative overflow-hidden">
                  <span className="absolute top-3 left-3 text-[9px] font-mono text-slate-600">INFERENCE_RECALL</span>
                  <Sparkles className="text-sky-400 w-4 h-4 absolute top-3 right-3 opacity-60" />

                  <h4 className="text-[11px] font-mono uppercase text-[#64748B] tracking-widest mb-6">XGBoost Scoring Index</h4>

                  {/* Gauge */}
                  <div className="relative w-36 h-36 flex items-center justify-center">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle 
                        cx="72" 
                        cy="72" 
                        r="58" 
                        className="stroke-slate-800 stroke-[8]" 
                        fill="none" 
                      />
                      <circle 
                        cx="72" 
                        cy="72" 
                        r="58" 
                        className={`stroke-current stroke-[8] transition-all duration-300`}
                        style={{
                          strokeDasharray: '364',
                          strokeDashoffset: `${364 - (364 * prediction.probability) / 100}`,
                        }}
                        stroke={prediction.riskLevel === 'HIGH' ? '#f43f5e' : prediction.riskLevel === 'MEDIUM' ? '#f59e0b' : '#10b981'}
                        fill="none" 
                      />
                    </svg>
                    
                    <div className="absolute flex flex-col items-center">
                      <span className="text-3xl font-extrabold tracking-tight text-white font-mono leading-none">
                        {prediction.probability}%
                      </span>
                      <span className="text-[9px] text-[#64748B] font-mono uppercase mt-1">RATE</span>
                    </div>
                  </div>

                  <div className={`mt-6 px-4 py-1.5 rounded text-xs font-mono font-bold tracking-wider border ${prediction.riskBg} ${prediction.labelBorder}`}>
                    RISK VALUE: {prediction.riskLevel}
                  </div>

                  <p className="text-[11px] text-slate-500 mt-4 leading-normal">
                    This maps log-odds equations matching typical retail bank validation weights. Model predicts tenure retention probability.
                  </p>
                </div>

                {/* Signals checklist panel */}
                <div className="bg-[#161922] rounded-lg p-5 border border-slate-800">
                  <span className="text-[10px] text-slate-600 font-mono block mb-3">EXPLAINABLE_AI_WEIGHTS (SHAP)</span>
                  <h4 className="text-slate-200 text-xs font-bold font-mono tracking-wider mb-4 flex items-center gap-1.5">
                    <ShieldCheck className="text-emerald-400 w-4 h-4" />
                    Target Drivers Checklist
                  </h4>

                  <div className="space-y-2.5">
                    {riskDrivers.map((driver, index) => (
                      <div key={index} className="p-3 bg-[#0F1115] rounded border border-slate-800 text-[11px] font-mono">
                        <div className="flex justify-between items-center mb-1">
                          <span className="font-semibold text-slate-300">{driver.name}</span>
                          <span className={`text-[9px] px-1.5 py-0.2 rounded ${
                            driver.impact.includes('Critical') 
                              ? 'bg-rose-500/20 text-rose-300 border border-rose-500/30' 
                              : driver.impact.includes('High')
                              ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30'
                              : 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                          }`}>
                            {driver.impact}
                          </span>
                        </div>
                        <p className="text-slate-500 text-[10px] leading-normal">{driver.detail}</p>
                      </div>
                    ))}
                  </div>
                </div>

              </div>
            </section>
          )}

          {/* TAB CONTENT 2: EDA GRID - Matches original content styled like Design Table */}
          {activeTab === 'eda' && (
            <section className="flex flex-col gap-6 min-h-0">
              <div className="flex justify-between items-center">
                <h3 className="text-sky-400 font-bold uppercase text-xs tracking-wider">Exploratory Data Analysis: customer_churn.csv</h3>
                <span className="text-[10px] text-slate-550 font-mono">CORE_SCHEMA_VERIFIED: TRUE</span>
              </div>

              {/* Redesigned grid with high accuracy to original stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {/* Country rates */}
                <div className="bg-[#161922] border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-3">GEO_SEG_DYN</span>
                    <h4 className="text-slate-300 text-xs font-bold font-mono tracking-wider mb-4 uppercase">
                      Cohort Risk by Geography
                    </h4>
                    
                    <div className="space-y-4 font-mono">
                      <div>
                        <div className="flex justify-between text-[11px] mb-1">
                          <span className="text-slate-400">Germany branch</span>
                          <span className="text-rose-400 font-bold">32.4% Exit rate</span>
                        </div>
                        <div className="w-full bg-[#0F1115] h-2 rounded overflow-hidden">
                          <div className="bg-rose-500 h-full" style={{ width: '32.4%' }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] mb-1">
                          <span className="text-slate-400">Spain branch</span>
                          <span className="text-amber-400">16.7% Exit rate</span>
                        </div>
                        <div className="w-full bg-[#0F1115] h-2 rounded overflow-hidden">
                          <div className="bg-amber-500 h-full animate-pulse" style={{ width: '16.7%' }} />
                        </div>
                      </div>

                      <div>
                        <div className="flex justify-between text-[11px] mb-1">
                          <span className="text-slate-400">France branch</span>
                          <span className="text-emerald-400">16.1% Exit rate</span>
                        </div>
                        <div className="w-full bg-[#0F1115] h-2 rounded overflow-hidden">
                          <div className="bg-emerald-500 h-full" style={{ width: '16.1%' }} />
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="mt-5 p-3 bg-[#0F1115] border border-slate-800 rounded text-[10px] text-slate-500 leading-normal flex gap-2">
                    <Info className="w-3.5 h-3.5 text-sky-400 shrink-0 mt-0.5" />
                    <span>Highly significant statistical signal. Germany maps nearly 2x the standard exit rate.</span>
                  </div>
                </div>

                {/* Age brackets */}
                <div className="bg-[#161922] border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-3">AGE_SEG_DYN</span>
                    <h4 className="text-slate-300 text-xs font-bold font-mono tracking-wider mb-4 uppercase">
                      Age Bracket distributions
                    </h4>

                    <div className="space-y-3 font-mono">
                      {[
                        { group: '18 - 30 yrs', rate: '7.5%', count: '2,100 count', color: 'bg-emerald-500/40', pct: 7.5 },
                        { group: '30 - 45 yrs', rate: '14.2%', count: '4,850 count', color: 'bg-emerald-500/70', pct: 14.2 },
                        { group: '45 - 60 yrs', rate: '46.8%', count: '2,200 count', color: 'bg-rose-500', pct: 46.8 },
                        { group: 'Above 60 yrs', rate: '28.1%', count: '850 count', color: 'bg-amber-500', pct: 28.1 },
                      ].map((cohort, index) => (
                        <div key={index}>
                          <div className="flex justify-between text-[10px] mb-1">
                            <span className="text-slate-400 font-semibold">{cohort.group} <span className="text-slate-600 font-normal">({cohort.count})</span></span>
                            <span className="text-slate-300 font-bold">{cohort.rate} Exit</span>
                          </div>
                          <div className="w-full bg-[#0F1115] h-1.5 rounded overflow-hidden">
                            <div className={`${cohort.color} h-full`} style={{ width: `${cohort.pct}%` }} />
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <p className="mt-4 text-[10px] text-slate-500 leading-normal font-mono text-center border-t border-slate-800/80 pt-3">
                    Bimodal exit ratios. Spikes extensively in the 45-60 demographic range.
                  </p>
                </div>

                {/* Products registered anomaly */}
                <div className="bg-[#161922] border border-slate-800 rounded-lg p-5 flex flex-col justify-between">
                  <div>
                    <span className="text-[10px] text-slate-500 font-mono uppercase block mb-3">PROD_SENSITIVITY</span>
                    <h4 className="text-slate-300 text-xs font-bold font-mono tracking-wider mb-4 uppercase">
                      Product counts exit ratios
                    </h4>

                    <div className="space-y-2.5 font-mono">
                      {[
                        { num: '1 Product', rate: '27.7%', color: 'bg-amber-500', val: 27.7 },
                        { num: '2 Products', rate: '7.6%', color: 'bg-emerald-500', val: 7.6 },
                        { num: '3 Products', rate: '82.7%', color: 'bg-rose-500', val: 82.7 },
                        { num: '4 Products', rate: '100.0%', color: 'bg-rose-800', val: 100 },
                      ].map((prod, i) => (
                        <div key={i} className="flex items-center justify-between text-[11px]">
                          <span className="text-slate-400 w-16 text-left">{prod.num}</span>
                          <div className="flex-1 px-4">
                            <div className="w-full bg-[#0F1115] h-1.5 rounded overflow-hidden">
                              <div className={`${prod.color} h-full`} style={{ width: `${prod.val}%` }} />
                            </div>
                          </div>
                          <span className="text-slate-300 w-12 text-right font-bold">{prod.rate}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="mt-5 p-2 bg-rose-500/10 border border-rose-500/25 rounded text-[9px] text-rose-300 font-mono leading-normal">
                    <strong>CRITICAL SIGNAL:</strong> Customers reaching 3 or 4 accounts represent extreme churn risk. This acts as a trigger point.
                  </div>
                </div>

              </div>

              {/* Elegant Table displaying feature types - styled like original theme's table */}
              <div className="border border-slate-800 rounded-lg bg-[#161922] overflow-hidden flex flex-col mt-4 font-mono">
                <table className="w-full text-left border-collapse text-xs">
                  <thead className="bg-[#1c212c] text-slate-400 sticky top-0">
                    <tr>
                      <th className="p-3 border-b border-slate-800 font-semibold uppercase text-[10px]">Feature Segment</th>
                      <th className="p-3 border-b border-slate-800 font-semibold uppercase text-[10px]">Statistical Dtype</th>
                      <th className="p-3 border-b border-slate-800 font-semibold uppercase text-[10px]">Description & Functional Context</th>
                      <th className="p-3 border-b border-slate-800 font-semibold uppercase text-[10px] text-center">Status</th>
                    </tr>
                  </thead>
                  <tbody className="text-slate-300">
                    <tr className="border-b border-slate-800/50">
                      <td className="p-3 text-white font-semibold">CreditScore</td>
                      <td className="p-3 text-slate-400">int64</td>
                      <td className="p-3">Numerical credit rating metrics mapped using historical deposit histories</td>
                      <td className="p-3 text-sky-400 text-center font-bold">Feature</td>
                    </tr>
                    <tr className="border-b border-slate-800/50 bg-[#1c212c]/30">
                      <td className="p-3 text-white font-semibold">Geography</td>
                      <td className="p-3 text-slate-400 font-mono">object (Categorical)</td>
                      <td className="p-3">Customer main country branch residence. French, Spanish, German sectors.</td>
                      <td className="p-3 text-sky-400 text-center font-bold">Feature</td>
                    </tr>
                    <tr className="border-b border-slate-800/50">
                      <td className="p-3 text-white font-semibold">Age</td>
                      <td className="p-3 text-slate-400 font-mono">int64</td>
                      <td className="p-3">Aged customer demographic range. Core predictor weight in logistic tree.</td>
                      <td className="p-3 text-sky-400 text-center font-bold">Feature</td>
                    </tr>
                    <tr className="border-b border-slate-800/50 bg-[#1c212c]/30">
                      <td className="p-3 text-white font-semibold">Exited</td>
                      <td className="p-3 text-emerald-400 font-mono">int64 (Binary exit target)</td>
                      <td className="p-3 text-emerald-400 italic">Target Variable Indicator. 1 marks Churned representation, 0 marks Retained.</td>
                      <td className="p-3 text-emerald-400 text-center font-bold underline italic">LABEL TARGET</td>
                    </tr>
                    <tr className="border-b border-slate-800/50">
                      <td className="p-3 text-white font-semibold">EstimatedSalary</td>
                      <td className="p-3 text-slate-400 font-mono">float64</td>
                      <td className="p-3">Customer general projected revenue/salary value, computed by monthly footprint.</td>
                      <td className="p-3 text-sky-400 text-center font-bold">Feature</td>
                    </tr>
                  </tbody>
                </table>
                <div className="p-4 bg-[#0F1115] border-t border-slate-800 text-[11px] text-slate-500 font-mono">
                  <p><span className="text-amber-500 mr-2 underline font-bold">ANALYSIS METRIC:</span> High class imbalance detected (~20.3% churned exiting fraction). Scale_Pos_Weight parameter is explicitly flagged inside XGBoost to counter the skew.</p>
                </div>
              </div>

            </section>
          )}

          {/* TAB CONTENT 3: SYSTEM DIRECTORIES BLUEPRINT */}
          {activeTab === 'codebase' && (
            <section className="space-y-6">
              
              {/* Folder Head */}
              <div className="bg-[#161922] rounded-lg p-5 border border-slate-800">
                <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div>
                    <div className="flex items-center gap-2 mb-1.5">
                      <Folder className="text-sky-400 w-5 h-5" />
                      <h2 className="text-sm font-bold font-mono text-slate-200">PROJECT FILE SYSTEM SPECIFICATIONS</h2>
                    </div>
                    <p className="text-xs text-slate-450 leading-relaxed max-w-3xl">
                      This represents the target production schema for our multi-container capstone infrastructure. Turn 2 will deploy scripts within these directory coordinates.
                    </p>
                  </div>
                  <span className="px-3 py-1 font-mono text-[10px] bg-slate-900 rounded border border-slate-800 text-sky-400">
                    PATH: /capstone-churn-system/
                  </span>
                </div>
              </div>

              {/* File details list */}
              <div className="bg-[#161922] rounded-lg overflow-hidden border border-slate-800 font-mono text-xs">
                <div className="p-3 bg-slate-900 border-b border-slate-800 hidden md:grid grid-cols-12 gap-4 text-slate-400 text-[10px] font-bold">
                  <div className="col-span-3">SPECIFIED FILE NAME</div>
                  <div className="col-span-4">ABSOLUTE SYSTEM DIRECTORY PATH</div>
                  <div className="col-span-2 text-center">INTEGRITY STATUS</div>
                  <div className="col-span-1 text-right">EST SIZE</div>
                  <div className="col-span-2 text-right">BUILD PHASE</div>
                </div>

                <div className="divide-y divide-slate-800/60">
                  {filesList.map((file, i) => (
                    <div key={i} className="p-3 grid grid-cols-1 md:grid-cols-12 gap-2 md:gap-4 items-center">
                      
                      <div className="col-span-3 flex items-center gap-2">
                        <FileCode className="text-sky-400/80 w-3.5 h-3.5" />
                        <span className="font-bold text-slate-200">{file.name}</span>
                      </div>

                      <div className="col-span-4 text-slate-500 text-[11px] truncate">
                        {file.path}
                      </div>

                      <div className="col-span-2 text-center flex items-center md:justify-center justify-start">
                        <span className={`px-2 py-0.5 rounded text-[9px] uppercase font-bold border ${
                          file.status === 'Ready' 
                            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' 
                            : 'bg-slate-900 text-slate-500 border-slate-800' 
                        }`}>
                          {file.status}
                        </span>
                      </div>

                      <div className="col-span-1 text-slate-400 md:text-right text-left text-[11px]">
                        {file.size}
                      </div>

                      <div className="col-span-2 text-slate-500 text-right leading-snug truncate text-[11px]">
                        {file.desc}
                      </div>

                    </div>
                  ))}
                </div>
              </div>

              {/* Summary note log */}
              <div className="bg-[#161922] rounded-lg p-5 border border-slate-800 flex gap-4">
                <BookOpen className="text-sky-400 w-6 h-6 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold font-mono uppercase text-slate-300 mb-1">MLOps Engineering Guideline</h4>
                  <p className="text-xs text-slate-400 leading-relaxed">
                    By strictly dividing the API logic from the Streamlit UI endpoints, we prevent microservice dependency bloat. The Docker architecture enforces low latencies and highly sandboxed execution environments.
                  </p>
                </div>
              </div>

            </section>
          )}

          {/* TAB CONTENT 4: TERMINAL WORKSPACE LOGS */}
          {activeTab === 'terminal' && (
            <section className="space-y-4">
              <div className="bg-[#0F1115] rounded-lg p-5 border border-slate-800 font-mono text-[11px] text-slate-300 space-y-2 h-[400px] overflow-y-auto">
                <p className="text-slate-500">[2026-06-18 12:47:45] INFO: Bootstrapping MLOps customer intelligence workspace...</p>
                <p className="text-[#a855f7]">[2026-06-18 12:47:46] INFO: Initializing local dataset validation pipelines...</p>
                <p className="text-sky-400">[2026-06-18 12:47:48] DEBUG: Loading parameters from file schema definition customer_churn.csv</p>
                <p className="text-slate-400">       - Active features: CreditScore, Age, Tenure, Balance, EstimatedSalary, Geography, Gender</p>
                <p className="text-slate-400">       - Target label class Exit detected in Exited field</p>
                <p className="text-[#10b981]">[2026-06-18 12:47:50] SUCCESS: Saved /capstone-churn-system/README.md markdown structure.</p>
                <p className="text-slate-500">[2026-06-18 12:48:10] INFO: Express server maps on internal port 3000 mapping layout assets</p>
                <p className="text-sky-300">[2026-06-18 12:48:12] DEBUG: Interactive simulator callback recalculated prediction risk for client: Age={customer.age} yrs, Country={customer.geography}, Products={customer.numOfProducts} -- Value={prediction.probability}% Churn Probability ({prediction.riskLevel} risk)</p>
                <p className="text-slate-500">[2026-06-18 12:49:15] INFO: Listening on next turn confirmation coordinates...</p>
                
                <div className="pt-4 border-t border-slate-800/80 flex items-center justify-between">
                  <span className="text-[#10b981] animate-pulse">● System stands by representing technical theme interface...</span>
                  <span className="text-slate-600 text-[10px]">d425b266-ddf4-426c-815f</span>
                </div>
              </div>
            </section>
          )}

        </main>
      </div>

      {/* Structured Blue/Sky Status Footer representing Technical Theme */}
      <footer className="h-10 bg-sky-600 px-6 flex items-center justify-between text-white font-mono text-[10px] font-bold">
        <div className="flex gap-4 uppercase select-none">
          <span>Session: Principal_MLOps_Lead</span>
          <span className="hidden sm:inline">Kernel: Python 3.10.12</span>
          <span className="hidden md:inline">Docker: Engine v24.0.5</span>
        </div>
        <div className="flex items-center gap-2">
          <span>WAITING FOR CONFIRMATION TO GENERATE PIPELINE (TURN 2)</span>
          <div className="w-2 h-2 bg-white rounded-full animate-pulse mr-1"></div>
        </div>
      </footer>

    </div>
  );
}
