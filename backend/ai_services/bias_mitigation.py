"""
Bias Mitigation for AI Matching Engine
Implements fairness controls and bias detection for creator recommendations
"""
import numpy as np
import logging
from typing import List, Dict, Any, Set
from dataclasses import dataclass
from accounts.models import CreatorProfile

logger = logging.getLogger(__name__)

@dataclass
class BiasMetrics:
    """Metrics for tracking bias in recommendations"""
    demographic_distribution: Dict[str, float]
    exposure_parity: Dict[str, float]
    recommendation_diversity: float
    protected_group_representation: Dict[str, float]

class FairnessMitigator:
    """
    Implements bias mitigation strategies for AI matching
    """
    
    def __init__(self):
        self.protected_attributes = ['gender', 'age_group', 'location', 'experience_level']
        self.min_diversity_threshold = 0.3
        self.max_bias_ratio = 2.0  # Max ratio between groups
        
    def mitigate_bias(self, candidates: List, user_profile: CreatorProfile) -> List:
        """
        Apply bias mitigation to candidate list
        
        Args:
            candidates: List of MatchCandidate objects
            user_profile: Requesting user's profile
            
        Returns:
            Bias-mitigated list of candidates
        """
        try:
            if len(candidates) <= 1:
                return candidates
            
            # Analyze current bias
            bias_metrics = self._analyze_bias(candidates)
            
            # Apply mitigation strategies
            mitigated_candidates = self._apply_demographic_parity(candidates)
            mitigated_candidates = self._apply_diversity_injection(mitigated_candidates)
            mitigated_candidates = self._apply_exposure_controls(mitigated_candidates, user_profile)
            
            # Log bias metrics
            self._log_bias_metrics(bias_metrics, user_profile.user.id)
            
            return mitigated_candidates
            
        except Exception as e:
            logger.error(f"Error in bias mitigation: {str(e)}")
            return candidates  # Return original on error
    
    def _analyze_bias(self, candidates: List) -> BiasMetrics:
        """Analyze bias in current candidate list"""
        try:
            total_candidates = len(candidates)
            if total_candidates == 0:
                return BiasMetrics({}, {}, 0.0, {})
            
            # Get candidate profiles
            candidate_profiles = []
            for candidate in candidates:
                try:
                    profile = CreatorProfile.objects.get(id=candidate.profile_id)
                    candidate_profiles.append(profile)
                except CreatorProfile.DoesNotExist:
                    continue
            
            # Analyze demographic distribution
            demographic_dist = self._calculate_demographic_distribution(candidate_profiles)
            
            # Calculate exposure parity
            exposure_parity = self._calculate_exposure_parity(candidates)
            
            # Calculate diversity score
            diversity_score = self._calculate_diversity_score(candidate_profiles)
            
            # Protected group representation
            protected_repr = self._calculate_protected_representation(candidate_profiles)
            
            return BiasMetrics(
                demographic_distribution=demographic_dist,
                exposure_parity=exposure_parity,
                recommendation_diversity=diversity_score,
                protected_group_representation=protected_repr
            )
            
        except Exception as e:
            logger.error(f"Error analyzing bias: {str(e)}")
            return BiasMetrics({}, {}, 0.0, {})
    
    def _apply_demographic_parity(self, candidates: List) -> List:
        """Apply demographic parity constraints"""
        try:
            if len(candidates) <= 5:
                return candidates  # Too few to apply parity
            
            # Group candidates by demographic attributes
            demographic_groups = self._group_by_demographics(candidates)
            
            # Calculate target representation for each group
            target_per_group = max(1, len(candidates) // len(demographic_groups))
            
            # Rebalance groups
            balanced_candidates = []
            remaining_slots = len(candidates)
            
            for group_key, group_candidates in demographic_groups.items():
                # Take up to target number from each group
                take_count = min(target_per_group, len(group_candidates), remaining_slots)
                
                # Sort by score and take top candidates
                group_candidates.sort(key=lambda x: x.score, reverse=True)
                balanced_candidates.extend(group_candidates[:take_count])
                remaining_slots -= take_count
                
                if remaining_slots <= 0:
                    break
            
            # Fill remaining slots with highest scoring candidates
            if remaining_slots > 0:
                all_remaining = []
                for group_candidates in demographic_groups.values():
                    all_remaining.extend(group_candidates[target_per_group:])
                
                all_remaining.sort(key=lambda x: x.score, reverse=True)
                balanced_candidates.extend(all_remaining[:remaining_slots])
            
            return balanced_candidates
            
        except Exception as e:
            logger.error(f"Error applying demographic parity: {str(e)}")
            return candidates
    
    def _apply_diversity_injection(self, candidates: List) -> List:
        """Inject diversity into candidate list"""
        try:
            if len(candidates) <= 3:
                return candidates
            
            # Calculate current diversity
            current_diversity = self._calculate_candidate_diversity(candidates)
            
            if current_diversity >= self.min_diversity_threshold:
                return candidates  # Already diverse enough
            
            # Inject diverse candidates
            diverse_candidates = []
            used_attributes = set()
            
            for candidate in candidates:
                candidate_attrs = self._get_candidate_attributes(candidate)
                
                # Check if this candidate adds diversity
                if not used_attributes or not candidate_attrs.issubset(used_attributes):
                    diverse_candidates.append(candidate)
                    used_attributes.update(candidate_attrs)
                elif len(diverse_candidates) < len(candidates) * 0.7:
                    # Still add high-scoring candidates
                    diverse_candidates.append(candidate)
            
            # Fill remaining slots with original candidates
            remaining_count = len(candidates) - len(diverse_candidates)
            if remaining_count > 0:
                remaining_candidates = [c for c in candidates if c not in diverse_candidates]
                remaining_candidates.sort(key=lambda x: x.score, reverse=True)
                diverse_candidates.extend(remaining_candidates[:remaining_count])
            
            return diverse_candidates
            
        except Exception as e:
            logger.error(f"Error applying diversity injection: {str(e)}")
            return candidates
    
    def _apply_exposure_controls(self, candidates: List, user_profile: CreatorProfile) -> List:
        """Apply exposure controls to prevent filter bubbles"""
        try:
            # Implement exposure controls to ensure users see diverse content
            # This prevents echo chambers and promotes discovery
            
            controlled_candidates = []
            user_category = user_profile.category
            user_skills = set(user_profile.skills or [])
            
            same_category_count = 0
            different_category_count = 0
            max_same_category = max(1, len(candidates) // 2)  # At most 50% same category
            
            for candidate in candidates:
                try:
                    candidate_profile = CreatorProfile.objects.get(id=candidate.profile_id)
                    candidate_category = candidate_profile.category
                    
                    if candidate_category == user_category:
                        if same_category_count < max_same_category:
                            controlled_candidates.append(candidate)
                            same_category_count += 1
                    else:
                        controlled_candidates.append(candidate)
                        different_category_count += 1
                        
                except CreatorProfile.DoesNotExist:
                    continue
            
            return controlled_candidates
            
        except Exception as e:
            logger.error(f"Error applying exposure controls: {str(e)}")
            return candidates
    
    def _group_by_demographics(self, candidates: List) -> Dict[str, List]:
        """Group candidates by demographic attributes"""
        groups = {}
        
        for candidate in candidates:
            try:
                profile = CreatorProfile.objects.get(id=candidate.profile_id)
                
                # Create demographic key
                demo_key = self._create_demographic_key(profile)
                
                if demo_key not in groups:
                    groups[demo_key] = []
                groups[demo_key].append(candidate)
                
            except CreatorProfile.DoesNotExist:
                continue
        
        return groups
    
    def _create_demographic_key(self, profile: CreatorProfile) -> str:
        """Create demographic grouping key for a profile"""
        # Simplified demographic grouping
        category = profile.category or 'unknown'
        
        # Location grouping (country level)
        location_group = 'unknown'
        if profile.location:
            location_parts = profile.location.split(',')
            if len(location_parts) > 1:
                location_group = location_parts[-1].strip().lower()
        
        # Experience level grouping
        experience_level = self._get_experience_group(profile)
        
        return f"{category}_{location_group}_{experience_level}"
    
    def _get_experience_group(self, profile: CreatorProfile) -> str:
        """Get experience level group for a profile"""
        portfolio_count = profile.portfolio_items.count() if hasattr(profile, 'portfolio_items') else 0
        skills_count = len(profile.skills or [])
        
        if portfolio_count >= 5 and skills_count >= 5:
            return 'experienced'
        elif portfolio_count >= 2 and skills_count >= 3:
            return 'intermediate'
        else:
            return 'beginner'
    
    def _calculate_demographic_distribution(self, profiles: List[CreatorProfile]) -> Dict[str, float]:
        """Calculate demographic distribution in candidate list"""
        if not profiles:
            return {}
        
        total = len(profiles)
        distribution = {}
        
        # Category distribution
        categories = {}
        for profile in profiles:
            category = profile.category or 'unknown'
            categories[category] = categories.get(category, 0) + 1
        
        for category, count in categories.items():
            distribution[f"category_{category}"] = count / total
        
        return distribution
    
    def _calculate_exposure_parity(self, candidates: List) -> Dict[str, float]:
        """Calculate exposure parity metrics"""
        if not candidates:
            return {}
        
        # Calculate average scores by group
        group_scores = {}
        group_counts = {}
        
        for candidate in candidates:
            try:
                profile = CreatorProfile.objects.get(id=candidate.profile_id)
                group_key = profile.category or 'unknown'
                
                if group_key not in group_scores:
                    group_scores[group_key] = 0.0
                    group_counts[group_key] = 0
                
                group_scores[group_key] += candidate.score
                group_counts[group_key] += 1
                
            except CreatorProfile.DoesNotExist:
                continue
        
        # Calculate average scores
        exposure_parity = {}
        for group_key in group_scores:
            if group_counts[group_key] > 0:
                avg_score = group_scores[group_key] / group_counts[group_key]
                exposure_parity[group_key] = avg_score
        
        return exposure_parity
    
    def _calculate_diversity_score(self, profiles: List[CreatorProfile]) -> float:
        """Calculate diversity score for candidate list"""
        if len(profiles) <= 1:
            return 0.0
        
        # Count unique values across different attributes
        unique_categories = len(set(p.category for p in profiles if p.category))
        unique_locations = len(set(p.location for p in profiles if p.location))
        # Skills diversity (placeholder - skills field doesn't exist in current model)
        all_skills = set()
        for profile in profiles:
            # Use category as proxy for skills diversity
            all_skills.add(profile.category)
        
        unique_skills = len(all_skills)
        avg_skills_per_profile = 1.0  # Placeholder
        
        total_candidates = len(profiles)
        diversity_score = (unique_categories + unique_locations + unique_skills) / (total_candidates * 3)
        
        return min(diversity_score, 1.0)
    
    def _calculate_protected_representation(self, profiles: List[CreatorProfile]) -> Dict[str, float]:
        """Calculate representation of protected groups"""
        if not profiles:
            return {}
        
        total = len(profiles)
        representation = {}
        
        # Experience level representation
        experience_groups = {'beginner': 0, 'intermediate': 0, 'experienced': 0}
        for profile in profiles:
            exp_group = self._get_experience_group(profile)
            experience_groups[exp_group] += 1
        
        for group, count in experience_groups.items():
            representation[f"experience_{group}"] = count / total
        
        return representation
    
    def _calculate_candidate_diversity(self, candidates: List) -> float:
        """Calculate diversity score for candidate list"""
        if len(candidates) <= 1:
            return 0.0
        
        # Get unique attributes across candidates
        unique_attrs = set()
        for candidate in candidates:
            attrs = self._get_candidate_attributes(candidate)
            unique_attrs.update(attrs)
        
        # Diversity is ratio of unique attributes to total possible
        max_possible_attrs = len(candidates) * 3  # Rough estimate
        return len(unique_attrs) / max_possible_attrs
    
    def _get_candidate_attributes(self, candidate) -> Set[str]:
        """Get attribute set for a candidate"""
        try:
            profile = CreatorProfile.objects.get(id=candidate.profile_id)
            attrs = set()
            
            if profile.category:
                attrs.add(f"category_{profile.category}")
            
            if profile.location:
                attrs.add(f"location_{profile.location.split(',')[-1].strip().lower()}")
            
            exp_group = self._get_experience_group(profile)
            attrs.add(f"experience_{exp_group}")
            
            return attrs
            
        except CreatorProfile.DoesNotExist:
            return set()
    
    def _log_bias_metrics(self, metrics: BiasMetrics, user_id: str):
        """Log bias metrics for monitoring"""
        logger.info(f"Bias metrics for user {user_id}: "
                   f"diversity={metrics.recommendation_diversity:.3f}, "
                   f"groups={len(metrics.demographic_distribution)}")
        
        # In production, would send to monitoring system
        # self.metrics_collector.record_bias_metrics(user_id, metrics)
