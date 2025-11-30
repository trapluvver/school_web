from django.db import models

# Проверка работы бд
class Task(models.Model):
    title = models.CharField('Название', max_length=50)
    task = models.TextField('Описание')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'

#Предметы
class Subject(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Subject')
    full_name = models.CharField(max_length=35, db_column='Full_name')
    short_name = models.CharField(max_length=20, null=True, blank=True, db_column='Short_name')

    def __str__(self):
        return self.full_name

    class Meta:
        db_table = 'Subject'
        verbose_name = 'Предмет'
        verbose_name_plural = 'Предметы'

# Таблица учитель
class Teacher(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Teacher')
    full_name = models.CharField(max_length=35, db_column='FIO')
    post = models.CharField(max_length=20, db_column='Post')
    category = models.CharField(max_length=15, null=True, blank=True, db_column='Category')
    education = models.CharField(max_length=70, db_column='Education', null=True, blank=True)
    #lesson = models.CharField(max_length=60, db_column='Lesson') # Нужно увеличить размерность

    subjects = models.ManyToManyField(
        Subject,
        verbose_name='Предметы',
        blank=True
    )

    experience = models.CharField(max_length=30, null=True, blank=True, db_column='Experience')
    prof_retrain = models.CharField(max_length=70, null=True, blank=True, db_column='Prof_retrain')

    # Метод для получения предметов в виде строки
    def get_subjects_display(self):
        return ", ".join([str(subject) for subject in self.subjects.all()]) or "Не указано"

    get_subjects_display.short_description = 'Предметы'


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Учитель {self.full_name}"

    class Meta:
        db_table = 'Teacher'
        verbose_name = 'Учитель'
        verbose_name_plural = 'Учителя'

class Cabinet(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Cabinet')
    number = models.CharField(max_length=20, db_column='Number_Cabinet')
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        db_column='ID_Teacher'
    )

    def __str__(self):
        return f"Кабинет {self.number}"

    class Meta:
        db_table = 'Cabinet'
        verbose_name = 'Кабинет'
        verbose_name_plural = 'Кабинеты'

class SchoolGroup(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Class')
    number = models.CharField(max_length=20, db_column='Number_Class')
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        db_column='ID_Teacher'
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        db_column='ID_Cabinet'
    )

    def __str__(self):
        return f"Класс {self.number}"

    class Meta:
        db_table = 'Class'
        verbose_name = 'Класс'
        verbose_name_plural = 'Классы'

# Таблица с учениками
class Student(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Student')
    full_name = models.CharField(max_length=35, null=True, blank=True, db_column='FIO_Student')
    parent_name = models.CharField(max_length=35, null=True, blank=True, db_column='FIO_Parent')
    birth_date = models.DateField(null=True, blank=True, db_column='Date')
    snills = models.CharField(max_length=20, null=True, blank=True, db_column='Snills')
    address = models.CharField(max_length=50, db_column='Adress', default='Не указан')
    phone = models.CharField(max_length=11, db_column='Phone')
    school_class = models.ForeignKey(
        SchoolGroup,
        on_delete=models.CASCADE,
        db_column='ID_Class'
    )

    def __str__(self):
        return self.full_name or f"Ученик {self.id}"

    class Meta:
        db_table = 'Student'
        verbose_name = 'Ученик'
        verbose_name_plural = 'Ученики'


class Schedule(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_Schedule')
    info = models.CharField(max_length=100, null=True, blank=True, db_column='Inf')
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        db_column='ID_Subject'
    )
    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        db_column='ID_Cabinet'
    )
    school_class = models.ForeignKey(
        SchoolGroup,
        on_delete=models.CASCADE,
        db_column='ID_Class'
    )


    LESSON_CHOICES = [
        (1, '1 урок (8:30-9:10)'),
        (2, '2 урок (9:20-10:00)'),
        (3, '3 урок (10:10-10:50)'),
        (4, '4 урок (11:10-11:50)'),
        (5, '5 урок (12:10-12:50)'),
        (6, '6 урок (13:00-13:40)'),
        (7, '7 урок (13:50-14:30)'),
        (8, '8 урок (14:40-15:20)'),
        (9, '9 урок (15:30-16:10)'),
    ]

    day_of_week = models.PositiveSmallIntegerField(
        choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'),
                 (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота')],
        default=1
    )
    lesson_number = models.PositiveSmallIntegerField(
        choices=LESSON_CHOICES,
        default=1,
        verbose_name='Номер урока'
    )

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.get_lesson_number_display()} - {self.subject}"

    class Meta:
        db_table = 'Schedule'
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
        ordering = ['day_of_week', 'lesson_number']

# Связующая таблица Учитель-Предмет (Many-to-Many)
class TeacherSubject(models.Model):
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        db_column='Subject'
    )
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        db_column='ID_Teacher'
    )
    info = models.CharField(max_length=100, null=True, blank=True, db_column='Inf')

    def __str__(self):
        return f"{self.teacher.full_name} - {self.subject.full_name}"

    class Meta:
        db_table = 'Teacher_Subject'
        verbose_name = 'Связь Учитель-Предмет'
        verbose_name_plural = 'Связи Учитель-Предмет'
        unique_together = ['subject', 'teacher']


