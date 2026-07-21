from sqlalchemy import create_engine, Column, String, Integer, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, declarative_base, relationship

engine = create_engine('sqlite:///database.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)

rec_ing = Table('recing', Base.metadata,
    Column('recepie_id', Integer, ForeignKey('recepie.id')),
    Column('ingredient_id', Integer, ForeignKey('ingredients.id'))
)

class Recipe(Base):
    __tablename__ = 'recepie'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    instructions = Column(String)

    ingredients = relationship("Ingredient", secondary=rec_ing, back_populates="recipes")

class Ingredient(Base):
    __tablename__ = 'ingredients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)

    recipes = relationship("Recipe", secondary=rec_ing, back_populates="ingredients")

class PantryItem(Base):
    __tablename__ = 'pantry_item'
    id = Column(Integer, primary_key=True)
    id_ingredient = Column(Integer, ForeignKey('ingredients.id'))

    ingredient = relationship("Ingredient")


def init_db():
    Base.metadata.create_all(engine)


def get_create_ingredient(session, name):
    exist = session.query(Ingredient).filter(Ingredient.name == name).first()
    if exist:
        return exist
    else:
        new_ingredient = Ingredient(name=name)
        session.add(new_ingredient)
        session.commit()
        return new_ingredient


def add_recipe(name: str, instructions: str, ingredients: list):
    session = Session()
    ingredient_objs = [get_create_ingredient(session, n.strip()) for n in ingredients]

    recepie = Recipe(name=name, instructions=instructions, ingredients=ingredient_objs)
    session.add(recepie)
    session.commit()
    session.close()
    return f"Recipe '{name}' added with {len(ingredient_objs)} ingredients."


def list_recipes():
    session = Session()
    recepies = session.query(Recipe).all()

    if not recepies:
        session.close()
        return "No Recipes"

    result = []
    for r in recepies:
        ing_names = ",".join(i.name for i in r.ingredients)
        result.append(f"[{r.id}] {r.name} — needs: {ing_names}")

    session.close()
    return "\n".join(result)


def add_to_pantry(ingredient_name: str):
    session = Session()
    ingredient = get_create_ingredient(session, ingredient_name)
    exist = session.query(PantryItem).filter_by(id_ingredient=ingredient.id).first()
    if exist:
        session.close()
        return f"'{ingredient_name}' is already in your pantry."

    pantry_item = PantryItem(id_ingredient=ingredient.id)
    session.add(pantry_item)
    session.commit()
    session.close()
    return f"'{ingredient_name}' added to pantry."


def list_pantry():
    session = Session()
    items = session.query(PantryItem).all()
    names = [item.ingredient.name for item in items]
    session.close()
    if not names:
        return "No Pantry"
    return "Pantry contains: " + ", ".join(names)


def what_can_i_cook():
    session = Session()
    pantry_ingredient_ids = {p.id_ingredient for p in session.query(PantryItem).all()}
    recepies = session.query(Recipe).all()

    cookable = []
    for r in recepies:
        needed_ids = {i.id for i in r.ingredients}
        if needed_ids.issubset(pantry_ingredient_ids):
            cookable.append(r.name)
    session.close()

    if not cookable:
        return "You don't have all the ingredients for any recipe yet."
    return "You can cook: " + ", ".join(cookable)