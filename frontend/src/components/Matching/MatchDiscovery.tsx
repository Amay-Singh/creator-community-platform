import React, { useState, useEffect } from 'react'
import { matchingAPI, MatchRequest, MatchResult } from '../../services/matchingAPI'
import Button from '../ui/Button'
import Card from '../ui/Card'
import Input from '../ui/Input'
import Select from '../ui/Select'
import Badge from '../ui/Badge'
import { Loader2, Search, Filter, Star, MapPin, Clock, Users } from 'lucide-react'

interface MatchDiscoveryProps {
  onMatchSelect?: (match: MatchResult) => void
}

export const MatchDiscovery: React.FC<MatchDiscoveryProps> = ({ onMatchSelect }) => {
  const [matches, setMatches] = useState<MatchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [searchFilters, setSearchFilters] = useState<MatchRequest>({
    limit: 10,
    match_type: 'collaboration',
    exclude_previous: true
  })
  const [showFilters, setShowFilters] = useState(false)

  const handleFindMatches = async () => {
    setLoading(true)
    try {
      const response = await matchingAPI.findMatches(searchFilters)
      setMatches(response.data.matches)
    } catch (error) {
      console.error('Error finding matches:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkViewed = async (matchId: number) => {
    try {
      await matchingAPI.markMatchViewed(matchId)
      setMatches(prev => 
        prev.map(match => 
          match.id === matchId 
            ? { ...match, status: 'viewed', viewed_at: new Date().toISOString() }
            : match
        )
      )
    } catch (error) {
      console.error('Error marking match as viewed:', error)
    }
  }

  const handleContact = async (matchId: number) => {
    try {
      await matchingAPI.markMatchContacted(matchId)
      setMatches(prev => 
        prev.map(match => 
          match.id === matchId 
            ? { ...match, status: 'contacted', contacted_at: new Date().toISOString() }
            : match
        )
      )
    } catch (error) {
      console.error('Error marking match as contacted:', error)
    }
  }

  const handleDecline = async (matchId: number) => {
    try {
      await matchingAPI.declineMatch(matchId)
      setMatches(prev => 
        prev.filter(match => match.id !== matchId)
      )
    } catch (error) {
      console.error('Error declining match:', error)
    }
  }

  const getCompatibilityColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100'
    if (score >= 60) return 'text-yellow-600 bg-yellow-100'
    return 'text-red-600 bg-red-100'
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending': return 'bg-blue-100 text-blue-800'
      case 'viewed': return 'bg-gray-100 text-gray-800'
      case 'contacted': return 'bg-green-100 text-green-800'
      case 'declined': return 'bg-red-100 text-red-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  useEffect(() => {
    handleFindMatches()
  }, [])

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Discover Collaborators</h2>
          <p className="text-gray-600">Find creators who match your skills and interests</p>
        </div>
        <Button
          onClick={() => setShowFilters(!showFilters)}
          variant="outline"
          className="flex items-center gap-2"
        >
          <Filter className="h-4 w-4" />
          Filters
        </Button>
      </div>

      {/* Filters Panel */}
      {showFilters && (
        <Card className="p-6 space-y-4">
          <h3 className="text-lg font-semibold">Search Filters</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <Input
                placeholder="Enter location"
                value={searchFilters.location || ''}
                onChange={(e) => setSearchFilters(prev => ({ ...prev, location: e.target.value }))}
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Experience Level
              </label>
              <Select
                value={searchFilters.experience_level || ''}
                onChange={(value) => setSearchFilters(prev => ({ ...prev, experience_level: value }))}
              >
                <option value="">Any Level</option>
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
                <option value="professional">Professional</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Match Type
              </label>
              <Select
                value={searchFilters.match_type || 'collaboration'}
                onChange={(value) => setSearchFilters(prev => ({ ...prev, match_type: value }))}
              >
                <option value="collaboration">Collaboration</option>
                <option value="mentorship">Mentorship</option>
                <option value="networking">Networking</option>
                <option value="general">General</option>
              </Select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Results Limit
              </label>
              <Select
                value={searchFilters.limit?.toString() || '10'}
                onChange={(value) => setSearchFilters(prev => ({ ...prev, limit: parseInt(value) }))}
              >
                <option value="5">5 matches</option>
                <option value="10">10 matches</option>
                <option value="20">20 matches</option>
                <option value="50">50 matches</option>
              </Select>
            </div>
          </div>
          
          <div className="flex items-center justify-between pt-4 border-t">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={searchFilters.exclude_previous || false}
                onChange={(e) => setSearchFilters(prev => ({ ...prev, exclude_previous: e.target.checked }))}
                className="rounded border-gray-300"
              />
              <span className="text-sm text-gray-700">Exclude previous matches</span>
            </label>
            
            <Button
              onClick={handleFindMatches}
              disabled={loading}
              className="flex items-center gap-2"
            >
              {loading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Search className="h-4 w-4" />
              )}
              Find Matches
            </Button>
          </div>
        </Card>
      )}

      {/* Results */}
      <div className="space-y-4">
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            <span className="ml-2 text-gray-600">Finding your perfect matches...</span>
          </div>
        ) : matches.length === 0 ? (
          <Card className="p-12 text-center">
            <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No matches found</h3>
            <p className="text-gray-600 mb-4">
              Try adjusting your filters or update your profile to get better matches.
            </p>
            <Button onClick={handleFindMatches} variant="outline">
              Search Again
            </Button>
          </Card>
        ) : (
          <div className="grid gap-6">
            {matches.map((match) => (
              <Card key={match.id} className="p-6 hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-xl font-semibold text-gray-900">
                        {match.matched_creator_name}
                      </h3>
                      <Badge className={getStatusColor(match.status)}>
                        {match.status}
                      </Badge>
                    </div>
                    
                    <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                      {match.matched_creator_location && (
                        <div className="flex items-center gap-1">
                          <MapPin className="h-4 w-4" />
                          {match.matched_creator_location}
                        </div>
                      )}
                      <div className="flex items-center gap-1">
                        <Clock className="h-4 w-4" />
                        {new Date(match.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    
                    <p className="text-gray-700 mb-4 line-clamp-2">
                      {match.matched_creator_bio}
                    </p>
                  </div>
                  
                  <div className="text-right ml-4">
                    <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getCompatibilityColor(match.compatibility_score)}`}>
                      <Star className="h-4 w-4" />
                      {match.compatibility_score.toFixed(1)}%
                    </div>
                  </div>
                </div>

                {/* Match Details */}
                <div className="space-y-3 mb-4">
                  {match.match_reasons.length > 0 && (
                    <div>
                      <h4 className="text-sm font-medium text-gray-900 mb-2">Why this match?</h4>
                      <ul className="text-sm text-gray-600 space-y-1">
                        {match.match_reasons.map((reason, index) => (
                          <li key={index} className="flex items-start gap-2">
                            <span className="text-blue-600 mt-1">•</span>
                            {reason}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  <div className="flex flex-wrap gap-4">
                    {match.shared_skills.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Shared Skills</h4>
                        <div className="flex flex-wrap gap-1">
                          {match.shared_skills.map((skill, index) => (
                            <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}

                    {match.complementary_skills.length > 0 && (
                      <div>
                        <h4 className="text-sm font-medium text-gray-900 mb-2">Complementary Skills</h4>
                        <div className="flex flex-wrap gap-1">
                          {match.complementary_skills.map((skill, index) => (
                            <Badge key={index} variant="secondary" className="bg-green-100 text-green-800">
                              {skill}
                            </Badge>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-3 pt-4 border-t">
                  {match.status === 'pending' && (
                    <Button
                      onClick={() => handleMarkViewed(match.id)}
                      variant="outline"
                      size="sm"
                    >
                      Mark as Viewed
                    </Button>
                  )}
                  
                  {(match.status === 'pending' || match.status === 'viewed') && (
                    <>
                      <Button
                        onClick={() => handleContact(match.id)}
                        size="sm"
                        className="bg-blue-600 hover:bg-blue-700"
                      >
                        Contact Creator
                      </Button>
                      
                      <Button
                        onClick={() => handleDecline(match.id)}
                        variant="outline"
                        size="sm"
                        className="text-red-600 border-red-300 hover:bg-red-50"
                      >
                        Not Interested
                      </Button>
                    </>
                  )}
                  
                  {onMatchSelect && (
                    <Button
                      onClick={() => onMatchSelect(match)}
                      variant="outline"
                      size="sm"
                    >
                      View Details
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default MatchDiscovery
