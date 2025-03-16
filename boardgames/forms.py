from django import forms
from django.forms import inlineformset_factory
from .models import Game, Category, Mechanic, History, Result, Expansion, Player
import datetime


class GameForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    mechanic = forms.ModelMultipleChoiceField(
        queryset=Mechanic.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    min_players = forms.IntegerField(
        min_value=1,
        max_value=99,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min', 'style': 'width: 70px;'})
    )
    max_players = forms.IntegerField(
        min_value=1,
        max_value=99,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max', 'style': 'width: 70px;'})
    )
    min_duration = forms.IntegerField(
        min_value=1,
        max_value=999,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Min', 'style': 'width: 70px;'})
    )
    max_duration = forms.IntegerField(
        min_value=1,
        max_value=999,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max', 'style': 'width: 70px;'})
    )
    summary = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}), required=False)

    class Meta:
        model = Game
        fields = ['title', 'image', 'min_players', 'max_players', 'min_duration', 'max_duration', 'summary', 'description', 'category', 'mechanic']

    def clean(self):
        cleaned_data = super().clean()
        min_players = cleaned_data.get('min_players')
        max_players = cleaned_data.get('max_players')
        min_duration = cleaned_data.get('min_duration')
        max_duration = cleaned_data.get('max_duration')

        if min_players and max_players and min_players > max_players:
            self.add_error('max_players', 'Max players must be greater than or equal to Min players.')
        
        if min_duration and max_duration and min_duration > max_duration:
            self.add_error('max_duration', 'Max duration must be greater than or equal to Min duration.')

        return cleaned_data
    

class HistoryForm(forms.ModelForm):

    play_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=forms.fields.datetime.date.today
    )
    play_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        initial=lambda: datetime.datetime.now().time().replace(microsecond=0)
    )
    duration = forms.IntegerField(
        min_value=1,
        max_value=999,
        error_messages={'max_value': 'Duration must be 3 digits or less.'}
    )
    game = forms.ModelChoiceField(
        queryset=Game.objects.all(),
        empty_label="Select a game"
    )
    expansions = forms.ModelMultipleChoiceField(
        queryset=Expansion.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = History
        fields = ['game', 'play_date', 'play_time', 'duration', 'expansions']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'game' in self.data:
            try:
                game_id = int(self.data.get('game'))
                self.fields['expansions'].queryset = Expansion.objects.filter(game_id=game_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['expansions'].queryset = self.instance.game.expansions.all()

class ResultForm(forms.ModelForm):
    is_winner = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    score = forms.IntegerField(
        required=False,
        initial=0
    )

    class Meta:
        model = Result
        fields = ['player', 'score', 'is_winner']
        widgets = {
            'score': forms.NumberInput(attrs={'placeholder': '0'}),
            'player': forms.Select(),
        }

# Creating an inline formset for Result related to History
ResultFormSet = forms.inlineformset_factory(History, Result, form=ResultForm, extra=2, can_delete=True)


class PlayerForm(forms.ModelForm):

    class Meta:
        model = Player
        fields = ['name']

class CategoryForm(forms.ModelForm):

    class Meta:
        model = Category
        fields = ['name', 'description']

class MechanicForm(forms.ModelForm):

    class Meta:
        model = Mechanic
        fields = ['name', 'description']