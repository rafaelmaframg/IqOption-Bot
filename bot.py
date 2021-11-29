from datetime import datetime
import time
from iqoptionapi.stable_api import IQ_Option
import sys


class Bot:
    def __init__(self, user, senha, timeframe, tentativas, modo, operacao, par, valor, loss, win,
                 inverso, multiplicador):
        self.tempo = int(timeframe)
        self.modo = 'REAL' if modo.upper() == 'REAL' else 'PRACTICE'
        self.conectar(user=user, senha=senha, modo=self.modo)
        self.operacao = 1 if operacao.lower() == 'digital' else 2
        self.tipo_mhi = 1 if inverso.lower() == 'sim' else 2
        self.par = par.upper()
        self.valor_entrada = float(valor)
        self.valor_entrada_b = float(self.valor_entrada)
        self.tentativas = int(tentativas) + 1
        self.stop_loss = float(loss)
        self.stop_gain = float(win)
        self.lucro = 0
        self.prejuizo = 0
        self.wins = 0
        self.loss = 0
        self.entrar = False
        self.payout = self.pega_payout(self.par)  # MOSTRA O PAYOUT da moeda
        self.parar = False
        self.multiplicador = int(multiplicador)
        self.get_candle(self.tempo)
        print('entrar OKK',self.entrar)
        self.entra_na_operacao()

    def pega_payout(self, par):
        self.iq.subscribe_strike_list(par, 1)
        while True:
            d = self.iq.get_digital_current_profit(par, 1)
            if d != False:
                d = round(int(d) / 100, 2)
                break
            time.sleep(1)
        self.iq.unsubscribe_strike_list(par, 1)
        return d

    def conectar(self, user, senha, modo):
        self.iq = IQ_Option(user, senha)
        self.iq.connect()
        self.iq.change_balance(modo)  # PRACTICE / REAL
        if self.iq.check_connect():
            print('conectado')
            time.sleep(2)
            print('Loggin Ok')
            print('Você Está Conectado!')

        else:
            time.sleep(2)
            print('ERRO NA CONEXÃO')
            input('\n\n Aperte enter para sair')
            sys.exit()


    def stop(self, lucro, gain, loss):
        if lucro <= float('-' + str(abs(loss))):
            self.parar = True
            print("Stop Loss batido!")

        if lucro >= float(abs(gain)):
            self.parar = True
            print('Stop Win Batido!')

    def get_candle(self, timeframe):
        while not self.entrar:
            print('entrar?', self.entrar)
            if timeframe == 1:
                self.minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
                self.entrar = True if self.minutos - int(self.minutos) > 0.58 and self.minutos - int(
                    self.minutos) <= 0.59 else False
                time.sleep(0.5)
            elif timeframe == 5:
                self.minutos = float(((datetime.now()).strftime('%M.%S'))[1:])
                self.entrar = True if (self.minutos >= 4.58 and self.minutos <= 5) or self.minutos >= 9.58 and self.minutos <= 9.59 else False
                time.sleep(0.5)

            elif timeframe == 15:
                self.minutos = float(((datetime.now()).strftime('%M.%S'))[:])
                self.entrar = True if (self.minutos >= 14.58 and self.minutos <= 15) or self.minutos >= 29.58 and self.minutos <= 29.59 or self.minutos >= 44.58 and self.minutos <= 44.59 else False
                time.sleep(0.5)



    def entra_na_operacao(self):
        print(f'{self.par} Operando')
        self.dir = False
        self.velas = self.iq.get_candles(self.par, self.tempo * 60, 1, time.time())
        self.cores = 'VERDE' if self.velas[0]['open'] < self.velas[0]['close'] else 'VERMELHO' if self.velas[0][
                                                                                                      'open'] > \
                                                                                                  self.velas[0][
                                                                               'close'] else 'DOJI'
        print(f'Verificando cores...{self.cores}')
        if self.cores == 'VERDE': self.dir = ('put' if self.tipo_mhi == 1 else 'call')
        if self.cores == 'VERMELHO': self.dir = ('call' if self.tipo_mhi == 1 else 'put')
        if self.cores == 'DOJI':
            print(f'DOJI - Operação Cancelada')

        if self.dir:
            print(f'Direção: {self.dir.upper()}')
            self.status, self.id = self.iq.buy_digital_spot(self.par, self.valor_entrada, self.dir, self.tempo) \
                if self.operacao == 1 else self.iq.buy(self.valor_entrada, self.par, self.dir, self.tempo)
            if self.status:
                while True:
                    try:
                        self.status, self.valor = self.iq.check_win_digital_v2(
                            self.id) if self.operacao == 1 else self.iq.check_win_v3(self.id)
                    except:
                        self.status = True
                        self.valor = 0
                    time.sleep(3)
                    if self.status:
                        self.valor = self.valor if self.valor > 0 else float('-' + str(abs(self.valor_entrada)))
                        self.lucro += round(self.valor, 2)
                        print(f'Resultado operação:')
                        resultado = 'WIN' if self.valor > 0 else 'LOSS'
                        print(f'{resultado} / {round(self.valor, 2)} / {round(self.lucro, 2)}')
                        if self.valor > 0:
                            self.wins += 1
                            self.lucro += (round(self.lucro, 2))
                            self.resultado = 'WIN'
                        else:
                            self.resultado = 'LOSS'
                            self.prejuizo += (round(self.lucro, 2))

                        print(f'{resultado} / {round(self.valor, 2)} / {round(self.lucro, 2)}')
                        self.stop(self.lucro, self.stop_gain, self.stop_loss)
                        break

            else:
                print(f'Operação não realizada {self.dir} != {self.sentido}')
        else:
            if self.dir != False:
                print(f'Operação não realizada {self.dir} != {self.sentido}')
                time.sleep(10)
