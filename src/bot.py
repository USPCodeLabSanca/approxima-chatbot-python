# This Python file uses the following encoding: utf-8

import os
import logging
import random
import ranker
import json
import numpy as np
from dbwrapper import Database
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler


# ================================== ENV =======================================

if not os.getenv("IS_PRODUCTION"):
    from dotenv import load_dotenv
    load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CONNECTION_STRING = os.getenv("CONNECTION_STRING")
ADMINS = json.loads(os.getenv("ADMINS"))

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# =============================== CATEGORIAS ===================================


categories = ['Filmes', 'Séries', 'Shows', 'Jogos eletrônicos', 'Jogos de tabuleiro',
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


# ================================== BD ========================================

is_production = False if os.getenv("IS_PRODUCTION") is None else True
db = Database(CONNECTION_STRING, is_production=is_production)

# ================================== BOT =======================================

# States
REGISTER_NAME, REGISTER_BIO, CHOOSE_ACTION, CHOOSE_ANSWER_FOR_BUTTONS, GIVE_NEW_NAME, GIVE_NEW_BIO, SEND_NOTIFICATION = range(
    7)
# States for interests conversation
CHOOSE_INTERESTS = 7


def help_command(update, context):
    '''
    Mostra os comandos disponiveis
    '''
    text = "/prefs --> Retorna uma lista com todas as categorias de interesse. A partir dela, você poderá adicionar ou remover interesses.\n"
    text += "/show --> Mostra uma pessoa que tem interesses em comum.\n"
    text += "/random --> Mostra uma pessoa aleatória.\n"
    text += "/clear --> Permite que as pessoas que você respondeu com \"Agora não\" apareçam de novo nos dois comando acima.\n"
    text += "/pending --> Mostra uma solicitação de conexão que você possui e ainda não respondeu.\n"
    text += "/friends --> Mostra o contato de todas as pessoas com que você já se conectou.\n"
    text += "/name --> Troca o seu nome.\n"
    text += "/desc --> Troca a sua descrição.\n"
    text += "/help --> Mostra novamente essa lista. Alternativamente, você pode digitar \"/\" e a lista de comandos também aparecerá!\n\n"
    text += "Caso tenha algum problema ou crítica/sugestão, chama um dos meus desenvolvedores (eles me disseram que não mordem) --> @vitorsanc @arenasoy @Angra018 @OliveiraNelson"
    update.message.reply_text(text)

    return CHOOSE_ACTION


def start_command(update, context):
    '''
    start => Inicia o bot. Se a pessoa não estiver cadastrada na base de dados
    (dá pra ver pelo ID do Tele), pede para ela fornecer:
    um nome, uma pequena descrição pessoal e, por último para escolher seus interesses iniciais.
    '''

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    my_data = db.get_by_id(myself)

    if my_data is not None:
        # Pega os dados dele do BD
        context.user_data['chat_id'] = my_data['chat_id']    # number
        context.user_data['username'] = my_data['username']    # string
        context.user_data['name'] = my_data['name']  # string
        context.user_data['bio'] = my_data['bio']    # string
        context.user_data['interests'] = my_data['interests']
        context.user_data['rejects'] = my_data['rejects']
        context.user_data['invited'] = my_data['invited']
        context.user_data['pending'] = my_data['pending']
        context.user_data['connections'] = my_data['connections']

        # Manda a mensagem de "boas-vindas"
        message = "É muito bom ter você de volta! Bora começar a usar o Approxima :)\n"
        message += "Me diz: o que você quer fazer agora?\n\n"
        message += "Use /help para uma lista dos comandos disponíveis.\n"

        update.message.reply_text(message)

        return CHOOSE_ACTION

    # Se chegou aqui é novo usuario e deve se registrar

    # Crio os campos necessarios para o user context
    context.user_data['chat_id'] = update.effective_chat.id
    context.user_data['username'] = update.effective_user.name
    context.user_data['name'] = ''  # string
    context.user_data['bio'] = ''    # string
    context.user_data['interests'] = []
    context.user_data['rejects'] = []
    context.user_data['invited'] = []
    context.user_data['pending'] = []
    context.user_data['connections'] = []

    message = "Muito prazer! Vamos começar o seu registro no Approxima!\n\n"
    message += "Primeiro, me forneça o seu nome.\n"
    message += "Ex: Joao Vitor dos Santos"

    update.message.reply_text(message)

    return REGISTER_NAME


def register_name(update, context):
    response = f"Seu nome é:\n\"{update.message.text}\"\n\n"
    response += "Legal! Agora, me conte um pouco mais sobre seus gostos... faça uma pequena descrição de si mesmo.\n"
    response += "Ela será utilizada para apresentar você para os outros usuários do Approxima (não mostrarei o seu nome).\n\n"
    response += "OBS: Você poderá mudar essa descrição depois, mas lembre-se de que somente ela irá aparecer para os outros usuários quando formos te apresentar a eles!"

    context.user_data['name'] = update.message.text

    update.message.reply_text(response)

    return REGISTER_BIO


def register_bio(update, context):

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    response = f"Sua descrição é:\n"
    response += f"\"{update.message.text}\".\n\n"
    response += "Boa! Agora só falta você adicionar alguns interesses para começar a usar o Approxima!\n"
    response += "Clique (ou toque) aqui --> /prefs\n\n"
    response += "Após essa etapa você já pode começar a usar os meus comandos!\n"
    response += "Caso se sinta perdido em algum momento, lembre-se que existe o comando /help para te ajudar ;)"

    context.user_data['bio'] = update.message.text

    # Joga as informacoes no BD
    db.insert(myself, context.user_data)

    # Loga que um novo usuario foi registrado
    logger.info(
        f"User {update.effective_user.name} has been registered in the database.")
    logger.info(
        f'{update.effective_user.name} (id: {update.effective_user.id}) data: {context.user_data}')

    update.message.reply_text(response)

    return CHOOSE_ACTION


def edit_name_command(update, context):
    response = f"Seu nome atual é: {context.user_data['name']}\n\n"
    response += "Agora, manda pra mim o seu novo nome! Envie um ponto (.) caso tenha desistido de mudá-lo."
    update.message.reply_text(response)

    return GIVE_NEW_NAME


def update_name(update, context):
    if update.message.text == ".":
        update.message.reply_text("Ok! Não vou alterar seu nome.")
        return CHOOSE_ACTION

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    context.user_data['name'] = update.message.text
    db.update_by_id(myself, {'name': update.message.text})

    update.message.reply_text("Seu nome foi alterado com sucesso!")

    return CHOOSE_ACTION


def edit_bio_command(update, context):
    response = "Sua descrição atual é:\n\n"
    response += f"{context.user_data['bio']}\n\n"
    response += "Agora, manda pra mim a sua nova descrição! Envie um ponto (.) caso tenha desistido de mudá-la."
    update.message.reply_text(response)

    return GIVE_NEW_BIO


def update_bio(update, context):
    if update.message.text == ".":
        update.message.reply_text("Ok! Não vou alterar sua descrição.")
        return CHOOSE_ACTION

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    context.user_data['bio'] = update.message.text
    db.update_by_id(myself, {'bio': update.message.text})

    update.message.reply_text("Sua descrição foi alterada com sucesso!")

    return CHOOSE_ACTION


def prefs_command(update, context):
    '''
    prefs => Retorna lista de interesses (caixa de seleção). A pessoa pode marcar
    ou desmarcar o que ela quiser.
    '''

    response = "Escolha suas categorias de interesse.\n"
    response += "Utilizaremos elas para te recomendar pessoas que tenham gostos parecidos com os seus.\n"
    response += "O que você marcar aqui NÃO SERÁ VISÍVEL para nenhum outro usuário além de você mesmo!\n"

    my_cats = context.user_data['interests']

    keyboard = [
        [
            InlineKeyboardButton("☑ " + cat, callback_data=str(id)) if id in my_cats
            else InlineKeyboardButton(cat, callback_data=str(id))
            for id, cat in row
        ]
        for row in norm_categories
    ]
    keyboard.append([InlineKeyboardButton("ENVIAR", callback_data="finish")])

    update.message.reply_text(
        response, reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSE_INTERESTS


def change_category_state(update, context):
    update.callback_query.answer()  # await for answer

    my_cats = context.user_data['interests']

    # Trata a resposta anterior
    category_id = int(update.callback_query.data)
    if category_id in my_cats:
        my_cats.remove(category_id)
    else:
        my_cats.append(category_id)

    # Constroi o novo teclado
    keyboard = [
        [
            InlineKeyboardButton("☑ " + cat, callback_data=str(id)) if id in my_cats
            else InlineKeyboardButton(cat, callback_data=str(id))
            for id, cat in row
        ]
        for row in norm_categories
    ]
    keyboard.append([InlineKeyboardButton("ENVIAR", callback_data="finish")])

    update.callback_query.edit_message_reply_markup(
        reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSE_INTERESTS


def submit_selection(update, context):
    update.callback_query.answer()  # await for answer

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    # Guarda as informacoes no BD
    db.update_by_id(myself, {'interests': context.user_data['interests']})

    update.effective_message.reply_text('Seus interesses foram atualizados!')
    return ConversationHandler.END


def show_person_command(update, context):
    '''
    show => Mostra uma pessoa que tem interesses em comum (vai com base no ranking).
    Embaixo, um botão para enviar a solicitação de conexão deve existir,
    bem como um botão de "agora não".
    '''

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    my_data = db.get_by_id(myself)

    context.user_data['pending'] = my_data['pending']
    context.user_data['connections'] = my_data['connections']
    context.user_data['rejects'] = my_data['rejects']
    context.user_data['invited'] = my_data['invited']

    # get all users (IDs) from the DB
    all_users = np.array(db.list_ids(), dtype=np.uint32)

    not_allowed_users = np.hstack(
        (
            [myself],
            context.user_data['pending'],
            context.user_data['invited'],
            context.user_data['connections'],
            context.user_data['rejects']
        )
    )

    # Usuarios que podem aparecer para mim, de acordo com os dados do meu perfil
    allowed_users = np.setdiff1d(
        all_users, not_allowed_users, assume_unique=True
    )

    # LEMBRAR QUE, A PARTIR DAQUI, TODOS OS USERS SÃO np.uint32 E NÃO int,
    # portanto o casting se faz necessario

    if len(all_users) == len(not_allowed_users):
        update.message.reply_text(
            'Não tenho ninguém novo para te mostrar no momento... que tal tentar amanhã? :)')
        return CHOOSE_ACTION

    # Mapeia os usuarios aos seus interesses
    users_interests = {}
    for user in allowed_users:
        user_data = db.get_by_id(int(user))
        if myself not in user_data['rejects']:
            users_interests[int(user)] = user_data.get('interests')

    target = ranker.rank(
        context.user_data['interests'].copy(), users_interests)

    if target is None:
        # Nao ha ninguem com as preferencias do usuario ainda
        response = "Parece que não há ninguém com os mesmos gostos que você no sistema ainda...\n\n"
        response += "Você pode tentar:\n"
        response += "- Marcar mais categorias de interesse\n"
        response += "- O comando /random (pessoa aleatória)"

        update.message.reply_text(response)

        return CHOOSE_ACTION

    # Daqui para frente, sabemos que uma pessoa similar existe
    target_bio = db.get_by_id(target).get('bio')

    # Avisa no contexto que essa pessoa foi a ultima a ser exibida para o usuario (ajuda nas callback queries)
    context.user_data['lastShownId'] = target

    # MENSAGEM DO BOT

    keyboard = [[
        InlineKeyboardButton('Conectar', callback_data='connect'),
        InlineKeyboardButton('Agora não', callback_data='dismiss')
    ]]

    text = f'\"{target_bio}\"'

    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSE_ANSWER_FOR_BUTTONS


def get_random_person_command(update, context):
    '''
    random => Mostra uma pessoa aleatória. Embaixo, um botão para enviar a solicitação
    de conexão deve existir, bem como um botão de "agora não".
    '''

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    my_data = db.get_by_id(myself)

    context.user_data['pending'] = my_data['pending']
    context.user_data['connections'] = my_data['connections']
    context.user_data['rejects'] = my_data['rejects']
    context.user_data['invited'] = my_data['invited']

    # get all users (IDs) from the DB
    all_users = np.array(db.list_ids(), dtype=np.uint32)

    not_allowed_users = np.hstack(
        (
            [myself],
            context.user_data['pending'],
            context.user_data['invited'],
            context.user_data['connections'],
            context.user_data['rejects']
        )
    )

    # Usuarios que podem aparecer para mim, de acordo com os dados do meu perfil
    allowed_users = np.setdiff1d(
        all_users, not_allowed_users, assume_unique=True
    )

    # Preciso, ainda, tirar aqueles que me tem em sua lista de rejects
    remove_index = []
    for i, user in enumerate(allowed_users):
        if myself in db.get_by_id(int(user)).get('rejects'):
            remove_index.append(i)
    allowed_users = np.delete(allowed_users, remove_index)

    # LEMBRAR QUE, A PARTIR DAQUI, TODOS OS USERS SÃO np.uint32 E NÃO int,
    # portanto o casting se faz necessario

    if len(allowed_users) == 0:
        update.message.reply_text(
            'Não tenho ninguém novo para te mostrar no momento... que tal tentar amanhã? :)')
        return CHOOSE_ACTION

    target = int(random.choice(allowed_users))
    target_bio = db.get_by_id(target).get('bio')

    # Avisa no contexto que essa pessoa foi a ultima a ser exibida para o usuario (ajuda nas callback queries)
    context.user_data['lastShownId'] = target

    # MENSAGEM DO BOT

    keyboard = [[
        InlineKeyboardButton('Conectar', callback_data='connect'),
        InlineKeyboardButton('Agora não', callback_data='dismiss')
    ]]

    text = f'\"{target_bio}\"'

    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSE_ANSWER_FOR_BUTTONS


def handle_invite_answer(update, context):
    target_id = context.user_data['lastShownId']
    del context.user_data['lastShownId']

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    update.callback_query.answer()  # awaits for answer
    answer = update.callback_query.data

    if answer == 'dismiss':
        context.user_data['rejects'].append(target_id)

        # Saves in DB
        db.update_by_id(myself, {'rejects': context.user_data['rejects']})

        context.bot.sendMessage(chat_id=context.user_data['chat_id'],
                                text='Sugestão rejeitada.')

        return CHOOSE_ACTION

    # For now on, we know that the answer is "connect"!

    context.user_data['invited'].append(target_id)

    # Update my info on BD
    db.update_by_id(myself, {'invited': context.user_data['invited']})

    # Now, let's update info from the target user
    target_data = db.get_by_id(target_id)

    target_data['pending'].append(myself)

    db.update_by_id(target_id, {'pending': target_data['pending']})

    # Send messages confirming the action
    target_msg = "Você recebeu uma nova solicitação de conexão!\n"
    target_msg += "Utilize o comando /pending para vê-la."

    target_chat = target_data['chat_id']
    context.bot.sendMessage(chat_id=target_chat,
                            text=target_msg)

    context.bot.sendMessage(chat_id=context.user_data['chat_id'],
                            text='Solicitação enviada.')

    return CHOOSE_ACTION


def clear_rejected_command(update, context):
    '''
    Deleta o array de pessoas que o usuario já rejeitou,
    permitindo que elas apareçam novamente nas buscas
    '''

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    if len(context.user_data['rejects']) == 0:
        update.message.reply_text(
            'Você não \"rejeitou\" ninguém por enquanto.')
        return CHOOSE_ACTION

    context.user_data['rejects'] = []
    db.update_by_id(myself, {'rejects': []})

    update.message.reply_text(
        'Tudo certo! Sua lista de \"rejeitados\" foi limpa!')

    return CHOOSE_ACTION


def pending_command(update, context):
    '''
    pending => Mostra todas as solicitações de conexão que aquela pessoa possui e
    para as quais ela ainda não deu uma resposta. Mostra, para cada solicitação,
    a descrição da pessoa e dois botões: conectar ou descartar).
    '''

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    my_data = db.get_by_id(myself)

    context.user_data['pending'] = my_data['pending']

    if len(context.user_data['pending']) == 0:
        update.message.reply_text(
            'Você não possui novas solicitações de conexão.')
        return CHOOSE_ACTION

    # Pego o primeiro elemento na "fila"
    target = context.user_data['pending'].pop(0)

    target_data = db.get_by_id(target)
    target_bio = target_data.get('bio')

    # Avisa no contexto que essa pessoa foi a ultima a ser exibida para o usuario (ajuda nas callback queries)
    context.user_data['lastShownId'] = target

    # Salvo no BD o novo array de 'pending'
    db.update_by_id(myself, {'pending': context.user_data['pending']})

    # Me retiro da lista de "invited" do outro usuario
    target_invited = target_data.get('invited')
    target_invited.remove(myself)
    db.update_by_id(target, {'invited': target_invited})

    # MENSAGEM DO BOT

    keyboard = [[
        InlineKeyboardButton('Aceitar', callback_data='accept'),
        InlineKeyboardButton('Rejeitar', callback_data='reject')
    ]]

    text = "A seguinte pessoa quer se conectar a você:\n\n"
    text += f'\"{target_bio}\"'

    update.message.reply_text(
        text, reply_markup=InlineKeyboardMarkup(keyboard))

    return CHOOSE_ANSWER_FOR_BUTTONS


def handle_pending_answer(update, context):
    target_id = context.user_data['lastShownId']
    del context.user_data['lastShownId']

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    update.callback_query.answer()  # awaits for answer
    answer = update.callback_query.data

    if answer == 'reject':
        context.user_data['rejects'].append(target_id)

        # Saves in DB
        db.update_by_id(myself, {'rejects': context.user_data['rejects']})

        context.bot.sendMessage(chat_id=context.user_data['chat_id'],
                                text='Pedido de conexão rejeitado.')

        return CHOOSE_ACTION

    # For now on, we know that the answer is "accept"!

    # Register the new connection
    context.user_data['connections'].append(target_id)
    context.user_data['pending']

    # Update my info on BD
    db.update_by_id(myself, {'connections': context.user_data['connections']})

    # Update their info on BD

    target_data = db.get_by_id(target_id)

    target_data['connections'].append(myself)

    db.update_by_id(target_id, {'connections': target_data['connections']})

    # Send messages confirming the action

    target_chat = target_data['chat_id']

    text_target = 'Uma pessoa acaba de aceitar seu pedido de conexão! Use o comando /friends para checar.'

    context.bot.sendMessage(chat_id=target_chat,
                            text=text_target)

    my_text = 'Parabéns! Você acaba de ganhar uma nova conexão! Que tal dar um \"oi\" pra elu? :)\n'
    my_text += "Use o comando /friends para ver a sua nova conexão!"

    context.bot.sendMessage(chat_id=context.user_data['chat_id'],
                            text=my_text)

    return CHOOSE_ACTION


def friends_command(update, context):
    '''
    friends => Mostra o contato (@ do Tele) de todas as pessoas com que o usuário
    já se conectou.
    '''

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    my_data = db.get_by_id(myself)

    context.user_data['connections'] = my_data['connections']

    if len(context.user_data['connections']) == 0:
        # Este usuario ainda nao tem conexoes
        response = "Você ainda não possui nenhuma conexão!\n"
        response += "Que tal usar o comando /show para conhecer alguém novo?"

        update.message.reply_text(response)

        return CHOOSE_ACTION

    # Se chegou ate aqui é porque ele tem conexoes

    response = "Suas conexões atuais são:\n\n"

    for user in context.user_data['connections']:
        user_info = db.get_by_id(user)

        user_info_txt = "_" * 33
        user_info_txt += "\n"
        user_info_txt += f"\n{user_info['name']}\n"
        user_info_txt += f"\n\"{user_info['bio']}\"\n"
        user_info_txt += f"\nPara conversar, clique aqui --> {user_info['username']}\n"
        user_info_txt += "\n"

        response += user_info_txt

    update.message.reply_text(response)

    return CHOOSE_ACTION


# ============================== ERROR/UNKNOWN =================================


def handle_incorrect_choice(update, context):
    context.bot.sendMessage(chat_id=context.user_data['chat_id'],
                            text='Você deve decidir a sua ação acerca do usuário acima antes de prosseguir.')

    return CHOOSE_ANSWER_FOR_BUTTONS


def prefs_unknown_message(update, context):
    '''
    Mensagem ou comando desconhecido (dentro da conversa de selecionar interesses)
    '''
    response_message = "Por favor, clique em ENVIAR para terminar de atualizar as suas preferências."
    update.message.reply_text(response_message)


def unknown_message(update, context):
    '''
    Mensagem ou comando desconhecido
    '''
    response_message = "Não entendi! Por favor, use um comando válido...\nUse /help se estiver com dificuldades."
    update.message.reply_text(response_message)


# ================================= ADMIN ======================================

def notify_command(update, context):

    # facilita na hora de referenciar esse usuario
    myself = update.effective_user.id

    is_admin = False
    admin_name = ""

    for admin in ADMINS:
        if myself == admin['telegramId']:
            is_admin = True
            admin_name = admin['name']
            break

    if not is_admin:
        response = "O que você está tentando fazer? Esse comando é só para admins."
        update.message.reply_text(response)

        return CHOOSE_ACTION

    response = f"Olá {admin_name}!\n"
    response += "Me informe a mensagem que deseja mandar para TODOS os usuários do Approxima.\n"
    response += "PS: Lembre-se de usar esse recurso com responsabilidade :)"

    update.message.reply_text(response)

    return SEND_NOTIFICATION


def send_notification(update, context):

    all_chats = db.list_chat_ids()

    for chat in all_chats:
        try:
            context.bot.sendMessage(chat_id=chat, text=update.message.text)
        except Exception as e:
            logger.error(f"Erro ao interagir com o chat {chat}: {e}")

    # Avisa que esse admin mandou o broadcast
    logger.info(
        f"{context.user_data['name']} mandou uma notificação para todos os usuários: {update.message.text}")

    return CHOOSE_ACTION

# ================================= MAIN =======================================


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    prefs_handler = ConversationHandler(
        entry_points=[
            CommandHandler('prefs', prefs_command)
        ],

        states={
            CHOOSE_INTERESTS: [
                CallbackQueryHandler(
                    change_category_state, pattern='^[\\d]+$'),
                CallbackQueryHandler(submit_selection, pattern='^finish$')
            ],
        },

        fallbacks=[
            MessageHandler(Filters.all, prefs_unknown_message)
        ],

        map_to_parent={
            ConversationHandler.END: CHOOSE_ACTION
        }
    )

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start_command)
        ],

        states={
            REGISTER_NAME: [
                MessageHandler(Filters.text, register_name)
            ],

            REGISTER_BIO: [
                MessageHandler(Filters.text, register_bio)
            ],

            CHOOSE_ACTION: [
                prefs_handler,  # /prefs
                CommandHandler('show', show_person_command),
                CommandHandler('random', get_random_person_command),
                CommandHandler('clear', clear_rejected_command),
                CommandHandler('pending', pending_command),
                CommandHandler('friends', friends_command),
                CommandHandler('name', edit_name_command),
                CommandHandler('desc', edit_bio_command),
                CommandHandler('help', help_command),
                CommandHandler('notify', notify_command),   # SO PARA ADMINS
            ],

            CHOOSE_ANSWER_FOR_BUTTONS: [
                CallbackQueryHandler(
                    handle_invite_answer, pattern='^(connect|dismiss)$'),
                CallbackQueryHandler(
                    handle_pending_answer, pattern='^(accept|reject)$'),
                MessageHandler(Filters.all, handle_incorrect_choice),
            ],

            GIVE_NEW_NAME: [
                MessageHandler(Filters.text, update_name)
            ],

            GIVE_NEW_BIO: [
                MessageHandler(Filters.text, update_bio)
            ],

            SEND_NOTIFICATION: [
                MessageHandler(Filters.text, send_notification)
            ],
        },

        fallbacks=[
            CommandHandler('start', start_command),
            MessageHandler(Filters.all, unknown_message)
        ]
    )

    updater.dispatcher.add_handler(conv_handler)

    updater.start_polling()
    logging.info("=== Bot running! ===")
    updater.idle()
    logging.info("=== Bot shutting down! ===")


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
