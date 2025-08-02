from django.core.management.base import BaseCommand
from app.models import InquiryCategory


class Command(BaseCommand):
    help = "Load initial categories into the InquiryCategory table"

    def handle(self, *args, **options):
        categories = [
            "complaint",
            "instruction",
            "error",
            "other"
        ]

        created_count = 0
        for name in categories:
            obj, created = InquiryCategory.objects.get_or_create(category_name=name)
            if created:
                self.stdout.write(self.style.SUCCESS(f"✅ 作成: {name}"))
                created_count += 1
            else:
                self.stdout.write(f"⚠️ 既に存在: {name}")

        self.stdout.write(self.style.SUCCESS(f"\n✅ 合計 {created_count} 件のカテゴリを作成しました。"))
