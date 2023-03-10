import json
import os

from django.conf import settings
from django.db import migrations

INGREDIENTS_FILE = os.path.join(settings.BASE_DIR,
                                'data/ingredients.json')
MIGRATION_ERR_MSG = (
    """\nОшибка миграции данных! 
Ингредиенты небыли загружены в базу данных.\n""")

FILE_ERR_MSG = MIGRATION_ERR_MSG + '{detail}'

JSON_ERR_MSG = MIGRATION_ERR_MSG + (
    """Ошибка парсинга файла {file}.
{detail}""")

INGREDIENT_ATTR_ERR_MSG = MIGRATION_ERR_MSG + (
    """Ошибка добавления ингредиента.
Не найден атрибут {attr}""")


def add_ingredients(apps, schema_editor):
    Ingredient = apps.get_model('recipes', 'Ingredient')
    try:
        with open(INGREDIENTS_FILE, 'r') as json_file:
            ingredients = json.load(json_file)
            ingredient_objs_list = []
            for ingredient in ingredients:
                ingredient_objs_list.append(
                    Ingredient(
                        name=ingredient['name'],
                        measurement_unit=ingredient['measurement_unit']
                    )
                )
            Ingredient.objects.bulk_create(ingredient_objs_list,
                                           ignore_conflicts=True)
    except FileNotFoundError as err:
        print(FILE_ERR_MSG.format(detail=err))
    except json.JSONDecodeError as err:
        print(JSON_ERR_MSG.format(detail=err, file=INGREDIENTS_FILE))
    except KeyError as err:
        print(INGREDIENT_ATTR_ERR_MSG.format(attr=err))


class Migration(migrations.Migration):
    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_ingredients, migrations.RunPython.noop)
    ]
