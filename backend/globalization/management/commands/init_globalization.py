"""
Initialize globalization data for Phase 10
"""
from django.core.management.base import BaseCommand
from globalization.models import Language, Currency, Region


class Command(BaseCommand):
    help = 'Initialize globalization data for Phase 10'

    def handle(self, *args, **options):
        self.stdout.write('Initializing globalization data...')
        
        # Create languages
        languages = [
            ('en', 'English', 'English', True, False),
            ('es', 'Spanish', 'Español', True, False),
            ('fr', 'French', 'Français', True, False),
            ('de', 'German', 'Deutsch', True, False),
            ('zh', 'Chinese', '中文', True, True),
            ('ja', 'Japanese', '日本語', True, True),
            ('ko', 'Korean', '한국어', True, True),
            ('ar', 'Arabic', 'العربية', True, True),
            ('pt', 'Portuguese', 'Português', True, False),
            ('it', 'Italian', 'Italiano', True, False),
            ('ru', 'Russian', 'Русский', True, False),
            ('hi', 'Hindi', 'हिन्दी', True, False),
            ('nl', 'Dutch', 'Nederlands', True, False),
            ('sv', 'Swedish', 'Svenska', True, False),
            ('no', 'Norwegian', 'Norsk', True, False),
        ]
        
        for code, name, native_name, is_active, is_rtl in languages:
            language, created = Language.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'native_name': native_name,
                    'is_active': is_active,
                    'is_rtl': is_rtl
                }
            )
            if created:
                self.stdout.write(f'Created language: {name}')
        
        # Create currencies
        currencies = [
            ('USD', 'US Dollar', '$', True),
            ('EUR', 'Euro', '€', True),
            ('GBP', 'British Pound', '£', True),
            ('JPY', 'Japanese Yen', '¥', True),
            ('CAD', 'Canadian Dollar', 'C$', True),
            ('AUD', 'Australian Dollar', 'A$', True),
            ('CHF', 'Swiss Franc', 'CHF', True),
            ('CNY', 'Chinese Yuan', '¥', True),
            ('INR', 'Indian Rupee', '₹', True),
            ('KRW', 'South Korean Won', '₩', True),
        ]
        
        for code, name, symbol, is_active in currencies:
            currency, created = Currency.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'symbol': symbol,
                    'is_active': is_active
                }
            )
            if created:
                self.stdout.write(f'Created currency: {name}')
        
        # Create regions with default currencies and languages
        usd = Currency.objects.get(code='USD')
        eur = Currency.objects.get(code='EUR')
        en = Language.objects.get(code='en')
        
        regions = [
            ('NA', 'North America', True, usd, en),
            ('EU', 'Europe', True, eur, en),
            ('AS', 'Asia', True, usd, en),
            ('SA', 'South America', True, usd, en),
            ('AF', 'Africa', True, usd, en),
            ('OC', 'Oceania', True, usd, en),
        ]
        
        for code, name, is_active, default_currency, default_language in regions:
            region, created = Region.objects.get_or_create(
                code=code,
                defaults={
                    'name': name,
                    'is_active': is_active,
                    'default_currency': default_currency,
                    'default_language': default_language
                }
            )
            if created:
                self.stdout.write(f'Created region: {name}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully initialized globalization data!')
        )
