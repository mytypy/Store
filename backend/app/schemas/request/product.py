from decimal import Decimal

from pydantic import BaseModel, Field, field_validator


class AddProductData(BaseModel):
    name: str = Field(description='Название продукта', min_length=2, max_length=255)
    description: str = Field(description='Описание продукта')
    count: int = Field(description='Кол-во продукта')
    
    category: int | None = Field(description='Категория товара')
    price: Decimal = Field(description='Цена за единицу товара',
                           default=Decimal('0.00'),
                           max_digits=3,
                           decimal_places=2
                           )
        
    protein: Decimal = Field(description='Белки (в граммах)', max_digits=5, decimal_places=1)
    fat: Decimal = Field(description='Жиры (в граммах)', max_digits=5, decimal_places=1)
    carbs: Decimal = Field(description='Углеводы (в граммах)', max_digits=5, decimal_places=1)
    kcal: Decimal = Field(description='Килокалории (в kkcal)', max_digits=5, decimal_places=1)
        
    attributes: dict[str, int | str] | None = None
    
    @field_validator("attributes")
    @classmethod
    def check_attributes(cls, attrs: dict) -> dict:
        """Пользовательская функция валидации поля с аттрибутами

        Args:
            attrs (dict): Аттрибуты продукта

        Returns:
            dict: Итоговый словарь
        """
        if attrs is None:
            return attrs
        
        attrs_len = len(attrs)
        
        if attrs_len > 10:
            raise ValueError("Слишком много атрибутов! Максимум 10")
        
        for key, value in attrs.items():
            key_length = len(key)
            
            if (1 <= key_length <= 32) is False or key.strip() == "":
                raise ValueError(
                    f"Ключ атрибута '{key}' должен быть от 1 до 32 символов"
                )
            
            if isinstance(value, str) and ((1 <= len(value) <= 32) is False or value.strip() == ""):
                raise ValueError(
                    f"Значение для '{key}' должно быть от 1 до 32 символов."
                )
            
            elif isinstance(value, int) and abs(value) > 2_147_483_647:
                raise ValueError(
                    f"Числовое значение для '{key}' выходит за допустимые пределы."
                )

        return attrs