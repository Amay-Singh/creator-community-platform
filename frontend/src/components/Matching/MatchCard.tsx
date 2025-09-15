import React from 'react'
import { MatchResult } from '../../services/matchingAPI'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import Button from '../ui/Button'
import { Star, MapPin, Clock, User, MessageCircle, X, Eye } from 'lucide-react'

interface MatchCardProps {
  match: MatchResult
  onContact?: (matchId: number) => void
  onDecline?: (matchId: number) => void
  onMarkViewed?: (matchId: number) => void
  onViewProfile?: (creatorId: number) => void
  compact?: boolean
}

export const MatchCard: React.FC<MatchCardProps> = ({
  match,
  onContact,
  onDecline,
  onMarkViewed,
  onViewProfile,
  compact = false
}) => {
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

  const formatDate = (dateString: string) => {
    const date = new Date(dateString)
    const now = new Date()
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))
    
    if (diffInHours < 1) return 'Just now'
    if (diffInHours < 24) return `${diffInHours}h ago`
    if (diffInHours < 48) return 'Yesterday'
    return date.toLocaleDateString()
  }

  if (compact) {
    return (
      <Card className="p-4 hover:shadow-md transition-shadow">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3 flex-1">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
              {match.matched_creator_name.charAt(0)}
            </div>
            <div className="flex-1 min-w-0">
              <h4 className="font-medium text-gray-900 truncate">
                {match.matched_creator_name}
              </h4>
              <p className="text-sm text-gray-600 truncate">
                {match.matched_creator_location}
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <div className={`px-2 py-1 rounded-full text-xs font-medium ${getCompatibilityColor(match.compatibility_score)}`}>
              {match.compatibility_score.toFixed(0)}%
            </div>
            <Badge className={getStatusColor(match.status)} size="sm">
              {match.status}
            </Badge>
          </div>
        </div>
      </Card>
    )
  }

  return (
    <Card className="p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-start gap-4 flex-1">
          <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xl font-semibold">
            {match.matched_creator_name.charAt(0)}
          </div>
          
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
                {formatDate(match.created_at)}
              </div>
              <div className="flex items-center gap-1">
                <User className="h-4 w-4" />
                {match.match_type}
              </div>
            </div>
          </div>
        </div>
        
        <div className="text-right">
          <div className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${getCompatibilityColor(match.compatibility_score)}`}>
            <Star className="h-4 w-4" />
            {match.compatibility_score.toFixed(1)}%
          </div>
          <div className="text-xs text-gray-500 mt-1">
            Similarity: {(match.similarity_score * 100).toFixed(1)}%
          </div>
        </div>
      </div>

      {/* Bio */}
      {match.matched_creator_bio && (
        <div className="mb-4">
          <p className="text-gray-700 line-clamp-3">
            {match.matched_creator_bio}
          </p>
        </div>
      )}

      {/* Match Reasons */}
      {match.match_reasons.length > 0 && (
        <div className="mb-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Why this match?</h4>
          <ul className="text-sm text-gray-600 space-y-1">
            {match.match_reasons.slice(0, 3).map((reason, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-600 mt-1 text-xs">•</span>
                {reason}
              </li>
            ))}
            {match.match_reasons.length > 3 && (
              <li className="text-xs text-gray-500 italic">
                +{match.match_reasons.length - 3} more reasons
              </li>
            )}
          </ul>
        </div>
      )}

      {/* Skills */}
      <div className="mb-4 space-y-3">
        {match.shared_skills.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Shared Skills</h4>
            <div className="flex flex-wrap gap-1">
              {match.shared_skills.slice(0, 5).map((skill, index) => (
                <Badge key={index} variant="secondary" className="bg-blue-100 text-blue-800 text-xs">
                  {skill}
                </Badge>
              ))}
              {match.shared_skills.length > 5 && (
                <Badge variant="secondary" className="bg-gray-100 text-gray-600 text-xs">
                  +{match.shared_skills.length - 5}
                </Badge>
              )}
            </div>
          </div>
        )}

        {match.complementary_skills.length > 0 && (
          <div>
            <h4 className="text-sm font-medium text-gray-900 mb-2">Complementary Skills</h4>
            <div className="flex flex-wrap gap-1">
              {match.complementary_skills.slice(0, 5).map((skill, index) => (
                <Badge key={index} variant="secondary" className="bg-green-100 text-green-800 text-xs">
                  {skill}
                </Badge>
              ))}
              {match.complementary_skills.length > 5 && (
                <Badge variant="secondary" className="bg-gray-100 text-gray-600 text-xs">
                  +{match.complementary_skills.length - 5}
                </Badge>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Expiry Warning */}
      {match.expires_at && new Date(match.expires_at) < new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-sm text-yellow-800">
            <Clock className="h-4 w-4 inline mr-1" />
            This match expires on {new Date(match.expires_at).toLocaleDateString()}
          </p>
        </div>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3 pt-4 border-t">
        {match.status === 'pending' && onMarkViewed && (
          <Button
            onClick={() => onMarkViewed(match.id)}
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
          >
            <Eye className="h-4 w-4" />
            Mark Viewed
          </Button>
        )}
        
        {(match.status === 'pending' || match.status === 'viewed') && onContact && (
          <Button
            onClick={() => onContact(match.id)}
            size="sm"
            className="bg-blue-600 hover:bg-blue-700 flex items-center gap-2"
          >
            <MessageCircle className="h-4 w-4" />
            Contact
          </Button>
        )}
        
        {onViewProfile && (
          <Button
            onClick={() => onViewProfile(match.matched_creator)}
            variant="outline"
            size="sm"
            className="flex items-center gap-2"
          >
            <User className="h-4 w-4" />
            View Profile
          </Button>
        )}
        
        {(match.status === 'pending' || match.status === 'viewed') && onDecline && (
          <Button
            onClick={() => onDecline(match.id)}
            variant="outline"
            size="sm"
            className="text-red-600 border-red-300 hover:bg-red-50 flex items-center gap-2 ml-auto"
          >
            <X className="h-4 w-4" />
            Decline
          </Button>
        )}
      </div>
    </Card>
  )
}

export default MatchCard
