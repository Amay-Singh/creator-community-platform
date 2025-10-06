import Dashboard from '../src/components/Dashboard/Dashboard.jsx';

export default function DashboardPage() {
  // AuthGuard handles authentication, so we can directly render Dashboard
  return <Dashboard />;
}
