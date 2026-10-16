from django import forms

from .models import Lead, Order, Review
from .utils import clean_phone_number


class AriaErrorsMixin:
    """Поля с ошибками получают aria-invalid и aria-describedby="<id поля>-error".

    Элемент с таким id рисуют шаблоны (partials/_lead_form.html, checkout.html).
    """

    def full_clean(self):
        super().full_clean()
        if not self.is_bound:
            return
        for name in self.errors:
            if name not in self.fields:
                continue
            attrs = self.fields[name].widget.attrs
            attrs['aria-invalid'] = 'true'
            attrs['aria-describedby'] = f'{self[name].id_for_label}-error'


class OrderForm(AriaErrorsMixin, forms.ModelForm):
    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_email', 'delivery_address', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'customer_phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 900 000-00-00'}),
            'customer_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (необязательно)'}),
            'delivery_address': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Адрес доставки'}),
            'comment': forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Комментарий к заявке'}),
        }

    def clean_customer_phone(self):
        try:
            return clean_phone_number(self.cleaned_data['customer_phone'])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class LeadForm(AriaErrorsMixin, forms.ModelForm):
    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'lead_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'phone': forms.TextInput(attrs={'class': 'form-input', 'placeholder': '+7 900 000-00-00'}),
            'email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email (необязательно)'}),
            'lead_type': forms.HiddenInput(),
            'message': forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Расскажите о вашем проекте'}),
        }

    def clean_phone(self):
        try:
            return clean_phone_number(self.cleaned_data['phone'])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class ReviewForm(forms.ModelForm):
    """Отзыв с PDP. Сохраняется неопубликованным (модерация в админке).

    ``website`` — honeypot: человек его не видит и не заполняет, бот заполняет.
    """

    website = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
    )

    class Meta:
        model = Review
        fields = ['author', 'rating', 'usage_duration', 'text']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'usage_duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Срок использования (необязательно)'}),
            'text': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Ваш отзыв'}),
        }

    @property
    def is_spam(self):
        return bool(self.cleaned_data.get('website'))
