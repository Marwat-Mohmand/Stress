# stress_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.http import HttpResponse
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.contrib import messages
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import csv
import io

from .models import (
    User, Expert, Category, Resource, StressJournal,
    SupportGroup, GroupMembership, WellnessPlan, UserSavedResource
)



# PDF Generation Function
def generate_pdf_report(modeladmin, request, queryset):
    """Generate PDF report for selected objects with Cyrillic font support"""
    # Create a file-like buffer to receive PDF data
    buffer = io.BytesIO()
    
    # Create the PDF object
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []
    
    # Register Cyrillic fonts
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    
    # Try to register Arial (Windows) or fallback
    try:
        # For Windows - Arial usually at this path
        pdfmetrics.registerFont(TTFont('Arial', 'C:/Windows/Fonts/arial.ttf'))
        pdfmetrics.registerFont(TTFont('Arial-Bold', 'C:/Windows/Fonts/arialbd.ttf'))
        font_name = 'Arial'
        bold_font_name = 'Arial-Bold'
    except:
        try:
            # Try DejaVuSans (common on Linux)
            pdfmetrics.registerFont(TTFont('DejaVu', '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'))
            pdfmetrics.registerFont(TTFont('DejaVu-Bold', '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'))
            font_name = 'DejaVu'
            bold_font_name = 'DejaVu-Bold'
        except:
            # Last resort - Helvetica (might not show Cyrillic)
            font_name = 'Helvetica'
            bold_font_name = 'Helvetica-Bold'
    
    # Get styles and apply our fonts
    styles = getSampleStyleSheet()
    
    # Create custom styles with our fonts
    from reportlab.lib.styles import ParagraphStyle
    
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=bold_font_name,
        fontSize=16,
        alignment=1,  # Center
        spaceAfter=20
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=font_name,
        fontSize=10
    )
    
    # Add title
    title_text = f"Отчет: {modeladmin.model._meta.verbose_name_plural}"
    title = Paragraph(title_text, title_style)
    elements.append(title)
    
    # Add generation date
    from datetime import datetime
    date_text = f"Сгенерировано: {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    date_para = Paragraph(date_text, normal_style)
    elements.append(date_para)
    elements.append(Paragraph("<br/>", normal_style))
    
    # Prepare data for table
    data = []
    
    # Add headers based on model with Russian text
    if modeladmin.model == Expert:
        data.append(["Имя", "Специализация", "Квалификация", "Email", "Дата"])
        for obj in queryset:
            # Convert all text to Unicode strings
            data.append([
                str(obj.name),
                str(obj.specialty),
                str(obj.qualification),
                str(obj.email),
                obj.join_date.strftime("%d.%m.%Y") if obj.join_date else "-"
            ])
    
    elif modeladmin.model == Resource:
        data.append(["Название", "Тип", "Эксперт", "Длительность", "Просмотры"])
        for obj in queryset:
            data.append([
                str(obj.title),
                str(obj.get_resource_type_display()),
                str(obj.expert.name) if obj.expert else "-",
                str(obj.duration),
                str(obj.views_count)
            ])
    
    elif modeladmin.model == User:
        data.append(["Имя пользователя", "Email", "Подписка", "Дата регистрации"])
        for obj in queryset:
            data.append([
                str(obj.username),
                str(obj.email),
                str(obj.get_subscription_type_display()) if hasattr(obj, 'get_subscription_type_display') else str(obj.subscription_type),
                obj.date_joined.strftime("%d.%m.%Y") if obj.date_joined else "-"
            ])
    
    elif modeladmin.model == SupportGroup:
        data.append(["Название группы", "Участников", "Модератор", "Создана"])
        for obj in queryset:
            data.append([
                str(obj.name),
                str(obj.members_count()),
                str(obj.moderator) if obj.moderator else "-",
                obj.created_date.strftime("%d.%m.%Y") if obj.created_date else "-"
            ])
    
    else:
        # Generic headers
        model_name = str(modeladmin.model._meta.verbose_name)
        data.append(["ID", model_name.capitalize(), "Дата создания"])
        for obj in queryset:
            created = getattr(obj, 'created_date', getattr(obj, 'join_date', 'N/A'))
            if hasattr(created, 'strftime'):
                created = created.strftime("%d.%m.%Y")
            data.append([str(obj.id), str(obj), str(created)])
    
    # Create table with better styling
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), bold_font_name),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), font_name),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('WORDWRAP', (0, 0), (-1, -1), True),
    ]))
    
    # Set column widths
    if data:
        num_cols = len(data[0])
        page_width = 500
        col_width = page_width / num_cols
        table._argW = [col_width] * num_cols
    
    elements.append(table)
    
    # Add footer
    elements.append(Paragraph("<br/><br/>", normal_style))
    footer_text = "© 2026 - Платформа управления стрессом"
    footer = Paragraph(footer_text, normal_style)
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get the PDF data
    pdf = buffer.getvalue()
    buffer.close()
    
    # Create response
    response = HttpResponse(content_type='application/pdf')
    filename = f"{modeladmin.model._meta.model_name}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    response.write(pdf)
    
    return response

