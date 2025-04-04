from django.contrib import admin
from .models import Category, Mechanic, Game, Expansion, Player, History, Result 

# Register your models here.

admin.site.register(Category)

admin.site.register(Mechanic)

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):

    prepopulated_fields = {'slug': ('title',)}

admin.site.register(Expansion)

admin.site.register(Player)

admin.site.register(History)

admin.site.register(Result)