# test_queries.py
import os
import django
from datetime import date, timedelta

# Set up Django environment FIRST - before any other imports
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stress_project.settings')
django.setup()

# Now import Django modules and models
from django.utils import timezone
from django.db import models
from django.db.models import Count, Avg, Sum, Max, Min, Q, F
from django.urls import reverse

from stress_app.models import (
    User, Expert, Category, Resource, StressJournal,
    SupportGroup, GroupMembership, WellnessPlan, UserSavedResource
)

print("=" * 80)
print("LABORATORY WORK 3: DEMONSTRATION OF DJANGO ORM FEATURES")
print("=" * 80)

# 1. DEMONSTRATION OF from django.utils import timezone
print("\n" + "=" * 80)
print("1. USING DJANGO.UTILS.TIMEZONE")
print("=" * 80)

# Get current date and time with timezone awareness
now = timezone.now()
print(f"Current date and time (with timezone): {now}")
print(f"Current date: {now.date()}")
print(f"Current time: {now.time()}")

# Example 1: Creating an object with automatic creation date
print("\n--- Example 1: Automatic creation date ---")
new_expert = Expert(
    name='Dr. Test',
    bio='Test expert for demonstration',
    specialty='Testing',
    qualification='PhD',
    email='test@example.com',
    join_date=timezone.now().date()
)
new_expert.save()
print(f"Created expert: {new_expert.name}")
print(f"Join date: {new_expert.join_date}")
print(f"Data type: {type(new_expert.join_date)}")

# Example 2: Filtering by date (objects created in the last 7 days)
print("\n--- Example 2: Date filtering (last 7 days) ---")
seven_days_ago = timezone.now() - timedelta(days=7)
recent_journals = StressJournal.objects.filter(entry_date__gte=seven_days_ago.date())
print(f"Journal entries in the last 7 days: {recent_journals.count()}")
for journal in recent_journals:
    print(f"  - {journal.user.username}: {journal.entry_date}, stress: {journal.stress_level}")

# Example 3: Calculating object age (days since creation)
print("\n--- Example 3: Calculating object age ---")
today = date.today()
for expert in Expert.objects.all()[:3]:
    days_joined = (today - expert.join_date).days
    print(f"Expert {expert.name}: working for {days_joined} days")

# 2. DEMONSTRATION OF class Meta: ordering
print("\n" + "=" * 80)
print("2. class Meta: ORDERING")
print("=" * 80)

print("Models already have Meta classes with ordering defined:")

# Users are ordered by -date_joined (newest first)
print("\n--- Users (ordered by registration date, newest first) ---")
for user in User.objects.all()[:5]:
    print(f"  - {user.username}: {user.date_joined}")

# Resources are ordered by -upload_date (newest first)
print("\n--- Resources (ordered by upload date, newest first) ---")
for resource in Resource.objects.all()[:5]:
    print(f"  - {resource.title}: {resource.upload_date}")

# Experts are ordered by name (alphabetical)
print("\n--- Experts (ordered by name) ---")
for expert in Expert.objects.all():
    print(f"  - {expert.name}")

# 3. DEMONSTRATION OF choices in model fields
print("\n" + "=" * 80)
print("3. CHOICES IN MODEL FIELDS")
print("=" * 80)

print("The following choices are defined in models:")

# Resource.RESOURCE_TYPES
print("\n--- Resource.RESOURCE_TYPES ---")
for value, label in Resource.RESOURCE_TYPES:
    print(f"  Value: '{value}', Display: '{label}'")

# Example usage in query
print("\n--- Example: Filtering by choice field ---")
meditations = Resource.objects.filter(resource_type='meditation')
print(f"Meditations in database: {meditations.count()}")
for m in meditations[:3]:
    print(f"  - {m.title}")

# Resource.DIFFICULTY_LEVELS
print("\n--- Resource.DIFFICULTY_LEVELS ---")
for value, label in Resource.DIFFICULTY_LEVELS:
    print(f"  Value: '{value}', Display: '{label}'")

# GroupMembership.ROLES
print("\n--- GroupMembership.ROLES ---")
for value, label in GroupMembership.ROLES:
    print(f"  Value: '{value}', Display: '{label}'")

