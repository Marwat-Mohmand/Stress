# stress_app/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import os

def resource_file_path(instance, filename):
    """Generate file path for resource files"""
    # File will be uploaded to MEDIA_ROOT/resources/<type>/<filename>
    return f'resources/{instance.resource_type}/{filename}'

def expert_photo_path(instance, filename):
    """Generate file path for expert photos"""
    # File will be uploaded to MEDIA_ROOT/expert_photos/<name>_<filename>
    return f'expert_photos/{instance.name}_{filename}'

class User(AbstractUser):
    """Модель пользователя"""
    email = models.EmailField(unique=True, verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name='Телефон')
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name='Дата регистрации')
    subscription_type = models.CharField(
        max_length=20,
        choices=[
            ('free', 'Бесплатный'),
            ('basic', 'Базовый'),
            ('premium', 'Премиум'),
        ],
        default='free',
        verbose_name='Тип подписки'
    )
    stress_profile_completed = models.BooleanField(default=False, verbose_name='Профиль стресса заполнен')
    birth_date = models.DateField(blank=True, null=True, verbose_name='Дата рождения')
    
    # ImageField for user avatar
    avatar = models.ImageField(
        upload_to='avatars/', 
        blank=True, 
        null=True, 
        verbose_name='Аватар',
        help_text='Загрузите изображение для аватара (JPEG, PNG)'
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name="custom_user_set",
        related_query_name="custom_user",
    )

    def __str__(self):
        return f"{self.username} - {self.get_full_name()}"
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']


class Expert(models.Model):
    """Модель эксперта/создателя контента"""
    name = models.CharField(max_length=200, verbose_name='Имя')
    bio = models.TextField(verbose_name='Биография')
    specialty = models.CharField(max_length=200, verbose_name='Специализация')
    qualification = models.CharField(max_length=200, verbose_name='Квалификация')
    
    # ImageField for expert photo
    photo = models.ImageField(
        upload_to=expert_photo_path, 
        blank=True, 
        null=True, 
        verbose_name='Фото',
        help_text='Загрузите фотографию эксперта'

    )

    website = models.URLField(
        blank=True, 
        null=True, 
        verbose_name='Веб-сайт',
        help_text='Ссылка на профессиональный сайт эксперта'
    )

    
    join_date = models.DateField(default=timezone.now, verbose_name='Дата присоединения')
    email = models.EmailField(verbose_name='Email')
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    website = models.URLField(blank=True, null=True, verbose_name='Вебсайт')

    def __str__(self):
        return f"{self.name} - {self.specialty}"
    
    class Meta:
        verbose_name = 'Эксперт'
        verbose_name_plural = 'Эксперты'
        ordering = ['name']


