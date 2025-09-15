import React, { useState, useEffect } from 'react'
import { matchingAPI, MatchResult } from '../services/matchingAPI'

export const MatchingPageSimple: React.FC = () => {
  const [matches, setMatches] = useState<MatchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchMatches = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await matchingAPI.getMatches({ limit: 10 })
      setMatches(response.data.results)
    } catch (err) {
      setError('Failed to fetch matches. Please try again.')
      console.error('Error fetching matches:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleMatchAction = async (matchId: number, action: 'contact' | 'decline' | 'view') => {
    try {
      switch (action) {
        case 'contact':
          await matchingAPI.markMatchContacted(matchId)
          break
        case 'decline':
          await matchingAPI.declineMatch(matchId)
          break
        case 'view':
          await matchingAPI.markMatchViewed(matchId)
          break
      }
      await fetchMatches()
    } catch (error) {
      console.error(`Error ${action}ing match:`, error)
    }
  }

  useEffect(() => {
    fetchMatches()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            AI Creator Matching
          </h1>
          <p className="text-gray-600">
            Discover and connect with creators who complement your skills
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">Total Matches</h3>
            <p className="text-3xl font-bold text-blue-600">{matches.length}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">Pending</h3>
            <p className="text-3xl font-bold text-orange-600">
              {matches.filter(m => m.status === 'pending').length}
            </p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-lg font-semibold text-gray-900">Contacted</h3>
            <p className="text-3xl font-bold text-green-600">
              {matches.filter(m => m.status === 'contacted').length}
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="mb-6">
          <button
            onClick={fetchMatches}
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Loading...' : 'Refresh Matches'}
          </button>
        </div>

        {/* Error */}
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-6">
            {error}
          </div>
        )}

        {/* Matches */}
        <div className="space-y-4">
          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              <p className="mt-2 text-gray-600">Loading matches...</p>
            </div>
          ) : matches.length === 0 ? (
            <div className="bg-white p-12 rounded-lg shadow text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No matches found</h3>
              <p className="text-gray-600">Try refreshing or check back later for new matches.</p>
            </div>
          ) : (
            matches.map((match) => (
              <div key={match.id} className="bg-white p-6 rounded-lg shadow">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Match #{match.id}
                    </h3>
                    <p className="text-gray-600">
                      {match.matched_creator_name} • {match.matched_creator_location}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      match.status === 'pending' ? 'bg-yellow-100 text-yellow-800' :
                      match.status === 'contacted' ? 'bg-green-100 text-green-800' :
                      match.status === 'declined' ? 'bg-red-100 text-red-800' :
                      'bg-gray-100 text-gray-800'
                    }`}>
                      {match.status}
                    </span>
                    <span className="text-sm font-medium text-blue-600">
                      {Math.round(match.compatibility_score * 100)}% match
                    </span>
                  </div>
                </div>

                <div className="mb-4">
                  <p className="text-gray-700">{match.match_reasons.join(', ')}</p>
                </div>

                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-900 mb-2">Skills</h4>
                  <div className="flex flex-wrap gap-2">
                    {match.shared_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded"
                      >
                        Shared: {skill}
                      </span>
                    ))}
                    {match.complementary_skills.map((skill) => (
                      <span
                        key={skill}
                        className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded"
                      >
                        Complementary: {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex space-x-3">
                  {match.status === 'pending' && (
                    <>
                      <button
                        onClick={() => handleMatchAction(match.id, 'contact')}
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                      >
                        Contact
                      </button>
                      <button
                        onClick={() => handleMatchAction(match.id, 'view')}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                      >
                        Mark Viewed
                      </button>
                      <button
                        onClick={() => handleMatchAction(match.id, 'decline')}
                        className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700"
                      >
                        Decline
                      </button>
                    </>
                  )}
                  {match.status === 'viewed' && (
                    <button
                      onClick={() => handleMatchAction(match.id, 'contact')}
                      className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                    >
                      Contact
                    </button>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default MatchingPageSimple
