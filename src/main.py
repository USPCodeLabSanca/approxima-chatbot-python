# This Python file uses the following encoding: utf-8

import os
from dotenv import load_dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
import logging
import json
from pathlib import Path
import copy
import random

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

categories = ['Filmes', 'Séries', 'Shows', 'Jogos eletrônicos', 'Jogos de tabuleiro',
              'Jogos de cartas', 'Livros e Literatura', 'Beleza e Fitness', 'Idiomas',
              'Ciência e Ensino (tópicos acadêmicos)', 'Hardware', 'Software', 'Esportes',
              'Dança', 'Música', 'Teatro', 'Pintura e Desenho', 'Culinária',
              'Mão na massa (consertos, costura, tricô, etc.)', 'Casa e Jardim', 'Pets',
              'Compras', 'Trabalho voluntário', 'Política', 'Finanças', 'Viagens e Turismo',
              'Intercâmbio', 'Rolês universitários', 'Automóveis e Veículos',
              'Esotérico e Holístico', 'Espiritualidade', 'Imobiliário', 'Artesanato',
              'Causas (ambientais, feminismo, vegan, etc.)', 'Moda',
              'Empreenderismo e Negócios', 'Fotografia', 'História', 'Mitologia',
              'Pessoas e Sociedade', 'Anime e Mangá', 'Ficção científica',
              'Fantasia (RPG, senhor dos anéis, etc.)', 'Ciclismo', 'Quadrinhos', 'Saúde']

# Give each category an ID
categories = enumerate(categories)


def normalizeCategories(categories, num_per_row=1):
    new_categories = []
    new_row = []
    for id, cat in categories:
        if id > 0 and id % num_per_row == 0:  # start a new row
            new_categories.append(new_row[:])  # makes a copy
            new_row = []
            new_row.append((id, cat))
        else:
            new_row.append((id, cat))
    return new_categories


# Categorias que já estão na forma certa para produzir o teclado do Bot depois
norm_categories = normalizeCategories(categories, 1)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# States
REGISTER_NAME, REGISTER_BIO, CHOOSE_ACTION, ACTING = range(4)
# States for interests conversation
CHOOSING = 4


def read_test_db():
    file_path = Path("src/data.json")
    # Tries to load DB, if any
    with open(file_path, 'r') as file:
        data = json.load(file)
    logger.info(f'Test Database opened! Original data: {data}')
    return copy.deepcopy(data)


def save_test_db(data):
    file_path = Path("src/data.json")
    with open(file_path, 'w') as file:
        json.dump(data, file)
    logger.info(f'Test Database saved! New data: {DB}')


# Define o nosso DB de teste (será chave-valor)
DB = read_test_db()


def help_command(update, context):
    '''
    Mostra os comandos disponiveis
    '''
    text = "/prefs - Retorna uma lista com todas as categorias de interesse. A partir dela que você poderá adicionar ou remover interesses.\n"
    text += "/show - Mostra uma pessoa que tem interesses em comum.\n"
    text += "/random - Mostra uma pessoa aleatória.\n"
    text += "/pending - Mostra todas as solicitações de conexão que você possui e ainda não respondeu.\n"
    text += "/friends - Mostra o contato de todas as pessoas com que você já se conectou.\n"
    text += "/help - Mostra novamente essa lista. Alternativamente, você pode digitar \"/\" e a lista de comando também aparecerá!"
    update.message.reply_text(text)
    return CHOOSE_ACTION


