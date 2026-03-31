# stress_app/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # Main page
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('resource/<int:resource_id>/', views.resource_detail_page, name='resource-detail-page'),
    
    # Statistics and API
    path('demo/groups/statistics/', views.group_statistics, name='group-statistics'),
    path('api/groups/', views.api_group_data, name='api-groups'),
    
    # Existing URLs...
    path('demo/resources/', views.resource_list, name='resource-list'),
    path('demo/resources/add/', views.add_resource, name='add-resource'),
    path('demo/resources/edit/<int:resource_id>/', views.edit_resource, name='edit-resource'),
    path('demo/resources/delete/<int:resource_id>/', views.delete_resource, name='delete-resource'),
    
    path('demo/groups/', views.group_list, name='group-list'),
    path('demo/group/<int:group_id>/add-member/', views.add_group_member, name='add-group-member'),
    path('demo/group/<int:group_id>/remove-member/<int:user_id>/', views.remove_group_member, name='remove-group-member'),
    
    path('demo/experts/', views.expert_crud_demo, name='expert-list'),
    path('demo/experts/add/', views.add_expert, name='add-expert'),
    path('demo/experts/edit/<int:expert_id>/', views.edit_expert, name='edit-expert'),
    path('demo/experts/delete/<int:expert_id>/', views.delete_expert, name='delete-expert'),
]


# from django.urls import path
# from . import views  # This imports views from the current app

# urlpatterns = [
#     # List views
#     path('demo/resources/', views.resource_list, name='resource-list'),
#     path('demo/groups/', views.group_list, name='group-list'),
#     path('demo/experts/', views.expert_crud_demo, name='expert-list'),

#     # CRUD operations for Experts
#     path('demo/experts/add/', views.add_expert, name='add-expert'),
#     path('demo/experts/edit/<int:expert_id>/', views.edit_expert, name='edit-expert'),
#     path('demo/experts/delete/<int:expert_id>/', views.delete_expert, name='delete-expert'),

#     # Group member management
#     path('demo/group/<int:group_id>/add-member/', views.add_group_member, name='add-group-member'),
#     path('demo/group/<int:group_id>/remove-member/<int:user_id>/', views.remove_group_member, name='remove-group-member'),


# ]
