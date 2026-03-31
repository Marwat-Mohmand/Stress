# populate_main.py
import os
import django
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stress_project.settings')
django.setup()

from stress_app.models import User, Expert, Category, Resource, SupportGroup, GroupMembership, StressJournal
from django.contrib.auth.hashers import make_password

print("Populating database with 10+ records per table...")

# Create 10 Users
users = []
for i in range(1, 11):
    user = User.objects.create(
        username=f'user{i}',
        email=f'user{i}@example.com',
        password=make_password('password123'),
        first_name=f'Имя{i}',
        last_name=f'Фамилия{i}',
        subscription_type='free' if i % 3 != 0 else 'premium',
        stress_profile_completed=True if i % 2 == 0 else False,
        birth_date=date(1990 + i % 20, i % 12 + 1, i % 28 + 1)
    )
    users.append(user)
print(f"Created {len(users)} users")

# Create 10 Experts
experts = []
expert_names = [
    "Доктор Анна Петрова", "Доктор Иван Соколов", "Профессор Елена Волкова", 
    "Доктор Мария Кузнецова", "Доктор Сергей Морозов", "Профессор Ольга Новикова",
    "Доктор Татьяна Лебедева", "Доктор Андрей Козлов", "Профессор Наталья Павлова",
    "Доктор Екатерина Смирнова"
]
specialties = [
    "Клиническая психология", "Когнитивная психология", "Нейробиология",
    "Психотерапия", "Медитация и майндфулнес", "Йога-терапия",
    "Арт-терапия", "Семейная психология", "Травма-терапия", "Стресс-менеджмент"
]

for i in range(10):
    expert = Expert.objects.create(
        name=expert_names[i],
        bio=f"Опытный специалист в области {specialties[i]}. Помогает справляться со стрессом уже 15 лет.",
        specialty=specialties[i],
        qualification="Кандидат психологических наук" if i % 2 == 0 else "Доктор медицинских наук",
        email=f'expert{i+1}@example.com',
        join_date=date(2020, i % 12 + 1, i % 28 + 1),
        is_active=True,
        website=f'https://example.com/expert{i+1}'
    )
    experts.append(expert)
print(f"Created {len(experts)} experts")

# Create 10 Categories
categories = [
    Category(name="Медитация", description="Практики осознанности", order=1),
    Category(name="Дыхательные упражнения", description="Техники дыхания", order=2),
    Category(name="Йога", description="Физические практики", order=3),
    Category(name="Психология", description="Статьи и советы", order=4),
    Category(name="Сон и отдых", description="Как улучшить сон", order=5),
    Category(name="Питание", description="Антистрессовое питание", order=6),
    Category(name="Физическая активность", description="Спорт и движение", order=7),
    Category(name="Творчество", description="Арт-терапия", order=8),
    Category(name="Природа", description="Эко-терапия", order=9),
    Category(name="Социальные связи", description="Поддержка близких", order=10),
]
for cat in categories:
    cat.save()
print(f"Created {len(categories)} categories")

# Create 10+ Resources
resources = []
resource_titles = [
    "10-минутная медитация для начинающих",
    "Как справиться с тревогой: пошаговое руководство",
    "Дыхание 4-7-8 для глубокого расслабления",
    "Йога для снятия напряжения в шее и плечах",
    "Наука стресса: как работает наш организм",
    "Практика благодарности: дневник счастья",
    "Сон и стресс: как наладить режим",
    "Питание против стресса: топ-10 продуктов",
    "Арт-терапия: рисуем эмоции",
    "Прогулка на природе как антидепрессант",
    "Как создать круг поддержки",
    "Тайм-менеджмент для снижения стресса",
    "Техники заземления при панической атаке",
    "Аффирмации для уверенности",
    "Как сказать нет: устанавливаем границы"
]

for i in range(15):
    resource = Resource.objects.create(
        title=resource_titles[i % len(resource_titles)],
        content=f"Подробное описание техники {resource_titles[i % len(resource_titles)]}...",
        resource_type=['meditation', 'article', 'video', 'audio', 'exercise'][i % 5],
        category=categories[i % len(categories)],
        expert=experts[i % len(experts)],
        duration=[5, 10, 15, 20, 30, 45, 60][i % 7],
        difficulty_level=['beginner', 'intermediate', 'advanced'][i % 3],
        is_published=True,
        views_count=i * 100 + (i % 5) * 50,
        cover_image=None,
        file=None
    )
    resources.append(resource)
print(f"Created {len(resources)} resources")

# Create 10 Support Groups
groups = []
group_names = [
    "Мамы в декрете", "Стресс на работе", "Тревожность и паника",
    "Йога для всех", "Медитативный клуб", "Книжный клуб по психологии",
    "Здоровый сон", "Питание без стресса", "Творческая мастерская",
    "Поддержка в кризисе"
]

for i in range(10):
    group = SupportGroup.objects.create(
        name=group_names[i],
        description=f"Группа поддержки для тех, кто сталкивается с {group_names[i].lower()}",
        moderator=users[i % len(users)],
        max_members=15 + (i * 5),
        meeting_schedule=f"Каждую {'Среду' if i % 2 == 0 else 'Субботу'} в {19 + i % 3}:00",
        is_private=i % 3 == 0
    )
    groups.append(group)
print(f"Created {len(groups)} support groups")

# Create Group Memberships
membership_count = 0
for group in groups:
    for user in users[:5]:  # Add first 5 users to each group
        if not GroupMembership.objects.filter(group=group, user=user).exists():
            GroupMembership.objects.create(
                user=user,
                group=group,
                role='member',
                is_active=True
            )
            membership_count += 1
print(f"Created {membership_count} group memberships")

print("\n✅ Database populated successfully!")
print(f"Users: {User.objects.count()}")
print(f"Experts: {Expert.objects.count()}")
print(f"Categories: {Category.objects.count()}")
print(f"Resources: {Resource.objects.count()}")
print(f"Support Groups: {SupportGroup.objects.count()}")
print(f"Group Memberships: {GroupMembership.objects.count()}")