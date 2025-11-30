'use client';

import LoginForm from '@/components/auth/LoginForm';
import { TrendingUp } from 'lucide-react';
import Link from 'next/link';

export default function LoginPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <Link href="/" className="inline-flex items-center space-x-2 mb-6">
            <TrendingUp className="w-10 h-10 text-indigo-500" />
            <span className="text-3xl font-bold text-white">TrendPulse</span>
          </Link>
        </div>
        <LoginForm />
      </div>
    </div>
  );
}
