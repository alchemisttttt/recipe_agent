from database import add_recipe, list_recipes, add_to_pantry, list_pantry, what_can_i_cook

print(add_recipe("Garlic Pasta", "Boil pasta, sauté garlic in oil, combine.", ["pasta", "garlic", "olive oil"]))
print(add_recipe("Tomato Toast", "Toast bread, top with tomato.", ["bread", "tomato"]))

print(list_recipes())

print(add_to_pantry("pasta"))
print(add_to_pantry("garlic"))
print(add_to_pantry("bread"))

print(list_pantry())
print(what_can_i_cook())