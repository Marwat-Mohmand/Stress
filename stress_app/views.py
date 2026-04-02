# stress_app/views.py - Add redirects after operations
from django.shortcuts import render, get_object_or_404, redirect
from django.db import connection
from django.contrib import messages
from django.utils import timezone  
from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Resource, SupportGroup, GroupMembership, User, Expert, Category
from django.db.models import F, Q, Count, Avg  # Add F here if not present
from django.core.paginator import Paginator
import random
from django.http import JsonResponse
# Resource CRUD Operations with redirects
def add_resource(request):
    experts = Expert.objects.all()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        title = request.POST.get('title')
        content = request.POST.get('content')
        resource_type = request.POST.get('resource_type')
        category_id = request.POST.get('category')
        expert_id = request.POST.get('expert')
        duration = request.POST.get('duration')
        difficulty_level = request.POST.get('difficulty_level')
        
        category = Category.objects.get(id=category_id) if category_id else None
        expert = Expert.objects.get(id=expert_id) if expert_id else None
        
        resource = Resource.objects.create(
            title=title,
            content=content,
            resource_type=resource_type,
            category=category,
            expert=expert,
            duration=duration,
            difficulty_level=difficulty_level,
            is_published=True
        )
        messages.success(request, f'Ресурс "{title}" успешно добавлен!')
        # Redirect to the resource list after successful creation
        return redirect('resource-list')
    
    return render(request, 'stress_app/add_resource.html', {
        'experts': experts,
        'categories': categories,
        'resource_types': Resource.RESOURCE_TYPES,
        'difficulty_levels': Resource.DIFFICULTY_LEVELS,
    })

def edit_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    experts = Expert.objects.all()
    categories = Category.objects.all()
    
    if request.method == 'POST':
        resource.title = request.POST.get('title')
        resource.content = request.POST.get('content')
        resource.resource_type = request.POST.get('resource_type')
        category_id = request.POST.get('category')
        expert_id = request.POST.get('expert')
        resource.duration = request.POST.get('duration')
        resource.difficulty_level = request.POST.get('difficulty_level')
        
        resource.category = Category.objects.get(id=category_id) if category_id else None
        resource.expert = Expert.objects.get(id=expert_id) if expert_id else None
        
        resource.save()
        messages.success(request, f'Ресурс "{resource.title}" обновлен!')
        # Redirect to resource list after successful edit
        return redirect('resource-list')
    
    return render(request, 'stress_app/edit_resource.html', {
        'resource': resource,
        'experts': experts,
        'categories': categories,
        'resource_types': Resource.RESOURCE_TYPES,
        'difficulty_levels': Resource.DIFFICULTY_LEVELS,
    })

