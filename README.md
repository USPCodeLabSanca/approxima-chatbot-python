# Approxima Chatbot (Telegram)

Chatbot de Telegram que será desenvolvido como MVP (Minimum Valueable Product) da iniciativa Approxima

## Acabou de clonar o repositório?

Rode o comando `pip install -r requirements.txt` para instalar as libs necessárias.

## Lista de comandos (@approxima_bot)

- /start => (Re)inicia o bot. Se a pessoa não estiver cadastrada na base de dados, pede para ela fornecer um nome, uma pequena descrição pessoal e sugere a ela escolher seus primeiros interesses.

- /prefs => Retorna lista de interesses (caixa de seleção). A pessoa pode marcar ou desmarcar o que ela quiser. O que ela marcar aqui será utilizado pelo algoritmo de rankeamento para encontrar as pessoas mais similares à ela. Até o presente momento, não há a intenção de mostrar os interesses marcados por uma pessoa às outras.

- /show => Mostra a descrição da pessoa mais similar ao usuário, com base nos interesses, e duas opções: "conectar" e "agora não".

- /random => Mostra a descrição de uma pessoa aleatória e duas opções: "conectar" e "agora não".

- [POSSIVEL FEATURE] /opposite => Mostra a descrição de uma pessoa que tem interesses opostos (vai com base no ranking reverso) e duas opções: "conectar" e "agora não".

- /clear => Permite que as pessoas que o usuário respondeu com "agora não" apareçam de novo nas sugestões dele (quando ele responde com "agora não", aquele usuário vai para o campo de "rejeitados", então não irá aparecer como sugestão novamente AO MENOS que ele dê esse comando).

- /pending => Pega a primeira solicitação de conexão da fila de não-respondidas, mostrando a descrição da pessoa e dois botões: "aceitar" ou "rejeitar".

- /friends => Mostra o nome, a descrição e o contato (@ do Telegram) de todas as pessoas com que o usuário já se conectou.

- /name => Troca o nome do usuário.

- /desc => Troca a descrição do usuário.

- /help => Mostra os comandos disponíveis.
