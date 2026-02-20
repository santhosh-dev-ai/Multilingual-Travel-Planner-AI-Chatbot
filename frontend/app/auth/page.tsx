'use client';

import { FormEvent, useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { authAPI } from '../services/api';
import { SparklesIcon } from '@heroicons/react/24/outline';

type AuthMode = 'login' | 'register';

export default function AuthPage() {
  const router = useRouter();
  const [mode, setMode] = useState<AuthMode>('login');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const [loginData, setLoginData] = useState({
    username: '',
    password: '',
  });

  const [registerData, setRegisterData] = useState({
    username: '',
    password: '',
    email: '',
    phone_number: '',
  });

  useEffect(() => {
    if (authAPI.isAuthenticated()) {
      router.replace('/');
    }
  }, [router]);

  const switchMode = (next: AuthMode) => {
    setMode(next);
    setError('');
    setSuccess('');
  };

  const handleLogin = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      await authAPI.login(loginData);
      router.push('/');
    } catch (err: any) {
      setError(err.message || 'Login failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRegister = async (event: FormEvent) => {
    event.preventDefault();
    setIsSubmitting(true);
    setError('');
    setSuccess('');

    try {
      await authAPI.register(registerData);
      setSuccess('Registration successful. Verify your email, then login.');
      setMode('login');
      setLoginData((prev) => ({ ...prev, username: registerData.username, password: '' }));
    } catch (err: any) {
      setError(err.message || 'Registration failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-[#0F172A] via-[#1E293B] to-[#334155] text-white flex items-center justify-center px-4 py-12">
      <div className="w-full max-w-5xl grid md:grid-cols-2 rounded-2xl border border-[#3AA8C1]/20 overflow-hidden shadow-2xl bg-[#1E293B]/70 backdrop-blur-xl">
        <section className="p-8 md:p-10 flex flex-col justify-center bg-gradient-to-br from-[#3AA8C1]/20 to-[#1E293B]">
          <div className="w-12 h-12 rounded-xl bg-[#3AA8C1]/20 flex items-center justify-center mb-4">
            <SparklesIcon className="w-7 h-7 text-[#3AA8C1]" />
          </div>
          <h1 className="text-3xl md:text-4xl font-bold leading-tight mb-4">TravelGenie Auth</h1>
          <p className="text-[#CBD5E1] leading-relaxed">
            Create your account, verify by email, and sign in securely to continue planning your trips.
          </p>

          <div className="mt-8 inline-flex bg-[#0F172A]/60 p-1 rounded-xl border border-[#334155]">
            <button
              type="button"
              onClick={() => switchMode('login')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                mode === 'login' ? 'bg-[#3AA8C1] text-white' : 'text-[#CBD5E1] hover:text-white'
              }`}
            >
              Login
            </button>
            <button
              type="button"
              onClick={() => switchMode('register')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${
                mode === 'register' ? 'bg-[#3AA8C1] text-white' : 'text-[#CBD5E1] hover:text-white'
              }`}
            >
              Register
            </button>
          </div>
        </section>

        <section className="p-8 md:p-10 bg-[#0F172A]/60 relative overflow-hidden">
          <div className="relative h-[520px]">
            <div className="absolute inset-x-2 top-3 bottom-0 rounded-2xl border border-[#334155]/70 bg-[#0B1730] shadow-lg" />

            <form
              onSubmit={handleLogin}
              className={`absolute inset-0 rounded-2xl border border-[#334155] bg-[#0F172A]/80 p-6 shadow-xl transition-all duration-500 ease-in-out ${
                mode === 'login'
                  ? 'z-20 translate-y-0 scale-100 opacity-100 pointer-events-auto'
                  : 'z-10 translate-y-4 scale-[0.97] opacity-100 pointer-events-none'
              }`}
            >
              <div className={`h-full flex flex-col justify-center transition-opacity duration-300 ${mode === 'login' ? 'opacity-100 visible' : 'opacity-0 invisible'}`}>
              <h2 className="text-2xl font-semibold mb-6">Login</h2>
              <div className="space-y-4">
                <input
                  required
                  type="text"
                  placeholder="Username"
                  value={loginData.username}
                  onChange={(e) => setLoginData((prev) => ({ ...prev, username: e.target.value }))}
                  className="input-field"
                />
                <input
                  required
                  type="password"
                  placeholder="Password"
                  value={loginData.password}
                  onChange={(e) => setLoginData((prev) => ({ ...prev, password: e.target.value }))}
                  className="input-field"
                />
              </div>

              {error && mode === 'login' && <p className="mt-4 text-sm text-red-400">{error}</p>}
              {success && mode === 'login' && <p className="mt-4 text-sm text-emerald-400">{success}</p>}

              <button type="submit" disabled={isSubmitting} className="btn-primary w-full mt-8 disabled:opacity-70">
                {isSubmitting ? 'Logging in...' : 'Login'}
              </button>

              <button
                type="button"
                onClick={() => switchMode('register')}
                className="btn-secondary w-full mt-3"
              >
                Register
              </button>
              </div>
            </form>

            <form
              onSubmit={handleRegister}
              className={`absolute inset-0 rounded-2xl border border-[#334155] bg-[#0F172A]/80 p-6 shadow-xl transition-all duration-500 ease-in-out ${
                mode === 'register'
                  ? 'z-20 translate-y-0 scale-100 opacity-100 pointer-events-auto'
                  : 'z-10 translate-y-4 scale-[0.97] opacity-100 pointer-events-none'
              }`}
            >
              <div className={`h-full flex flex-col justify-center transition-opacity duration-300 ${mode === 'register' ? 'opacity-100 visible' : 'opacity-0 invisible'}`}>
              <h2 className="text-2xl font-semibold mb-6">Register</h2>
              <div className="space-y-4">
                <input
                  required
                  type="text"
                  placeholder="Username"
                  value={registerData.username}
                  onChange={(e) => setRegisterData((prev) => ({ ...prev, username: e.target.value }))}
                  className="input-field"
                />
                <input
                  required
                  type="password"
                  placeholder="Password"
                  value={registerData.password}
                  onChange={(e) => setRegisterData((prev) => ({ ...prev, password: e.target.value }))}
                  className="input-field"
                />
                <input
                  required
                  type="email"
                  placeholder="Email"
                  value={registerData.email}
                  onChange={(e) => setRegisterData((prev) => ({ ...prev, email: e.target.value }))}
                  className="input-field"
                />
                <input
                  required
                  type="tel"
                  placeholder="Phone Number"
                  value={registerData.phone_number}
                  onChange={(e) => setRegisterData((prev) => ({ ...prev, phone_number: e.target.value }))}
                  className="input-field"
                />
              </div>

              {error && mode === 'register' && <p className="mt-4 text-sm text-red-400">{error}</p>}

              <button type="submit" disabled={isSubmitting} className="btn-primary w-full mt-8 disabled:opacity-70">
                {isSubmitting ? 'Creating account...' : 'Register'}
              </button>

              <button
                type="button"
                onClick={() => switchMode('login')}
                className="btn-secondary w-full mt-3"
              >
                Go to Login
              </button>
              </div>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}
