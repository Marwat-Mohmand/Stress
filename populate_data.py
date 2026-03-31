# populate_data.py
import os
import django
from datetime import date, timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stress_project.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from stress_app.models import (
    User, Expert, Category, Resource, StressJournal,
    SupportGroup, GroupMembership, WellnessPlan, UserSavedResource
)

def create_test_data():
    print("Создание тестовых данных...")
    
    # 1. Создание пользователей
    users = [
        User(
            username='anna_smith',
            email='anna@example.com',
            password=make_password('password123'),
            first_name='Анна',
            last_name='Смит',
            subscription_type='premium',
            stress_profile_completed=True,
            birth_date=date(1990, 5, 15)
        ),
        User(
            username='maria_ivanova',
            email='maria@example.com',
            password=make_password('password123'),
            first_name='Мария',
            last_name='Иванова',
            subscription_type='basic',
            stress_profile_completed=True,
            birth_date=date(1988, 3, 22)
        ),
        User(
            username='elena_kuznetsova',
            email='elena@example.com',
            password=make_password('password123'),
            first_name='Елена',
            last_name='Кузнецова',
            subscription_type='free',
            stress_profile_completed=False,
            birth_date=date(1995, 11, 8)
        ),
    ]
    for user in users:
        user.save()
    print(f"Создано {len(users)} пользователей")
    
    # 2. Создание экспертов
    experts = [
        Expert(
            name='Доктор Елена Петрова',
            bio='Клинический психолог с 15-летним опытом работы в области стресс-менеджмента',
            specialty='Клиническая психология',
            qualification='Кандидат психологических наук',
            email='dr.petrova@example.com',
            join_date=date(2020, 1, 15),
            is_active=True
        ),
        Expert(
            name='Анна Соколова',
            bio='Сертифицированный инструктор по медитации и йоге',
            specialty='Медитация и майндфулнес',
            qualification='Сертифицированный преподаватель медитации',
            email='anna.sokolova@example.com',
            join_date=date(2021, 3, 10),
            is_active=True
        ),
        Expert(
            name='Профессор Игорь Морозов',
            bio='Исследователь в области нейробиологии стресса',
            specialty='Нейробиология',
            qualification='Доктор медицинских наук',
            email='morozov@example.com',
            join_date=date(2019, 8, 5),
            is_active=True
        ),
    ]
    for expert in experts:
        expert.save()
    print(f"Создано {len(experts)} экспертов")
    
    # 3. Создание категорий
    categories = [
        Category(name='Медитация', description='Практики медитации для снижения стресса', order=1, is_active=True),
        Category(name='Дыхательные упражнения', description='Техники дыхания для успокоения', order=2, is_active=True),
        Category(name='Йога', description='Йога для снятия напряжения', order=3, is_active=True),
        Category(name='Психология', description='Статьи по психологии стресса', order=4, is_active=True),
    ]
    for category in categories:
        category.save()
    
    # Подкатегории
    subcategories = [
        Category(name='Для начинающих', parent=categories[0], order=1, is_active=True),
        Category(name='Для сна', parent=categories[0], order=2, is_active=True),
        Category(name='Дыхание 4-7-8', parent=categories[1], order=1, is_active=True),
    ]
    for subcat in subcategories:
        subcat.save()
    print(f"Создано {len(categories) + len(subcategories)} категорий")
    
    # 4. Создание ресурсов
    resources = [
        Resource(
            title='Медитация для снятия тревоги',
            content='Эта медитация поможет вам успокоить ум и снизить уровень тревоги...',
            resource_type='meditation',
            category=subcategories[0],  # Для начинающих
            expert=experts[1],  # Анна Соколова
            duration=15,
            difficulty_level='beginner',
            is_published=True,
            views_count=1245
        ),
        Resource(
            title='Как стресс влияет на организм',
            content='Стресс запускает каскад физиологических реакций...',
            resource_type='article',
            category=categories[3],  # Психология
            expert=experts[0],  # Доктор Петрова
            duration=10,
            difficulty_level='intermediate',
            is_published=True,
            views_count=3456
        ),
        Resource(
            title='Йога для снятия напряжения в шее',
            content='Комплекс упражнений для расслабления мышц шеи и плеч...',
            resource_type='video',
            category=categories[2],  # Йога
            expert=experts[1],  # Анна Соколова
            duration=20,
            difficulty_level='beginner',
            is_published=True,
            views_count=892
        ),
        Resource(
            title='Техника дыхания 4-7-8',
            content='Древняя техника пранаямы для быстрого успокоения нервной системы...',
            resource_type='exercise',
            category=subcategories[2],  # Дыхание 4-7-8
            expert=experts[2],  # Профессор Морозов
            duration=5,
            difficulty_level='beginner',
            is_published=True,
            views_count=2341
        ),
    ]
    for resource in resources:
        resource.save()
    print(f"Создано {len(resources)} ресурсов")
    
    # 5. Создание записей в журнале стресса
    today = timezone.now().date()
    journal_entries = [
        StressJournal(
            user=users[0],  # Анна
            entry_date=today - timedelta(days=1),
            stress_level=7,
            mood='Тревожное',
            notes='Сложный день на работе',
            triggers='Дедлайн проекта',
            coping_methods='Медитация 15 минут',
            sleep_hours=6.5
        ),
        StressJournal(
            user=users[0],  # Анна
            entry_date=today,
            stress_level=4,
            mood='Спокойное',
            notes='Лучше, чем вчера',
            triggers='Нет особых',
            coping_methods='Прогулка',
            sleep_hours=7.5
        ),
        StressJournal(
            user=users[1],  # Мария
            entry_date=today - timedelta(days=2),
            stress_level=9,
            mood='Раздраженное',
            notes='Проблемы в семье',
            triggers='Ссора',
            coping_methods='Дыхательные упражнения',
            sleep_hours=5.0
        ),
    ]
    for entry in journal_entries:
        entry.save()
    print(f"Создано {len(journal_entries)} записей в журнале")
    
    # 6. Создание групп поддержки
    groups = [
        SupportGroup(
            name='Мамы в декрете',
            description='Группа поддержки для мам с маленькими детьми',
            moderator=users[0],  # Анна
            max_members=15,
            meeting_schedule='Среда 20:00',
            is_private=False
        ),
        SupportGroup(
            name='Стресс на работе',
            description='Обсуждение рабочих стрессов и способов их преодоления',
            moderator=users[1],  # Мария
            max_members=20,
            meeting_schedule='Вторник 19:00',
            is_private=False
        ),
        SupportGroup(
            name='Тревожность и паника',
            description='Закрытая группа для людей с тревожными расстройствами',
            moderator=users[0],  # Анна
            max_members=10,
            meeting_schedule='Четверг 18:30',
            is_private=True
        ),
    ]
    for group in groups:
        group.save()
    print(f"Создано {len(groups)} групп поддержки")
    
    # 7. Создание членства в группах (многие-ко-многим)
    memberships = [
        GroupMembership(user=users[0], group=groups[0], role='moderator', is_active=True),
        GroupMembership(user=users[1], group=groups[0], role='member', is_active=True),
        GroupMembership(user=users[2], group=groups[0], role='member', is_active=True),
        GroupMembership(user=users[0], group=groups[1], role='member', is_active=True),
        GroupMembership(user=users[1], group=groups[1], role='moderator', is_active=True),
        GroupMembership(user=users[2], group=groups[2], role='member', is_active=True),
    ]
    for membership in memberships:
        membership.save()
    print(f"Создано {len(memberships)} записей членства в группах")
    
    # 8. Создание планов оздоровления
    wellness_plans = [
        WellnessPlan(
            user=users[0],
            goal_type='stress_reduction',
            goal='Снизить уровень стресса с 7 до 4 за 4 недели',
            duration_weeks=4,
            current_week=2,
            completed=False,
            start_date=today - timedelta(days=14),
            daily_reminder=True
        ),
        WellnessPlan(
            user=users[1],
            goal_type='sleep_improvement',
            goal='Улучшить качество сна, спать не менее 7 часов',
            duration_weeks=6,
            current_week=3,
            completed=False,
            start_date=today - timedelta(days=21),
            daily_reminder=True
        ),
        WellnessPlan(
            user=users[2],
            goal_type='mindfulness',
            goal='Практиковать осознанность ежедневно',
            duration_weeks=8,
            current_week=1,
            completed=False,
            start_date=today - timedelta(days=7),
            daily_reminder=True
        ),
    ]
    for plan in wellness_plans:
        plan.save()
    print(f"Создано {len(wellness_plans)} планов оздоровления")
    
    # 9. Создание сохраненных ресурсов (многие-ко-многим)
    saved_resources = [
        UserSavedResource(user=users[0], resource=resources[0], is_favorite=True),
        UserSavedResource(user=users[0], resource=resources[2], is_favorite=False),
        UserSavedResource(user=users[1], resource=resources[1], is_favorite=True),
        UserSavedResource(user=users[1], resource=resources[3], is_favorite=True),
        UserSavedResource(user=users[2], resource=resources[0], is_favorite=False),
    ]
    for saved in saved_resources:
        saved.save()
    print(f"Создано {len(saved_resources)} сохраненных ресурсов")
    
    print("\n✅ Все тестовые данные успешно созданы!")
    print(f"Всего создано:")
    print(f"- Пользователей: {User.objects.count()}")
    print(f"- Экспертов: {Expert.objects.count()}")
    print(f"- Категорий: {Category.objects.count()}")
    print(f"- Ресурсов: {Resource.objects.count()}")
    print(f"- Записей журнала: {StressJournal.objects.count()}")
    print(f"- Групп поддержки: {SupportGroup.objects.count()}")
    print(f"- Участников групп: {GroupMembership.objects.count()}")
    print(f"- Планов оздоровления: {WellnessPlan.objects.count()}")
    print(f"- Сохраненных ресурсов: {UserSavedResource.objects.count()}")

if __name__ == '__main__':
    create_test_data()