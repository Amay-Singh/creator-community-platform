import { useAuth } from '../contexts/AuthContext';
import { useRouter } from 'next/router';
import { useEffect } from 'react';
import Dashboard from '../components/Dashboard/Dashboard.jsx';

export default function DashboardPage() {
  const { user, profile, loading } = useAuth();
  const router = useRouter();

  console.log('DashboardPage render - user:', !!user, 'profile:', !!profile, 'loading:', loading);

  useEffect(() => {
    if (!loading && !user) {
      console.log('DashboardPage: No user, redirecting to login');
      router.push('/login');
    }
  }, [user, loading, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return <Dashboard />;
}
