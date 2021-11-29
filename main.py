from bot import Bot
import Crypt as cr

print(cr.dados)

Bot(
    user=cr.dados['usuario'], senha=cr.dados['senha'], timeframe=cr.dados['time_frame'], tentativas=cr.dados['tentativas'],
    modo=cr.dados['tipo_conta'], operacao=cr.dados['operacao'], par=cr.dados['paridade'], valor=cr.dados['entrada'],
    loss=cr.dados['stop_loss'], win=cr.dados['stop_win'], inverso=cr.dados['tendencia'],
    multiplicador=cr.dados['multiplicador']
    )

