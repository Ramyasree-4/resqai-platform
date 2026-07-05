import { Link } from 'react-router-dom'
import { Shield, Zap, Map, Brain, Wifi, Globe, ArrowRight, ChevronRight, Activity } from 'lucide-react'

const stats = [
  { value: '1.4B+', label: 'Citizens Protected' },
  { value: '83%', label: 'Faster Response' },
  { value: '5 sec', label: 'AI Triage Time' },
  { value: '750+', label: 'Districts Ready' },
]

const features = [
  { icon: Brain, title: 'Gemini AI Triage', desc: 'Google Gemini 1.5 Pro classifies incidents, scores severity 1–10 and recommends exact rescue resources in under 5 seconds.', color: 'text-purple-600', bg: 'bg-purple-50 dark:bg-purple-900/20' },
  { icon: Map, title: 'Real-time Operations Map', desc: 'Live incident markers, resource tracking, severity heatmap, and route overlay — all on a single Google Maps dashboard.', color: 'text-blue-600', bg: 'bg-blue-50 dark:bg-blue-900/20' },
  { icon: Zap, title: 'Explainable AI', desc: 'Every AI recommendation includes plain-language reasoning so authorities understand why — not just what — the AI decided.', color: 'text-yellow-600', bg: 'bg-yellow-50 dark:bg-yellow-900/20' },
  { icon: Shield, title: 'Multi-Agency Coordination', desc: 'NDRF, SDRF, Police, Fire, NGO — all coordinated through a single unified platform with role-based dashboards.', color: 'text-green-600', bg: 'bg-green-50 dark:bg-green-900/20' },
  { icon: Wifi, title: 'Offline PWA', desc: 'Submit reports even without internet. Service worker caches the UI. Reports sync automatically when connectivity returns.', color: 'text-indigo-600', bg: 'bg-indigo-50 dark:bg-indigo-900/20' },
  { icon: Globe, title: 'Multilingual Support', desc: 'Available in English and Hindi. Regional language AI analysis coming in Phase 2 for all major Indian languages.', color: 'text-orange-600', bg: 'bg-orange-50 dark:bg-orange-900/20' },
]

