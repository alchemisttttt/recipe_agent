from database import init_db, Session, Recipe, Ingredient, PantryItem

init_db()
session = Session()

pasta = Ingredient(name="pasta")
garlic = Ingredient(name="garlic")
olive_oil = Ingredient(name="olive oil")
session.add_all([pasta, garlic, olive_oil])
session.commit()

recipe = Recipe(
    name="Garlic Pasta",
    instructions="Boil pasta, sauté garlic in oil, combine.",
    ingredients=[pasta, garlic, olive_oil]
)
session.add(recipe)
session.commit()

session.add_all([
    PantryItem(id_ingredient=pasta.id),
    PantryItem(id_ingredient=garlic.id)
])
session.commit()

print("Recipe:", recipe.name)
print("Ingredients needed:", [i.name for i in recipe.ingredients])

pantry_items = session.query(PantryItem).all()
print("Pantry has:", [p.ingredient.name for p in pantry_items])

session.close()