
# Change categories ids from int to string
# Categories now have subcategories!

import os
import json

import os
import sys

from os.path import dirname, join, abspath
sys.path.insert(1, abspath(join(dirname(__file__), '..')))

if not os.getenv("IS_PRODUCTION"):
    from dotenv import load_dotenv
    load_dotenv()

from dbwrapper import Database
from categories import categories

CONNECTION_STRING = os.getenv("CONNECTION_STRING")

is_production = False if os.getenv("IS_PRODUCTION") is None else True
db = Database(CONNECTION_STRING, is_production=is_production)

old_categories = ['Filmes', 'Séries', 'Shows', 'Jogos eletrônicos', 'Jogos de tabuleiro',
              'Jogos de cartas', 'Livros e Literatura', 'Beleza e Fitness', 'Idiomas',
              'Ciência e Ensino (tópicos acadêmicos)', 'Hardware', 'Software', 'Esportes',
              'Dança', 'Música', 'Teatro', 'Pintura e Desenho', 'Culinária',
              'Mão na massa (consertos, costura, tricô, etc.)', 'Casa e Jardim', 'Pets',
              'Compras', 'Trabalho voluntário', 'Política', 'Finanças', 'Viagens e Turismo',
              'Intercâmbio', 'Rolês universitários', 'Automóveis e Veículos',
              'Esotérico e Holístico', 'Espiritualidade', 'Imobiliário', 'Artesanato',
              'Causas (ambientais, feminismo, vegan...)', 'Moda',
              'Empreenderismo e Negócios', 'Fotografia', 'História', 'Mitologia',
              'Pessoas e Sociedade', 'Anime e Mangá', 'Ficção científica',
              'Fantasia (RPG, senhor dos anéis, etc.)', 'Ciclismo', 'Quadrinhos', 'Saúde']

def get_new_categoria_id(old_id):
  if not isinstance(old_id, int):
    return ''
  old_category = old_categories[old_id]

  [new_id, sub_categories] = categories[old_category]
  if sub_categories and isinstance(sub_categories, dict) and len(sub_categories.keys()) > 0:
    return ''
  return new_id

def migrate_user_categories_ids(user_id):
  my_data = db.get_by_id(user_id)
  new_ids = []
  for category_id in my_data['interests']:
    new_id = get_new_categoria_id(category_id)
    if new_id != '':
      new_ids.append(str(new_id))
  # print(new_ids)
  db.update_by_id(user_id, {'interests': new_ids})

def migrate():
  for id in db.list_ids():
    migrate_user_categories_ids(id)
  # migrate_user_categories_ids(341699070)

migrate()