# WellnessPlan.GOAL_TYPES
print("\n--- WellnessPlan.GOAL_TYPES ---")
for value, label in WellnessPlan.GOAL_TYPES:
    print(f"  Value: '{value}', Display: '{label}'")

# 4. DEMONSTRATION OF related_name
print("\n" + "=" * 80)
print("4. RELATED_NAME IN MODELS")
print("=" * 80)

print("related_name allows accessing related objects in reverse direction")

# Example 1: User -> journal_entries (via related_name='journal_entries')
print("\n--- Example 1: Getting all journal entries of a user ---")
user = User.objects.first()
journal_entries = user.journal_entries.all()
print(f"User: {user.username}")
print(f"Number of journal entries: {journal_entries.count()}")
for entry in journal_entries[:3]:
    print(f"  - {entry.entry_date}: stress {entry.stress_level}")

# Example 2: User -> moderated_groups (related_name='moderated_groups')
print("\n--- Example 2: Groups moderated by user ---")
moderated_groups = user.moderated_groups.all()
print(f"User {user.username} moderates {moderated_groups.count()} groups")
for group in moderated_groups:
    print(f"  - {group.name}")

# Example 3: User -> group_memberships (related_name='group_memberships')
print("\n--- Example 3: User's group memberships ---")
memberships = user.group_memberships.all()
print(f"User {user.username} is a member of {memberships.count()} groups")
for membership in memberships:
    print(f"  - {membership.group.name} (role: {membership.get_role_display()})")

# Example 4: Expert -> resources (related_name='resources')
print("\n--- Example 4: Resources created by expert ---")
expert = Expert.objects.first()
resources = expert.resources.all()
print(f"Expert {expert.name} created {resources.count()} resources")
for resource in resources:
    print(f"  - {resource.title}")

# Example 5: Category -> resources (related_name='resources')
print("\n--- Example 5: Resources in category ---")
category = Category.objects.filter(parent__isnull=False).first()
if category:
    resources_in_category = category.resources.all()
    print(f"Category '{category.name}' contains {resources_in_category.count()} resources")

# 5. DEMONSTRATION OF filter() method
print("\n" + "=" * 80)
print("5. FILTER() METHOD")
print("=" * 80)

# Simple filtering
print("\n--- Simple filtering: active experts ---")
active_experts = Expert.objects.filter(is_active=True)
print(f"Active experts: {active_experts.count()}")

# Filtering with multiple conditions
print("\n--- Filtering with multiple conditions: published beginner meditations ---")
beginner_meditations = Resource.objects.filter(
    resource_type='meditation',
    difficulty_level='beginner',
    is_published=True
)
print(f"Found: {beginner_meditations.count()}")
for rm in beginner_meditations:
    print(f"  - {rm.title}")

# Filtering by related field (using __)
print("\n--- Filtering by related field: resources by expert Anna ---")
anna_resources = Resource.objects.filter(expert__name__icontains='Анна')
print(f"Found: {anna_resources.count()}")
for ar in anna_resources:
    print(f"  - {ar.title} (expert: {ar.expert.name})")

# 6. DEMONSTRATION OF __ (double underscore)
print("\n" + "=" * 80)
print("6. USING __ (DOUBLE UNDERSCORE)")
print("=" * 80)

# Option 1: Field lookup methods
print("\n--- Option 1: Field lookup methods ---")
print("1.1 __gt (greater than): resources with duration > 15 minutes")
long_resources = Resource.objects.filter(duration__gt=15)
print(f"Found: {long_resources.count()}")
for r in long_resources[:3]:
    print(f"  - {r.title}: {r.duration} min")

print("\n1.2 __icontains (contains text, case insensitive): resources with 'медитация' in title")
meditation_resources = Resource.objects.filter(title__icontains='медитация')
print(f"Found: {meditation_resources.count()}")
for r in meditation_resources:
    print(f"  - {r.title}")

print("\n1.3 __gte (greater than or equal): stress level >= 7")
high_stress = StressJournal.objects.filter(stress_level__gte=7)
print(f"Entries with high stress: {high_stress.count()}")

print("\n1.4 __year (year): journal entries from 2026")
journal_2026 = StressJournal.objects.filter(entry_date__year=2026)
print(f"Entries in 2026: {journal_2026.count()}")

