import React, { useState } from 'react'
import { matchingAPI, MatchResult } from '../../services/matchingAPI'
import Card from '../ui/Card'
import Button from '../ui/Button'
import Textarea from '../ui/Textarea'
import Select from '../ui/Select'
import { Star, MessageSquare, CheckCircle, X } from 'lucide-react'

interface MatchFeedbackProps {
  match: MatchResult
  onFeedbackSubmitted?: () => void
  onClose?: () => void
}

export const MatchFeedback: React.FC<MatchFeedbackProps> = ({
  match,
  onFeedbackSubmitted,
  onClose
}) => {
  const [rating, setRating] = useState(0)
  const [feedbackType, setFeedbackType] = useState('quality')
  const [comment, setComment] = useState('')
  const [contactedMatch, setContactedMatch] = useState(false)
  const [collaborationStarted, setCollaborationStarted] = useState(false)
  const [wouldRecommend, setWouldRecommend] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (rating === 0) return

    setSubmitting(true)
    try {
      await matchingAPI.createFeedback({
        match_result: match.id,
        rating,
        feedback_type: feedbackType,
        comment: comment.trim() || undefined,
        contacted_match: contactedMatch,
        collaboration_started: collaborationStarted,
        would_recommend: wouldRecommend
      })
      
      onFeedbackSubmitted?.()
    } catch (error) {
      console.error('Error submitting feedback:', error)
    } finally {
      setSubmitting(false)
    }
  }

  const StarRating = () => (
    <div className="flex items-center gap-1">
      {[1, 2, 3, 4, 5].map((star) => (
        <button
          key={star}
          type="button"
          onClick={() => setRating(star)}
          className={`p-1 rounded transition-colors ${
            star <= rating 
              ? 'text-yellow-400 hover:text-yellow-500' 
              : 'text-gray-300 hover:text-gray-400'
          }`}
        >
          <Star className={`h-6 w-6 ${star <= rating ? 'fill-current' : ''}`} />
        </button>
      ))}
      <span className="ml-2 text-sm text-gray-600">
        {rating > 0 && (
          <>
            {rating}/5 - {
              rating === 5 ? 'Excellent' :
              rating === 4 ? 'Good' :
              rating === 3 ? 'Average' :
              rating === 2 ? 'Poor' : 'Very Poor'
            }
          </>
        )}
      </span>
    </div>
  )

  return (
    <Card className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <MessageSquare className="h-6 w-6 text-blue-600" />
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Rate This Match</h3>
            <p className="text-sm text-gray-600">
              Help us improve by sharing your experience with {match.matched_creator_name}
            </p>
          </div>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-100"
          >
            <X className="h-5 w-5" />
          </button>
        )}
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Rating */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Overall Rating *
          </label>
          <StarRating />
        </div>

        {/* Feedback Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Feedback Category
          </label>
          <Select
            value={feedbackType}
            onChange={setFeedbackType}
            className="w-full"
          >
            <option value="quality">Match Quality</option>
            <option value="relevance">Relevance</option>
            <option value="experience">User Experience</option>
            <option value="other">Other</option>
          </Select>
        </div>

        {/* Comment */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Comments (Optional)
          </label>
          <Textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Share your thoughts about this match..."
            rows={4}
            className="w-full"
          />
        </div>

        {/* Experience Questions */}
        <div className="space-y-4">
          <h4 className="text-sm font-medium text-gray-700">Your Experience</h4>
          
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={contactedMatch}
              onChange={(e) => setContactedMatch(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">I contacted this creator</span>
          </label>

          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={collaborationStarted}
              onChange={(e) => setCollaborationStarted(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">We started a collaboration</span>
          </label>

          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={wouldRecommend}
              onChange={(e) => setWouldRecommend(e.target.checked)}
              className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">I would recommend this creator to others</span>
          </label>
        </div>

        {/* Match Summary */}
        <div className="bg-gray-50 p-4 rounded-lg">
          <h4 className="text-sm font-medium text-gray-700 mb-2">Match Summary</h4>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-600">Creator:</span>
              <span className="ml-2 font-medium">{match.matched_creator_name}</span>
            </div>
            <div>
              <span className="text-gray-600">Compatibility:</span>
              <span className="ml-2 font-medium">{match.compatibility_score.toFixed(1)}%</span>
            </div>
            <div>
              <span className="text-gray-600">Match Type:</span>
              <span className="ml-2 font-medium capitalize">{match.match_type}</span>
            </div>
            <div>
              <span className="text-gray-600">Date:</span>
              <span className="ml-2 font-medium">
                {new Date(match.created_at).toLocaleDateString()}
              </span>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center justify-end gap-3 pt-4 border-t">
          {onClose && (
            <Button
              type="button"
              onClick={onClose}
              variant="outline"
            >
              Cancel
            </Button>
          )}
          <Button
            type="submit"
            disabled={rating === 0 || submitting}
            className="flex items-center gap-2"
          >
            {submitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Submitting...
              </>
            ) : (
              <>
                <CheckCircle className="h-4 w-4" />
                Submit Feedback
              </>
            )}
          </Button>
        </div>
      </form>
    </Card>
  )
}

export default MatchFeedback
