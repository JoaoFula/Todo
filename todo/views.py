from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import todo_form
from .models import todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def home(request):
    return render(request, 'todo/home.html')

############################ AUTH #######################################
def signup_user(request):
    if request.method == 'GET':
        return render(request, 'todo/signup_user.html', {'form': UserCreationForm()})
    else:
        if request.POST['password1'] == request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'], request.POST['email'], password = request.POST['password1'])
                user.save()
                login(request, user)
                user.confirmation = False
                ############################## mailing system##############################
                print(settings.EMAIL_HOST_PASSWORD)
                subject = 'Thank you for registering to our site'
                message = render_to_string('todo/mail_template.html', {'user': user})
                plain_message = strip_tags(message)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email, ]
                send_mail(subject, plain_message, email_from, recipient_list, html_message=message)


                return redirect('current_todos')
            except IntegrityError:
                return render(request, 'todo/signup_user.html',
                              {'form': UserCreationForm(), 'error': 'That username has been taken!'})
        else:
            return render(request, 'todo/signup_user.html',
                          {'form': UserCreationForm(), 'error': 'Passwords did not match!'})
            # Create error (passwords didn't match)

def login_user(request):
    if request.method == 'GET':
        return render(request, 'todo/login_user.html', {'form': AuthenticationForm()})
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'todo/login_user.html',
                          {'form': AuthenticationForm(), 'error': 'Username and password did not match!'})
        else:
            login(request, user)
            return redirect('current_todos')

@login_required
def logout_user(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')




############################ TODOS #######################################

@login_required
def create_todo(request):
    if request.method == 'GET':
        return render(request, 'todo/create_todo.html', {'form':todo_form()})
    else:
        try:
            form = todo_form(request.POST)
            new_todo = form.save(commit=False)
            new_todo.user = request.user
            new_todo.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/create_todo.html',
                                 {'form':todo_form(), 'error':'Bad data passed in. Try again!'})

@login_required
def current_todos(request):
    todos = todo.objects.filter(user=request.user,
                                date_completed__isnull=True).order_by('-important')

    return render(request, 'todo/current_todos.html', {'todos': todos})

@login_required
def view_todo(request, todo_pk):
    todo_obj = get_object_or_404(todo, pk=todo_pk, user=request.user)

    if request.method == 'GET':
        form = todo_form(instance=todo_obj)
        return render(request, 'todo/view_todo.html', {'todo': todo_obj, 'form':form})
    else:
        try:
            form = todo_form(request.POST, instance=todo_obj)
            form.save()
            return redirect('current_todos')
        except ValueError:
            return render(request, 'todo/view_todo.html',
                          {'todo': todo_obj, 'form':form,
                          'error': 'Bad data passed in. Try again!'})

@login_required
def complete_todo(request, todo_pk):
    todo_obj = get_object_or_404(todo, pk=todo_pk, user=request.user)

    if request.method == 'POST':
        todo_obj.date_completed = timezone.now()
        todo_obj.save()
        return redirect('current_todos')

@login_required
def delete_todo(request, todo_pk):
    todo_obj = get_object_or_404(todo, pk=todo_pk, user=request.user)
    if request.method == 'POST':
        todo_obj.delete()
        return redirect('current_todos')

@login_required
def completed_todos(request):
    todos = todo.objects.filter(user=request.user,
                                date_completed__isnull=False).order_by('-date_completed')

    return render(request, 'todo/completed_todos.html', {'todos': todos})