const steps = [
  { num: '01', title: 'Citizen Reports', desc: 'Submit emergency with GPS location, photos, and description from any device — even low-bandwidth mobile.' },
  { num: '02', title: 'AI Analyzes', desc: 'Gemini AI classifies disaster type, scores severity, identifies risks, and recommends exact resources needed.' },
  { num: '03', title: 'Rescue Dispatched', desc: 'Nearest available resources assigned automatically. Citizen receives live tracking of the response team.' },
]

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white dark:bg-gray-950 text-gray-900 dark:text-white">
      {/* Navbar */}
      <nav className="sticky top-0 z-40 border-b border-gray-200/80 dark:border-gray-800 bg-white/90 dark:bg-gray-950/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6">
          <Link to="/" className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-600">
              <Shield className="h-4 w-4 text-white" />
            </div>
            <span className="text-lg font-bold">ResQAI</span>
          </Link>
          <div className="hidden items-center gap-6 text-sm font-medium text-gray-600 dark:text-gray-400 md:flex">
            <a href="#features" className="hover:text-blue-600 transition-colors">Features</a>
            <a href="#how" className="hover:text-blue-600 transition-colors">How It Works</a>
            <a href="#impact" className="hover:text-blue-600 transition-colors">Impact</a>
          </div>
          <div className="flex items-center gap-3">
            <Link to="/login" className="rounded-lg px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors">
              Sign In
            </Link>
            <Link to="/register" className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700 transition-colors">
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="relative overflow-hidden bg-gradient-to-br from-slate-900 via-blue-950 to-slate-900">
        <div className="absolute inset-0 opacity-20" style={{
          backgroundImage: 'radial-gradient(circle at 25% 50%, #3B82F6 0%, transparent 50%), radial-gradient(circle at 75% 20%, #8B5CF6 0%, transparent 50%)'
        }} />
        <div className="relative mx-auto max-w-7xl px-4 py-24 sm:px-6 sm:py-32 text-center">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-500/30 bg-blue-500/10 px-4 py-1.5 text-sm text-blue-300 mb-8">
            <Activity className="h-3.5 w-3.5 animate-pulse" />
            Powered by Google Gemini AI
          </div>
          <h1 className="text-4xl font-black tracking-tight text-white sm:text-6xl lg:text-7xl">
            AI-Powered<br />
            <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              Disaster Response
            </span>
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-lg text-gray-300 leading-relaxed">
            ResQAI transforms emergency chaos into coordinated action. Every report is analyzed by Google Gemini AI in under 5 seconds — severity scored, resources recommended, rescue dispatched.
          </p>
          <div className="mt-10 flex flex-wrap items-center justify-center gap-4">
            <Link
              to="/register"
              className="flex items-center gap-2 rounded-xl bg-red-600 hover:bg-red-700 px-8 py-3.5 text-base font-bold text-white transition-all shadow-lg hover:shadow-red-500/25"
            >
              🆘 Report Emergency
            </Link>
            <Link
              to="/login"
              className="flex items-center gap-2 rounded-xl border border-white/20 bg-white/10 hover:bg-white/20 px-8 py-3.5 text-base font-semibold text-white transition-all backdrop-blur-sm"
            >
              Authority Login <ArrowRight className="h-4 w-4" />
            </Link>
          </div>

          {/* Live stats ticker */}
          <div className="mt-14 flex flex-wrap items-center justify-center gap-6 sm:gap-12">
            {[
              { dot: 'bg-red-500', label: '47 Active Incidents' },
              { dot: 'bg-green-500', label: '23 Resolved Today' },
              { dot: 'bg-blue-500', label: '15 Units Deployed' },
              { dot: 'bg-purple-500', label: '99.9% Uptime' },
            ].map((item, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-gray-300">
                <span className={`h-2 w-2 rounded-full ${item.dot} animate-pulse`} />
                {item.label}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats */}
      <section id="impact" className="border-y border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900/50">
        <div className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
          <div className="grid grid-cols-2 gap-8 sm:grid-cols-4">
            {stats.map((s, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl font-black text-blue-600 dark:text-blue-400">{s.value}</div>
                <div className="mt-1 text-sm font-medium text-gray-600 dark:text-gray-400">{s.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="mx-auto max-w-7xl px-4 py-24 sm:px-6">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">
            Built for <span className="text-blue-600">National-Scale</span> Emergencies
          </h2>
          <p className="mt-3 text-gray-500 dark:text-gray-400 max-w-xl mx-auto">
            Every feature designed for the realities of disaster response in India — low bandwidth, high pressure, multi-agency coordination.
          </p>
        </div>
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {features.map((f, i) => (
            <div key={i} className="group rounded-2xl border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-6 hover:shadow-lg hover:border-blue-200 dark:hover:border-blue-700 transition-all duration-300">
              <div className={`inline-flex h-12 w-12 items-center justify-center rounded-xl ${f.bg} mb-4`}>
                <f.icon className={`h-6 w-6 ${f.color}`} />
              </div>
              <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">{f.title}</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* How It Works */}
      <section id="how" className="bg-gray-50 dark:bg-gray-900/50 py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white sm:text-4xl">How ResQAI Works</h2>
          </div>
          <div className="grid gap-8 sm:grid-cols-3">
            {steps.map((step, i) => (
              <div key={i} className="relative text-center">
                {i < steps.length - 1 && (
                  <div className="absolute top-8 left-[calc(50%+2.5rem)] hidden w-[calc(100%-5rem)] border-t-2 border-dashed border-blue-200 dark:border-blue-800 sm:block" />
                )}
                <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white text-xl font-black shadow-lg shadow-blue-500/25 mb-4">
                  {step.num}
                </div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">{step.title}</h3>
                <p className="text-sm text-gray-600 dark:text-gray-400 max-w-xs mx-auto leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="mx-auto max-w-7xl px-4 py-16 sm:px-6">
        <p className="text-center text-sm font-semibold uppercase tracking-widest text-gray-400 dark:text-gray-500 mb-8">Built on Google Cloud</p>
        <div className="flex flex-wrap items-center justify-center gap-8 grayscale opacity-60 hover:grayscale-0 hover:opacity-100 transition-all duration-500">
          {['Google Cloud', 'Gemini AI', 'Firebase', 'Google Maps', 'Cloud Run', 'Firestore'].map((tech) => (
            <div key={tech} className="flex items-center gap-2 rounded-xl border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 px-4 py-2.5">
              <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">{tech}</span>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gradient-to-r from-blue-600 to-blue-800 py-16">
        <div className="mx-auto max-w-4xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold text-white">Ready to Transform Disaster Response?</h2>
          <p className="mt-3 text-blue-100 max-w-xl mx-auto">Join authorities across India using AI to save lives faster.</p>
          <div className="mt-8 flex flex-wrap gap-4 justify-center">
            <Link to="/register" className="rounded-xl bg-white text-blue-700 font-bold px-8 py-3 hover:bg-blue-50 transition-colors">
              Create Account
            </Link>
            <Link to="/login" className="rounded-xl border-2 border-white/40 text-white font-semibold px-8 py-3 hover:border-white hover:bg-white/10 transition-colors">
              Authority Login
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-gray-200 dark:border-gray-800 py-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="flex h-7 w-7 items-center justify-center rounded-lg bg-blue-600">
              <Shield className="h-3.5 w-3.5 text-white" />
            </div>
            <span className="font-bold text-gray-900 dark:text-white">ResQAI</span>
            <span className="text-sm text-gray-400">© 2024</span>
          </div>
          <div className="flex gap-6 text-sm text-gray-500 dark:text-gray-400">
            <a href="#" className="hover:text-blue-600 transition-colors">Privacy</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Terms</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
