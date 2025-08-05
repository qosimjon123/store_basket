from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _



class Brand(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='Уникальный идентификатор')
    title = models.CharField(max_length=255, unique=True, verbose_name="Название бренда")
    image = models.CharField(max_length=255, null=True, blank=True , verbose_name="Ссылка на логотип",
                              help_text="URL изображения логотипа бренда")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_only_warehouse = models.BooleanField(default=False, verbose_name="Только для склада",
                                          help_text="Отметьте, если бренд не продается в розницу")
    def __str__(self):
        return self.title







class Store(models.Model):
    id = models.CharField(primary_key=True, editable=False, max_length=36, verbose_name="Уникальный идентификатор")
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, verbose_name="Бренд")
    address = models.TextField(verbose_name="Адрес")
    city = models.CharField(max_length=100, verbose_name="Город")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Широта")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, verbose_name="Долгота")
    delivery_radius_km = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Радиус доставки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_only_warehouse = models.BooleanField(default=False, verbose_name="Только для склада",
                                          help_text="Отметьте, если склад не продается в розницу")

    def __str__(self):
        return f"{self.brand.title} - {self.address}"




class Schedule(models.Model):
    """График работы магазина/склада"""
    WEEKDAYS = [
        (0, _('Понедельник')),
        (1, _('Вторник')),
        (2, _('Среда')),
        (3, _('Четверг')),
        (4, _('Пятница')),
        (5, _('Суббота')),
        (6, _('Воскресенье')),
    ]
    
    SCHEDULE_TYPES = [
        ('store', _('Магазин')),
        ('warehouse', _('Склад')),
    ]
    
    id = models.IntegerField(primary_key=True, verbose_name="ID")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Магазин/Склад")
    schedule_type = models.CharField(max_length=20, choices=SCHEDULE_TYPES, default='store', 
                                   verbose_name="Тип графика", help_text="Для магазина или склада")
    weekday = models.PositiveSmallIntegerField(choices=WEEKDAYS, verbose_name="День недели")
    is_working = models.BooleanField(default=True, verbose_name="Рабочий день")
    open_time = models.TimeField(verbose_name="Время открытия", default='09:00')
    close_time = models.TimeField(verbose_name="Время закрытия", default='18:00')
    
    # Дополнительные поля для магазина
    is_retail_open = models.BooleanField(default=True, verbose_name="Розничная торговля",
                                       help_text="Открыта ли розничная торговля")
    is_delivery_available = models.BooleanField(default=True, verbose_name="Доставка доступна",
                                              help_text="Работает ли доставка")
    
    # Дополнительные поля для склада
    is_warehouse_open = models.BooleanField(default=True, verbose_name="Склад открыт",
                                          help_text="Работает ли склад")

    class Meta:
        db_table = 'schedules'
        verbose_name = 'График работы'
        verbose_name_plural = 'Графики работы'
        unique_together = ('store', 'schedule_type', 'weekday')
        ordering = ['store', 'schedule_type', 'weekday']

    def __str__(self):
        schedule_type_display = self.get_schedule_type_display() # type: ignore
        return f"{self.store} ({schedule_type_display}) - {self.get_weekday_display()} {self.open_time}-{self.close_time}" # type: ignore

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.is_working and self.close_time <= self.open_time:
            raise ValidationError("Время закрытия должно быть позже времени открытия")



class Category(models.Model):
    """Категории товаров"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    title = models.CharField(max_length=255, verbose_name="Название",
                           help_text="Название категории, например 'Напитки'")
    description = models.CharField(max_length=255, verbose_name="Описание",
                                 help_text="Краткое описание категории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания (timestamp)",
                                      help_text="Unix timestamp создания записи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления (timestamp)",
                                      help_text="Unix timestamp обновления записи")
    image = models.CharField(max_length=255, null=True, blank=True , verbose_name="Логотип",
                              help_text="URL изображения логотипа категории")

    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Магазин",
                            help_text="Для какого магазина эта категория")

    class Meta:
        db_table = 'Categories'
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['store', 'title']

    def __str__(self):
        return f"{self.title} ({self.store})"




class SubCategory(models.Model):
    """Подкатегории товаров"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    title = models.CharField(max_length=255, verbose_name="Название подкатегории",
                                 help_text="Название подкатегории")
    image_url = models.CharField(max_length=255, null=True, blank=True , verbose_name="Логотип",
                                 help_text="URL изображения логотипа подкатегории")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания (timestamp)")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления (timestamp)")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категория",
                              help_text="К какой категории относится")

    class Meta:
        db_table = 'SubCategories'
        verbose_name = 'Подкатегория'
        verbose_name_plural = 'Подкатегории'
        ordering = ['category', 'title']
        unique_together = ('category', 'title')

    def __str__(self):
        return f"Подкатегория {self.title} ({self.category})"




