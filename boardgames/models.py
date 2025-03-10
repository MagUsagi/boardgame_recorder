from django.db import models
from django.utils.text import slugify
import os
from django.dispatch import receiver

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'categories'

    def __str__(self):
        return self.name


class Game(models.Model):
    title = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='game_images/', blank=True, null=True)
    min_players = models.PositiveIntegerField()
    max_players = models.PositiveIntegerField()
    min_duration = models.PositiveIntegerField()
    max_duration = models.PositiveIntegerField()
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True)
    category = models.ManyToManyField(Category, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

# delete images files when delete Game 
@receiver(models.signals.post_delete, sender=Game)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
    
    

class Expansion(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='expansions')
    name = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.game.title} - {self.name}"
    

class Player(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name
    

class History(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='histories')
    play_date = models.DateField()
    duration = models.PositiveIntegerField(blank=True, null=True)
    expansions_used = models.ManyToManyField(Expansion, blank=True)

    class Meta:
        verbose_name_plural = 'histories'

    def __str__(self):
        return f"{self.game.title} on {self.play_date}"
    

class Result(models.Model):
    history = models.ForeignKey(History, on_delete=models.CASCADE, related_name='results')
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='results')
    score = models.IntegerField()
    is_winner = models.BooleanField(default=False)

    def __str__(self):
        status = 'Winner' if self.is_winner else 'Loser'
        return f"{self.player.name} - {self.score} points ({status})"