# Option 2: Reference to related table
print("\n--- Option 2: Reference to related table ---")
print("2.1 Filter by related field: resources by expert qualification")
expert_resources = Resource.objects.filter(expert__qualification__icontains='PhD')
print(f"Resources by experts with PhD: {expert_resources.count()}")
for r in expert_resources[:3]:
    print(f"  - {r.title} (expert: {r.expert.name})")

print("\n2.2 Filter by related field: group memberships of a specific user")
user_memberships = GroupMembership.objects.filter(user__username='anna_smith')
print(f"Group memberships for anna_smith: {user_memberships.count()}")

print("\n2.3 Filter by related field: stress journal entries of premium users")
premium_entries = StressJournal.objects.filter(user__subscription_type='premium')
print(f"Journal entries from premium users: {premium_entries.count()}")

# 7. DEMONSTRATION OF exclude() method
print("\n" + "=" * 80)
print("7. EXCLUDE() METHOD")
print("=" * 80)

print("exclude() removes objects that match the criteria")

# Simple exclude
print("\n--- Simple exclude: resources that are NOT published ---")
unpublished = Resource.objects.exclude(is_published=True)
print(f"Unpublished resources: {unpublished.count()}")

# Exclude with multiple conditions
print("\n--- Exclude with multiple conditions: resources NOT for beginners AND NOT meditations ---")
not_beginner_not_meditation = Resource.objects.exclude(
    difficulty_level='beginner'
).exclude(
    resource_type='meditation'
)
print(f"Resources not for beginners and not meditations: {not_beginner_not_meditation.count()}")

# Exclude with related fields
print("\n--- Exclude with related fields: journal entries NOT from premium users ---")
non_premium_entries = StressJournal.objects.exclude(user__subscription_type='premium')
print(f"Entries from non-premium users: {non_premium_entries.count()}")

# 8. DEMONSTRATION OF order_by() method
print("\n" + "=" * 80)
print("8. ORDER_BY() METHOD")
print("=" * 80)

print("order_by() allows custom sorting regardless of Meta.ordering")

# Ascending order
print("\n--- Ascending order: resources by title ---")
resources_by_title = Resource.objects.all().order_by('title')[:5]
for r in resources_by_title:
    print(f"  - {r.title}")

# Descending order
print("\n--- Descending order: resources by duration (longest first) ---")
resources_by_duration = Resource.objects.all().order_by('-duration')[:5]
for r in resources_by_duration:
    print(f"  - {r.title}: {r.duration} min")

# Multiple fields
print("\n--- Multiple fields: resources by type, then by title ---")
resources_by_type_title = Resource.objects.all().order_by('resource_type', 'title')[:5]
for r in resources_by_type_title:
    print(f"  - {r.resource_type}: {r.title}")

# Order by related field
print("\n--- Order by related field: resources by expert name ---")
resources_by_expert = Resource.objects.all().order_by('expert__name')[:5]
for r in resources_by_expert:
    expert_name = r.expert.name if r.expert else "No expert"
    print(f"  - {r.title} (expert: {expert_name})")

# 9. DEMONSTRATION OF custom model manager
print("\n" + "=" * 80)
print("9. CUSTOM MODEL MANAGER")
print("=" * 80)

print("Demonstrating custom manager concept:")

# Show what a custom manager would do
published_count = Resource.objects.filter(is_published=True).count()
total_resources = Resource.objects.count()
print(f"Published resources (what a custom manager would return): {published_count}")
print(f"Total resources: {total_resources}")
print(f"Unpublished resources: {total_resources - published_count}")

premium_count = User.objects.filter(subscription_type='premium').count()
total_users = User.objects.count()
print(f"\nPremium users (what a custom manager would return): {premium_count}")
print(f"Total users: {total_users}")

print("\nExample of how to define custom managers in models.py:")
print("""
class PublishedResourceManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_published=True)

class Resource(models.Model):
    # ... fields ...
    objects = models.Manager()  # default manager
    published_objects = PublishedResourceManager()  # custom manager

# Usage:
published = Resource.published_objects.all()
""")

# 10. DEMONSTRATION OF get_absolute_url and reverse (FIXED VERSION)
print("\n" + "=" * 80)
print("10. GET_ABSOLUTE_URL AND REVERSE")
print("=" * 80)

print("get_absolute_url is a convention in Django to return the URL for a specific object")
print("reverse() generates URLs from view names and parameters")

