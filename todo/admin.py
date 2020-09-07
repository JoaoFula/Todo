from django.contrib import admin
from .models import todo

class todo_admin(admin.ModelAdmin):
    readonly_fields = ('created',)

# Register your models here.
admin.site.register(todo, todo_admin)