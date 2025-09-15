import api from './api'

export interface CreatorEmbedding {
  id: number
  creator: number
  creator_name: string
  embedding_vector: number[]
  embedding_version: string
  skills_hash: string
  bio_hash: string
  interests_hash: string
  needs_update: boolean
  last_profile_update: string | null
  updated_at: string
  created_at: string
}

export interface MatchResult {
  id: number
  requester: number
  matched_creator: number
  matched_creator_name: string
  matched_creator_bio: string
  matched_creator_location: string
  similarity_score: number
  compatibility_score: number
  match_reasons: string[]
  shared_skills: string[]
  complementary_skills: string[]
  match_type: string
  status: 'pending' | 'viewed' | 'contacted' | 'declined'
  expires_at: string | null
  viewed_at: string | null
  contacted_at: string | null
  created_at: string
}

export interface MatchFeedback {
  id: number
  match_result: number
  user: number
  user_name: string
  rating: number
  feedback_type: 'quality' | 'relevance' | 'experience' | 'other'
  comment: string
  contacted_match: boolean
  collaboration_started: boolean
  would_recommend: boolean
  match_info: {
    matched_creator: string
    compatibility_score: number
    match_date: string
  }
  created_at: string
}

export interface MatchHistory {
  id: number
  user: number
  request_type: string
  filters_used: Record<string, any>
  results_count: number
  processing_time_ms: number
  embedding_version: string
  top_similarity_score: number | null
  average_compatibility: number | null
  created_at: string
}

export interface MatchRequest {
  limit?: number
  location?: string
  skills?: string[]
  experience_level?: string
  match_type?: string
  exclude_previous?: boolean
}

export interface BatchMatchRequest {
  creator_ids: number[]
  limit_per_creator?: number
  filters?: MatchRequest
}

export interface MatchStatistics {
  total_matches: number
  matches_viewed: number
  matches_contacted: number
  matches_declined: number
  feedback_given: number
  average_rating: number | null
  collaboration_rate: number
  top_skills: string[]
  recent_activity: {
    last_match_date: string | null
    matches_this_week: number
    matches_this_month: number
  }
}

export const matchingAPI = {
  // Creator Embeddings
  getEmbeddings: () => 
    api.get<{ results: CreatorEmbedding[] }>('/ai-services/embeddings/'),
  
  updateEmbedding: (forceUpdate = false) =>
    api.post('/ai-services/embeddings/update_embedding/', { force_update: forceUpdate }),

  // Match Results
  getMatches: (params?: { status?: string; limit?: number; offset?: number }) =>
    api.get<{ results: MatchResult[] }>('/ai-services/matches/', { params }),
  
  findMatches: (request: MatchRequest) =>
    api.post<{ matches: MatchResult[]; count: number; processing_time_ms: number }>('/ai-services/matches/find_matches/', request),
  
  getMatch: (matchId: number) =>
    api.get<MatchResult>(`/ai-services/matches/${matchId}/`),
  
  markMatchViewed: (matchId: number) =>
    api.post(`/ai-services/matches/${matchId}/mark_viewed/`),
  
  markMatchContacted: (matchId: number) =>
    api.post(`/ai-services/matches/${matchId}/contact/`),
  
  declineMatch: (matchId: number) =>
    api.post(`/ai-services/matches/${matchId}/decline/`),

  // Match Feedback
  getFeedback: () =>
    api.get<{ results: MatchFeedback[] }>('/ai-services/match-feedback/'),
  
  createFeedback: (feedback: {
    match_result: number
    rating: number
    feedback_type: string
    comment?: string
    contacted_match?: boolean
    collaboration_started?: boolean
    would_recommend?: boolean
  }) =>
    api.post<MatchFeedback>('/ai-services/match-feedback/', feedback),
  
  updateFeedback: (feedbackId: number, data: Partial<MatchFeedback>) =>
    api.patch<MatchFeedback>(`/ai-services/match-feedback/${feedbackId}/`, data),

  // Match History
  getHistory: (params?: { limit?: number; offset?: number }) =>
    api.get<{ results: MatchHistory[] }>('/ai-services/match-history/', { params }),

  // Batch Operations
  batchMatch: (request: BatchMatchRequest) =>
    api.post<{
      results: Array<{
        creator_id: number
        matches: MatchResult[]
        count: number
      }>
      total_creators: number
      total_matches: number
      processing_time_ms: number
    }>('/ai-services/batch_match/', request),

  // Statistics
  getStatistics: () =>
    api.get<MatchStatistics>('/ai-services/match_statistics/'),

  // Batch Embedding Updates
  batchUpdateEmbeddings: (creatorIds: number[], forceUpdate = false) =>
    api.post('/ai-services/batch_update_embeddings/', {
      creator_ids: creatorIds,
      force_update: forceUpdate
    }),

  // Health Check
  healthCheck: () =>
    api.get('/ai-services/health/')
}

export default matchingAPI