# Дополнительные занятия

class ExtraActivity(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_ExtraActivity')
    name = models.CharField(max_length=100, verbose_name='Название занятия', db_column='Name')
    description = models.TextField(blank=True, null=True, verbose_name='Описание', db_column='Description')

    ACTIVITY_TYPES = [
        ('sport', 'Спортивное'),
        ('art', 'Творческое'),
        ('science', 'Научное'),
        ('language', 'Языковое'),
        ('other', 'Другое'),
    ]

    activity_type = models.CharField(
        max_length=20,
        choices=ACTIVITY_TYPES,
        default='other',
        verbose_name='Тип занятия',
        db_column='Activity_Type'
    )

    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        verbose_name='Преподаватель',
        db_column='ID_Teacher'
    )

    max_students = models.PositiveSmallIntegerField(
        default=15,
        verbose_name='Максимум учеников',
        db_column='Max_Students'
    )

    is_active = models.BooleanField(default=True, verbose_name='Активно', db_column='Is_Active')

    def __str__(self):
        return f"{self.name} ({self.get_activity_type_display()})"

    class Meta:
        db_table = 'ExtraActivity'
        verbose_name = 'Дополнительное занятие'
        verbose_name_plural = 'Дополнительные занятия'

# Расписание дополнительных занятий
class ExtraSchedule(models.Model):
    id = models.AutoField(primary_key=True, db_column='ID_ExtraSchedule')
    activity = models.ForeignKey(
        ExtraActivity,
        on_delete=models.CASCADE,
        verbose_name='Занятие',
        db_column='ID_ExtraActivity'
    )

    day_of_week = models.PositiveSmallIntegerField(
        choices=[(1, 'Понедельник'), (2, 'Вторник'), (3, 'Среда'),
                 (4, 'Четверг'), (5, 'Пятница'), (6, 'Суббота')],
        default=1,
        verbose_name='День недели'
    )

    LESSON_CHOICES = [
        (1, '1 урок (8:00-8:45)'),
        (2, '2 урок (8:55-9:40)'),
        (3, '3 урок (9:50-10:35)'),
        (4, '4 урок (10:45-11:30)'),
        (5, '5 урок (11:40-12:25)'),
        (6, '6 урок (12:35-13:20)'),
        (7, '7 урок (13:30-14:15)'),
        (8, '8 урок (14:25-15:10)'),
        (9, '9 урок (15:20-16:05)'),
        (10, 'После уроков (16:15-17:00)'),
        (11, 'После уроков (17:10-17:55)'),
    ]

    lesson_number = models.PositiveSmallIntegerField(
        choices=LESSON_CHOICES,
        default=10,
        verbose_name='Время занятия'
    )

    cabinet = models.ForeignKey(
        Cabinet,
        on_delete=models.CASCADE,
        verbose_name='Кабинет',
        db_column='ID_Cabinet'
    )

    def __str__(self):
        return f"{self.activity.name} - {self.get_day_of_week_display()} {self.get_lesson_number_display()}"

    class Meta:
        db_table = 'ExtraSchedule'
        verbose_name = 'Расписание доп. занятий'
        verbose_name_plural = 'Расписание доп. занятий'
        ordering = ['day_of_week', 'lesson_number']