def start_command(update, context):
    '''
    start => Inicia o bot. Se a pessoa não estiver cadastrada na base de dados
    (dá pra ver pelo ID do Tele), pede para ela fornecer:
    um nome, uma pequena descrição pessoal e, por último para escolher seus interesses iniciais.
    '''

    # Checa se o usuário já está no DB
    if str(update.effective_user.id) in DB:
        update.message.reply_text(
            "Bora começar a usar o aplicativo!\nMe diz: o que você quer fazer agora? :)\n")

        # "Copies" user data of DB in context.user_data
        myself = str(update.effective_user.id)
        context.user_data['name'] = DB[myself]['name']
        context.user_data['bio'] = DB[myself]['bio']
        context.user_data['interests'] = DB[myself]['interests']
        context.user_data['chat_id'] = DB[myself]['chat_id']

        if DB[myself].get('rejects'):
            context.user_data['rejects'] = DB[myself]['rejects']
        else:
            context.user_data['rejects'] = []

        help_command(update, context)
        return CHOOSE_ACTION

    # Caso contrario, o usuario devera se registrar
    update.message.reply_text(
        'Parece que você não está registrado no Approxima ainda...\nPor favor, me forneça o seu nome! (ex: Joao Vitor dos Santos)')
    return REGISTER_NAME


def register_name(update, context):
    response = f"Seu nome é:\n \"{update.message.text}\".\n\n"
    response += "Legal! Agora, me conte um pouco mais sobre seus gostos... Usaremos essa descrição para te apresentar para os outros usuários do Approxima."

    update.message.reply_text(response)
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['name'] = update.message.text
    return REGISTER_BIO


def register_bio(update, context):
    update.message.reply_text(
        f"Sua mini bio é:\n \"{update.message.text}\".\n\nBoa! Agora só falta você adicionar alguns interesses para começar a usar o app!\nClique aqui --> /prefs")
    context.user_data['bio'] = update.message.text

    # Comeca elx com 0 categorias selecionadas
    context.user_data['interests'] = []

    # Joga as informacoes no DB
    DB[str(update.effective_user.id)] = copy.deepcopy(context.user_data)
    save_test_db(DB)

    logger.info(
        f"User {update.effective_user.name} has been registered in the database.")
    logger.info(
        f'{update.effective_user.name} (id: {update.effective_user.id}) data: {context.user_data}')

    return CHOOSE_ACTION


def prefs_command(update, context):
    '''
    prefs => Retorna lista de interesses (caixa de seleção). A pessoa pode marcar
    ou desmarcar o que ela quiser.
    '''
    cats = context.user_data['interests']

    keyboard = [
        [
            InlineKeyboardButton("☑ " + cat, callback_data=str(id)) if id in cats
            else InlineKeyboardButton(cat, callback_data=str(id))
            for id, cat in row
        ]
        for row in norm_categories
    ]
    keyboard.append([InlineKeyboardButton("ENVIAR", callback_data="finish")])

    update.message.reply_text(
        'Escolha suas categorias de interesse:', reply_markup=InlineKeyboardMarkup(keyboard))
    return CHOOSING


def change_category_state(update, context):
    update.callback_query.answer()  # await for answer

    cats = context.user_data['interests']

    # Trata a resposta anterior
    data_id = int(update.callback_query.data)
    if data_id in cats:
        cats.remove(data_id)
    else:
        cats.append(data_id)

    # Constroi o novo teclado
    keyboard = [
        [
            InlineKeyboardButton("☑ " + cat, callback_data=str(id)) if id in cats
            else InlineKeyboardButton(cat, callback_data=str(id))
            for id, cat in row
        ]
        for row in norm_categories
    ]
    keyboard.append([InlineKeyboardButton(
        "ENVIAR", callback_data="finish")])

    update.callback_query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSING


def submit_selection(update, context):
    update.callback_query.answer()  # await for answer

    # Guarda as informacoes no DB
    DB[str(update.effective_user.id)]['interests'] = copy.deepcopy(
        context.user_data['interests'])
    save_test_db(DB)

    update.effective_message.reply_text('Seus interesses foram atualizados!')
    return ConversationHandler.END


def show_person_command(update, context):
    '''
    show => Mostra uma pessoa que tem interesses em comum (vai com base no ranking).
    Embaixo, um botão para enviar a solicitação de conexão deve existir.
    '''
    update.message.reply_text('Mostrei um amigo')
    return CHOOSE_ACTION


