import os
from dotenv import load_dotenv
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Updater, Filters,  CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler
import logging

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

categories = ['Filmes', 'Séries', 'Shows', 'Jogos', 'Livros e Literatura',
            'Beleza e Fitness', 'Idiomas', 'Ciência e Ensino (tópicos acadêmicos)',
            'Hardware', 'Software', 'Esportes', 'Dança', 'Música', 'Pintura e Desenho',
            'Culinária', 'Mão na massa (consertos, costura, tricô, etc.)', 'Casa e Jardim',
            'Pets', 'Compras', 'Trabalho voluntário', 'Hobbies e Lazer', 'Política',
            'Finanças', 'Viagens e Turismo', 'Intercâmbio', 'Automóveis e Veículos',
            'Esotérico e Holístico', 'Espiritualidade', 'Times do coração',
            'Causas (ambientais, feminismo, vegan, etc.)', 'Moda',
            'Empreenderismo e Negócios', 'Imobiliário', 'Artesanato', 'Fotografia',
            'História', 'Mitologia', 'Pessoas e Sociedade', 'Anime e Mangá']

# Give each category an ID
categories = enumerate(categories)

def normalizeCategories(categories, num_per_row=1):
    new_categories = []
    new_row = []
    for id, cat in categories:
        if id > 0 and id % num_per_row == 0: # start a new row
            new_categories.append(new_row[:]) # makes a copy
            new_row = []
            new_row.append((id, cat))
        else:
            new_row.append((id, cat))
    return new_categories

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logging.getLogger(__name__)

# start => Inicia o bot. Se a pessoa não estiver cadastrada na base de dados
# (dá pra ver pelo ID da conversa/Tele [ver qual é melhor]), pede para ela fornecer
# um nome, uma pequena descrição pessoal e, por último, para escolher, no mínimo,
# 3 interesses para começar.
def start(update, context):
    update.message.reply_text('Hi!')

# prefs => Retorna lista de interesses (caixa de seleção). A pessoa pode marcar
# ou desmarcar o que ela quiser.
def prefs(update, context):
    keyboard = [ [ InlineKeyboardButton(cat + "✅", callback_data=str(id)) for id, cat in row] for row in normalizeCategories(categories, 1) ]
    update.message.reply_text('Escolha suas categorias de interesse:', reply_markup=InlineKeyboardMarkup(keyboard))

def button(update, context):
    query = update.callback_query

    # CallbackQueries need to be answered, even if no notification to the user is needed
    # Some clients may have trouble otherwise. See https://core.telegram.org/bots/api#callbackquery
    query.answer()

    query.edit_message_text(text="Selected option: {}".format(query.data))

# show => Mostra uma pessoa que tem interesses em comum (vai com base no ranking).
# Embaixo, um botão para enviar a solicitação de conexão deve existir.
def show(update, context):
    update.message.reply_text(update.message.text)

# random => Mostra uma pessoa aleatória. Embaixo, um botão para enviar a solicitação
# de conexão deve existir.
def random(update, context):
    update.message.reply_text(update.message.text)

# pending => Mostra todas as solicitações de conexão que aquela pessoa possui e
# para as quais ela ainda não deu uma resposta. Mostra, para cada solicitação,
# a descrição da pessoa e dois botões: conectar ou descartar).
def pending(update, context):
    update.message.reply_text(update.message.text)

# friends => Mostra o contato (@ do Tele) de todas as pessoas com que o usuário
# já se conectou.
def friends(update, context):
    update.message.reply_text(update.message.text)

# help => Mostra os comandos disponíveis.
def help_command(update, context):
    reply_message = 'prefs - retorna uma lista (caixa de seleção) com todas as categorias de interesse. A partir daí, você poderá adicionar ou remover interesses à vontade.\
        show - mostra uma pessoa que tem interesses em comum.\
        random - mostra uma pessoa aleatória.\
        pending - mostra todas as solicitações de conexão que você possui e ainda não respondeu.\
        friends - mostra o contato de todas as pessoas com que você já se conectou.\
        help - mostra os comandos que você pode usar'
    update.message.reply_text(reply_message)

# mensagem ou comando desconhecido
def unknown(update, context):
    response_message = "Não entendi! Por favor, use um comando (eles começam com '/')."
    update.message.reply_text(response_message)


def main():
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)

    updater.dispatcher.add_handler(CommandHandler("start", start))
    updater.dispatcher.add_handler(CommandHandler("prefs", prefs))
    updater.dispatcher.add_handler(CallbackQueryHandler(button))
    updater.dispatcher.add_handler(CommandHandler("help", help_command))
    updater.dispatcher.add_handler(MessageHandler(Filters.all, unknown))

    updater.start_polling()
    logging.info("=== Bot running! ===")
    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()
    logging.info("=== Bot shutting down! ===")


if __name__ == '__main__':
    print("press CTRL + C to cancel.")
    main()
