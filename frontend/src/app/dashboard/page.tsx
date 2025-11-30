'use client';

import { useEffect, useState } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import Header from '@/components/layout/Header';
import { useAuthStore } from '@/stores/authStore';
import { initializeAuth } from '@/lib/auth';
import { 
  TrendingUp, 
  Users, 
  BarChart3, 
  Activity,
  Sparkles,
  ArrowUpRight,
  ArrowDownRight,
  Search,
  Bell,
  Zap,
  Globe,
  Youtube,
  MessageSquare,
  ChevronRight,
  Clock,
  Target,
  Flame
} from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const [greeting, setGreeting] = useState('');

  useEffect(() => {
    initializeAuth();
    const hour = new Date().getHours();
    if (hour < 12) setGreeting('Good morning');
    else if (hour < 18) setGreeting('Good afternoon');
    else setGreeting('Good evening');
  }, []);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950">
        <Header />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="mb-10">
            <div className="flex items-center gap-3 mb-2">
              <div className="p-2 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-lg">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <span className="text-indigo-400 font-medium text-sm uppercase tracking-wider">Dashboard</span>
            </div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-white via-slate-200 to-slate-400 bg-clip-text text-transparent mb-3">
              {greeting}, {user?.name?.split(' ')[0] || 'there'}!
            </h1>
            <p className="text-slate-400 text-lg">
              Discover what's trending in your niche today
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5 mb-8">
            <div className="group relative overflow-hidden bg-gradient-to-br from-indigo-600/20 to-indigo-900/20 backdrop-blur-xl rounded-2xl border border-indigo-500/20 p-6 hover:border-indigo-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-indigo-500/10 hover:-translate-y-1">
              <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-500/10 rounded-full blur-3xl group-hover:bg-indigo-500/20 transition-all"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-indigo-500/20 rounded-xl">
                    <TrendingUp className="w-6 h-6 text-indigo-400" />
                  </div>
                  <div className="flex items-center gap-1 text-emerald-400 text-sm font-medium bg-emerald-500/10 px-2 py-1 rounded-full">
                    <ArrowUpRight className="w-3 h-3" />
                    <span>+23%</span>
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">12</span>
                <h3 className="text-sm font-medium text-slate-400">Active Trends</h3>
              </div>
            </div>

            <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-600/20 to-emerald-900/20 backdrop-blur-xl rounded-2xl border border-emerald-500/20 p-6 hover:border-emerald-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-emerald-500/10 hover:-translate-y-1">
              <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 rounded-full blur-3xl group-hover:bg-emerald-500/20 transition-all"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-emerald-500/20 rounded-xl">
                    <Target className="w-6 h-6 text-emerald-400" />
                  </div>
                  <div className="flex items-center gap-1 text-emerald-400 text-sm font-medium bg-emerald-500/10 px-2 py-1 rounded-full">
                    <ArrowUpRight className="w-3 h-3" />
                    <span>+12%</span>
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">847</span>
                <h3 className="text-sm font-medium text-slate-400">Opportunities Found</h3>
              </div>
            </div>

            <div className="group relative overflow-hidden bg-gradient-to-br from-purple-600/20 to-purple-900/20 backdrop-blur-xl rounded-2xl border border-purple-500/20 p-6 hover:border-purple-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/10 hover:-translate-y-1">
              <div className="absolute top-0 right-0 w-32 h-32 bg-purple-500/10 rounded-full blur-3xl group-hover:bg-purple-500/20 transition-all"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-purple-500/20 rounded-xl">
                    <BarChart3 className="w-6 h-6 text-purple-400" />
                  </div>
                  <div className="flex items-center gap-1 text-emerald-400 text-sm font-medium bg-emerald-500/10 px-2 py-1 rounded-full">
                    <ArrowUpRight className="w-3 h-3" />
                    <span>+5%</span>
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">87%</span>
                <h3 className="text-sm font-medium text-slate-400">Accuracy Rate</h3>
              </div>
            </div>

            <div className="group relative overflow-hidden bg-gradient-to-br from-orange-600/20 to-orange-900/20 backdrop-blur-xl rounded-2xl border border-orange-500/20 p-6 hover:border-orange-500/40 transition-all duration-300 hover:shadow-lg hover:shadow-orange-500/10 hover:-translate-y-1">
              <div className="absolute top-0 right-0 w-32 h-32 bg-orange-500/10 rounded-full blur-3xl group-hover:bg-orange-500/20 transition-all"></div>
              <div className="relative">
                <div className="flex items-center justify-between mb-4">
                  <div className="p-3 bg-orange-500/20 rounded-xl">
                    <Flame className="w-6 h-6 text-orange-400" />
                  </div>
                  <div className="flex items-center gap-1 text-orange-400 text-sm font-medium bg-orange-500/10 px-2 py-1 rounded-full">
                    <Zap className="w-3 h-3" />
                    <span>Hot</span>
                  </div>
                </div>
                <span className="text-3xl font-bold text-white block mb-1">5</span>
                <h3 className="text-sm font-medium text-slate-400">Trending Now</h3>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="lg:col-span-2 bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6">
              <div className="flex items-center justify-between mb-6">
                <div>
                  <h2 className="text-xl font-bold text-white mb-1">Top Trending Topics</h2>
                  <p className="text-slate-500 text-sm">Based on your niche preferences</p>
                </div>
                <button className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 text-sm font-medium transition-colors">
                  View all <ChevronRight className="w-4 h-4" />
                </button>
              </div>
              
              <div className="space-y-4">
                <div className="group flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all cursor-pointer border border-transparent hover:border-slate-700/50">
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-red-500 to-pink-500 rounded-xl">
                    <Youtube className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white group-hover:text-indigo-300 transition-colors">AI Video Editing Tools</h3>
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">+340%</span>
                    </div>
                    <p className="text-sm text-slate-400">Trending on YouTube • 2.4M searches</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">92</div>
                    <div className="text-xs text-slate-500">Score</div>
                  </div>
                </div>

                <div className="group flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all cursor-pointer border border-transparent hover:border-slate-700/50">
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl">
                    <Globe className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white group-hover:text-indigo-300 transition-colors">No-Code SaaS Builders</h3>
                      <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-xs rounded-full">+180%</span>
                    </div>
                    <p className="text-sm text-slate-400">Trending on Google • 890K searches</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">87</div>
                    <div className="text-xs text-slate-500">Score</div>
                  </div>
                </div>

                <div className="group flex items-center gap-4 p-4 bg-slate-800/30 hover:bg-slate-800/50 rounded-xl transition-all cursor-pointer border border-transparent hover:border-slate-700/50">
                  <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-orange-500 to-amber-500 rounded-xl">
                    <MessageSquare className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold text-white group-hover:text-indigo-300 transition-colors">Voice AI Agents</h3>
                      <span className="px-2 py-0.5 bg-orange-500/20 text-orange-400 text-xs rounded-full">New</span>
                    </div>
                    <p className="text-sm text-slate-400">Trending on Reddit • 45K mentions</p>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold text-white">78</div>
                    <div className="text-xs text-slate-500">Score</div>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-white">Quick Actions</h2>
              </div>
              
              <div className="space-y-3">
                <button className="w-full flex items-center gap-3 p-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-500 hover:to-purple-500 rounded-xl transition-all group">
                  <Search className="w-5 h-5 text-white" />
                  <span className="font-medium text-white">Discover New Trends</span>
                  <ArrowUpRight className="w-4 h-4 text-white/70 ml-auto group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </button>
                
                <button className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group">
                  <BarChart3 className="w-5 h-5 text-slate-400" />
                  <span className="font-medium text-slate-300">Generate Report</span>
                  <ArrowUpRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </button>
                
                <button className="w-full flex items-center gap-3 p-4 bg-slate-800/50 hover:bg-slate-800 rounded-xl transition-all border border-slate-700/50 group">
                  <Bell className="w-5 h-5 text-slate-400" />
                  <span className="font-medium text-slate-300">Set Alert</span>
                  <ArrowUpRight className="w-4 h-4 text-slate-500 ml-auto group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                </button>
              </div>

              <div className="mt-6 p-4 bg-gradient-to-r from-indigo-900/30 to-purple-900/30 rounded-xl border border-indigo-500/20">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-indigo-500/20 rounded-lg">
                    <Zap className="w-4 h-4 text-indigo-400" />
                  </div>
                  <span className="font-semibold text-white text-sm">Pro Tip</span>
                </div>
                <p className="text-slate-400 text-sm leading-relaxed">
                  Set up alerts for your niche keywords to get notified when new trends emerge.
                </p>
              </div>
            </div>
          </div>

          <div className="bg-slate-900/50 backdrop-blur-xl rounded-2xl border border-slate-800/50 p-6">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-bold text-white mb-1">Recent Activity</h2>
                <p className="text-slate-500 text-sm">Your latest updates and discoveries</p>
              </div>
              <div className="flex items-center gap-2 text-slate-400 text-sm">
                <Clock className="w-4 h-4" />
                <span>Last 24 hours</span>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center gap-4 p-4 bg-slate-800/30 rounded-xl hover:bg-slate-800/50 transition-all">
                <div className="w-2 h-2 bg-emerald-400 rounded-full animate-pulse"></div>
                <div className="p-2 bg-emerald-500/10 rounded-lg">
                  <TrendingUp className="w-4 h-4 text-emerald-400" />
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium">New trend detected</p>
                  <p className="text-sm text-slate-400">AI technology trends are rising rapidly</p>
                </div>
                <span className="text-sm text-slate-500 bg-slate-800 px-3 py-1 rounded-full">2h ago</span>
              </div>
              
              <div className="flex items-center gap-4 p-4 bg-slate-800/30 rounded-xl hover:bg-slate-800/50 transition-all">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <div className="p-2 bg-blue-500/10 rounded-lg">
                  <BarChart3 className="w-4 h-4 text-blue-400" />
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium">Weekly report ready</p>
                  <p className="text-sm text-slate-400">Your trends analysis is complete</p>
                </div>
                <span className="text-sm text-slate-500 bg-slate-800 px-3 py-1 rounded-full">5h ago</span>
              </div>
              
              <div className="flex items-center gap-4 p-4 bg-slate-800/30 rounded-xl hover:bg-slate-800/50 transition-all">
                <div className="w-2 h-2 bg-purple-400 rounded-full"></div>
                <div className="p-2 bg-purple-500/10 rounded-lg">
                  <Bell className="w-4 h-4 text-purple-400" />
                </div>
                <div className="flex-1">
                  <p className="text-white font-medium">Alert triggered</p>
                  <p className="text-sm text-slate-400">"SaaS tools" keyword reached 100K searches</p>
                </div>
                <span className="text-sm text-slate-500 bg-slate-800 px-3 py-1 rounded-full">1d ago</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
