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
    lesson = models.CharField(max_length=60, db_column='Lesson') # Нужно увеличить размерность
    experience = models.CharField(max_length=30, null=True, blank=True, db_column='Experience')
    prof_retrain = models.CharField(max_length=70, null=True, blank=True, db_column='Prof_retrain')

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
    birth_date = models.DateField(max_length=15, null=True, blank=True, db_column='Date')
    snills = models.CharField(max_length=20, null=True, blank=True, db_column='Skills')
    address = models.CharField(max_length=50, db_column='Address')
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

    def __str__(self):
        return f"Расписание {self.id}"

    class Meta:
        db_table = 'Schedule'
        verbose_name = 'Расписание'
        verbose_name_plural = 'Расписание'
