# lab4_demo.py
import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stress_project.settings')
django.setup()

from stress_app.models import Resource, SupportGroup, User, Expert

print("=" * 80)
print("LAB 4: DEMONSTRATION")
print("=" * 80)

# 1. DEMONSTRATE select_related()
print("\n" + "-" * 40)
print("1. SELECT_RELATED() DEMO")
print("-" * 40)

# Without select_related - makes multiple queries
print("\n🔴 WITHOUT select_related (many queries):")
connection.queries_log.clear()
resources = Resource.objects.all()[:3]
for r in resources:
    if r.expert:
        print(f"  Resource: {r.title} -> Expert: {r.expert.name}")
print(f"  Number of queries: {len(connection.queries)}")

# With select_related - makes one query
print("\n✅ WITH select_related (one query):")
connection.queries_log.clear()
resources = Resource.objects.select_related('expert').all()[:3]
for r in resources:
    if r.expert:
        print(f"  Resource: {r.title} -> Expert: {r.expert.name}")
print(f"  Number of queries: {len(connection.queries)}")

# 2. DEMONSTRATE prefetch_related()
print("\n" + "-" * 40)
print("2. PREFETCH_RELATED() DEMO")
print("-" * 40)

# Without prefetch_related
print("\n🔴 WITHOUT prefetch_related:")
connection.queries_log.clear()
groups = SupportGroup.objects.all()[:3]
for g in groups:
    member_count = g.memberships.count()
    print(f"  Group: {g.name} -> Members: {member_count}")
print(f"  Number of queries: {len(connection.queries)}")

# With prefetch_related
print("\n✅ WITH prefetch_related:")
connection.queries_log.clear()
groups = SupportGroup.objects.prefetch_related('memberships').all()[:3]
for g in groups:
    member_count = g.memberships.count()
    print(f"  Group: {g.name} -> Members: {member_count}")
print(f"  Number of queries: {len(connection.queries)}")

# 3. DEMONSTRATE ManyToManyField with through
print("\n" + "-" * 40)
print("3. MANYTOMANYFIELD WITH THROUGH DEMO")
print("-" * 40)

# Show the relationship
group = SupportGroup.objects.first()
if group:
    print(f"\nGroup: {group.name}")
    print(f"Members (via through model):")
    for membership in group.memberships.all()[:3]:
        print(f"  - {membership.user.username} (Role: {membership.role})")
    
    print(f"\nMembers (via new 'members' field):")
    for user in group.members.all()[:3]:
        print(f"  - {user.username}")

# 4. CRUD OPERATIONS DEMO
print("\n" + "-" * 40)
print("4. CRUD OPERATIONS DEMO")
print("-" * 40)

# CREATE
print("\n✅ CREATE: Creating a new expert")
new_expert = Expert.objects.create(
    name='Lab4 Demo Expert',
    specialty='Demonstration',
    qualification='PhD',
    email='demo@example.com',
    bio='Created for Lab 4 demonstration',
    join_date='2026-03-03'
)
print(f"  Created: {new_expert.name} (ID: {new_expert.id})")

# READ
print("\n📖 READ: Getting the expert we just created")
expert = Expert.objects.get(id=new_expert.id)
print(f"  Found: {expert.name} - {expert.specialty}")

# UPDATE
print("\n✏️ UPDATE: Updating the expert's specialty")
expert.specialty = 'Updated Demo Specialty'
expert.save()
print(f"  Updated: {expert.name} - {expert.specialty}")

# DELETE
print("\n🗑️ DELETE: Deleting the expert")
expert_id = expert.id
expert.delete()
print(f"  Deleted expert with ID: {expert_id}")
print(f"  Verify deletion: {Expert.objects.filter(id=expert_id).exists()}")

print("\n" + "=" * 80)
print("LAB 4 DEMONSTRATION COMPLETE!")
print("=" * 80)