"""
Management command to initialize subscription plans
"""
from django.core.management.base import BaseCommand
from accounts.subscription_models import SubscriptionPlan

class Command(BaseCommand):
    help = 'Initialize default subscription plans'

    def handle(self, *args, **options):
        plans = [
            {
                'name': 'Free',
                'plan_type': 'free',
                'description': 'Basic features for getting started',
                'price_monthly': 0.00,
                'price_yearly': 0.00,
                'max_portfolio_items': 5,
                'max_collaborations': 2,
                'ai_generations_per_month': 10,
                'storage_gb': 1,
                'priority_support': False,
                'advanced_analytics': False,
                'custom_branding': False,
                'api_access': False,
            },
            {
                'name': 'Basic',
                'plan_type': 'basic',
                'description': 'Perfect for individual creators',
                'price_monthly': 9.99,
                'price_yearly': 99.99,
                'max_portfolio_items': 25,
                'max_collaborations': 5,
                'ai_generations_per_month': 50,
                'storage_gb': 5,
                'priority_support': False,
                'advanced_analytics': True,
                'custom_branding': False,
                'api_access': False,
            },
            {
                'name': 'Pro',
                'plan_type': 'pro',
                'description': 'Advanced features for professional creators',
                'price_monthly': 29.99,
                'price_yearly': 299.99,
                'max_portfolio_items': 100,
                'max_collaborations': 15,
                'ai_generations_per_month': 200,
                'storage_gb': 25,
                'priority_support': True,
                'advanced_analytics': True,
                'custom_branding': True,
                'api_access': True,
            }
        ]

        for plan_data in plans:
            plan, created = SubscriptionPlan.objects.get_or_create(
                plan_type=plan_data['plan_type'],
                defaults=plan_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created plan: {plan.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Plan already exists: {plan.name}')
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully initialized subscription plans')
        )
