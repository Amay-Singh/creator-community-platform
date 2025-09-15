import React, { useState, useEffect } from 'react'
import { matchingAPI, MatchResult } from '../services/matchingAPI'
import { MatchDiscovery, MatchCard, MatchFeedback, MatchStatistics } from '../components/Matching'
import Card from '../components/ui/Card'
import Button from '../components/ui/Button'
import Badge from '../components/ui/Badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/Tabs'
import { 
  Users, 
  TrendingUp, 
  MessageSquare, 
  RefreshCw,
  Sparkles,
  Filter,
  Search
} from 'lucide-react'

export const MatchingPage: React.FC = () => {
  const [activeTab, setActiveTab] = useState('discover')
  const [myMatches, setMyMatches] = useState<MatchResult[]>([])
  const [selectedMatch, setSelectedMatch] = useState<MatchResult | null>(null)
  const [showFeedback, setShowFeedback] = useState(false)
  const [loading, setLoading] = useState(false)
  const [embeddingStatus, setEmbeddingStatus] = useState<'checking' | 'updating' | 'ready'>('checking')

  const fetchMyMatches = async () => {
    setLoading(true)
    try {
      const response = await matchingAPI.getMatches({ limit: 50 })
      setMyMatches(response.data.results)
    } catch (error) {
      console.error('Error fetching matches:', error)
    } finally {
      setLoading(false)
    }
  }

  const checkEmbeddingStatus = async () => {
    try {
      const response = await matchingAPI.getEmbeddings()
      const embeddings = response.data.results
      
      if (embeddings.length === 0 || embeddings.some(e => e.needs_update)) {
        setEmbeddingStatus('updating')
        await matchingAPI.updateEmbedding(true)
      }
      setEmbeddingStatus('ready')
    } catch (error) {
      console.error('Error checking embedding status:', error)
      setEmbeddingStatus('ready')
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
      await fetchMyMatches()
    } catch (error) {
      console.error(`Error ${action}ing match:`, error)
    }
  }

  const handleFeedbackSubmitted = () => {
    setShowFeedback(false)
    setSelectedMatch(null)
    fetchMyMatches()
  }

  useEffect(() => {
    checkEmbeddingStatus()
    fetchMyMatches()
  }, [])

  const pendingMatches = myMatches.filter(m => m.status === 'pending')
  const viewedMatches = myMatches.filter(m => m.status === 'viewed')
  const contactedMatches = myMatches.filter(m => m.status === 'contacted')

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Sparkles className="h-8 w-8 text-blue-600" />
                AI Creator Matching
              </h1>
              <p className="text-gray-600 mt-2">
                Discover and connect with creators who complement your skills and interests
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              {embeddingStatus === 'updating' && (
                <Badge variant="secondary" className="bg-yellow-100 text-yellow-800">
                  <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                  Updating Profile
                </Badge>
              )}
              {embeddingStatus === 'ready' && (
                <Badge variant="secondary" className="bg-green-100 text-green-800">
                  Profile Ready
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Total Matches</p>
                <p className="text-2xl font-bold text-gray-900">{myMatches.length}</p>
              </div>
              <Users className="h-8 w-8 text-blue-600" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Pending</p>
                <p className="text-2xl font-bold text-orange-600">{pendingMatches.length}</p>
              </div>
              <Search className="h-8 w-8 text-orange-600" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Contacted</p>
                <p className="text-2xl font-bold text-green-600">{contactedMatches.length}</p>
              </div>
              <MessageSquare className="h-8 w-8 text-green-600" />
            </div>
          </Card>
          
          <Card className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Success Rate</p>
                <p className="text-2xl font-bold text-purple-600">
                  {myMatches.length > 0 
                    ? Math.round((contactedMatches.length / myMatches.length) * 100)
                    : 0
                  }%
                </p>
              </div>
              <TrendingUp className="h-8 w-8 text-purple-600" />
            </div>
          </Card>
        </div>

        {/* Main Content */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="discover" className="flex items-center gap-2">
              <Search className="h-4 w-4" />
              Discover
            </TabsTrigger>
            <TabsTrigger value="matches" className="flex items-center gap-2">
              <Users className="h-4 w-4" />
              My Matches ({myMatches.length})
            </TabsTrigger>
            <TabsTrigger value="statistics" className="flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Statistics
            </TabsTrigger>
            <TabsTrigger value="feedback" className="flex items-center gap-2">
              <MessageSquare className="h-4 w-4" />
              Feedback
            </TabsTrigger>
          </TabsList>

          <TabsContent value="discover" className="space-y-6">
            <MatchDiscovery
              onMatchSelect={(match) => {
                setSelectedMatch(match)
                setActiveTab('matches')
              }}
            />
          </TabsContent>

          <TabsContent value="matches" className="space-y-6">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <RefreshCw className="h-8 w-8 animate-spin text-blue-600" />
                <span className="ml-2 text-gray-600">Loading matches...</span>
              </div>
            ) : myMatches.length === 0 ? (
              <Card className="p-12 text-center">
                <Users className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">No matches yet</h3>
                <p className="text-gray-600 mb-4">
                  Start discovering creators to build your match list.
                </p>
                <Button onClick={() => setActiveTab('discover')}>
                  Discover Matches
                </Button>
              </Card>
            ) : (
              <div className="space-y-6">
                {/* Pending Matches */}
                {pendingMatches.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                      <Filter className="h-5 w-5" />
                      Pending Matches ({pendingMatches.length})
                    </h3>
                    <div className="space-y-4">
                      {pendingMatches.map((match) => (
                        <MatchCard
                          key={match.id}
                          match={match}
                          onContact={(id) => handleMatchAction(id, 'contact')}
                          onDecline={(id) => handleMatchAction(id, 'decline')}
                          onMarkViewed={(id) => handleMatchAction(id, 'view')}
                          onViewProfile={(creatorId) => {
                            // Navigate to profile page
                            console.log('View profile:', creatorId)
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Viewed Matches */}
                {viewedMatches.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Viewed Matches ({viewedMatches.length})
                    </h3>
                    <div className="space-y-4">
                      {viewedMatches.map((match) => (
                        <MatchCard
                          key={match.id}
                          match={match}
                          onContact={(id) => handleMatchAction(id, 'contact')}
                          onDecline={(id) => handleMatchAction(id, 'decline')}
                          onViewProfile={(creatorId) => {
                            console.log('View profile:', creatorId)
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}

                {/* Contacted Matches */}
                {contactedMatches.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Contacted Matches ({contactedMatches.length})
                    </h3>
                    <div className="space-y-4">
                      {contactedMatches.map((match) => (
                        <MatchCard
                          key={match.id}
                          match={match}
                          onViewProfile={(creatorId) => {
                            console.log('View profile:', creatorId)
                          }}
                        />
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </TabsContent>

          <TabsContent value="statistics">
            <MatchStatistics />
          </TabsContent>

          <TabsContent value="feedback" className="space-y-6">
            {showFeedback && selectedMatch ? (
              <MatchFeedback
                match={selectedMatch}
                onFeedbackSubmitted={handleFeedbackSubmitted}
                onClose={() => {
                  setShowFeedback(false)
                  setSelectedMatch(null)
                }}
              />
            ) : (
              <Card className="p-12 text-center">
                <MessageSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Share Your Feedback</h3>
                <p className="text-gray-600 mb-4">
                  Select a match from your matches tab to provide feedback and help improve our matching algorithm.
                </p>
                <Button 
                  onClick={() => setActiveTab('matches')}
                  variant="outline"
                >
                  View My Matches
                </Button>
              </Card>
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

export default MatchingPage
