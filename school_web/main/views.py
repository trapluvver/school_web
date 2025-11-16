from django.shortcuts import redirect
from .models import Task
from .forms import TaskForm

from django.shortcuts import render
from .models import Teacher




def index(request):
    tasks = Task.objects.all()
    return render(request, 'main/index.html', {'title': 'Главная - МБОУ СОШ №32', 'tasks': tasks})


def about(request):
    return render(request, 'main/about.html')


def create(request):
    error = ''
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            error = 'Форма была неверной'
    form = TaskForm()
    context = {
        'form': form,
        'error': error
    }
    return render(request, 'main/create.html', context)

def teacher_report(self, request):
    teachers = Teacher.objects.all().order_by('name')

    context = {
        'teachers': teachers,
        'title': 'Отчет о преподавательском составе',
        **self.admin_site.each_context(request)
    }

    return render(request, 'admin/teachers/simple_report.html', context)