def delete_resource(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    
    if request.method == 'POST':
        resource_title = resource.title
        resource.delete()
        messages.success(request, f'Ресурс "{resource_title}" удален!')
        # Redirect after deletion
        return redirect('resource-list')
    
    return render(request, 'stress_app/delete_resource.html', {'resource': resource})

# Expert CRUD with redirects
def add_expert(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        specialty = request.POST.get('specialty')
        qualification = request.POST.get('qualification')
        email = request.POST.get('email')
        bio = request.POST.get('bio')
        
        expert = Expert.objects.create(
            name=name,
            specialty=specialty,
            qualification=qualification,
            email=email,
            bio=bio,
            join_date=timezone.now().date()
        )
        messages.success(request, f'Эксперт "{name}" добавлен успешно!')
        return redirect('expert-list')
    
    return render(request, 'stress_app/add_expert.html')

def edit_expert(request, expert_id):
    expert = get_object_or_404(Expert, id=expert_id)
    
    if request.method == 'POST':
        expert.name = request.POST.get('name')
        expert.specialty = request.POST.get('specialty')
        expert.qualification = request.POST.get('qualification')
        expert.email = request.POST.get('email')
        expert.bio = request.POST.get('bio')
        expert.save()
        messages.success(request, f'Эксперт "{expert.name}" успешно обновлен!')
        return redirect('expert-list')
    
    return render(request, 'stress_app/edit_expert.html', {'expert': expert})

def delete_expert(request, expert_id):  #delete!
    expert = get_object_or_404(Expert, id=expert_id)
    
    if request.method == 'POST':
        expert_name = expert.name
        expert.delete()
        messages.success(request, f'Эксперт "{expert_name}" успешно удален!')
        return redirect('expert-list')
    
    return render(request, 'stress_app/delete_expert.html', {'expert': expert})

# Group member management with redirects
def add_group_member(request, group_id):
    group = get_object_or_404(SupportGroup, id=group_id)
    users = User.objects.all()
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role', 'member')
        user = get_object_or_404(User, id=user_id)
        
        if group.members.filter(id=user.id).exists():
            messages.warning(request, f'{user.username} уже является участником!')
        else:
            group.members.add(user, through_defaults={'role': role})
            messages.success(request, f'Участник {user.username} добавлен в группу {group.name}!')
        return redirect('group-list')
    
    return render(request, 'stress_app/add_group_member.html', {
        'group': group,
        'users': users
    })

def remove_group_member(request, group_id, user_id):
    group = get_object_or_404(SupportGroup, id=group_id)
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        if group.members.filter(id=user.id).exists():
            group.members.remove(user)
            messages.success(request, f'Участник {user.username} удален из группы {group.name}')
        else:
            messages.warning(request, f'{user.username} не является участником группы')
        return redirect('group-list')
    
    return render(request, 'stress_app/remove_member.html', {
        'group': group,
        'user': user
    })

# Resource list with select_related
def resource_list(request):
    from django.db import connection
    connection.queries_log.clear()
    
    resources = Resource.objects.select_related('expert').all()
    list(resources)
    num_queries = len(connection.queries)
    
    return render(request, 'stress_app/resource_list.html', {
        'resources': resources,
        'num_queries': num_queries,
    })

# Group list with prefetch_related
def group_list(request):
    from django.db import connection
    connection.queries_log.clear()
    
    groups = SupportGroup.objects.prefetch_related('memberships__user').all()
    
    groups_data = []
    for group in groups:
        members = [m.user for m in group.memberships.filter(is_active=True)]
        groups_data.append({
            'group': group,
            'members': members,
            'member_count': len(members)
        })
    
    num_queries = len(connection.queries)
    
    return render(request, 'stress_app/group_list.html', {
        'groups_data': groups_data,
        'num_queries': num_queries
    })

def group_statistics(request):
    """View to demonstrate values() and values_list()"""
    
    # 1. values() - returns dictionaries
    groups_dict = SupportGroup.objects.values('id', 'name', 'max_members', 'is_private')
    
    # 2. values_list() - returns tuples
    groups_list = SupportGroup.objects.values_list('id', 'name')
    
    # 3. values_list(flat=True) - single values
    group_names = SupportGroup.objects.values_list('name', flat=True)
    
    # 4. With annotations
    from django.db.models import Count
    groups_with_count = SupportGroup.objects.annotate(
        member_count=Count('memberships')
    ).values('id', 'name', 'member_count', 'max_members')
    
    # 5. count() demonstration
    total = SupportGroup.objects.count()
    private = SupportGroup.objects.filter(is_private=True).count()
    
    return render(request, 'stress_app/group_statistics.html', {
        'groups_dict': groups_dict,
        'groups_list': groups_list,
        'group_names': list(group_names),
        'groups_with_count': groups_with_count,
        'total': total,
        'private': private,
    })


# Expert list
def expert_crud_demo(request):
    experts = Expert.objects.all().order_by('-join_date')
    return render(request, 'stress_app/crud_demo.html', {
        'experts': experts
    })

# Handle 404 - Non-existent object redirect
def resource_detail(request, resource_id):
    resource = get_object_or_404(Resource, id=resource_id)
    return render(request, 'stress_app/resource_detail.html', {'resource': resource})

# Custom 404 handler - redirects to home with message
def handle_not_found(request, exception):
    messages.error(request, 'Запрашиваемая страница не найдена.')
    return redirect('resource-list')

def index(request):
    """
    Main page with 3 main functionalities:
    1. Latest resources (newest content)
    2. Popular resources (most viewed)
    3. Expert recommendations (top experts with most resources)
    """
    
    # Widget 1: Latest Releases - newest resources first
    latest_resources = Resource.objects.filter(
        is_published=True
    ).select_related('expert', 'category').order_by('-upload_date')[:6]
    
    # Widget 2: Popular Resources - most viewed
    popular_resources = Resource.objects.filter(
        is_published=True,
        views_count__gt=0
    ).select_related('expert', 'category').order_by('-views_count')[:6]
    
    # Widget 3: Expert Recommendations - experts with most resources
    expert_recommendations = Expert.objects.annotate(
        resources_count=Count('resources')
    ).filter(
        resources_count__gt=0,
        is_active=True
    ).order_by('-resources_count')[:4]
    
    # Aggregate function: Total statistics
    total_resources = Resource.objects.filter(is_published=True).count()
    total_experts = Expert.objects.filter(is_active=True).count()
    total_users = User.objects.count()
    avg_views = Resource.objects.filter(views_count__gt=0).aggregate(
        avg_views=Avg('views_count')
    )['avg_views'] or 0
    
    # Random featured resource
    featured_resource = Resource.objects.filter(
        is_published=True,
        cover_image__isnull=False
    ).order_by('?').first()
    
    context = {
        'latest_resources': latest_resources,
        'popular_resources': popular_resources,
        'expert_recommendations': expert_recommendations,
        'total_resources': total_resources,
        'total_experts': total_experts,
        'total_users': total_users,
        'avg_views': round(avg_views, 1),
        'featured_resource': featured_resource,
    }
    
    return render(request, 'stress_app/index.html', context)

#Main Page Logic

def search(request):
    """
    Search functionality using __icontains
    """
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # all, resources, experts, groups
    
    resources_results = []
    experts_results = []
    groups_results = []
    total_results = 0
    
    if query:
        if search_type in ['all', 'resources']:
            resources_results = Resource.objects.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(expert__name__icontains=query)
            ).select_related('expert', 'category').distinct()[:10]
            total_results += resources_results.count()
        
        if search_type in ['all', 'experts']:
            experts_results = Expert.objects.filter(
                Q(name__icontains=query) |
                Q(specialty__icontains=query) |
                Q(bio__icontains=query)
            ).filter(is_active=True)[:10]
            total_results += experts_results.count()
        
        if search_type in ['all', 'groups']:
            groups_results = SupportGroup.objects.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__icontains=query)
            )[:10]
            total_results += groups_results.count()
    
    context = {
        'query': query,
        'search_type': search_type,
        'resources_results': resources_results,
        'experts_results': experts_results,
        'groups_results': groups_results,
        'total_results': total_results,
    }
    
    return render(request, 'stress_app/search_results.html', context)