class Unit(models.Model):
    """Единицы измерения товаров"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    title = models.CharField(max_length=255, verbose_name="Название",
                           help_text="Полное название единицы измерения")
    short_name = models.CharField(max_length=255, verbose_name="Сокращение",
                                help_text="Краткое обозначение (кг, л, шт)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания (timestamp)",
                                      help_text="Unix timestamp создания записи")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления (timestamp)",
                                      help_text="Unix timestamp обновления записи")

    class Meta:
        db_table = 'Units'
        verbose_name = 'Единица измерения'
        verbose_name_plural = 'Единицы измерения'
        ordering = ['title']

    def __str__(self):
        return f"{self.title} ({self.short_name})"

class Product(models.Model):
    """Основная информация о товарах"""
    id = models.CharField(primary_key=True, max_length=10, verbose_name="ID")
    title = models.CharField(max_length=255, verbose_name="Название",
                           help_text="Полное название товара")
    description = models.CharField(max_length=255, verbose_name="Описание",
                                 help_text="Краткое описание товара")
    options = models.JSONField(verbose_name="Опции", help_text="Дополнительные характеристики в JSON")
    internal_sku = models.CharField(max_length=255, verbose_name="Артикул",
                                  help_text="Внутренний артикул товара")
    image = models.CharField(max_length=255, null=True, blank=True, verbose_name="Главное изображение",
                                help_text="URL основного изображения товара")
    group_id = models.CharField(max_length=255, verbose_name="ID группы",
                              help_text="Идентификатор группы товаров")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    sub_category = models.ForeignKey(SubCategory, on_delete=models.PROTECT, verbose_name="Подкатегория",
                                   help_text="К какой подкатегории относится")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Склад/Магазин",
                            help_text="К какому складу/магазину относится товар")

    unit = models.ForeignKey(Unit, on_delete=models.CASCADE, verbose_name="Единица измерения",
                           help_text="В каких единицах измеряется товар", null=True, blank=True)
    age_restriction = models.PositiveBigIntegerField(verbose_name="Возрастное ограничение",
                                      help_text="Возрастное ограничение для товара", null=True, blank=True)

    class Meta:
        db_table = 'Products'
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ['title']
        indexes = [
            models.Index(fields=['internal_sku']),
            models.Index(fields=['group_id']),
        ]

    def __str__(self):
        return self.title



class ProductImage(models.Model):
    """Дополнительные изображения товаров"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images', 
                              verbose_name="Товар", help_text="Товар, к которому относится изображение")
    image = models.CharField(max_length=255, verbose_name="Изображение",
                            help_text="Дополнительное изображение товара")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок",
                                      help_text="Порядок отображения изображения")
    alt_text = models.CharField(max_length=255, blank=True, verbose_name="Alt текст",
                              help_text="Альтернативный текст для изображения")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        db_table = 'Product_images'
        verbose_name = 'Изображение товара'
        verbose_name_plural = 'Изображения товаров'
        ordering = ['product', 'order']
        unique_together = ('product', 'order')

    def __str__(self):
        return f"Изображение {self.order} для {self.product}"




class ProductVariant(models.Model):
    """Варианты товаров (только размеры и т.д.)"""
    id = models.CharField(primary_key=True, max_length=12, verbose_name="ID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар",
                              help_text="Основной товар")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена",
                              help_text="Цена за единицу товара")
    discount = models.IntegerField(default=0, verbose_name="Скидка (%)",
                                 help_text="Процент скидки (0-100)", validators=[MinValueValidator(0), MaxValueValidator(100)])
    variant_value = models.CharField(max_length=255, verbose_name="Значение варианта",
                                    help_text="Значение варианта")
    variant_attributes = models.CharField(max_length=255, verbose_name="Значения атрибутов",
                                        help_text="Значения атрибутов варианта")
    height = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Высота",
                               help_text="Высота товара в см")
    width = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Ширина",
                              help_text="Ширина товара в см")
    depth = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Глубина",
                              help_text="Глубина товара в см")
    barcode = models.CharField(max_length=255, verbose_name="Штрих-код",
                             help_text="Штрих-код варианта товара")
    weight = models.IntegerField(verbose_name="Вес (г)",
                               help_text="Вес единицы товара в граммах")


    class Meta:
        db_table = 'Product_variants'
        verbose_name = 'Вариант товара'
        verbose_name_plural = 'Варианты товаров'
        ordering = ['product', 'barcode']
        indexes = [
            models.Index(fields=['barcode']),
        ]

    def __str__(self):
        return f"{self.product} - {self.barcode}"



class Inventory(models.Model):
    """Остатки товаров на складах"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    quantity = models.IntegerField(default=0, verbose_name="Количество",
                                 help_text="Доступное количество товара")
    reserved = models.PositiveIntegerField(default=0, verbose_name="Зарезервировано",
                                 help_text="Зарезервирован ли товар")
    damaged = models.PositiveIntegerField(default=0, verbose_name="Бракованный",
                                help_text="Является ли товар бракованным")
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, verbose_name="Вариант товара",
                              help_text="Какой вариант товара")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Склад",
                            help_text="На каком складе находится товар")

    class Meta:
        db_table = 'Inventory'
        verbose_name = 'Остаток товара'
        verbose_name_plural = 'Остатки товаров'
        ordering = ['store', 'variant']
        indexes = [
            models.Index(fields=['variant']),
            models.Index(fields=['store']),
        ]
        unique_together = ('variant', 'store')  # Один вариант товара на один склад

    def __str__(self):
        status = "Брак" if self.damaged else "Резерв" if self.reserved else "Доступно"
        return f"{self.variant} на {self.store}: {self.quantity} ({status})"




class PriceHistory(models.Model):
    """История цен на товары"""
    id = models.BigAutoField(primary_key=True, verbose_name="ID")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар",
                              help_text="Товар, для которого изменялась цена")
    store = models.ForeignKey(Store, on_delete=models.CASCADE, verbose_name="Склад",
                            help_text="Склад, на котором изменялась цена")
    old_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Старая цена",
                                help_text="Старая цена товара")
    new_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Новая цена",
                                help_text="Новая цена товара")
    old_discount = models.IntegerField()
    new_discount = models.IntegerField()
    changed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.title} в {self.store.address}"