# Demonstrate get_absolute_url concept without requiring actual URLs
print("\n--- Demonstrating get_absolute_url concept ---")

sample_resource = Resource.objects.first()
if sample_resource:
    print(f"Resource: {sample_resource.title}")
    print(f"ID: {sample_resource.id}")
    print(f"In a real project, get_absolute_url might return: '/resource/{sample_resource.id}/'")
    print(f"Example implementation:")
    print("""
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('resource-detail', args=[str(self.id)])
    """)

sample_expert = Expert.objects.first()
if sample_expert:
    print(f"\nExpert: {sample_expert.name}")
    print(f"ID: {sample_expert.id}")
    print(f"Example URL: '/expert/{sample_expert.id}/'")

# Demonstrate reverse() with admin URLs (which definitely exist)
print("\n--- Using reverse() with existing admin URLs ---")
from django.urls import reverse

# These URLs exist in every Django project
admin_index_url = reverse('admin:index')
print(f"Admin index URL: {admin_index_url}")

# URLs for our models in admin
try:
    user_changelist_url = reverse('admin:stress_app_user_changelist')
    print(f"User list in admin: {user_changelist_url}")
    
    expert_changelist_url = reverse('admin:stress_app_expert_changelist')
    print(f"Expert list in admin: {expert_changelist_url}")
    
    resource_changelist_url = reverse('admin:stress_app_resource_changelist')
    print(f"Resource list in admin: {resource_changelist_url}")
except Exception as e:
    print(f"Some admin URLs not available: {e}")

# 11. DEMONSTRATION OF aggregation and annotation
print("\n" + "=" * 80)
print("11. AGGREGATION AND ANNOTATION")
print("=" * 80)

# Aggregation examples
print("\n--- Aggregation: calculating statistics across all objects ---")

from django.db.models import Count, Avg, Sum, Max, Min

# Example 1: Count total objects
print("\n1.1 Count - total resources")
total_resources = Resource.objects.count()
print(f"Total resources: {total_resources}")

# Example 2: Average, Max, Min of numeric fields
print("\n1.2 Average, Max, Min of stress levels")
stats = StressJournal.objects.aggregate(
    avg_stress=Avg('stress_level'),
    max_stress=Max('stress_level'),
    min_stress=Min('stress_level'),
    total_entries=Count('id')
)
print(f"Average stress: {stats['avg_stress']:.2f}")
print(f"Maximum stress: {stats['max_stress']}")
print(f"Minimum stress: {stats['min_stress']}")
print(f"Total entries: {stats['total_entries']}")

# Example 3: Sum of durations
print("\n1.3 Sum - total minutes of all resources")
total_minutes = Resource.objects.aggregate(total_duration=Sum('duration'))
print(f"Total duration of all resources: {total_minutes['total_duration']} minutes")

# Annotation examples
print("\n--- Annotation: adding calculated fields to each object ---")

# Example 1: Annotate resources with number of times saved
print("\n2.1 Annotate resources with save count")
resources_with_save_count = Resource.objects.annotate(
    save_count=Count('saved_by_users')
).order_by('-save_count')[:5]
for r in resources_with_save_count:
    print(f"  - {r.title}: saved {r.save_count} times")

# Example 2: Annotate users with journal entry count and average stress
print("\n2.2 Annotate users with journal stats")
users_with_stats = User.objects.annotate(
    entry_count=Count('journal_entries'),
    avg_stress=Avg('journal_entries__stress_level')
).filter(entry_count__gt=0).order_by('-entry_count')[:5]
for u in users_with_stats:
    print(f"  - {u.username}: {u.entry_count} entries, avg stress {u.avg_stress:.2f}")

# Example 3: Annotate groups with member count
print("\n2.3 Annotate groups with member count")
groups_with_members = SupportGroup.objects.annotate(
    member_count=Count('memberships')
).order_by('-member_count')
for g in groups_with_members:
    print(f"  - {g.name}: {g.member_count} members")

print("\n" + "=" * 80)
print("DEMONSTRATION COMPLETE!")
print("=" * 80)

#questions
 
#Migrations in Django track database changes:

#1. python manage.py makemigrations - Creates migration files
#2. python manage.py migrate - Applies migrations to database
#3. python manage.py showmigrations - Shows applied migrations
#4. python manage.py sqlmigrate - Shows SQL that will run
