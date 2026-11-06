// Same text as Django's `intcomma` + "&nbsp;₽" in templates: ru groups digits with a no-break space.
export const formatPrice = (value: number | string): string =>
  `${Number(value).toLocaleString('ru-RU').replace(/\s/g, ' ')} ₽`;
