"""
Django management command to populate personality quizzes
Creates default personality assessment quizzes for the platform
"""
from django.core.management.base import BaseCommand
from accounts.personality_models import PersonalityQuiz
import json

class Command(BaseCommand):
    help = 'Populate personality quizzes with default assessments'
    
    def handle(self, *args, **options):
        self.stdout.write('Creating personality quizzes...')
        
        # Big Five Personality Quiz
        big_five_questions = [
            {
                "id": "bf_1",
                "text": "I see myself as someone who is talkative",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "extraversion"
            },
            {
                "id": "bf_2", 
                "text": "I see myself as someone who tends to find fault with others",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "agreeableness",
                "reverse": True
            },
            {
                "id": "bf_3",
                "text": "I see myself as someone who does a thorough job",
                "type": "likert", 
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "conscientiousness"
            },
            {
                "id": "bf_4",
                "text": "I see myself as someone who is depressed, blue",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5], 
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "neuroticism"
            },
            {
                "id": "bf_5",
                "text": "I see myself as someone who is original, comes up with new ideas",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "openness"
            },
            {
                "id": "bf_6",
                "text": "I see myself as someone who is reserved",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "extraversion",
                "reverse": True
            },
            {
                "id": "bf_7",
                "text": "I see myself as someone who is helpful and unselfish with others",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "agreeableness"
            },
            {
                "id": "bf_8",
                "text": "I see myself as someone who can be somewhat careless",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "conscientiousness",
                "reverse": True
            },
            {
                "id": "bf_9",
                "text": "I see myself as someone who is relaxed, handles stress well",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "neuroticism",
                "reverse": True
            },
            {
                "id": "bf_10",
                "text": "I see myself as someone who is curious about many different things",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"],
                "trait": "openness"
            }
        ]
        
        big_five_quiz, created = PersonalityQuiz.objects.update_or_create(
            quiz_type='big_five',
            defaults={
                'title': 'Big Five Personality Assessment',
                'description': 'A scientifically-backed personality assessment measuring five key dimensions of personality that influence how you work and collaborate with others.',
                'questions': big_five_questions,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Big Five Personality Quiz'))
        else:
            self.stdout.write(self.style.WARNING('✓ Updated Big Five Personality Quiz'))
        
        # Creative Style Assessment
        creative_questions = [
            {
                "id": "cs_1",
                "text": "When starting a new creative project, I prefer to:",
                "type": "multiple_choice",
                "options": [
                    {"value": "plan", "text": "Plan everything in detail before starting"},
                    {"value": "outline", "text": "Create a rough outline and adapt as I go"},
                    {"value": "dive_in", "text": "Dive right in and let creativity flow"},
                    {"value": "research", "text": "Research extensively first"}
                ],
                "trait": "creative_approach"
            },
            {
                "id": "cs_2",
                "text": "I get my best creative ideas when:",
                "type": "multiple_choice",
                "options": [
                    {"value": "alone", "text": "Working alone in quiet spaces"},
                    {"value": "brainstorming", "text": "Brainstorming with others"},
                    {"value": "walking", "text": "Taking walks or doing physical activity"},
                    {"value": "pressure", "text": "Under pressure or tight deadlines"}
                ],
                "trait": "inspiration_source"
            },
            {
                "id": "cs_3",
                "text": "How comfortable are you with creative risks?",
                "type": "likert",
                "scale": [1, 2, 3, 4, 5],
                "labels": ["Very Uncomfortable", "Uncomfortable", "Neutral", "Comfortable", "Very Comfortable"],
                "trait": "risk_tolerance"
            },
            {
                "id": "cs_4",
                "text": "When receiving feedback on my work, I prefer:",
                "type": "multiple_choice",
                "options": [
                    {"value": "direct", "text": "Direct, honest criticism"},
                    {"value": "constructive", "text": "Constructive suggestions for improvement"},
                    {"value": "positive", "text": "Focus on what's working well"},
                    {"value": "detailed", "text": "Detailed technical analysis"}
                ],
                "trait": "feedback_preference"
            },
            {
                "id": "cs_5",
                "text": "I consider myself most creative when working on:",
                "type": "multiple_choice",
                "options": [
                    {"value": "personal", "text": "Personal passion projects"},
                    {"value": "collaborative", "text": "Collaborative team projects"},
                    {"value": "client", "text": "Client or commission work"},
                    {"value": "experimental", "text": "Experimental or avant-garde pieces"}
                ],
                "trait": "creative_context"
            }
        ]
        
        creative_quiz, created = PersonalityQuiz.objects.update_or_create(
            quiz_type='creative_style',
            defaults={
                'title': 'Creative Style Assessment',
                'description': 'Discover your unique creative process, inspiration sources, and preferred working styles to find the perfect creative collaborators.',
                'questions': creative_questions,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Creative Style Assessment'))
        else:
            self.stdout.write(self.style.WARNING('✓ Updated Creative Style Assessment'))
        
        # Collaboration Preference Quiz
        collab_questions = [
            {
                "id": "cp_1",
                "text": "In group projects, I naturally tend to:",
                "type": "multiple_choice",
                "options": [
                    {"value": "lead", "text": "Take charge and organize the team"},
                    {"value": "contribute", "text": "Contribute ideas and execute tasks equally"},
                    {"value": "support", "text": "Support others' visions with my skills"},
                    {"value": "specialize", "text": "Focus on my area of expertise"}
                ],
                "trait": "collaboration_role"
            },
            {
                "id": "cp_2",
                "text": "My ideal team size for creative projects is:",
                "type": "multiple_choice",
                "options": [
                    {"value": "solo", "text": "Just me (solo work)"},
                    {"value": "pair", "text": "2 people (partnership)"},
                    {"value": "small", "text": "3-4 people (small team)"},
                    {"value": "large", "text": "5+ people (large team)"}
                ],
                "trait": "team_size_preference"
            },
            {
                "id": "cp_3",
                "text": "How do you prefer to communicate during projects?",
                "type": "multiple_choice",
                "options": [
                    {"value": "frequent", "text": "Daily check-ins and constant updates"},
                    {"value": "scheduled", "text": "Scheduled meetings and milestone reviews"},
                    {"value": "asneeded", "text": "As-needed basis when issues arise"},
                    {"value": "minimal", "text": "Minimal communication, focus on work"}
                ],
                "trait": "communication_style"
            },
            {
                "id": "cp_4",
                "text": "When conflicts arise in creative work, I:",
                "type": "multiple_choice",
                "options": [
                    {"value": "address", "text": "Address them directly and immediately"},
                    {"value": "mediate", "text": "Try to find compromise solutions"},
                    {"value": "avoid", "text": "Prefer to avoid confrontation"},
                    {"value": "seek_help", "text": "Seek outside perspective or help"}
                ],
                "trait": "conflict_resolution"
            },
            {
                "id": "cp_5",
                "text": "I work best with collaborators who:",
                "type": "multiple_choice",
                "options": [
                    {"value": "similar", "text": "Have similar creative styles to mine"},
                    {"value": "complementary", "text": "Have complementary skills to mine"},
                    {"value": "experienced", "text": "Are more experienced than me"},
                    {"value": "experimental", "text": "Are willing to experiment and take risks"}
                ],
                "trait": "partner_preference"
            }
        ]
        
        collab_quiz, created = PersonalityQuiz.objects.update_or_create(
            quiz_type='collaboration_preference',
            defaults={
                'title': 'Collaboration Preference Assessment',
                'description': 'Understand your collaboration style, communication preferences, and ideal team dynamics to build successful creative partnerships.',
                'questions': collab_questions,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Collaboration Preference Assessment'))
        else:
            self.stdout.write(self.style.WARNING('✓ Updated Collaboration Preference Assessment'))
        
        # Work Style Assessment
        work_questions = [
            {
                "id": "ws_1",
                "text": "I prefer to work:",
                "type": "multiple_choice",
                "options": [
                    {"value": "morning", "text": "Early morning (6-10 AM)"},
                    {"value": "midday", "text": "Mid-day (10 AM - 2 PM)"},
                    {"value": "afternoon", "text": "Afternoon (2-6 PM)"},
                    {"value": "evening", "text": "Evening/Night (6 PM+)"}
                ],
                "trait": "work_schedule"
            },
            {
                "id": "ws_2",
                "text": "My ideal work environment is:",
                "type": "multiple_choice",
                "options": [
                    {"value": "quiet", "text": "Quiet and distraction-free"},
                    {"value": "music", "text": "With background music or sounds"},
                    {"value": "social", "text": "Around other people working"},
                    {"value": "varied", "text": "Changes depending on my mood"}
                ],
                "trait": "work_environment"
            },
            {
                "id": "ws_3",
                "text": "When facing creative blocks, I:",
                "type": "multiple_choice",
                "options": [
                    {"value": "push_through", "text": "Push through and keep working"},
                    {"value": "take_break", "text": "Take a break and come back later"},
                    {"value": "seek_input", "text": "Seek input from others"},
                    {"value": "switch_tasks", "text": "Switch to a different task or project"}
                ],
                "trait": "block_handling"
            },
            {
                "id": "ws_4",
                "text": "I prefer project timelines that are:",
                "type": "multiple_choice",
                "options": [
                    {"value": "tight", "text": "Tight and urgent (energizes me)"},
                    {"value": "moderate", "text": "Moderate with some pressure"},
                    {"value": "flexible", "text": "Flexible with room for iteration"},
                    {"value": "open", "text": "Open-ended without strict deadlines"}
                ],
                "trait": "deadline_preference"
            },
            {
                "id": "ws_5",
                "text": "I measure project success by:",
                "type": "multiple_choice",
                "options": [
                    {"value": "quality", "text": "Quality and artistic merit"},
                    {"value": "completion", "text": "Meeting deadlines and requirements"},
                    {"value": "innovation", "text": "Innovation and uniqueness"},
                    {"value": "impact", "text": "Audience response and impact"}
                ],
                "trait": "success_metrics"
            }
        ]
        
        work_quiz, created = PersonalityQuiz.objects.update_or_create(
            quiz_type='work_style',
            defaults={
                'title': 'Work Style Assessment',
                'description': 'Identify your optimal working conditions, creative process, and productivity patterns to find compatible collaborators.',
                'questions': work_questions,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created Work Style Assessment'))
        else:
            self.stdout.write(self.style.WARNING('✓ Updated Work Style Assessment'))
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 Successfully created/updated {PersonalityQuiz.objects.filter(is_active=True).count()} personality quizzes!'
            )
        )
