from django.shortcuts import render, redirect

from .models import Todo
from .forms import TodoForm


def index(request):
    if request.method == 'POST':
        new_todo = Todo(
            name = request.POST['name']
        )
        new_todo.save()
        return redirect('/')
    todo_list = Todo.objects.all()
    form = TodoForm()
    context = {'todo_list': todo_list, 'form': form}
    return render(request, 'index.html', context)
    

def delete(request, pk):
    todo = Todo.objects.get(id=pk)
    todo.delete()
    return redirect('/')