from django import forms
from django.core.validators import ValidationError

class ExtraSearch(forms.Form):
    jobs_num = forms.ChoiceField(choices=(('', 'Укажи количество обьявлений.'), ('1', '1'), ('5', '5'), ('10', '10'), ('25', '25')), label='Количество обьявлений:')
    price = forms.ChoiceField(choices=(('0-0', 'Поиск без ценового диапазона.'), ('0-500', 'от 0 грн до 500 грн'), ('500-1000', 'от 500 грн до 1000 грн'), ('1000-2000', 'от 1000 грн до 2000 грн'), ('2000-5000', 'от 2000 грн до 5000 грн'), ('5000-9999999999', 'от 5000 грн')),label='Ценовой диапазон:')

    def clean_jobs_num(self):
        jobs_num = self.cleaned_data['jobs_num']
        if isinstance(jobs_num, int):
            raise ValidationError('Выбери количество обьявлений!')
        return jobs_num