class Category(models.Model):
    """Модель категории ресурсов"""
    name = models.CharField(max_length=100, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='subcategories',
        verbose_name='Родительская категория'
    )
    
    # ImageField for category icon
    icon = models.ImageField(
        upload_to='category_icons/', 
        blank=True, 
        null=True, 
        verbose_name='Иконка',
        help_text='Иконка для категории (32x32 px)'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')

    def __str__(self):
        if self.parent:
            return f"{self.parent.name} → {self.name}"
        return self.name
    
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['order', 'name']


class Resource(models.Model):
    """Модель ресурса (статья, медитация, видео)"""
    RESOURCE_TYPES = [
        ('article', 'Статья'),
        ('meditation', 'Медитация'),
        ('video', 'Видео'),
        ('audio', 'Аудио'),
        ('exercise', 'Упражнение'),
    ]
    
    DIFFICULTY_LEVELS = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    content = models.TextField(verbose_name='Содержание')
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES, verbose_name='Тип ресурса')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        related_name='resources',
        verbose_name='Категория'
    )
    expert = models.ForeignKey(
        Expert,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='resources',
        verbose_name='Эксперт'
    )
    duration = models.PositiveIntegerField(help_text='Длительность в минутах', verbose_name='Длительность')
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_LEVELS, verbose_name='Уровень сложности')
    upload_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата загрузки')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    views_count = models.PositiveIntegerField(default=0, verbose_name='Количество просмотров')
    
    # ImageField for cover image
    cover_image = models.ImageField(
        upload_to='resource_covers/', 
        blank=True, 
        null=True, 
        verbose_name='Обложка',
        help_text='Изображение для обложки ресурса'
    )
    
    # FileField for resource file (PDF, audio, etc.)
    file = models.FileField(
        upload_to=resource_file_path, 
        blank=True, 
        null=True, 
        verbose_name='Файл',
        help_text='Загрузите файл ресурса (PDF, MP3, MP4 и т.д.)',
        validators=[FileExtensionValidator(allowed_extensions=['pdf', 'mp3', 'mp4', 'txt', 'doc', 'docx'])]

    )

    source_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name='URL источника',
        help_text='Ссылка на оригинальный источник материала'
    )
    
    video_url = models.URLField(
        blank=True, 
        null=True, 
        verbose_name='Ссылка на видео',
        help_text='Ссылка на YouTube или Vimeo видео'
    )

    def __str__(self):
        return f"{self.title} ({self.get_resource_type_display()})"
    
    # Custom functional method (Requirement: Creating your own functional method in a model)
    def get_file_size(self):
        """Return file size in human-readable format"""
        if self.file and hasattr(self.file, 'size'):
            size_bytes = self.file.size
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"
        return "Нет файла"
    
    def get_file_extension(self):
        """Return file extension"""
        if self.file:
            name, ext = os.path.splitext(self.file.name)
            return ext[1:].upper() if ext else "Unknown"
        return "None"
    
    def is_audio(self):
        """Check if resource is audio type"""
        return self.resource_type == 'audio' or (
            self.file and self.file.name.lower().endswith(('.mp3', '.wav', '.ogg'))
        )
    
    class Meta:
        verbose_name = 'Ресурс'
        verbose_name_plural = 'Ресурсы'
        ordering = ['-upload_date']


class GroupMembership(models.Model):
    """Модель членства в группе"""
    ROLES = [
        ('member', 'Участник'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='group_memberships',
        verbose_name='Пользователь'
    )
    group = models.ForeignKey(
        'SupportGroup',
        on_delete=models.CASCADE,
        related_name='memberships',
        verbose_name='Группа'
    )
    join_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата присоединения')
    role = models.CharField(max_length=20, choices=ROLES, default='member', verbose_name='Роль')
    is_active = models.BooleanField(default=True, verbose_name='Активно')
    last_active = models.DateTimeField(auto_now=True, verbose_name='Последняя активность')

    def __str__(self):
        return f"{self.user.username} → {self.group.name} ({self.get_role_display()})"
    
    class Meta:
        verbose_name = 'Участник группы'
        verbose_name_plural = 'Участники групп'
        unique_together = ['user', 'group']


class SupportGroup(models.Model):
    """Модель группы поддержки"""
    name = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='moderated_groups',
        verbose_name='Модератор'
    )
    max_members = models.PositiveIntegerField(default=20, verbose_name='Максимум участников')
    meeting_schedule = models.CharField(max_length=200, blank=True, verbose_name='Расписание встреч')
    is_private = models.BooleanField(default=False, verbose_name='Закрытая группа')
    tags = models.CharField(max_length=500, blank=True, help_text='Теги через запятую', verbose_name='Теги')
    
    # ImageField for group image
    group_image = models.ImageField(
        upload_to='group_images/', 
        blank=True, 
        null=True, 
        verbose_name='Изображение',
        help_text='Изображение для группы поддержки'
    )
    
    members = models.ManyToManyField(
        User,
        through='GroupMembership',
        through_fields=('group', 'user'),
        related_name='joined_groups'
    )

    meeting_link = models.URLField(
        blank=True, 
        null=True, 
        verbose_name='Ссылка на встречу',
        help_text='Zoom, Google Meet или другая ссылка для онлайн встреч'
    )

    def __str__(self):
        return f"{self.name} ({self.members_count()}/{self.max_members})"
    
    def members_count(self):
        return self.memberships.filter(is_active=True).count()
    members_count.short_description = 'Участников'
    
    class Meta:
        verbose_name = 'Группа поддержки'
        verbose_name_plural = 'Группы поддержки'
        ordering = ['-created_date']


