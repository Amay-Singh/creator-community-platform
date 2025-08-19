"""
AI Content Validation Service
Implements REQ-2: AI-based content validation to prevent fake/repetitive content
"""
import openai
import hashlib
import json
from typing import Dict, List, Tuple, Optional
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image
import io
import requests
from .models import ContentValidation

class ContentValidator:
    """
    AI-powered content validation service
    """
    
    def __init__(self):
        self.client = None
        self.duplicate_threshold = 0.85
        self.fake_content_threshold = 0.7
    
    def _get_client(self):
        """Lazy initialization of OpenAI client"""
        if self.client is None:
            try:
                self.client = openai.OpenAI(api_key=getattr(settings, 'OPENAI_API_KEY', None))
            except Exception:
                self.client = None
        return self.client
    
    def validate_portfolio_item(self, portfolio_item, user_profile) -> Dict[str, any]:
        """
        Comprehensive validation of portfolio items
        
        Args:
            portfolio_item: PortfolioItem instance
            user_profile: CreatorProfile instance
        
        Returns:
            Dict with validation results
        """
        validation_results = {
            'is_valid': True,
            'confidence_score': 0.0,
            'issues': [],
            'recommendations': [],
            'duplicate_check': None,
            'authenticity_check': None,
            'content_quality': None
        }
        
        # 1. Duplicate content detection
        duplicate_result = self._check_duplicate_content(portfolio_item)
        validation_results['duplicate_check'] = duplicate_result
        
        if duplicate_result['is_duplicate']:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Duplicate content detected')
        
        # 2. Authenticity verification
        auth_result = self._verify_authenticity(portfolio_item, user_profile)
        validation_results['authenticity_check'] = auth_result
        
        if not auth_result['is_authentic']:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Content authenticity questionable')
        
        # 3. Content quality assessment
        quality_result = self._assess_content_quality(portfolio_item)
        validation_results['content_quality'] = quality_result
        
        if quality_result['quality_score'] < 0.3:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Content quality below minimum standards')
        
        # 4. Generate recommendations
        validation_results['recommendations'] = self._generate_recommendations(
            duplicate_result, auth_result, quality_result
        )
        
        # 5. Calculate overall confidence
        validation_results['confidence_score'] = self._calculate_confidence(
            duplicate_result, auth_result, quality_result
        )
        
        # 6. Store validation record
        self._store_validation_record(portfolio_item, validation_results)
        
        return validation_results
    
    def _check_duplicate_content(self, portfolio_item) -> Dict[str, any]:
        """Check for duplicate content using content hashing and AI comparison"""
        
        result = {
            'is_duplicate': False,
            'similarity_score': 0.0,
            'similar_items': [],
            'hash_matches': []
        }
        
        try:
            # Generate content hash
            content_hash = self._generate_content_hash(portfolio_item)
            
            # Check for exact hash matches
            from accounts.models import PortfolioItem
            hash_matches = PortfolioItem.objects.filter(
                content_hash=content_hash
            ).exclude(id=portfolio_item.id)
            
            if hash_matches.exists():
                result['is_duplicate'] = True
                result['similarity_score'] = 1.0
                result['hash_matches'] = [str(item.id) for item in hash_matches]
                return result
            
            # AI-based similarity check for near-duplicates
            if portfolio_item.description:
                similar_items = self._find_similar_content(portfolio_item)
                if similar_items:
                    max_similarity = max(item['similarity'] for item in similar_items)
                    result['similarity_score'] = max_similarity
                    result['similar_items'] = similar_items
                    
                    if max_similarity > self.duplicate_threshold:
                        result['is_duplicate'] = True
            
        except Exception as e:
            # Log error but don't fail validation
            result['error'] = str(e)
        
        return result
    
    def _verify_authenticity(self, portfolio_item, user_profile) -> Dict[str, any]:
        """Verify content authenticity using AI analysis"""
        
        result = {
            'is_authentic': True,
            'authenticity_score': 0.8,
            'flags': [],
            'analysis': ''
        }
        
        client = self._get_client()
        if not client:
            return result
        
        try:
            # Prepare content for analysis
            analysis_prompt = self._build_authenticity_prompt(portfolio_item, user_profile)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content authenticity analyzer. Assess whether creative content appears to be original work by the claimed creator."
                    },
                    {
                        "role": "user",
                        "content": analysis_prompt
                    }
                ],
                temperature=0.2,
                max_tokens=500
            )
            
            analysis_text = response.choices[0].message.content
            result['analysis'] = analysis_text
            
            # Parse AI response for authenticity indicators
            authenticity_indicators = self._parse_authenticity_response(analysis_text)
            result.update(authenticity_indicators)
            
        except Exception as e:
            # Fallback to basic checks
            result = self._basic_authenticity_check(portfolio_item, user_profile)
        
        return result
    
    def _assess_content_quality(self, portfolio_item) -> Dict[str, any]:
        """Assess content quality using AI analysis"""
        
        result = {
            'quality_score': 0.7,
            'technical_quality': 0.7,
            'creative_merit': 0.7,
            'completeness': 0.8,
            'feedback': []
        }
        
        client = self._get_client()
        if not client:
            return result
        
        try:
            quality_prompt = self._build_quality_assessment_prompt(portfolio_item)
            
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a creative arts quality assessor. Evaluate portfolio items for technical quality, creative merit, and completeness."
                    },
                    {
                        "role": "user",
                        "content": quality_prompt
                    }
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            quality_analysis = response.choices[0].message.content
            quality_scores = self._parse_quality_response(quality_analysis)
            result.update(quality_scores)
            
        except Exception as e:
            # Use basic quality metrics
            result = self._basic_quality_assessment(portfolio_item)
        
        return result
    
    def _generate_content_hash(self, portfolio_item) -> str:
        """Generate hash for content deduplication"""
        
        hash_content = ""
        
        # Include text content
        if portfolio_item.title:
            hash_content += portfolio_item.title.lower().strip()
        if portfolio_item.description:
            hash_content += portfolio_item.description.lower().strip()
        
        # Include file metadata if available
        if hasattr(portfolio_item, 'media_file') and portfolio_item.media_file:
            try:
                # For images, include basic metadata
                if portfolio_item.media_type == 'image':
                    with Image.open(portfolio_item.media_file) as img:
                        hash_content += f"{img.size[0]}x{img.size[1]}"
                        if hasattr(img, 'format'):
                            hash_content += img.format
            except Exception:
                pass
        
        # Generate SHA-256 hash
        return hashlib.sha256(hash_content.encode('utf-8')).hexdigest()
    
    def _find_similar_content(self, portfolio_item) -> List[Dict]:
        """Find similar content using text similarity"""
        
        if not portfolio_item.description:
            return []
        
        similar_items = []
        
        try:
            from accounts.models import PortfolioItem
            from django.db.models import Q
            
            # Find items with similar descriptions
            other_items = PortfolioItem.objects.filter(
                Q(media_type=portfolio_item.media_type) |
                Q(profile__category=portfolio_item.profile.category)
            ).exclude(id=portfolio_item.id)[:50]  # Limit for performance
            
            for item in other_items:
                if item.description:
                    similarity = self._calculate_text_similarity(
                        portfolio_item.description,
                        item.description
                    )
                    
                    if similarity > 0.5:  # Threshold for similarity
                        similar_items.append({
                            'item_id': str(item.id),
                            'similarity': similarity,
                            'title': item.title
                        })
            
        except Exception as e:
            pass
        
        return sorted(similar_items, key=lambda x: x['similarity'], reverse=True)[:5]
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate basic text similarity using word overlap"""
        
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _build_authenticity_prompt(self, portfolio_item, user_profile) -> str:
        """Build prompt for authenticity analysis"""
        
        prompt = f"""
        Analyze this creative portfolio item for authenticity:
        
        Creator Profile:
        - Name: {user_profile.display_name}
        - Category: {user_profile.get_category_display()}
        - Experience: {user_profile.get_experience_level_display()}
        - Bio: {user_profile.bio[:200]}
        
        Portfolio Item:
        - Title: {portfolio_item.title}
        - Type: {portfolio_item.get_media_type_display()}
        - Description: {portfolio_item.description[:500]}
        - Tags: {', '.join(portfolio_item.tags) if portfolio_item.tags else 'None'}
        
        Assess authenticity on a scale of 0.0-1.0 and identify any red flags:
        - Does the content match the creator's stated experience level?
        - Is the description consistent with the creator's style and category?
        - Are there any indicators of plagiarism or stock content?
        - Does the technical quality match claimed experience?
        
        Respond with:
        AUTHENTICITY_SCORE: [0.0-1.0]
        FLAGS: [list any concerns]
        ANALYSIS: [brief explanation]
        """
        
        return prompt
    
    def _build_quality_assessment_prompt(self, portfolio_item) -> str:
        """Build prompt for quality assessment"""
        
        prompt = f"""
        Assess the quality of this creative portfolio item:
        
        Item Details:
        - Title: {portfolio_item.title}
        - Type: {portfolio_item.get_media_type_display()}
        - Description: {portfolio_item.description[:500]}
        
        Evaluate on these dimensions (0.0-1.0 scale):
        1. Technical Quality - execution, skill level, craftsmanship
        2. Creative Merit - originality, artistic value, innovation
        3. Completeness - is it a finished work or rough draft?
        
        Provide specific feedback for improvement.
        
        Respond with:
        TECHNICAL_QUALITY: [0.0-1.0]
        CREATIVE_MERIT: [0.0-1.0]
        COMPLETENESS: [0.0-1.0]
        FEEDBACK: [constructive suggestions]
        """
        
        return prompt
    
    def _parse_authenticity_response(self, analysis_text: str) -> Dict[str, any]:
        """Parse AI authenticity analysis response"""
        
        result = {
            'is_authentic': True,
            'authenticity_score': 0.8,
            'flags': []
        }
        
        try:
            lines = analysis_text.split('\n')
            for line in lines:
                if 'AUTHENTICITY_SCORE:' in line:
                    score_str = line.split(':')[1].strip()
                    score = float(score_str)
                    result['authenticity_score'] = score
                    result['is_authentic'] = score >= self.fake_content_threshold
                
                elif 'FLAGS:' in line:
                    flags_str = line.split(':', 1)[1].strip()
                    if flags_str and flags_str != 'None':
                        result['flags'] = [flag.strip() for flag in flags_str.split(',')]
        
        except Exception:
            pass
        
        return result
    
    def _parse_quality_response(self, quality_text: str) -> Dict[str, any]:
        """Parse AI quality assessment response"""
        
        result = {
            'technical_quality': 0.7,
            'creative_merit': 0.7,
            'completeness': 0.8,
            'feedback': []
        }
        
        try:
            lines = quality_text.split('\n')
            for line in lines:
                if 'TECHNICAL_QUALITY:' in line:
                    result['technical_quality'] = float(line.split(':')[1].strip())
                elif 'CREATIVE_MERIT:' in line:
                    result['creative_merit'] = float(line.split(':')[1].strip())
                elif 'COMPLETENESS:' in line:
                    result['completeness'] = float(line.split(':')[1].strip())
                elif 'FEEDBACK:' in line:
                    feedback_str = line.split(':', 1)[1].strip()
                    if feedback_str:
                        result['feedback'] = [feedback_str]
            
            # Calculate overall quality score
            result['quality_score'] = (
                result['technical_quality'] * 0.4 +
                result['creative_merit'] * 0.4 +
                result['completeness'] * 0.2
            )
        
        except Exception:
            pass
        
        return result
    
    def _basic_authenticity_check(self, portfolio_item, user_profile) -> Dict[str, any]:
        """Basic authenticity check without AI"""
        
        result = {
            'is_authentic': True,
            'authenticity_score': 0.7,
            'flags': [],
            'analysis': 'Basic authenticity check performed'
        }
        
        # Check for basic red flags
        if portfolio_item.description:
            desc_lower = portfolio_item.description.lower()
            
            # Check for stock content indicators
            stock_indicators = ['stock', 'template', 'sample', 'example', 'placeholder']
            if any(indicator in desc_lower for indicator in stock_indicators):
                result['flags'].append('Possible stock content')
                result['authenticity_score'] -= 0.2
            
            # Check description length vs experience
            if user_profile.experience_level == 'beginner' and len(portfolio_item.description) > 1000:
                result['flags'].append('Description complexity vs experience mismatch')
                result['authenticity_score'] -= 0.1
        
        result['is_authentic'] = result['authenticity_score'] >= self.fake_content_threshold
        
        return result
    
    def _basic_quality_assessment(self, portfolio_item) -> Dict[str, any]:
        """Basic quality assessment without AI"""
        
        result = {
            'quality_score': 0.6,
            'technical_quality': 0.6,
            'creative_merit': 0.6,
            'completeness': 0.7,
            'feedback': []
        }
        
        # Basic completeness check
        if portfolio_item.title and portfolio_item.description:
            result['completeness'] = 0.8
            
            if len(portfolio_item.description) > 100:
                result['completeness'] = 0.9
        else:
            result['completeness'] = 0.4
            result['feedback'].append('Add more detailed description')
        
        # Update overall score
        result['quality_score'] = (
            result['technical_quality'] * 0.4 +
            result['creative_merit'] * 0.4 +
            result['completeness'] * 0.2
        )
        
        return result
    
    def _generate_recommendations(self, duplicate_result, auth_result, quality_result) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        if duplicate_result['is_duplicate']:
            recommendations.append("Create original content to avoid duplication issues")
        
        if not auth_result['is_authentic']:
            recommendations.append("Ensure all content is your original work")
            if auth_result['flags']:
                recommendations.extend([f"Address: {flag}" for flag in auth_result['flags']])
        
        if quality_result['quality_score'] < 0.7:
            recommendations.append("Consider improving technical execution")
            recommendations.extend(quality_result.get('feedback', []))
        
        if quality_result['completeness'] < 0.7:
            recommendations.append("Add more detailed description and context")
        
        return recommendations
    
    def _calculate_confidence(self, duplicate_result, auth_result, quality_result) -> float:
        """Calculate overall validation confidence score"""
        
        confidence = 0.8  # Base confidence
        
        # Adjust based on duplicate check
        if duplicate_result.get('error'):
            confidence -= 0.1
        
        # Adjust based on authenticity check
        if auth_result.get('error'):
            confidence -= 0.1
        else:
            confidence = min(confidence, auth_result['authenticity_score'])
        
        # Adjust based on quality assessment
        if quality_result.get('error'):
            confidence -= 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _store_validation_record(self, portfolio_item, validation_results):
        """Store validation record in database"""
        
        try:
            ContentValidation.objects.create(
                portfolio_item=portfolio_item,
                is_valid=validation_results['is_valid'],
                confidence_score=validation_results['confidence_score'],
                validation_data=validation_results,
                issues=validation_results['issues'],
                recommendations=validation_results['recommendations']
            )
        except Exception as e:
            # Log error but don't fail validation
            pass

# Service instance
content_validator = ContentValidator()
