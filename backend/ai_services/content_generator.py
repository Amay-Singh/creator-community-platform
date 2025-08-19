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