generate_pdf_report.short_description = "Сгенерировать PDF отчет (выбранные элементы)"

# CSV Export Action
def export_to_csv(modeladmin, request, queryset):
    """Export selected objects to CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{modeladmin.model._meta.model_name}_export.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    if modeladmin.model == Expert:
        writer.writerow(['Name', 'Specialty', 'Qualification', 'Email', 'Join Date', 'Active'])
        for obj in queryset:
            writer.writerow([
                obj.name,
                obj.specialty,
                obj.qualification,
                obj.email,
                obj.join_date,
                'Yes' if obj.is_active else 'No'
            ])
    elif modeladmin.model == Resource:
        writer.writerow(['Title', 'Type', 'Expert', 'Duration', 'Difficulty', 'Views'])
        for obj in queryset:
            writer.writerow([
                obj.title,
                obj.get_resource_type_display(),
                obj.expert.name if obj.expert else '',
                obj.duration,
                obj.get_difficulty_level_display(),
                obj.views_count
            ])
    else:
        # Generic export
        writer.writerow(['ID', 'String Representation'])
        for obj in queryset:
            writer.writerow([obj.id, str(obj)])
    
    return response

export_to_csv.short_description = "Export to CSV"

# Action to mark as published/unpublished
def make_published(modeladmin, request, queryset): # update action!
    queryset.update(is_published=True)
    messages.success(request, f"{queryset.count()} resources were published")

make_published.short_description = "Mark selected as Published"

def make_unpublished(modeladmin, request, queryset):
    queryset.update(is_published=False)
    messages.success(request, f"{queryset.count()} resources were unpublished")

make_unpublished.short_description = "Mark selected as Unpublished"

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Административная панель для модели User"""
    list_display = [
        'username', 'email', 'first_name', 'last_name', 
        'subscription_type', 'stress_profile_completed', 
        'date_joined_display', 'get_full_name', 'avatar_preview'
    ]
    list_filter = ['subscription_type', 'stress_profile_completed', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    list_display_links = ['username', 'email']
    list_editable = ['subscription_type', 'stress_profile_completed']
    readonly_fields = ['date_joined', 'last_login', 'avatar_preview']
    date_hierarchy = 'date_joined'
    filter_horizontal = ['groups', 'user_permissions']
    raw_id_fields = []
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('username', 'email', 'password', 'first_name', 'last_name', 'phone')
        }),
        ('Профиль и аватар', {
            'fields': ('avatar', 'avatar_preview', 'birth_date', 'subscription_type', 'stress_profile_completed')
        }),
        ('Даты', {
            'fields': ('date_joined', 'last_login')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
    )
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    @admin.display(description='Дата регистрации', ordering='date_joined')
    def date_joined_display(self, obj):
        return obj.date_joined.strftime('%d.%m.%Y')
    
    @admin.display(description='Полное имя')
    def get_full_name(self, obj):
        return obj.get_full_name() or '-'
    
    @admin.display(description='Аватар')
    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />', obj.avatar.url)
        return '-'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


@admin.register(Expert)
class ExpertAdmin(admin.ModelAdmin):
    """Административная панель для модели Expert"""
    list_display = [
        'name', 'specialty', 'qualification', 'is_active', 
        'join_date', 'resources_count', 'photo_preview'
    ]
    list_filter = ['is_active', 'specialty', 'join_date']
    #__icontains INTERNALLY
    search_fields = ['name', 'specialty', 'qualification', 'email']
    list_display_links = ['name']
    list_editable = ['is_active']
    date_hierarchy = 'join_date'
    readonly_fields = ['photo_preview']
    raw_id_fields = []
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'email', 'website')
        }),
        ('Профессиональные данные', {
            'fields': ('specialty', 'qualification', 'bio')
        }),
        ('Медиа', {
            'fields': ('photo', 'photo_preview')
        }),
        ('Статус', {
            'fields': ('is_active', 'join_date')
        }),
    )
    
    @admin.display(description='Кол-во ресурсов')
    def resources_count(self, obj):
        count = obj.resources.count()
        url = f'/admin/stress_app/resource/?expert__id__exact={obj.id}'
        return format_html('<a href="{}">{} ресурсов</a>', url, count)
    
    @admin.display(description='Фото')
    def photo_preview(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 50%; object-fit: cover;" />', obj.photo.url)
        return '-'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('resources')


class ResourceInline(admin.TabularInline):
    """Инлайн для ресурсов в категории"""
    model = Resource
    extra = 0
    fields = ['title', 'resource_type', 'difficulty_level', 'is_published', 'file_preview']
    readonly_fields = ['upload_date', 'file_preview']
    show_change_link = True
    raw_id_fields = ['expert']
    
    def file_preview(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">📎 Файл</a>', obj.file.url)
        return '-'
    file_preview.short_description = 'Файл'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Административная панель для модели Category"""
    list_display = [
        'name', 'parent', 'is_active', 'order', 
        'resources_count', 'icon_preview'
    ]
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'description']
    list_display_links = ['name']
    list_editable = ['order', 'is_active']
    raw_id_fields = ['parent']
    readonly_fields = ['icon_preview']
    inlines = [ResourceInline]
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'parent')
        }),
        ('Настройки отображения', {
            'fields': ('icon', 'icon_preview', 'order', 'is_active')
        }),
    )
    
    @admin.display(description='Ресурсов')
    def resources_count(self, obj):
        count = obj.resources.count()
        return count
    
    @admin.display(description='Иконка')
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" width="30" height="30" />', obj.icon.url)
        return '-'
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('resources')


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """Административная панель для модели Resource"""
    list_display = [
        'title', 'resource_type', 'category', 'expert',
        'duration', 'difficulty_level', 'views_count', 'is_published',
        'file_indicator', 'cover_preview'  # REMOVED file_info from here!
    ]
    list_filter = ['resource_type', 'difficulty_level', 'is_published', 'category']
    search_fields = ['title', 'content', 'expert__name']
    list_display_links = ['title']
    list_editable = ['is_published']
    date_hierarchy = 'upload_date'
    readonly_fields = ['upload_date', 'views_count', 'cover_preview_display', 'file_info_display']
    raw_id_fields = ['expert', 'category']
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv, make_published, make_unpublished]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'content', 'resource_type')
        }),
        ('Классификация', {
            'fields': ('category', 'expert', 'difficulty_level', 'duration')
        }),
        ('Медиа файлы', {
            'fields': ('cover_image', 'cover_preview_display', 'file', 'file_info_display')
        }),
        ('Статистика и статус', {
            'fields': ('views_count', 'is_published', 'upload_date')
        }),
    )
    
    @admin.display(description='Файл')
    def file_indicator(self, obj):
        if obj.file:
            return "✅ Есть"
        return "❌ Нет"
    
    @admin.display(description='Обложка')
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.cover_image.url)
        return '-'
    
    # This is for readonly_fields - safe version without format_html
    @admin.display(description='Предпросмотр обложки')
    def cover_preview_display(self, obj):
        if obj.cover_image:
            return mark_safe(f'<img src="{obj.cover_image.url}" width="100" style="max-height: 100px; object-fit: contain;" />')
        return "Нет изображения"
    
    # This is for readonly_fields - FIXED VERSION without format_html
    @admin.display(description='Информация о файле')
    def file_info_display(self, obj):
        if obj.file and obj.file.name:
            size = obj.get_file_size() or "Неизвестно"
            ext = obj.get_file_extension() or "Неизвестно"
            return mark_safe(
                f'<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
                f'<strong>Размер:</strong> {size}<br>'
                f'<strong>Тип:</strong> {ext}<br>'
                f'<strong>Имя:</strong> {obj.file.name}<br>'
                f'<a href="{obj.file.url}" target="_blank" style="display: inline-block; margin-top: 10px; padding: 8px 15px; background: #417690; color: white; text-decoration: none; border-radius: 4px;">📥 Скачать файл</a>'
                f'</div>'
            )
        return "Файл не загружен"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('category', 'expert')

class GroupMembershipInline(admin.TabularInline):
    """Инлайн для участников группы"""
    model = GroupMembership
    extra = 0
    fields = ['user', 'role', 'join_date', 'is_active']
    readonly_fields = ['join_date', 'last_active']
    raw_id_fields = ['user']
    show_change_link = True


@admin.register(SupportGroup)
class SupportGroupAdmin(admin.ModelAdmin):
    """Административная панель для модели SupportGroup"""
    list_display = [
        'name', 'moderator', 'created_date', 
        'members_count', 'max_members', 'is_private', 'image_preview'
    ]
    list_filter = ['is_private', 'created_date']
    search_fields = ['name', 'description', 'tags']
    list_display_links = ['name']
    list_editable = ['is_private']
    date_hierarchy = 'created_date'
    raw_id_fields = ['moderator']
    readonly_fields = ['image_preview']
    inlines = [GroupMembershipInline]
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'tags')
        }),
        ('Настройки', {
            'fields': ('moderator', 'max_members', 'is_private', 'meeting_schedule')
        }),
        ('Медиа', {
            'fields': ('group_image', 'image_preview')
        }),
    )
    
    @admin.display(description='Изображение')
    def image_preview(self, obj):
        if obj.group_image:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 8px; object-fit: cover;" />', obj.group_image.url)
        return '-'
    
    @admin.display(description='Участников')
    def members_count(self, obj):
        count = obj.memberships.filter(is_active=True).count() # uses count()!
        return f"{count}/{obj.max_members}"
        
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('moderator')


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    """Административная панель для модели GroupMembership"""
    list_display = ['user', 'group', 'role', 'join_date', 'is_active']
    list_filter = ['role', 'is_active', 'join_date']
    search_fields = ['user__username', 'user__email', 'group__name']
    list_display_links = ['user', 'group']
    list_editable = ['role', 'is_active']
    date_hierarchy = 'join_date'
    raw_id_fields = ['user', 'group']
    readonly_fields = ['join_date', 'last_active']
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'group', 'role', 'is_active')
        }),
        ('Даты', {
            'fields': ('join_date', 'last_active'),
        }),
    )


@admin.register(StressJournal)
class StressJournalAdmin(admin.ModelAdmin):
    """Административная панель для модели StressJournal"""
    list_display = [
        'user', 'entry_date', 'stress_level', 
        'mood', 'sleep_hours', 'has_triggers'
    ]
    list_filter = ['stress_level', 'entry_date', 'user']
    search_fields = ['user__username', 'user__email', 'notes', 'triggers']
    list_display_links = ['user', 'entry_date']
    date_hierarchy = 'entry_date'
    raw_id_fields = ['user']
    readonly_fields = ['created_at']
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'entry_date')
        }),
        ('Оценки', {
            'fields': ('stress_level', 'mood', 'sleep_hours')
        }),
        ('Детали', {
            'fields': ('notes', 'triggers', 'coping_methods')
        }),
        ('Метаданные', {
            'fields': ('created_at',)
        }),
    )
    
    @admin.display(description='Есть триггеры', boolean=True)
    def has_triggers(self, obj):
        return bool(obj.triggers)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(WellnessPlan)
class WellnessPlanAdmin(admin.ModelAdmin):
    """Административная панель для модели WellnessPlan"""
    list_display = [
        'user', 'goal_type', 'current_week', 
        'duration_weeks', 'completed', 'end_date'
    ]
    list_filter = ['goal_type', 'completed', 'daily_reminder']
    search_fields = ['user__username', 'goal']
    list_display_links = ['user', 'goal_type']
    list_editable = ['completed', 'current_week']
    date_hierarchy = 'created_date'
    raw_id_fields = ['user']
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        ('Пользователь', {
            'fields': ('user', 'goal_type', 'goal')
        }),
        ('Прогресс', {
            'fields': ('current_week', 'duration_weeks', 'completed')
        }),
        ('Даты', {
            'fields': ('start_date', 'end_date', 'created_date')
        }),
        ('Настройки', {
            'fields': ('daily_reminder', 'notes')
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(UserSavedResource)
class UserSavedResourceAdmin(admin.ModelAdmin):
    """Административная панель для модели UserSavedResource"""
    list_display = ['user', 'resource', 'saved_date', 'is_favorite']
    list_filter = ['is_favorite', 'saved_date']
    search_fields = ['user__username', 'resource__title']
    list_display_links = ['user', 'resource']
    list_editable = ['is_favorite']
    date_hierarchy = 'saved_date'
    raw_id_fields = ['user', 'resource']
    readonly_fields = ['saved_date']
    
    # Add admin actions
    actions = [generate_pdf_report, export_to_csv]
    
    fieldsets = (
        (None, {
            'fields': ('user', 'resource', 'is_favorite', 'notes')
        }),
        ('Дата', {
            'fields': ('saved_date',),
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'resource')