class WellnessPlan(models.Model):
    """Модель плана оздоровления"""
    GOAL_TYPES = [
        ('stress_reduction', 'Снижение стресса'),
        ('sleep_improvement', 'Улучшение сна'),
        ('anxiety_management', 'Управление тревогой'),
        ('mindfulness', 'Осознанность'),
        ('self_care', 'Забота о себе'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='wellness_plans',
        verbose_name='Пользователь'
    )
    created_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    goal_type = models.CharField(max_length=30, choices=GOAL_TYPES, verbose_name='Тип цели')
    goal = models.TextField(verbose_name='Цель')
    duration_weeks = models.PositiveIntegerField(default=4, verbose_name='Длительность (недель)')
    current_week = models.PositiveIntegerField(default=1, verbose_name='Текущая неделя')
    completed = models.BooleanField(default=False, verbose_name='Завершен')
    start_date = models.DateField(default=timezone.now, verbose_name='Дата начала')
    end_date = models.DateField(blank=True, null=True, verbose_name='Дата окончания')
    daily_reminder = models.BooleanField(default=True, verbose_name='Ежедневное напоминание')
    notes = models.TextField(blank=True, verbose_name='Заметки')

    def __str__(self):
        return f"{self.user.username} - {self.get_goal_type_display()} ({self.current_week}/{self.duration_weeks})"
    
    def save(self, *args, **kwargs):
        if not self.end_date and self.start_date:
            from datetime import timedelta
            self.end_date = self.start_date + timedelta(weeks=self.duration_weeks)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = 'План оздоровления'
        verbose_name_plural = 'Планы оздоровления'
        ordering = ['-created_date']


class StressJournal(models.Model):
    """Модель журнала стресса"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='journal_entries',
        verbose_name='Пользователь'
    )
    entry_date = models.DateField(default=timezone.now, verbose_name='Дата записи')
    stress_level = models.PositiveSmallIntegerField(
        choices=[(i, str(i)) for i in range(1, 11)],
        verbose_name='Уровень стресса'
    )
    mood = models.CharField(max_length=100, verbose_name='Настроение')
    notes = models.TextField(blank=True, verbose_name='Заметки')
    triggers = models.TextField(blank=True, verbose_name='Триггеры')
    coping_methods = models.TextField(blank=True, verbose_name='Методы преодоления')
    sleep_hours = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True, verbose_name='Часов сна')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    def __str__(self):
        return f"{self.user.username} - {self.entry_date} (Стресс: {self.stress_level})"
    
    class Meta:
        verbose_name = 'Запись журнала стресса'
        verbose_name_plural = 'Записи журнала стресса'
        ordering = ['-entry_date']
        unique_together = ['user', 'entry_date']


class UserSavedResource(models.Model):
    """Модель сохраненных ресурсов пользователя"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='saved_resources',
        verbose_name='Пользователь'
    )
    resource = models.ForeignKey(
        Resource,
        on_delete=models.CASCADE,
        related_name='saved_by_users',
        verbose_name='Ресурс'
    )
    saved_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата сохранения')
    notes = models.CharField(max_length=500, blank=True, verbose_name='Заметки')
    is_favorite = models.BooleanField(default=False, verbose_name='Избранное')

    def __str__(self):
        return f"{self.user.username} - {self.resource.title}"
    
    class Meta:
        verbose_name = 'Сохраненный ресурс'
        verbose_name_plural = 'Сохраненные ресурсы'
        unique_together = ['user', 'resource']