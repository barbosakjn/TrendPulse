'use client';

import { useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import Header from '@/components/layout/Header';
import { useAuthStore } from '@/stores/authStore';
import { initializeAuth } from '@/lib/auth';
import { TrendingUp, Users, BarChart3, Activity } from 'lucide-react';

export default function DashboardPage() {
  const { user } = useAuthStore();

  useEffect(() => {
    initializeAuth();
  }, []);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-slate-950">
        <Header />
        
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="mb-8">
            <h1 className="text-4xl font-bold text-white mb-2">
              Welcome back, {user?.name || 'User'}!
            </h1>
            <p className="text-slate-400">
              Here is your TrendPulse dashboard
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-indigo-500/10 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-indigo-400" />
                </div>
                <span className="text-2xl font-bold text-white">12</span>
              </div>
              <h3 className="text-sm font-medium text-slate-400">Active Trends</h3>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-green-500/10 rounded-lg">
                  <Users className="w-6 h-6 text-green-400" />
                </div>
                <span className="text-2xl font-bold text-white">1.2K</span>
              </div>
              <h3 className="text-sm font-medium text-slate-400">Followers</h3>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-purple-500/10 rounded-lg">
                  <BarChart3 className="w-6 h-6 text-purple-400" />
                </div>
                <span className="text-2xl font-bold text-white">87%</span>
              </div>
              <h3 className="text-sm font-medium text-slate-400">Engagement</h3>
            </div>

            <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-orange-500/10 rounded-lg">
                  <Activity className="w-6 h-6 text-orange-400" />
                </div>
                <span className="text-2xl font-bold text-white">24</span>
              </div>
              <h3 className="text-sm font-medium text-slate-400">Active Reports</h3>
            </div>
          </div>

          <div className="bg-slate-900/50 backdrop-blur-xl rounded-xl border border-slate-800 p-8">
            <h2 className="text-2xl font-bold text-white mb-4">Recent Activity</h2>
            <div className="space-y-4">
              <div className="flex items-center space-x-4 p-4 bg-slate-800/50 rounded-lg">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-white font-medium">New trend detected</p>
                  <p className="text-sm text-slate-400">AI technology trends are rising</p>
                </div>
                <span className="text-sm text-slate-500">2 hours ago</span>
              </div>
              <div className="flex items-center space-x-4 p-4 bg-slate-800/50 rounded-lg">
                <div className="w-2 h-2 bg-blue-400 rounded-full"></div>
                <div className="flex-1">
                  <p className="text-white font-medium">Report generated</p>
                  <p className="text-sm text-slate-400">Weekly trends analysis completed</p>
                </div>
                <span className="text-sm text-slate-500">5 hours ago</span>
              </div>
            </div>
          </div>
        </main>
      </div>
    </ProtectedRoute>
  );
}
