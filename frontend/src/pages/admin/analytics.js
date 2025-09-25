import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Layout from '../../components/Layout';
import { 
  ChartBarIcon, 
  UsersIcon, 
  BellIcon, 
  ChatBubbleLeftRightIcon,
  ArrowTrendingUpIcon,
  ClockIcon
} from '@heroicons/react/24/outline';

export default function AnalyticsDashboard() {
  const router = useRouter();
  const [dashboardData, setDashboardData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState(30);

  useEffect(() => {
    fetchDashboardData();
  }, [timeRange]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      if (!token) {
        router.push('/login');
        return;
      }

      const response = await fetch(`/api/analytics/dashboard?days=${timeRange}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          router.push('/login');
          return;
        }
        throw new Error('Failed to fetch analytics data');
      }

      const data = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const StatCard = ({ title, value, change, icon: Icon, color = 'blue' }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 rounded-md bg-${color}-100`}>
          <Icon className={`h-6 w-6 text-${color}-600`} />
        </div>
        <div className="ml-4 flex-1">
          <p className="text-sm font-medium text-gray-500">{title}</p>
          <p className="text-2xl font-semibold text-gray-900">{value}</p>
          {change && (
            <p className={`text-sm ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
              {change >= 0 ? '+' : ''}{change}% from last period
            </p>
          )}
        </div>
      </div>
    </div>
  );

  const MetricChart = ({ title, data, color = 'blue' }) => (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-medium text-gray-900 mb-4">{title}</h3>
      <div className="h-64 flex items-end space-x-2">
        {data && data.map((item, index) => (
          <div key={index} className="flex-1 flex flex-col items-center">
            <div 
              className={`w-full bg-${color}-500 rounded-t`}
              style={{ 
                height: `${Math.max((item.value / Math.max(...data.map(d => d.value))) * 200, 4)}px` 
              }}
            />
            <span className="text-xs text-gray-500 mt-1">
              {new Date(item.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
            </span>
          </div>
        ))}
      </div>
    </div>
  );

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-50 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="animate-pulse">
              <div className="h-8 bg-gray-200 rounded w-1/4 mb-8"></div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow p-6">
                    <div className="h-16 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow p-6">
                    <div className="h-64 bg-gray-200 rounded"></div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="min-h-screen bg-gray-50 py-8">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="bg-red-50 border border-red-200 rounded-md p-4">
              <div className="flex">
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800">
                    Error loading analytics data
                  </h3>
                  <div className="mt-2 text-sm text-red-700">
                    <p>{error}</p>
                  </div>
                  <div className="mt-4">
                    <button
                      onClick={fetchDashboardData}
                      className="bg-red-100 px-3 py-2 rounded-md text-sm font-medium text-red-800 hover:bg-red-200"
                    >
                      Try again
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  const { platform_overview, matching_performance, notification_performance } = dashboardData || {};

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
              <p className="mt-2 text-gray-600">Platform performance and user engagement metrics</p>
            </div>
            <div className="flex items-center space-x-4">
              <select
                value={timeRange}
                onChange={(e) => setTimeRange(parseInt(e.target.value))}
                className="rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={30}>Last 30 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
          </div>

          {/* Key Metrics */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Total Users"
              value={platform_overview?.total_users?.toLocaleString() || '0'}
              icon={UsersIcon}
              color="blue"
            />
            <StatCard
              title="Daily Active Users"
              value={platform_overview?.active_users_daily?.toLocaleString() || '0'}
              icon={ArrowTrendingUpIcon}
              color="green"
            />
            <StatCard
              title="Match Acceptance Rate"
              value={`${matching_performance?.match_acceptance_rate?.toFixed(1) || '0'}%`}
              icon={ChartBarIcon}
              color="purple"
            />
            <StatCard
              title="Notification Open Rate"
              value={`${notification_performance?.open_rate?.toFixed(1) || '0'}%`}
              icon={BellIcon}
              color="yellow"
            />
          </div>

          {/* Performance Metrics */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">System Performance</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">API Response Time</span>
                  <span className="text-sm font-medium">
                    {platform_overview?.avg_api_response_time?.toFixed(3) || '0'}s
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Error Rate</span>
                  <span className="text-sm font-medium">
                    {platform_overview?.error_rate?.toFixed(2) || '0'}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Cache Hit Rate</span>
                  <span className="text-sm font-medium">
                    {platform_overview?.cache_hit_rate?.toFixed(1) || '0'}%
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">User Engagement</h3>
              <div className="space-y-4">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Weekly Active Users</span>
                  <span className="text-sm font-medium">
                    {platform_overview?.active_users_weekly?.toLocaleString() || '0'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Monthly Active Users</span>
                  <span className="text-sm font-medium">
                    {platform_overview?.active_users_monthly?.toLocaleString() || '0'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">Avg Match Score</span>
                  <span className="text-sm font-medium">
                    {matching_performance?.avg_match_score?.toFixed(2) || '0'}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
              <div className="space-y-3">
                {dashboardData?.recent_events?.slice(0, 5).map((event, index) => (
                  <div key={index} className="flex items-center text-sm">
                    <div className="flex-shrink-0 w-2 h-2 bg-blue-400 rounded-full mr-3"></div>
                    <div className="flex-1">
                      <span className="text-gray-600">{event.event_type.replace('_', ' ')}</span>
                      {event.username && (
                        <span className="text-gray-400 ml-1">by {event.username}</span>
                      )}
                    </div>
                    <span className="text-gray-400 text-xs">
                      {new Date(event.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <MetricChart
              title="Daily Active Users"
              data={platform_overview?.daily_metrics?.map(m => ({
                date: m.date,
                value: m.active_users
              }))}
              color="blue"
            />
            <MetricChart
              title="New Registrations"
              data={platform_overview?.daily_metrics?.map(m => ({
                date: m.date,
                value: m.new_registrations
              }))}
              color="green"
            />
            <MetricChart
              title="Match Acceptance Rate"
              data={matching_performance?.daily_metrics?.map(m => ({
                date: m.date,
                value: m.acceptance_rate
              }))}
              color="purple"
            />
            <MetricChart
              title="Notification Performance"
              data={notification_performance?.daily_metrics?.map(m => ({
                date: m.date,
                value: m.open_rate
              }))}
              color="yellow"
            />
          </div>
        </div>
      </div>
    </Layout>
  );
}
