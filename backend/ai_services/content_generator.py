"""
AI Content Generation Service
Implements REQ-13, REQ-15: AI collaboration features and portfolio generation
"""
import openai
from django.conf import settings
from typing import Dict, Any, List
import logging
import json
import requests
from io import BytesIO
from PIL import Image
import base64
from django.core.cache import cache
from django.utils import timezone
from analytics.services import AnalyticsCollector

logger = logging.getLogger(__name__)

class ContentGenerator:
    """AI-powered content generation service"""
    
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
    
    @staticmethod
    def generate_music_for_lyrics(lyrics: str, style: str = "pop") -> Dict[str, Any]:
        """Generate music composition suggestions for given lyrics (REQ-13)"""
        try:
            prompt = f"""
            Create a detailed music composition guide for these lyrics:
            
            Lyrics: {lyrics}
            Style: {style}
            
            Provide a JSON response with:
            1. chord_progression: Array of chord progressions for verses/chorus
            2. tempo_bpm: Suggested tempo in BPM
            3. key_signature: Suggested key
            4. structure: Song structure (verse, chorus, bridge, etc.)
            5. instrumentation: Suggested instruments
            6. melody_notes: Basic melody suggestions for key phrases
            7. production_tips: Production and arrangement suggestions
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional music composer and producer. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Music generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate music composition',
                'chord_progression': ['C', 'Am', 'F', 'G'],
                'tempo_bpm': 120,
                'key_signature': 'C major'
            }
    
    @staticmethod
    def generate_visual_concept(description: str, art_style: str = "modern") -> Dict[str, Any]:
        """Generate visual art concept and composition guide"""
        try:
            prompt = f"""
            Create a detailed visual art concept for: {description}
            Art Style: {art_style}
            
            Provide a JSON response with:
            1. composition: Detailed composition description
            2. color_palette: Array of hex color codes
            3. techniques: Recommended art techniques
            4. materials: Suggested materials/tools
            5. lighting: Lighting setup description
            6. mood: Overall mood and atmosphere
            7. reference_styles: Similar art movements or artists
            8. step_by_step: Array of creation steps
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional visual artist and art director. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Visual concept generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate visual concept',
                'composition': 'Creative visual composition',
                'color_palette': ['#FF6B6B', '#4ECDC4', '#45B7D1']
            }
    
    @staticmethod
    def generate_story_outline(genre: str, theme: str, length: str = "short") -> Dict[str, Any]:
        """Generate story outline for writers"""
        try:
            prompt = f"""
            Create a detailed story outline:
            Genre: {genre}
            Theme: {theme}
            Length: {length}
            
            Provide a JSON response with:
            1. title_suggestions: Array of 3 title options
            2. plot_summary: One paragraph plot summary
            3. characters: Array of main characters with descriptions
            4. structure: Story structure breakdown
            5. key_scenes: Array of key scenes
            6. conflict: Main conflict description
            7. resolution: Resolution approach
            8. writing_tips: Genre-specific writing advice
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional story editor and creative writing instructor. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Story outline generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate story outline',
                'title_suggestions': ['Creative Story'],
                'plot_summary': 'An engaging narrative exploring the given theme.'
            }
    
    @staticmethod
    def generate_portfolio_content(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate AI portfolio content (REQ-15)"""
        try:
            category = profile_data.get('category', 'visual_arts')
            experience = profile_data.get('experience_level', 'intermediate')
            bio = profile_data.get('bio', '')
            
            prompt = f"""
            Generate a professional portfolio structure for a {category} creator:
            Experience Level: {experience}
            Bio: {bio}
            
            Provide a JSON response with:
            1. portfolio_sections: Array of recommended portfolio sections
            2. project_ideas: Array of 5 project suggestions with descriptions
            3. presentation_tips: Tips for presenting work effectively
            4. technical_requirements: Technical specs for portfolio pieces
            5. industry_standards: Industry-specific portfolio standards
            6. personal_branding: Personal branding suggestions
            7. portfolio_layout: Recommended layout structure
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional portfolio consultant and creative director. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            result['export_formats'] = ['PDF', 'Web Gallery', 'Print Ready']
            return result
            
        except Exception as e:
            logger.error(f"Portfolio generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate portfolio content',
                'project_ideas': ['Creative project showcase'],
                'export_formats': ['PDF']
            }
    
    @staticmethod
    def generate_collaboration_ideas(profile1_data: Dict, profile2_data: Dict) -> Dict[str, Any]:
        """Generate specific collaboration project ideas for two creators"""
        try:
            prompt = f"""
            Generate creative collaboration ideas for these two creators:
            
            Creator 1: {json.dumps(profile1_data, indent=2)}
            Creator 2: {json.dumps(profile2_data, indent=2)}
            
            Provide a JSON response with:
            1. project_ideas: Array of 5 specific collaboration projects
            2. role_distribution: How each creator contributes to each project
            3. timeline_estimates: Estimated timeline for each project
            4. required_resources: Resources needed for each project
            5. success_metrics: How to measure project success
            6. monetization_potential: Revenue opportunities
            7. skill_development: What each creator will learn
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a creative collaboration consultant specializing in cross-disciplinary projects. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Collaboration ideas generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate collaboration ideas',
                'project_ideas': ['Creative collaboration project']
            }
    
    @staticmethod
    def enhance_profile_bio(current_bio: str, category: str, experience: str) -> Dict[str, Any]:
        """AI-enhanced bio generation for profiles"""
        try:
            prompt = f"""
            Enhance this creator profile bio to be more engaging and professional:
            
            Current Bio: {current_bio}
            Category: {category}
            Experience: {experience}
            
            Create 3 different enhanced versions:
            1. Professional tone
            2. Creative/artistic tone  
            3. Gen-Z friendly tone
            
            Each should be 100-150 words and highlight the creator's unique value proposition.
            
            Provide JSON response with enhanced_bios array.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a professional copywriter specializing in creative profiles. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Bio enhancement failed: {e}")
            return {
                'success': False,
                'error': 'Failed to enhance bio',
                'enhanced_bios': [current_bio]
            }
    
    @staticmethod
    def generate_project_brief(collaboration_type: str, participants: List[str]) -> Dict[str, Any]:
        """Generate detailed project brief for collaborations"""
        try:
            prompt = f"""
            Create a comprehensive project brief for a {collaboration_type} collaboration:
            Participants: {', '.join(participants)}
            
            Provide a JSON response with:
            1. project_title: Catchy project title
            2. objective: Clear project objective
            3. deliverables: List of expected deliverables
            4. timeline: Project phases with deadlines
            5. roles_responsibilities: Each participant's role
            6. success_criteria: How to measure success
            7. budget_considerations: Cost factors to consider
            8. risk_mitigation: Potential risks and solutions
            9. communication_plan: How team will communicate
            10. quality_standards: Quality benchmarks
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional project manager specializing in creative collaborations. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1200,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Project brief generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate project brief',
                'project_title': f'{collaboration_type} Collaboration',
                'objective': 'Create innovative collaborative work'
            }
    
    @staticmethod
    def generate_marketing_copy(product_info: Dict[str, Any], target_audience: str) -> Dict[str, Any]:
        """Generate marketing copy for creator products/services"""
        try:
            prompt = f"""
            Create compelling marketing copy for this creator's offering:
            
            Product/Service: {json.dumps(product_info, indent=2)}
            Target Audience: {target_audience}
            
            Provide a JSON response with:
            1. headline: Attention-grabbing headline
            2. tagline: Memorable tagline
            3. description: Detailed description (150-200 words)
            4. key_benefits: Array of 5 key benefits
            5. call_to_action: Strong call-to-action phrases
            6. social_media_posts: Array of 3 social media post variations
            7. email_subject_lines: Array of 5 email subject line options
            8. value_proposition: Clear value proposition statement
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a professional copywriter and marketing strategist. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.8
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            
            # Track analytics
            AnalyticsCollector.track_event(
                'marketing_copy_generated',
                event_data={
                    'target_audience': target_audience,
                    'product_type': product_info.get('type', 'unknown')
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Marketing copy generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate marketing copy',
                'headline': 'Amazing Creative Work',
                'description': 'Professional creative services tailored to your needs.'
            }
    
    @staticmethod
    def generate_social_media_strategy(creator_profile: Dict[str, Any], goals: List[str]) -> Dict[str, Any]:
        """Generate comprehensive social media strategy for creators"""
        try:
            prompt = f"""
            Create a comprehensive social media strategy for this creator:
            
            Profile: {json.dumps(creator_profile, indent=2)}
            Goals: {', '.join(goals)}
            
            Provide a JSON response with:
            1. platform_strategy: Strategy for each major platform (Instagram, TikTok, Twitter, LinkedIn)
            2. content_calendar: 30-day content calendar with post ideas
            3. hashtag_strategy: Relevant hashtags for each platform
            4. engagement_tactics: Ways to increase engagement
            5. growth_strategies: Organic growth techniques
            6. brand_voice: Recommended brand voice and tone
            7. posting_schedule: Optimal posting times and frequency
            8. kpi_metrics: Key performance indicators to track
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a social media strategist specializing in creator economy. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Social media strategy generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate social media strategy',
                'platform_strategy': {'instagram': 'Share visual content regularly'},
                'posting_schedule': 'Daily posts recommended'
            }
    
    @staticmethod
    def generate_course_outline(topic: str, skill_level: str, duration: str) -> Dict[str, Any]:
        """Generate educational course outline for creators"""
        try:
            prompt = f"""
            Create a comprehensive course outline for teaching:
            
            Topic: {topic}
            Skill Level: {skill_level}
            Duration: {duration}
            
            Provide a JSON response with:
            1. course_title: Engaging course title
            2. course_description: Detailed course description
            3. learning_objectives: Array of learning objectives
            4. modules: Array of course modules with lessons
            5. assignments: Practical assignments for each module
            6. resources: Required and recommended resources
            7. assessment_methods: How to evaluate student progress
            8. prerequisites: What students should know beforehand
            9. target_audience: Who this course is for
            10. pricing_strategy: Suggested pricing tiers
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an educational content designer and curriculum specialist. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1800,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Course outline generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate course outline',
                'course_title': f'Learn {topic}',
                'modules': ['Introduction', 'Fundamentals', 'Advanced Techniques']
            }
    
    @staticmethod
    def generate_pitch_deck(business_idea: Dict[str, Any]) -> Dict[str, Any]:
        """Generate pitch deck content for creator businesses"""
        try:
            prompt = f"""
            Create a comprehensive pitch deck for this creative business:
            
            Business Idea: {json.dumps(business_idea, indent=2)}
            
            Provide a JSON response with:
            1. slide_structure: Array of slide titles and content
            2. problem_statement: Clear problem definition
            3. solution_overview: How the business solves the problem
            4. market_analysis: Target market and size
            5. business_model: Revenue streams and pricing
            6. competitive_advantage: What makes this unique
            7. financial_projections: Revenue and growth projections
            8. team_overview: Key team members and roles
            9. funding_requirements: How much funding needed and why
            10. call_to_action: What you're asking investors for
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a business consultant specializing in creative industries and startup pitch decks. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            return result
            
        except Exception as e:
            logger.error(f"Pitch deck generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate pitch deck',
                'slide_structure': ['Problem', 'Solution', 'Market', 'Business Model'],
                'problem_statement': 'Identifying market opportunity'
            }
    
    @staticmethod
    def generate_contract_template(collaboration_type: str, project_details: Dict[str, Any]) -> Dict[str, Any]:
        """Generate legal contract templates for collaborations"""
        try:
            prompt = f"""
            Create a professional contract template for this collaboration:
            
            Type: {collaboration_type}
            Project Details: {json.dumps(project_details, indent=2)}
            
            Provide a JSON response with:
            1. contract_sections: Array of contract sections with content
            2. key_terms: Important terms and definitions
            3. payment_terms: Payment structure and schedule
            4. intellectual_property: IP ownership and usage rights
            5. deliverables: Specific deliverables and deadlines
            6. termination_clauses: How to end the contract
            7. dispute_resolution: How to handle disagreements
            8. liability_limitations: Liability and insurance considerations
            9. confidentiality: Non-disclosure provisions
            10. signatures: Signature requirements and process
            
            Note: This is a template for reference only and should be reviewed by legal counsel.
            """
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a legal document specialist focusing on creative industry contracts. Always include disclaimers about legal review. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.5
            )
            
            result = json.loads(response.choices[0].message.content)
            result['success'] = True
            result['legal_disclaimer'] = 'This template is for reference only. Please consult with a qualified attorney before using any contract.'
            return result
            
        except Exception as e:
            logger.error(f"Contract template generation failed: {e}")
            return {
                'success': False,
                'error': 'Failed to generate contract template',
                'legal_disclaimer': 'Please consult with a qualified attorney for all legal documents.',
                'contract_sections': ['Parties', 'Scope of Work', 'Payment Terms', 'Signatures']
            }
