from django import forms

from .models import Lead, Order, Review
from .utils import clean_phone_number


class AriaErrorsMixin:
    """Поля с ошибками получают aria-invalid и aria-describedby="<id поля>-error".

    Элемент с таким id рисуют шаблоны (partials/_lead_form.html, checkout.html), поэтому
    атрибуты ставятся только полям из ``aria_error_fields`` (у остальных нет элемента ошибки).
    """

    aria_error_fields = ()

    def full_clean(self):
        super().full_clean()
        if not self.is_bound:
            return
        for name in self.errors:
            if name not in self.aria_error_fields or name not in self.fields:
                continue
            attrs = self.fields[name].widget.attrs
            attrs['aria-invalid'] = 'true'
            attrs['aria-describedby'] = f'{self[name].id_for_label}-error'


class HoneypotMixin:
    """``website`` — honeypot: человек его не видит и не заполняет, бот заполняет.

    View отвечает боту так же, как человеку, но ничего не сохраняет и не шлёт в Telegram.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['website'] = forms.CharField(
            required=False,
            widget=forms.TextInput(attrs={'tabindex': '-1', 'autocomplete': 'off'}),
        )

    @property
    def is_spam(self):
        return bool(self.cleaned_data.get('website'))


class OrderForm(HoneypotMixin, AriaErrorsMixin, forms.ModelForm):
    aria_error_fields = ('customer_name', 'customer_phone', 'customer_email', 'delivery_address', 'comment')

    # В модели это TextField без лимита; ограничиваем в форме, без миграции.
    delivery_address = forms.CharField(
        label='Адрес доставки', required=False, max_length=500,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Адрес доставки'}))
    comment = forms.CharField(
        label='Комментарий', required=False, max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 2, 'placeholder': 'Комментарий к заявке'}))

    class Meta:
        model = Order
        fields = ['customer_name', 'customer_phone', 'customer_email', 'delivery_address', 'comment']
        widgets = {
            'customer_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя', 'autocomplete': 'name'}),
            'customer_phone': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': '+7 (___) ___-__-__', 'inputmode': 'tel', 'autocomplete': 'tel'}),
            'customer_email': forms.EmailInput(attrs={
                'class': 'form-input', 'placeholder': 'Email (необязательно)', 'autocomplete': 'email'}),
        }

    def clean_customer_phone(self):
        try:
            return clean_phone_number(self.cleaned_data['customer_phone'])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class LeadForm(HoneypotMixin, AriaErrorsMixin, forms.ModelForm):
    aria_error_fields = ('name', 'phone', 'email', 'message')

    message = forms.CharField(
        label='Сообщение', required=False, max_length=2000,
        widget=forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Расскажите о вашем проекте'}))

    class Meta:
        model = Lead
        fields = ['name', 'phone', 'email', 'lead_type', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя', 'autocomplete': 'name'}),
            'phone': forms.TextInput(attrs={
                'class': 'form-input', 'placeholder': '+7 (___) ___-__-__', 'inputmode': 'tel', 'autocomplete': 'tel'}),
            'email': forms.EmailInput(attrs={
                'class': 'form-input', 'placeholder': 'Email (необязательно)', 'autocomplete': 'email'}),
            'lead_type': forms.HiddenInput(),
        }

    def clean_phone(self):
        try:
            return clean_phone_number(self.cleaned_data['phone'])
        except ValueError as exc:
            raise forms.ValidationError(str(exc))


class ReviewForm(HoneypotMixin, forms.ModelForm):
    """Отзыв с PDP. Сохраняется неопубликованным (модерация в админке)."""

    class Meta:
        model = Review
        fields = ['author', 'rating', 'usage_duration', 'text']
        widgets = {
            'author': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Ваше имя'}),
            'rating': forms.NumberInput(attrs={'class': 'form-input', 'min': 1, 'max': 5}),
            'usage_duration': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Срок использования (необязательно)'}),
            'text': forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Ваш отзыв'}),
        }
