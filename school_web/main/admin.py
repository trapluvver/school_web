from django.contrib import admin
from .models import *
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Q
from django.urls import reverse
from django.utils.html import format_html
from django.http import HttpResponseRedirect
from collections import defaultdict


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'post', 'get_subjects_display', 'category', 'experience']
    list_filter = ['category', 'post', 'subjects']
    search_fields = ['full_name', 'post', 'education']
    filter_horizontal = ['subjects']
    list_per_page = 20

    def get_urls(self):
        # Получаем оригинальные URL от родительского класса
        urls = super().get_urls()

        # Определяем кастомные URL - используем self.admin_site для доступа к методам класса
        custom_urls = [
            path('teachers-report/', self.admin_site.admin_view(self.teachers_report), name='teachers_report'),
            path('subjects-teachers-report/', self.admin_site.admin_view(self.subjects_teachers_report),
                 name='subjects_teachers_report'),
            path('prof-retrain-report/', self.admin_site.admin_view(self.prof_retrain_report),
                 name='prof_retrain_report'),
            path('teachers-classes-report/', self.admin_site.admin_view(self.teachers_classes_report),
                 name='teachers_classes_report'),
            path('extra-activities-report/', self.admin_site.admin_view(self.extra_activities_report),
                 name='extra_activities_report'),
            path('schedule-report/', self.admin_site.admin_view(self.schedule_report), name='schedule_report'),
            path('extra-schedule-report/', self.admin_site.admin_view(self.extra_schedule_report),
                 name='extra_schedule_report'),
        ]

        # Правильно объединяем URL - сначала кастомные, потом оригинальные
        return custom_urls + urls

    def schedule_report(self, request):
        """Отчет по расписанию уроков"""
        # Получаем все расписания с оптимизацией запросов
        schedules = Schedule.objects.all().select_related(
            'subject', 'school_class', 'cabinet'
        ).order_by('day_of_week', 'lesson_number', 'school_class__number')

        # Фильтры
        day_filter = request.GET.get('day')
        class_filter = request.GET.get('class')
        subject_filter = request.GET.get('subject')

        if day_filter and day_filter != 'all':
            schedules = schedules.filter(day_of_week=day_filter)

        if class_filter and class_filter != 'all':
            schedules = schedules.filter(school_class_id=class_filter)

        if subject_filter and subject_filter != 'all':
            schedules = schedules.filter(subject_id=subject_filter)

        # Статистика
        total_lessons = schedules.count()

        # Группируем по дням недели
        day_stats = schedules.values('day_of_week').annotate(
            count=Count('id')
        ).order_by('day_of_week')

        # Группируем по классам
        class_stats = schedules.values(
            'school_class__number'
        ).annotate(
            count=Count('id')
        ).order_by('school_class__number')

        # Получаем список классов для фильтра
        all_classes = SchoolGroup.objects.all().order_by('number')
        all_subjects = Subject.objects.all().order_by('full_name')

        # Группируем расписание для удобного отображения
        schedule_by_day = defaultdict(lambda: defaultdict(list))

        for schedule in schedules:
            day_name = schedule.get_day_of_week_display()
            class_name = schedule.school_class.number if schedule.school_class else "—"
            schedule_by_day[day_name][class_name].append(schedule)

        # Сортируем дни и классы
        day_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']
        sorted_days = sorted(schedule_by_day.keys(), key=lambda x: day_order.index(x) if x in day_order else 99)

        context = {
            'schedule_by_day': dict(schedule_by_day),
            'sorted_days': sorted_days,
            'all_classes': all_classes,
            'all_subjects': all_subjects,
            'total_lessons': total_lessons,
            'day_stats': day_stats,
            'class_stats': class_stats,
            'day_filter': day_filter or 'all',
            'class_filter': class_filter or 'all',
            'subject_filter': subject_filter or 'all',
            'title': 'Отчет по расписанию уроков',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/schedule_report.html', context)

    def extra_schedule_report(self, request):
        """Отчет по расписанию дополнительных занятий"""
        # Получаем все расписания дополнительных занятий
        extra_schedules = ExtraSchedule.objects.all().select_related(
            'activity', 'cabinet', 'activity__teacher'
        ).order_by('day_of_week', 'lesson_number', 'activity__name')

        # Фильтры
        day_filter = request.GET.get('day')
        activity_type_filter = request.GET.get('activity_type')

        if day_filter and day_filter != 'all':
            extra_schedules = extra_schedules.filter(day_of_week=day_filter)

        if activity_type_filter and activity_type_filter != 'all':
            extra_schedules = extra_schedules.filter(activity__activity_type=activity_type_filter)

        # Статистика
        total_activities = extra_schedules.count()

        # Группируем по дням недели
        day_stats = extra_schedules.values('day_of_week').annotate(
            count=Count('id')
        ).order_by('day_of_week')

        # Группируем по типам занятий
        type_stats = extra_schedules.values(
            'activity__activity_type'
        ).annotate(
            count=Count('id')
        ).order_by('activity__activity_type')

        # Группируем расписание для удобного отображения - простая структура
        schedule_data = []
        day_order = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота']

        # Сначала создаем структуру для всех дней
        day_dict = {day_name: [] for day_name in day_order}

        for schedule in extra_schedules:
            day_name = schedule.get_day_of_week_display()
            day_dict[day_name].append({
                'schedule': schedule,
                'activity': schedule.activity,
                'teacher': schedule.activity.teacher,
                'cabinet': schedule.cabinet,
                'time': schedule.get_lesson_number_display(),
                'day': day_name
            })

        # Преобразуем в список для шаблона
        for day_name in day_order:
            activities = day_dict[day_name]
            if activities:
                schedule_data.append({
                    'day_name': day_name,
                    'activities': sorted(activities, key=lambda x: x['schedule'].lesson_number)
                })

        context = {
            'schedule_data': schedule_data,
            'total_activities': total_activities,
            'day_stats': day_stats,
            'type_stats': type_stats,
            'day_filter': day_filter or 'all',
            'activity_type_filter': activity_type_filter or 'all',
            'title': 'Отчет по расписанию дополнительных занятий',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/extra_schedule_report.html', context)
    def extra_activities_report(self, request):
        """Отчет по дополнительным занятиям"""
        # Получаем все дополнительные занятия
        activities = ExtraActivity.objects.all().select_related('teacher').prefetch_related(
            'extraschedule_set').order_by('name')

        # Фильтры
        activity_type = request.GET.get('activity_type')
        is_active = request.GET.get('is_active')

        if activity_type and activity_type != 'all':
            activities = activities.filter(activity_type=activity_type)

        if is_active and is_active != 'all':
            activities = activities.filter(is_active=(is_active == 'yes'))

        # Статистика
        total_activities = activities.count()
        active_activities = activities.filter(is_active=True).count()
        inactive_activities = total_activities - active_activities

        # Группируем по типам занятий
        type_stats = activities.values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')

        # Группируем по преподавателям
        teacher_stats = activities.values(
            'teacher__full_name',
            'teacher__post'
        ).annotate(
            count=Count('id')
        ).order_by('-count')

        # Подготавливаем данные для отчета
        activity_data = []
        for activity in activities:
            schedules = activity.extraschedule_set.all()
            schedule_count = schedules.count()

            # Формируем список расписаний
            schedule_list = []
            for schedule in schedules:
                schedule_list.append({
                    'day': schedule.get_day_of_week_display(),
                    'time': schedule.get_lesson_number_display(),
                    'cabinet': schedule.cabinet.number if schedule.cabinet else "—"
                })

            activity_data.append({
                'activity': activity,
                'teacher': activity.teacher,
                'schedules': schedule_list,
                'schedule_count': schedule_count,
                'max_students': activity.max_students,
                'is_active': activity.is_active,
            })

        context = {
            'activity_data': activity_data,
            'total_activities': total_activities,
            'active_activities': active_activities,
            'inactive_activities': inactive_activities,
            'type_stats': type_stats,
            'teacher_stats': teacher_stats,
            'activity_type_filter': activity_type or 'all',
            'is_active_filter': is_active or 'all',
            'title': 'Отчет по дополнительным занятиям',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/extra_activities_report.html', context)

    def teachers_classes_report(self, request):
        """Отчет по учителям и классам"""
        # Получаем всех учителей с классами
        teachers = Teacher.objects.all().prefetch_related('schoolgroup_set').order_by('full_name')

        # Фильтры
        has_classes = request.GET.get('has_classes')
        if has_classes == 'yes':
            teachers = teachers.filter(schoolgroup__isnull=False).distinct()
        elif has_classes == 'no':
            teachers = teachers.filter(schoolgroup__isnull=True)

        # Статистика
        total_teachers = Teacher.objects.count()
        with_classes = Teacher.objects.filter(schoolgroup__isnull=False).distinct().count()
        without_classes = total_teachers - with_classes

        # Группируем по должностям
        post_stats = teachers.values('post').annotate(
            count=Count('id')
        ).order_by('-count')

        # Подготавливаем данные для отчета
        teacher_data = []
        for teacher in teachers:
            classes = teacher.schoolgroup_set.all()
            cabinets = teacher.cabinet_set.all()

            teacher_data.append({
                'teacher': teacher,
                'classes': classes,
                'classes_count': classes.count(),
                'cabinet_numbers': ", ".join([cab.number for cab in cabinets]) if cabinets else "—",
                'cabinets_count': cabinets.count(),
            })

        context = {
            'teacher_data': teacher_data,
            'total_teachers': total_teachers,
            'with_classes': with_classes,
            'without_classes': without_classes,
            'post_stats': post_stats,
            'has_classes_filter': has_classes,
            'title': 'Отчет по учителям и классам',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/teachers_classes_report.html', context)

    def prof_retrain_report(self, request):
        """Отчет по переподготовке преподавателей"""
        # Получаем всех преподавателей с переподготовкой
        teachers = Teacher.objects.all().order_by('full_name')

        # Фильтры
        has_retrain = request.GET.get('has_retrain')
        if has_retrain == 'yes':
            teachers = teachers.filter(prof_retrain__isnull=False).exclude(prof_retrain__exact='')
        elif has_retrain == 'no':
            teachers = teachers.filter(Q(prof_retrain__isnull=True) | Q(prof_retrain__exact=''))

        # Статистика
        total_teachers = Teacher.objects.count()
        with_retrain = Teacher.objects.filter(
            prof_retrain__isnull=False
        ).exclude(prof_retrain__exact='').count()
        without_retrain = total_teachers - with_retrain

        # Группируем по категориям
        category_stats = teachers.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        context = {
            'teachers': teachers,
            'total_teachers': total_teachers,
            'with_retrain': with_retrain,
            'without_retrain': without_retrain,
            'category_stats': category_stats,
            'has_retrain_filter': has_retrain,
            'title': 'Отчет по профессиональной переподготовке преподавателей',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/prof_retrain_report.html', context)

    def subjects_teachers_report(self, request):
        """Отчет по предметам и преподавателям"""
        # Получаем все предметы с преподавателями
        subjects = Subject.objects.all().prefetch_related('teacher_set').order_by('full_name')

        # Статистика
        total_subjects = subjects.count()
        subjects_with_teachers = subjects.filter(teacher__isnull=False).distinct().count()
        subjects_without_teachers = total_subjects - subjects_with_teachers

        # Группируем данные для отчета
        subject_data = []
        for subject in subjects:
            teachers = subject.teacher_set.all()
            subject_data.append({
                'subject': subject,
                'teachers': teachers,
                'teachers_count': teachers.count()
            })

        context = {
            'subject_data': subject_data,
            'total_subjects': total_subjects,
            'subjects_with_teachers': subjects_with_teachers,
            'subjects_without_teachers': subjects_without_teachers,
            'title': 'Отчет по предметам и преподавателям',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/subjects_teachers_report.html', context)

    # Используем кастомный шаблон
    change_list_template = "admin/teachers/teacher_change_list.html"

    # Поля для формы редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'post', 'category', 'experience')
        }),
        ('Образование и предметы', {
            'fields': ('education', 'subjects', 'prof_retrain')
        }),
    )

    def teachers_report(self, request):
        # Получаем всех преподавателей с оптимизацией запроса
        teachers = Teacher.objects.all().prefetch_related('subjects').order_by('full_name')

        # Статистика по категориям
        categories_stats = Teacher.objects.values('category').annotate(
            count=Count('id')
        ).order_by('-count')

        # Статистика по должностям
        posts_stats = Teacher.objects.values('post').annotate(
            count=Count('id')
        ).order_by('-count')

        # Контекст для шаблона
        context = {
            'teachers': teachers,
            'total_count': teachers.count(),
            'categories_stats': categories_stats,
            'posts_stats': posts_stats,
            'title': 'Отчет о преподавательском составе',
            **self.admin_site.each_context(request)
        }

        return render(request, 'admin/teachers/report_template.html', context)

    # Дополнительные методы для админки
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('subjects')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        # Добавляем поле subjects в нужный fieldset
        fieldsets[1][1]['fields'] = ('education', 'subjects', 'prof_retrain')
        return fieldsets

    # Добавим кнопки отчетов в интерфейс админки
    def changelist_view(self, request, extra_context=None):
        # Добавляем ссылки на отчеты в контекст
        extra_context = extra_context or {}
        extra_context['report_urls'] = {
            'teachers_report': reverse('admin:teachers_report'),
            'subjects_teachers_report': reverse('admin:subjects_teachers_report'),
            'prof_retrain_report': reverse('admin:prof_retrain_report'),
            'teachers_classes_report': reverse('admin:teachers_classes_report'),
            'extra_activities_report': reverse('admin:extra_activities_report'),
            'schedule_report': reverse('admin:schedule_report'),
            'extra_schedule_report': reverse('admin:extra_schedule_report'),
        }
        return super().changelist_view(request, extra_context=extra_context)


# Остальные модели регистрируем как обычно
@admin.register(Cabinet)
class CabinetAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher']
    list_filter = ['teacher']
    search_fields = ['number', 'teacher__full_name']


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'short_name', 'teachers_count']
    search_fields = ['full_name', 'short_name']

    def teachers_count(self, obj):
        return obj.teacher_set.count()

    teachers_count.short_description = 'Количество учителей'


@admin.register(SchoolGroup)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ['number', 'teacher', 'cabinet']
    list_filter = ['teacher']
    search_fields = ['number', 'teacher__full_name']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'school_class', 'phone']
    list_filter = ['school_class']
    search_fields = ['full_name', 'parent_name', 'phone']


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'day_of_week_display',
        'lesson_display',
        'subject',
        'school_class',
        'cabinet'
    ]
    list_filter = ['day_of_week', 'lesson_number', 'subject', 'school_class']
    search_fields = ['subject__full_name', 'school_class__number', 'info']
    list_per_page = 20

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()

    day_of_week_display.short_description = 'День недели'

    def lesson_display(self, obj):
        return obj.get_lesson_number_display()

    lesson_display.short_description = 'Урок'

    # Поля для формы редактирования
    fieldsets = (
        ('Основная информация', {
            'fields': ('day_of_week', 'lesson_number', 'info')
        }),
        ('Расписание', {
            'fields': ('subject', 'school_class', 'cabinet')
        }),
    )


