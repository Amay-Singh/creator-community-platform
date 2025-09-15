import React, { useState, useEffect } from 'react'
import { matchingAPI, MatchStatistics as MatchStatsType } from '../../services/matchingAPI'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import { TrendingUp, Users, MessageCircle, Star, Calendar, Target } from 'lucide-react'

export const MatchStatistics: React.FC = () => {
  const [stats, setStats] = useState<MatchStatsType | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await matchingAPI.getStatistics()
        setStats(response.data)
      } catch (error) {
        console.error('Error fetching match statistics:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  if (loading) {
    return (
      <Card className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-6 bg-gray-200 rounded w-1/4"></div>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="space-y-2">
                <div className="h-8 bg-gray-200 rounded"></div>
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              </div>
            ))}
          </div>
        </div>
      </Card>
    )
  }

  if (!stats) {
    return (
      <Card className="p-6 text-center">
        <p className="text-gray-600">Unable to load statistics</p>
      </Card>
    )
  }

  const StatCard = ({ 
    icon: Icon, 
    title, 
    value, 
    subtitle, 
    color = 'text-blue-600' 
  }: {
    icon: React.ComponentType<any>
    title: string
    value: string | number
    subtitle?: string
    color?: string
  }) => (
    <div className="bg-white p-4 rounded-lg border border-gray-200">
      <div className="flex items-center justify-between mb-2">
        <Icon className={`h-5 w-5 ${color}`} />
        <span className="text-2xl font-bold text-gray-900">{value}</span>
      </div>
      <h4 className="text-sm font-medium text-gray-700">{title}</h4>
      {subtitle && <p className="text-xs text-gray-500 mt-1">{subtitle}</p>}
    </div>
  )

  return (
    <div className="space-y-6">
      <div className="flex items-center gap-3">
        <TrendingUp className="h-6 w-6 text-blue-600" />
        <h3 className="text-xl font-semibold text-gray-900">Match Statistics</h3>
      </div>

      {/* Overview Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <StatCard
          icon={Users}
          title="Total Matches"
          value={stats.total_matches}
          subtitle="All time"
          color="text-blue-600"
        />
        <StatCard
          icon={MessageCircle}
          title="Contacted"
          value={stats.matches_contacted}
          subtitle={`${((stats.matches_contacted / Math.max(stats.total_matches, 1)) * 100).toFixed(1)}% rate`}
          color="text-green-600"
        />
        <StatCard
          icon={Star}
          title="Avg Rating"
          value={stats.average_rating ? stats.average_rating.toFixed(1) : 'N/A'}
          subtitle={stats.feedback_given > 0 ? `${stats.feedback_given} reviews` : 'No reviews yet'}
          color="text-yellow-600"
        />
        <StatCard
          icon={Target}
          title="Success Rate"
          value={`${(stats.collaboration_rate * 100).toFixed(1)}%`}
          subtitle="Collaborations started"
          color="text-purple-600"
        />
      </div>

      {/* Recent Activity */}
      <Card className="p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600 mb-1">
              {stats.recent_activity.matches_this_week}
            </div>
            <div className="text-sm text-gray-600">This Week</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">
              {stats.recent_activity.matches_this_month}
            </div>
            <div className="text-sm text-gray-600">This Month</div>
          </div>
          <div className="text-center">
            <div className="text-sm text-gray-600 mb-1">Last Match</div>
            <div className="text-sm font-medium text-gray-900">
              {stats.recent_activity.last_match_date 
                ? new Date(stats.recent_activity.last_match_date).toLocaleDateString()
                : 'No matches yet'
              }
            </div>
          </div>
        </div>
      </Card>

      {/* Top Skills */}
      {stats.top_skills.length > 0 && (
        <Card className="p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">Top Matching Skills</h4>
          <div className="flex flex-wrap gap-2">
            {stats.top_skills.map((skill, index) => (
              <Badge
                key={skill}
                variant="secondary"
                className={`
                  ${index === 0 ? 'bg-yellow-100 text-yellow-800' : ''}
                  ${index === 1 ? 'bg-gray-100 text-gray-800' : ''}
                  ${index === 2 ? 'bg-orange-100 text-orange-800' : ''}
                  ${index > 2 ? 'bg-blue-100 text-blue-800' : ''}
                `}
              >
                {skill}
                {index < 3 && (
                  <span className="ml-1 text-xs">
                    {index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉'}
                  </span>
                )}
              </Badge>
            ))}
          </div>
        </Card>
      )}

      {/* Match Status Breakdown */}
      <Card className="p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">Match Status Breakdown</h4>
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Viewed</span>
            <div className="flex items-center gap-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full" 
                  style={{ 
                    width: `${(stats.matches_viewed / Math.max(stats.total_matches, 1)) * 100}%` 
                  }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-900 w-12 text-right">
                {stats.matches_viewed}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Contacted</span>
            <div className="flex items-center gap-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-600 h-2 rounded-full" 
                  style={{ 
                    width: `${(stats.matches_contacted / Math.max(stats.total_matches, 1)) * 100}%` 
                  }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-900 w-12 text-right">
                {stats.matches_contacted}
              </span>
            </div>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Declined</span>
            <div className="flex items-center gap-2">
              <div className="w-32 bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-red-600 h-2 rounded-full" 
                  style={{ 
                    width: `${(stats.matches_declined / Math.max(stats.total_matches, 1)) * 100}%` 
                  }}
                ></div>
              </div>
              <span className="text-sm font-medium text-gray-900 w-12 text-right">
                {stats.matches_declined}
              </span>
            </div>
          </div>
        </div>
      </Card>
    </div>
  )
}

export default MatchStatistics
