import cryptocode
import re



# criado lista de chaves para criar dicionario com todos dados necessarios para a aplicação
lista_chaves = ['usuario', 'senha', 'paridade', 'tipo_conta', 'time_frame', 'operacao', 'entrada', 'stop_loss', 'stop_win',
                'tentativas', 'tendencia', 'multiplicador']
dados = {}

#realiza a primeira leitura do arquivo
with open('config.txt') as config:
    leitura = config.readlines()

#abre o arquivo para gravação e coletar os dados
with open('config.txt','w') as gravando:
    for item, chave in zip(leitura, lista_chaves):
        dado = item.strip()
        m = re.search("= ", dado)
        if dado[0:m.start()] in 'senha ':
            str_encoded = cryptocode.encrypt(dado[m.start()+2:], "senha")
            dados[chave] = (dado[m.start() + 2:])
            item = f'coded = {str_encoded}\n'

        elif dado[0:m.start()] in 'coded ':
            dado = cryptocode.decrypt(dado[m.start()+2:], "senha")
            dados[chave] = (dado)
            gravando.write(item)
            continue
        dados[chave]= (dado[m.start()+2:])
        gravando.write(item)