# Список дополнительных занятий
@admin.register(ExtraActivity)
class ExtraActivityAdmin(admin.ModelAdmin):
    list_display = ['name', 'activity_type', 'teacher', 'max_students', 'is_active']
    list_filter = ['activity_type', 'is_active', 'teacher']
    search_fields = ['name', 'description', 'teacher__full_name']
    list_editable = ['is_active']

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'description', 'activity_type')
        }),
        ('Организация', {
            'fields': ('teacher', 'max_students', 'is_active')
        }),
    )


# Расписание дополнительных занятий
@admin.register(ExtraSchedule)
class ExtraScheduleAdmin(admin.ModelAdmin):
    list_display = [
        'day_of_week_display',
        'lesson_display',
        'activity',
        'teacher',
        'cabinet'
    ]
    list_filter = ['day_of_week', 'lesson_number', 'activity__activity_type']
    search_fields = ['activity__name', 'cabinet__number', 'activity__teacher__full_name']

    def day_of_week_display(self, obj):
        return obj.get_day_of_week_display()

    day_of_week_display.short_description = 'День недели'

    def lesson_display(self, obj):
        return obj.get_lesson_number_display()

    lesson_display.short_description = 'Время'

    def teacher(self, obj):
        return obj.activity.teacher

    teacher.short_description = 'Преподаватель'

    fieldsets = (
        ('Расписание', {
            'fields': ('day_of_week', 'lesson_number', 'cabinet')
        }),
        ('Занятие', {
            'fields': ('activity',)
        }),
    )


# Также нужно зарегистрировать модель Task если она используется
@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task']
    search_fields = ['title', 'task']


# И модель TeacherSubject если она используется
@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ['teacher', 'subject', 'info']
    list_filter = ['teacher', 'subject']
    search_fields = ['teacher__full_name', 'subject__full_name', 'info']