def get_random_person_command(update, context):
    '''
    random => Mostra uma pessoa aleatória. Embaixo, um botão para enviar a solicitação
    de conexão deve existir, bem como um botão de "agora não".
    '''
    users = list(DB)

    if context.user_data.get('rejects'):
        if len(users) == len(context.user_data['rejects']) + 1:
            # Já rejeitei todos da lista de usuários
            update.message.reply_text(
                'Você já rejeitou todos os usuários possíveis... manx, que feito!')
            return CHOOSE_ACTION

    target = random.choice(users)
    # while the target is me or was rejected by me, keep going on
    while target == str(update.effective_user.id) or target in context.user_data['rejects']:
        target = random.choice(users)
    # Avisa no contexto que essa pessoa foi a ultima a ser exibida para o usuario (ajuda nas callback queries)
    context.user_data['lastOffer'] = target

    target_bio = DB[target]['bio']

    keyboard = [[
        InlineKeyboardButton('Conectar', callback_data='connect'),
        InlineKeyboardButton('Agora não', callback_data='dismiss')
    ]]

    update.message.reply_text(
        f'\"{target_bio}\"', reply_markup=InlineKeyboardMarkup(keyboard))

    return ACTING


def handle_invite_answer(update, context):
    target_id = context.user_data['lastOffer']
    del context.user_data['lastOffer']

    update.callback_query.answer()
    answer = update.callback_query.data

    myself = str(update.effective_user.id)

    if answer == 'dismiss':
        context.user_data['rejects'].append(target_id)

        DB[myself]['rejects'] = context.user_data['rejects']
        save_test_db(DB)

        context.bot.sendMessage(chat_id=DB[myself]['chat_id'],
                                text='Sugestão rejeitada.')

        return CHOOSE_ACTION

    # For now on, we know that the answer is "connect"!

    target_chat = DB[target_id]['chat_id']
    context.bot.sendMessage(chat_id=target_chat,
                            text='Você recebeu uma nova solicitação de conexão!')

    context.bot.sendMessage(chat_id=DB[myself]['chat_id'],
                            text='Solicitação enviada.')

    return CHOOSE_ACTION


def pending_command(update, context):
    '''
    pending => Mostra todas as solicitações de conexão que aquela pessoa possui e
    para as quais ela ainda não deu uma resposta. Mostra, para cada solicitação,
    a descrição da pessoa e dois botões: conectar ou descartar).
    '''
    update.message.reply_text('Mostrei os que faltam responder')
    return CHOOSE_ACTION


def friends_command(update, context):
    '''
    friends => Mostra o contato (@ do Tele) de todas as pessoas com que o usuário
    já se conectou.
    '''
    update.message.reply_text('Mostrei suas conexoes')
    return CHOOSE_ACTION


# def unknown(update, context):
#     '''
#     Mensagem ou comando desconhecido
#     '''
#     response_message = "Não entendi! Por favor, use um comando (eles começam com '/')."
#     update.message.reply_text(response_message)

def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    prefs_handler = ConversationHandler(
        entry_points=[CommandHandler('prefs', prefs_command)],

        states={
            CHOOSING: [
                CallbackQueryHandler(
                    change_category_state, pattern='^[\\d]+$'),
                CallbackQueryHandler(submit_selection, pattern='^finish$')
            ],
        },

        fallbacks=[MessageHandler(Filters.text, submit_selection)],

        map_to_parent={
            ConversationHandler.END: CHOOSE_ACTION
        }
    )

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start_command)],

        states={
            REGISTER_NAME: [
                MessageHandler(Filters.text, register_name)
            ],

            REGISTER_BIO: [
                MessageHandler(Filters.text, register_bio)
            ],

            CHOOSE_ACTION: [
                prefs_handler,
                CommandHandler('show', show_person_command),
                CommandHandler('random', get_random_person_command),
                CommandHandler('pending', pending_command),
                CommandHandler('friends', friends_command),
                CommandHandler('help', help_command),
            ],

            ACTING: [
                CallbackQueryHandler(
                    handle_invite_answer, pattern='^(connect|dismiss)$'),
            ],
        },

        fallbacks=[CommandHandler('start', start_command)]
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    logging.info("=== Bot running! ===")
    updater.idle()
    logging.info("=== Bot shutting down! ===")


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