def resource_detail_page(request, resource_id):
    """
    Individual resource page with get_object_or_404 (Http404 demonstration)
    """
    from django.http import Http404
    
    try:
        resource = Resource.objects.select_related('expert', 'category').get(id=resource_id)
        # Increment views count using F expression
        Resource.objects.filter(id=resource_id).update(views_count=F('views_count') + 1)
        resource.refresh_from_db()
    except Resource.DoesNotExist:
        raise Http404("Ресурс не найден")
    
    # Get related resources (same category)
    related_resources = Resource.objects.filter(
        category=resource.category,
        is_published=True
    ).exclude(id=resource_id)[:4]
    
    return render(request, 'stress_app/resource_detail.html', {
        'resource': resource,
        'related_resources': related_resources,
    })
def api_group_data(request):
    """API endpoint demonstrating values() and values_list()"""
    from django.db.models import Count
    from django.http import JsonResponse
    
    # values() - for JSON response
    groups_data = SupportGroup.objects.values(
        'id', 'name', 'max_members', 'is_private'
    ).annotate(
        member_count=Count('memberships')
    )
    
    # values_list() - for simple lists
    group_names = SupportGroup.objects.values_list('name', flat=True)
    
    return JsonResponse({
        'using_values': list(groups_data),
        'using_values_list': list(group_names),
        'count_total': groups_data.count(),
    }, json_dumps_params={'ensure_ascii': False})