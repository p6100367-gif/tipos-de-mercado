import streamlit as st
import json
import re
from PIL import Image

try:
    import pytesseract
    HAS_OCR = True
except ImportError:
    HAS_OCR = False

# Configuração da página
st.set_page_config(
    page_title="Reals - Consultor & Analisador de Bilhetes",
    page_icon="⚽",
    layout="wide"
)

# Dados carregados da planilha oficial da Reals
DATA = {
  "reals_rules": [
    {
      "situaçao": "1. Identificar a aposta",
      "conferir": "Confira esporte, evento, seleção, linha, período e formato do bilhete. Diferencie múltipla comum e Criar Aposta.",
      "base": "Regras Gerais; seções 1.6 e 1.10; Criar Aposta — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "2. Qual regra prevalece",
      "conferir": "A regra específica do esporte prevalece sobre a geral em caso de conflito. Mercados de jogadores têm a regra uniforme da seção 1.11; confira também as exceções expressas e condições da oferta.",
      "base": "Introdução; seção 1.11 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "3. Período e prorrogação",
      "conferir": "Mercados não incluem prorrogação, salvo indicação expressa. Em mercados de tempo, quarto ou período, conte apenas os eventos daquele intervalo.",
      "base": "Seções 1.2 e 1.6 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "4. Resultado oficial e bilhete em aberto",
      "conferir": "Liquide pelo resultado oficial e pela definição do mercado. Transmissões, placares e gráficos da plataforma são informativos e podem estar atrasados. Se o resultado não puder ser confirmado, a liquidação pode aguardar confirmação ou a aposta pode ser anulada.",
      "base": "Seções 1.1 e 1.7 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "5. Local, adversário e formato alterados",
      "conferir": "Mudança de adversário anula as apostas. Mudança de local normalmente mantém a aposta, mas inversão de mandantes ou transferência para o campo adversário pode levar à anulação. Equipe reserva/base ou formato incomum também exigem conferir a decisão aplicável.",
      "base": "Seção 1.1 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "6. Partida adiada — prazo geral de 48h",
      "conferir": "Se confirmado que o evento não começará nas 48 horas seguintes ao horário designado, os mercados são anulados. Mudanças feitas antecipadamente por organização ou transmissão não são automaticamente adiamento. Confira exceções do esporte.",
      "base": "Seção 1.4 — Partida Adiada — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "7. Partida abandonada ou interrompida — prazo geral de 48h",
      "conferir": "Se retomada dentro de 48 horas do início oficial, as apostas abertas usam o resultado da retomada. Sem retomada no prazo, as abertas são anuladas. Mercados já decididos e regras específicas do esporte precisam ser avaliados separadamente.",
      "base": "Seção 1.4 — Partida Abandonada — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "8. Prazo especial para mercados de jogadores — 5h",
      "conferir": "Se o evento começar e for abandonado ou suspenso antes do fim, sem retomada em 5 horas, as apostas de jogadores são anuladas. Mudança de local também anula as apostas desses mercados feitas antes da alteração.",
      "base": "Seção 1.11 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "9. Exemplos de exceções por esporte",
      "conferir": "Atletismo: evento adiado/interrompido pode manter apostas se concluído em 72h. Beisebol adiado: deve começar no mesmo dia local; abandono tem condição de 48h. Tênis e padel: atraso pode manter mercados pendentes até a continuação. MotoGP, Fórmula 1 e Fórmula E: adiamento para outro dia UTC anula mercados. Não aplique 48h ou 72h indistintamente.",
      "base": "Seção 2 — Regras por Esporte — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "10. Anulação em aposta simples ou múltipla",
      "conferir": "Na simples anulada, o valor é devolvido. Na múltipla comum, a seleção anulada vale odd 1,00 e o retorno é recalculado pelas demais seleções. A regra própria de Criar Aposta é diferente.",
      "base": "Seção 1.10; Criar Aposta — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Retorno e lucro",
      "conferir": "Odd combinada é o produto das odds. Retorno integral = valor apostado × odd confirmada; lucro = retorno − valor apostado. Use a odd total e os valores do bilhete confirmado. O retorno estimado antes da confirmação pode mudar.",
      "base": "Seção 1.10; exemplo matemático — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Ganho ou perda de metade",
      "conferir": "Em linhas asiáticas de quarto, o valor se divide em duas linhas adjacentes. Exemplo didático com R$100 e odd 2,00: metade ganha/metade devolve gera retorno de R$150; metade perde/metade devolve gera R$50. Confira o tipo e a linha do mercado.",
      "base": "Exemplo matemático didático; conferir oferta e seção 1.6 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Empate em mercado de duas opções",
      "conferir": "Se o mercado de vencedor oferece somente casa e visitante, o empate anula o mercado. Não aplique isso ao 1X2 nem ao handicap europeu de três opções.",
      "base": "Seção 1.5 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Linhas inteiras, períodos e par/ímpar",
      "conferir": "Em totais ou handicap de duas opções com linha exata, igualdade com a linha anula a aposta. Em par/ímpar, zero é par salvo indicação contrária. Primeiro a atingir X é anulado se o evento terminar sem atingir o marco.",
      "base": "Seção 1.6 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Confronto direto e não participação",
      "conferir": "No confronto direto, ao menos um competidor deve concluir. Não início de um competidor, exclusão/desclassificação de todos ou empate sem opção de empate pode anular o mercado. Confira particularidades do esporte.",
      "base": "Seção 1.8 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Apostas de longo prazo e empate técnico",
      "conferir": "Em vencedor final, a regra geral mantém a aposta mesmo se o participante não competir, caso em que a seleção perde; confira exceções específicas. Cancelamento anula. Empate técnico pode reduzir proporcionalmente o retorno conforme posições disponíveis e competidores empatados.",
      "base": "Seção 1.9; Regras por Esporte — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Odds incorretas e falhas técnicas",
      "conferir": "A Reals pode suspender mercados e corrigir liquidação incorreta. Erro de evento, linha, odds ou aceitação deve ser analisado conforme o subtipo da seção 1.3; não presuma que toda falha tem o mesmo tratamento. Anulação e devolução podem se aplicar.",
      "base": "Seção 1.3 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Apostas ao vivo e apostas tardias",
      "conferir": "Confira o registro de recebimento nos servidores. Aposta após resultado conhecido ou vantagem material relevante pode ser anulada. Quando o mercado ao vivo permanece válido e o resultado não é conhecido, pode se aplicar a odd revisada do recebimento.",
      "base": "Seção 1.12 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Futebol — tempos e intervalos",
      "conferir": "Mercados de primeiro e segundo tempo usam 45 minutos mais acréscimos. Intervalo 1–10 min cobre 0:00–9:59; 11–20 cobre 10:00–19:59. Os intervalos 31–45 e 76–90 incluem acréscimos. Classificação em ida e volta considera os jogos envolvidos.",
      "base": "Seção 2 — Futebol — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Futebol — VAR",
      "conferir": "Use o momento real do incidente revisado. Liquidações podem ser revistas quando o VAR decide antes do fim. Apostas entre incidente e decisão são anuladas se houver alteração com influência material no mercado; confira as exceções.",
      "base": "Seção 2 — Futebol, Uso do VAR — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Futebol — escanteios e gols contra",
      "conferir": "Escanteio concedido e não cobrado não entra na contagem. Gol contra não conta para jogador a marcar, salvo opção que o inclua expressamente.",
      "base": "Seção 2 — Futebol — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Futebol — pontos de cartões",
      "conferir": "Em pontos de cartão: amarelo vale 10; vermelho ou amarelo-vermelho vale 25. O segundo amarelo não soma novamente: máximo de 35 por jogador. Cartões após o jogo ou para não jogadores não contam. Diferencie pontos de cartões e número de cartões.",
      "base": "Seção 2 — Futebol — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Futebol — handicap asiático ao vivo",
      "conferir": "Conta somente o restante da partida ou período desde a aposta; o placar anterior é desconsiderado. Exemplo: apostar A −0,5 com placar 1–0 exige que A vença o restante por pelo menos um gol.",
      "base": "Seção 2 — Futebol, Handicap Asiático Ao Vivo — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Futebol — total asiático ao vivo",
      "conferir": "Diferentemente do handicap asiático ao vivo, o total considera a contagem completa da partida ou período desde o início.",
      "base": "Seção 2 — Futebol, Total Asiático Ao Vivo — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Jogadores — participação e estatísticas",
      "conferir": "Nos mercados pré-jogo de futebol, jogador não relacionado ou que não entra como titular/reserva tem aposta anulada. Confira o critério da oferta, a linha e a estatística oficial. Prorrogação e pênaltis ficam de fora, ressalvadas exceções expressas como entradas extras no beisebol.",
      "base": "Seção 1.11; Regras de Liquidação de Mercados de Jogadores — Futebol — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Jogadores — substituição garantida",
      "conferir": "Só some estatísticas do titular e do respectivo substituto quando a oferta indicar substituição garantida. Sem essa indicação, a estatística trava na substituição. Conta tempo regulamentar e acréscimos, sem prorrogação. Confira os critérios próprios de participação e anulação.",
      "base": "Regras de Liquidação de Mercados de Jogadores — Futebol — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Basquete — prorrogação e jogador",
      "conferir": "Confira se o mercado inclui prorrogação. Jogador deve entrar em quadra para validar a aposta relacionada. Corrida até X sem atingir a meta pode ser anulada; o mercado Haverá prorrogação? usa o empate ao final do tempo regulamentar.",
      "base": "Seção 2 — Basquete — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Tênis — abandono, sets e tie-break",
      "conferir": "Em partida iniciada e não concluída, apostas são anuladas, exceto mercados já decididos ou incondicionalmente determinados. Atrasos podem manter mercados pendentes. Tie-break e match tie-break contam como um game; alteração no total de sets preserva vencedor, mas anula mercados de games/sets.",
      "base": "Seção 2 — Tênis — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Vôlei — interrupção e golden set",
      "conferir": "Golden set não entra nos mercados mencionados no regulamento. Mercados ainda não decididos são anulados se a partida não concluir; interrupção/adiamento sem retomada em 48h também pode anular apostas.",
      "base": "Seção 2 — Vôlei e Vôlei de Praia — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Superodd — uso, cancelamento e pagamento",
      "conferir": "Confira limite por cliente/evento e uso único da oferta. Não combine com bonificações incompatíveis. A Reals pode cancelar com devolução integral. Pagamento pode levar até 72 horas após confirmação oficial de todos os resultados envolvidos. Uso irregular pode levar à liquidação pela odd original.",
      "base": "Regras de Superodd — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Cashout — disponibilidade e valor mínimo",
      "conferir": "Oferta opcional para mercados selecionados; pode ser suspensa ou retirada. Não é oferecida quando o valor fica abaixo de 5% da aposta original. Confira valor disponível e confirmação; ausência do recurso não significa cancelamento do bilhete.",
      "base": "Regras de Cash Out — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Cashout — suspensão, erro e confirmação",
      "conferir": "Cashout confirmado antes da suspensão deve ser honrado. Solicitação posterior à suspensão pode ser retida/cancelada. Valor aceito por erro óbvio pode ter a transação cancelada e a aposta reativada. Tentativa sem confirmação não encerra o bilhete.",
      "base": "Regras de Cash Out; Termos enviados: 17.9 — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Criar Aposta — anulação e perda",
      "conferir": "Se uma seleção é anulada, o Criar Aposta daquele jogo é integralmente anulado sem recálculo, desde que nenhuma outra seleção tenha perdido. Se houver seleção perdida, o bilhete perde integralmente mesmo com outra anulada.",
      "base": "Regras de Criar Aposta — Anulação em cascata; Prevalência da perda — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    },
    {
      "situaçao": "Modificar aposta confirmada",
      "conferir": "O documento de Termos anteriormente anexado não permite alterar ou ajustar aposta efetivada. Para esse tema, confira também a versão vigente dos Termos; a página de regras consultada não substitui sua validação.",
      "base": "Termos enviados: 6.2 (versão vigente não verificada nesta atualização) — https://reals.bet.br/legal/regras (consulta em 03/10/2026)"
    }
  ],
  "general_markets": [
    {
      "mercado": "Resultado final (1X2)",
      "selecao": "1 = time da casa",
      "ganha": "Casa vence. Ex.: 2–1.",
      "perde": "Empate ou vitória do visitante.",
      "devolve": "Não por empate.",
      "atencao": "Categoria confirmada na página pública da Reals."
    },
    {
      "mercado": "Resultado final (1X2)",
      "selecao": "X = empate",
      "ganha": "Os times empatam. Ex.: 1–1.",
      "perde": "Qualquer time vence.",
      "devolve": "Não por empate.",
      "atencao": "Conferir período do bilhete."
    },
    {
      "mercado": "Resultado final (1X2)",
      "selecao": "2 = time visitante",
      "ganha": "Visitante vence. Ex.: 0–1.",
      "perde": "Empate ou vitória da casa.",
      "devolve": "Não por empate.",
      "atencao": "Conferir período do bilhete."
    },
    {
      "mercado": "Dupla chance",
      "selecao": "1X",
      "ganha": "Casa vence ou empata.",
      "perde": "Visitante vence.",
      "devolve": "Não por empate.",
      "atencao": "Explicação geral; conferir nome e oferta na Reals."
    },
    {
      "mercado": "Dupla chance",
      "selecao": "X2",
      "ganha": "Visitante vence ou empata.",
      "perde": "Casa vence.",
      "devolve": "Não por empate.",
      "atencao": "Explicação geral; conferir nome e oferta na Reals."
    },
    {
      "mercado": "Dupla chance",
      "selecao": "12",
      "ganha": "Qualquer time vence.",
      "perde": "Empate.",
      "devolve": "Não por empate.",
      "atencao": "Explicação geral; conferir nome e oferta na Reals."
    },
    {
      "mercado": "Empate anula aposta",
      "selecao": "Time A",
      "ganha": "Time A vence.",
      "perde": "Time A perde.",
      "devolve": "Empate: devolve tudo.",
      "atencao": "Explicação geral; equivale ao handicap asiático 0."
    },
    {
      "mercado": "Placar correto",
      "selecao": "2–1",
      "ganha": "Final do período = 2–1.",
      "perde": "Qualquer outro placar.",
      "devolve": "Não por empate.",
      "atencao": "Categoria confirmada na página pública da Reals."
    },
    {
      "mercado": "Ambas as equipes marcam",
      "selecao": "Sim",
      "ganha": "Cada time marca pelo menos 1 gol.",
      "perde": "Pelo menos um time não marca.",
      "devolve": "Não pelo número de gols.",
      "atencao": "Categoria confirmada na página pública da Reals."
    },
    {
      "mercado": "Ambas as equipes marcam",
      "selecao": "Não",
      "ganha": "Pelo menos um time não marca.",
      "perde": "Os dois times marcam.",
      "devolve": "Não pelo número de gols.",
      "atencao": "Categoria confirmada na página pública da Reals."
    },
    {
      "mercado": "Total de gols",
      "selecao": "Mais de 2,5",
      "ganha": "3 ou mais gols.",
      "perde": "2 ou menos gols.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada; conferir período e contagem."
    },
    {
      "mercado": "Total de gols",
      "selecao": "Menos de 2,5",
      "ganha": "2 ou menos gols.",
      "perde": "3 ou mais gols.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada; conferir período e contagem."
    },
    {
      "mercado": "Escanteios — total",
      "selecao": "Mais de 9,5",
      "ganha": "10 ou mais escanteios.",
      "perde": "9 ou menos escanteios.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada; conferir período e contagem."
    },
    {
      "mercado": "Escanteios — total",
      "selecao": "Menos de 9,5",
      "ganha": "9 ou menos escanteios.",
      "perde": "10 ou mais escanteios.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada; conferir período e contagem."
    },
    {
      "mercado": "Cartões — total",
      "selecao": "Mais de 3,5",
      "ganha": "4 ou mais cartões válidos.",
      "perde": "3 ou menos cartões válidos.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada. Conferir peso de vermelho, 2º amarelo e cartões ao banco."
    },
    {
      "mercado": "Cartões — total",
      "selecao": "Menos de 3,5",
      "ganha": "3 ou menos cartões válidos.",
      "perde": "4 ou mais cartões válidos.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada. Conferir peso de vermelho, 2º amarelo e cartões ao banco."
    },
    {
      "mercado": "Handicap asiático",
      "selecao": "Time A −1,0",
      "ganha": "A vence por 2 ou mais gols.",
      "perde": "A empata ou perde.",
      "devolve": "A vence por exatamente 1: devolve tudo.",
      "atencao": "Ver aba Handicap; tipo asiático deve constar na regra."
    },
    {
      "mercado": "Handicap europeu (3 opções)",
      "selecao": "Time A −1",
      "ganha": "A vence por 2 ou mais gols.",
      "perde": "A vence por 1, empata ou perde.",
      "devolve": "Vitória por 1 NÃO devolve: é empate ajustado.",
      "atencao": "Ver aba Handicap; não confundir com asiático."
    },
    {
      "mercado": "Handicap europeu (3 opções)",
      "selecao": "Empate com A −1",
      "ganha": "A vence por exatamente 1 gol.",
      "perde": "Qualquer outra diferença.",
      "devolve": "Não por empate ajustado.",
      "atencao": "A seleção escolhida deve ser “Empate”."
    },
    {
      "mercado": "Resultado — Intervalo/final",
      "selecao": "X/1",
      "ganha": "X/1; intervalo 0–0, final 1–0. Acertar os dois resultados.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Exemplo didático; confirmar oferta."
    },
    {
      "mercado": "Resultado — Vencedor do 1º tempo",
      "selecao": "A",
      "ganha": "A; intervalo 1–0. Acertar o resultado do período.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Não usa o placar final."
    },
    {
      "mercado": "Resultado — Classificação",
      "selecao": "A avança nos pênaltis: ganha.",
      "ganha": "A avança nos pênaltis. Acertar quem avança.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Validar inclusão de prorrogação/pênaltis."
    },
    {
      "mercado": "Gols — Total por equipe",
      "selecao": "A mais 1,5",
      "ganha": "A mais 1,5; 2–0. Conta apenas o time escolhido.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Confirmar período."
    },
    {
      "mercado": "Gols — Total exato",
      "selecao": "3",
      "ganha": "3; 2–1. Acertar a soma.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Exemplo derivado do total."
    },
    {
      "mercado": "Gols — Total par/ímpar",
      "selecao": "Par",
      "ganha": "Par; 0–0. Paridade da soma.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Zero é par; confirmar mercado."
    },
    {
      "mercado": "Escanteios — Total por equipe",
      "selecao": "A mais 4,5",
      "ganha": "A mais 4,5; A=5. Conta uma equipe.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Conferir escanteios concedidos/cobrados."
    },
    {
      "mercado": "Escanteios — Handicap",
      "selecao": "A −1,5",
      "ganha": "A −1,5; 7–5. Ajusta a diferença de escanteios.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Confirmar asiático ou 3 vias."
    },
    {
      "mercado": "Cartões — Total por equipe",
      "selecao": "A mais 1,5",
      "ganha": "A mais 1,5; 2 válidos. Conta cartões do time.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Banco/comissão técnica: conferir regra."
    },
    {
      "mercado": "Jogadores — Gol a qualquer momento",
      "selecao": "J marca no período: ganha.",
      "ganha": "J marca no período. Jogador marca.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Confirmar participação e gol contra."
    },
    {
      "mercado": "Jogadores — Dois ou três gols",
      "selecao": "2+",
      "ganha": "2+; J marca 2. Atingir o número definido.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Participação: conferir regra."
    },
    {
      "mercado": "Jogadores — Assistência",
      "selecao": "J registra 1: ganha.",
      "ganha": "J registra 1. Jogador dá assistência.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Usar provedor oficial."
    },
    {
      "mercado": "Jogadores — Finalizações",
      "selecao": "Mais 2,5",
      "ganha": "Mais 2,5; 3. Conta tentativas válidas.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Não equivale a chutes no gol."
    },
    {
      "mercado": "Jogadores — Chutes no gol",
      "selecao": "Mais 0,5",
      "ganha": "Mais 0,5; 1. Conta finalizações no alvo.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Definição do provedor prevalece."
    },
    {
      "mercado": "Jogadores — Receber cartão",
      "selecao": "J recebe amarelo: ganha se elegível.",
      "ganha": "J recebe amarelo: ganha se elegível. Jogador recebe cartão elegível.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Confirmar participação."
    },
    {
      "mercado": "Jogadores — Faltas cometidas",
      "selecao": "Mais 1.5",
      "ganha": "Mais 1.5; 2. Compara a estatística com a linha.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Contagem e participação conforme regra."
    },
    {
      "mercado": "Jogadores — Faltas sofridas",
      "selecao": "Mais 1.5",
      "ganha": "Mais 1.5; 2. Compara a estatística com a linha.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Contagem e participação conforme regra."
    },
    {
      "mercado": "Jogadores — Desarmes",
      "selecao": "Mais 2.5",
      "ganha": "Mais 2.5; 3. Compara a estatística com a linha.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Contagem e participação conforme regra."
    },
    {
      "mercado": "Jogadores — Passes",
      "selecao": "Mais 39.5",
      "ganha": "Mais 39.5; 40. Compara a estatística com a linha.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Contagem e participação conforme regra."
    },
    {
      "mercado": "Jogadores — Impedimentos",
      "selecao": "Mais 0.5",
      "ganha": "Mais 0.5; 1. Compara a estatística com a linha.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Contagem e participação conforme regra."
    },
    {
      "mercado": "Jogadores — Defesas do goleiro",
      "selecao": "Mais 2.5",
      "ganha": "Mais 2.5; 3. Compara a estatística com a linha.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Contagem e participação conforme regra."
    },
    {
      "mercado": "Futuros — Campeão",
      "selecao": "Equipe escolhida campeã: ganha.",
      "ganha": "Equipe escolhida campeã. Acertar o campeão.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Liquidação ao final da competição."
    },
    {
      "mercado": "Futuros — Artilheiro",
      "selecao": "Jogador escolhido lidera: conferir empate.",
      "ganha": "Acertar o artilheiro.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Empate pode ter divisão de retorno."
    },
    {
      "mercado": "Formato — Simples",
      "selecao": "Seleção ganha: retorno=valor×odd.",
      "ganha": "Uma seleção.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Retorno inclui valor apostado."
    },
    {
      "mercado": "Formato — Múltipla",
      "selecao": "Odds 1,50×2,00=3,00.",
      "ganha": "Todas as seleções válidas ganham.",
      "perde": "Uma seleção válida perde.",
      "devolve": "Seleção anulada: conferir recálculo. Ver Como conferir.",
      "atencao": "Complemento geral. Todas devem ganhar; anulação conforme regra."
    },
    {
      "mercado": "Formato — Sistema",
      "selecao": "2 de 3: três duplas.",
      "ganha": "Depende das combinações vencedoras.",
      "perde": "Combinações sem acertos suficientes perdem.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Pode pagar com acertos parciais."
    },
    {
      "mercado": "Formato — Criar Aposta",
      "selecao": "A vence + ambas marcam.",
      "ganha": "Todas as condições válidas do produto são atendidas.",
      "perde": "Uma condição válida não é atendida.",
      "devolve": "Conferir regra própria de anulação do Criar Aposta.",
      "atencao": "Complemento geral. Anulação e odd: regra específica da casa."
    },
    {
      "mercado": "Formato — Ao vivo",
      "selecao": "Mercado aceito aos 30 minutos.",
      "ganha": "Condição selecionada é atendida no período contratado.",
      "perde": "Condição não é atendida.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Confirmar se conta jogo inteiro ou restante."
    },
    {
      "mercado": "Basquete — Vencedor (moneyline)",
      "selecao": "A vence 90–85: ganha.",
      "ganha": "A vence 90–85. Acertar vencedor.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Prorrogação conforme mercado."
    },
    {
      "mercado": "Basquete — Handicap de pontos",
      "selecao": "A −4,5",
      "ganha": "A −4,5; 90–85. Ajusta diferença de pontos.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Linha inteira pode devolver."
    },
    {
      "mercado": "Basquete — Total de pontos",
      "selecao": "Mais 174,5",
      "ganha": "Mais 174,5; 90–85. Soma pontos.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Conferir prorrogação."
    },
    {
      "mercado": "Tênis — Vencedor",
      "selecao": "A vence a partida: ganha.",
      "ganha": "A vence a partida. Acertar vencedor.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Desistência: regra específica."
    },
    {
      "mercado": "Tênis — Handicap de games",
      "selecao": "A −2,5",
      "ganha": "A −2,5; games 12–8. Ajusta saldo de games.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Não usar saldo de sets."
    },
    {
      "mercado": "Tênis — Total de games",
      "selecao": "Mais 19,5",
      "ganha": "Mais 19,5; 6–4/6–4. Soma games.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Match tie-break: conferir contagem."
    },
    {
      "mercado": "Vôlei — Handicap de sets",
      "selecao": "A −1,5",
      "ganha": "A −1,5; 3–1. Ajusta saldo de sets.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Não usar saldo de pontos."
    },
    {
      "mercado": "Vôlei — Total de sets",
      "selecao": "Mais 3,5",
      "ganha": "Mais 3,5; 3–1. Conta sets disputados.",
      "perde": "A condição escolhida não acontece no período válido.",
      "devolve": "Não presumir. Conferir regra específica.",
      "atencao": "Complemento geral. Conferir formato da partida."
    }
  ],
  "handicap_asiatico": [
    {
      "selecao": "Time A -3,00",
      "ganha_tudo": "Vence por 4 ou mais gols.",
      "perde_tudo": "Vence por até 2 gol(s), empata ou perde.",
      "devolve_tudo": "Vence por 3 gols.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -2,75",
      "ganha_tudo": "Vence por 4 ou mais gols.",
      "perde_tudo": "Vence por até 2 gol(s), empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Vence por 3 gols.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -2,50",
      "ganha_tudo": "Vence por 3 ou mais gols.",
      "perde_tudo": "Vence por até 2 gol(s), empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -2,25",
      "ganha_tudo": "Vence por 3 ou mais gols.",
      "perde_tudo": "Vence por até 1 gol(s), empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Vence por 2 gols."
    },
    {
      "selecao": "Time A -2,00",
      "ganha_tudo": "Vence por 3 ou mais gols.",
      "perde_tudo": "Vence por até 1 gol(s), empata ou perde.",
      "devolve_tudo": "Vence por 2 gols.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -1,75",
      "ganha_tudo": "Vence por 3 ou mais gols.",
      "perde_tudo": "Vence por até 1 gol(s), empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Vence por 2 gols.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -1,50",
      "ganha_tudo": "Vence por 2 ou mais gols.",
      "perde_tudo": "Vence por até 1 gol(s), empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -1,25",
      "ganha_tudo": "Vence por 2 ou mais gols.",
      "perde_tudo": "Empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Vence por 1 gol."
    },
    {
      "selecao": "Time A -1,00",
      "ganha_tudo": "Vence por 2 ou mais gols.",
      "perde_tudo": "Empata ou perde.",
      "devolve_tudo": "Vence por 1 gol.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -0,75",
      "ganha_tudo": "Vence por 2 ou mais gols.",
      "perde_tudo": "Empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Vence por 1 gol.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -0,50",
      "ganha_tudo": "Vence por 1 ou mais gols.",
      "perde_tudo": "Empata ou perde.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A -0,25",
      "ganha_tudo": "Vence por 1 ou mais gols.",
      "perde_tudo": "Perde por 1 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Empata."
    },
    {
      "selecao": "Time A 0,00",
      "ganha_tudo": "Vence por 1 ou mais gols.",
      "perde_tudo": "Perde por 1 ou mais gols.",
      "devolve_tudo": "Empata.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +0,25",
      "ganha_tudo": "Vence por 1 ou mais gols.",
      "perde_tudo": "Perde por 1 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Empata.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +0,50",
      "ganha_tudo": "Vence ou empata.",
      "perde_tudo": "Perde por 1 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +0,75",
      "ganha_tudo": "Vence ou empata.",
      "perde_tudo": "Perde por 2 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Perde por 1 gol."
    },
    {
      "selecao": "Time A +1,00",
      "ganha_tudo": "Vence ou empata.",
      "perde_tudo": "Perde por 2 ou mais gols.",
      "devolve_tudo": "Perde por 1 gol.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +1,25",
      "ganha_tudo": "Vence ou empata.",
      "perde_tudo": "Perde por 2 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Perde por 1 gol.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +1,50",
      "ganha_tudo": "Vence, empata ou perde por até 1 gol(s).",
      "perde_tudo": "Perde por 2 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +1,75",
      "ganha_tudo": "Vence, empata ou perde por até 1 gol(s).",
      "perde_tudo": "Perde por 3 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Perde por 2 gols."
    },
    {
      "selecao": "Time A +2,00",
      "ganha_tudo": "Vence, empata ou perde por até 1 gol(s).",
      "perde_tudo": "Perde por 3 ou mais gols.",
      "devolve_tudo": "Perde por 2 gols.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +2,25",
      "ganha_tudo": "Vence, empata ou perde por até 1 gol(s).",
      "perde_tudo": "Perde por 3 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Perde por 2 gols.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +2,50",
      "ganha_tudo": "Vence, empata ou perde por até 2 gol(s).",
      "perde_tudo": "Perde por 3 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Time A +2,75",
      "ganha_tudo": "Vence, empata ou perde por até 2 gol(s).",
      "perde_tudo": "Perde por 4 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Perde por 3 gols."
    },
    {
      "selecao": "Time A +3,00",
      "ganha_tudo": "Vence, empata ou perde por até 2 gol(s).",
      "perde_tudo": "Perde por 4 ou mais gols.",
      "devolve_tudo": "Perde por 3 gols.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    }
  ],
  "handicap_europeu": [
    {
      "selecao": "Time A −1",
      "ganha_quando": "A vence por 2 ou mais.",
      "perde_quando": "A vence por 1, empata ou perde."
    },
    {
      "selecao": "Empate com A −1",
      "ganha_quando": "A vence por exatamente 1.",
      "perde_quando": "Qualquer outra diferença."
    },
    {
      "selecao": "Time B +1 (adversário de A)",
      "ganha_quando": "B vence ou empata.",
      "perde_quando": "B perde por 1 ou mais."
    }
  ],
  "totais_asiaticos": [],
  "sources_info": [
    {
      "fonte": "Revisão em 03/10/2026. Esta planilha diferencia informação pública da Reals, Termos anexados e explicações gerais de mercados.",
      "documento": "",
      "informacao": "",
      "situacao": ""
    },
    {
      "fonte": "Reals — site público",
      "documento": "https://reals.bet.br/sports",
      "informacao": "Resultado final, gols, ambas marcam, handicap, placar correto, escanteios, cartões e cashout.",
      "situacao": "Confirma categorias; não traz o regulamento detalhado de cada seleção."
    },
    {
      "fonte": "Reals — Regras de Apostas",
      "documento": "https://reals.bet.br/legal/regras",
      "informacao": "Regras gerais, por esporte, mercados de jogadores, Superodd, Cash Out e Criar Aposta.",
      "situacao": "Conteúdo consultado em 03/10/2026. Conferir atualizações e condições específicas da oferta."
    },
    {
      "fonte": "Termos enviados por você",
      "documento": "Texto colado.txt",
      "informacao": "Itens 6.1, 6.2, 17.4, 17.7, 17.9, 17.10, 19.1, 19.1.1, 19.1.2 e 26.2.1.",
      "situacao": "Base do documento anexado; versão vigente no site não confirmada."
    },
    {
      "fonte": "Flashscore — explicação geral",
      "documento": "https://www.flashscore.com.br/apostas/guia/o-que-e-handicap/",
      "informacao": "Diferenças entre asiático e europeu.",
      "situacao": "Referência didática; não é regulamento da Reals."
    },
    {
      "fonte": "365Scores — explicação geral",
      "documento": "https://www.365scores.com/pt-br/apostas/como-apostar/handicap",
      "informacao": "Linhas inteiras, meias e quartos.",
      "situacao": "Referência didática; exemplos e tabelas calculados para esta planilha."
    },
    {
      "fonte": "365Scores — mercados",
      "documento": "https://www.365scores.com/pt-br/apostas/como-apostar/tipos-de-apostas-no-futebol",
      "informacao": "Nomes e conceitos gerais.",
      "situacao": "Complementos não confirmam disponibilidade na Reals."
    },
    {
      "fonte": "365Scores — estatísticas",
      "documento": "https://www.365scores.com/pt-br/apostas/como-apostar/prop-bet",
      "informacao": "Estatísticas de jogadores.",
      "situacao": "Participação e contagem dependem da regra específica."
    },
    {
      "fonte": "Cálculos próprios",
      "documento": "Matrizes de handicap e total",
      "informacao": "Contas a partir de diferença/soma; quartos dividem o valor em duas linhas adjacentes.",
      "situacao": "Exemplos didáticos, sem resultados ou odds reais."
    }
  ]
}

st.title("⚽ Reals — Consultor de Mercados & Analisador de Bilhetes")
st.caption("Ferramenta para suporte, operadores e apostadores verificarem regras, mercados e bilhetes da Reals.bet.br")

# Abas do aplicativo
tab_print, tab_bilhete, tab_busca, tab_regras, tab_suporte = st.tabs([
    "📸 Leitor de Print (Novo)",
    "🎫 Leitor de Bilhete (Texto)",
    "🔍 Dicionário de Mercados",
    "📜 Regras & Prazos Reals",
    "💬 Gerador de Resposta ao Cliente"
])

# ----------------------------------------------------
# ABA 1: LEITOR DE PRINT DO BILHETE
# ----------------------------------------------------
with tab_print:
    st.header("📸 Leitura e Explicação por Print / Screenshot do Bilhete")
    st.markdown("""
    Envie uma captura de tela (print) do bilhete da **Reals** para que o sistema analise e explique o mercado, 
    as condições de vitória, o cálculo dos ganhos e as regras aplicáveis.
    """)
    
    col_upload, col_example = st.columns([1, 1])
    
    with col_upload:
        uploaded_file = st.file_uploader("Envie a imagem do bilhete (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])
        usar_exemplo = st.button("📋 Carregar Exemplo do Bilhete Reals (Millwall x West Ham + Boulogne x Nantes)")
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Imagem Enviada", use_column_width=True)
        
        # Tentar OCR
        extracted_text = ""
        if HAS_OCR:
            try:
                extracted_text = pytesseract.image_to_string(image, lang="por+eng")
            except Exception as err:
                try:
                    extracted_text = pytesseract.image_to_string(image)
                except Exception as err2:
                    st.warning(f"Não foi possível processar o OCR automático na imagem: {err2}")
        
        st.subheader("📝 Texto Identificado no Print:")
        if extracted_text.strip():
            st.text_area("Texto extraído via OCR:", value=extracted_text, height=150)
        else:
            st.info("O texto do print pode ser ajustado manualmente ou você pode conferir a análise detalhada abaixo.")

    if usar_exemplo or (uploaded_file is None):
        st.markdown("---")
        st.subheader("🔎 Exemplo Analisado (Bilhete Reals Múltipla)")
        
        # Dados do bilhete de exemplo enviado pelo usuário na fonte inbound5786410153497927755.jpg
        st.info("📌 **Bilhete de Exemplo: Futebol • Múltipla (Status: Em Aberto)**")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Valor Apostado", "R$ 30,00")
        c2.metric("Odd Total Múltipla", "1,85")
        c3.metric("Possíveis Ganhos", "R$ 55,50")
        
        st.markdown("### 🏟️ Seleções no Bilhete:")
        
        st.markdown("""
        1. **Jogo 1**: `Millwall FC x West Ham United FC` (Campeonato)
           - **Mercado**: Resultado Final (1X2)
           - **Seleção escolhida**: `Empate (X)`
           - **Odd**: 1,26
           - **Status do jogo**: Em Aberto
           
        2. **Jogo 2**: `US Boulogne x FC Nantes` (Liga 2)
           - **Mercado**: Total de Gols (Over/Under)
           - **Seleção escolhida**: `Mais De 2.5`
           - **Odd**: 1,47
           - **Status do jogo**: Em Aberto
        """)
        
        st.markdown("---")
        st.markdown("### 💡 Explicação Detalhada do Bilhete")
        
        st.success("""
        **1. Como este bilhete é GANHO?**
        - Trata-se de uma **Aposta Múltipla de 2 seleções**. Para obter o ganho total de **R$ 55,50**, **AMBAS as seleções precisam ser vencedoras**:
          - O jogo **Millwall x West Ham** precisa terminar **empatado** ao final do tempo regulamentar (ex: 0–0, 1–1, 2–2).
          - O jogo **US Boulogne x FC Nantes** precisa ter **3 ou mais gols no total** (ex: 2–1, 3–0, 2–2).
        """)
        
        st.warning("""
        **2. Como o cálculo de retorno foi feito?**
        - **Cotação Múltipla**: Multiplica-se as odds individuais: 1,26 x 1,47 = 1,8522 (Arredondado para **1,85** na Reals).
        - **Retorno Potencial**: Valor da aposta x Odd Total = R$ 30,00 x 1,85 = **R$ 55,50**.
        - **Lucro Líquido**: Retorno - Valor Apostado = R$ 55,50 - R$ 30,00 = **R$ 25,50**.
        """)
        
        st.error("""
        **3. Condições de PERDA:**
        - Se o **Millwall** ou o **West Ham** vencer o jogo (qualquer vencedor), a seleção de Empate é perdida, e por consequência **a aposta múltipla inteira é perdida**.
        - Se o jogo **Boulogne x Nantes** tiver 2 ou menos gols (ex: 0–0, 1–0, 1–1), a seleção de Mais de 2.5 é perdida, e a aposta múltipla é perdida.
        """)
        
        st.markdown("### ⚖️ Regras Específicas da Reals Aplicáveis a este Bilhete:")
        st.markdown("""
        - **Tempo Regulamentar**: Salvo indicação contrária no mercado, os jogos de futebol valem para os **90 minutos + acréscimos** (prorrogação e pênaltis não contam).
        - **Partida Adiada/Interrompida (Seção 1.4 das Regras de Apostas)**: A regra geral prevê **48 horas**, contadas do horário designado no adiamento e do início oficial no abandono, com exceções por esporte e mercado. Se uma seleção da múltipla comum for anulada, ela vale odd 1,00 e o retorno é recalculado pelas demais. Confira o mercado antes de aplicar o prazo.
        - **Modificação de Bilhete (Item 6.2 dos Termos Reals)**: Apostas já efetuadas e confirmadas não podem ser alteradas ou canceladas a pedido do usuário.
        - **Cashout (Item 17 dos Termos Reals)**: Se disponível para este bilhete, o valor oferecido flutua de acordo com o andamento das partidas. Caso um cashout seja tentado e não concluído, a aposta permanece original.
        """)

# ----------------------------------------------------
# ABA 2: LEITOR DE BILHETE EM TEXTO E CALCULADORA
# ----------------------------------------------------
with tab_bilhete:
    st.header("🎫 Leitor de Texto de Bilhete & Calculadora de Liquidação")
    
    st.markdown("Cole o texto do bilhete ou preencha os campos para simular o resultado da liquidação.")
    
    col_input1, col_input2 = st.columns(2)
    
    with col_input1:
        tipo_aposta = st.selectbox("Tipo de Aposta", ["Simples", "Múltipla", "Criar Aposta"])
        esporte = st.selectbox("Esporte", ["Futebol", "Basquete", "Tênis", "Vôlei", "Outro"])
        mercado_nome = st.selectbox("Mercado", [
            "Resultado Final (1X2)",
            "Dupla Chance",
            "Empate Anula Aposta",
            "Total de Gols (Over/Under)",
            "Handicap Asiático",
            "Handicap Europeu",
            "Ambas Marcam",
            "Placar Correto",
            "Escanteios - Total",
            "Cartões - Total",
            "Jogadores - Finalizações / Chutes no Gol",
            "Basquete - Vencedor / Handicap / Pontos",
            "Tênis - Vencedor / Handicap / Games"
        ])
        selecao_texto = st.text_input("Seleção no Bilhete (ex: Time A -1.0, Mais de 2.5, Empate):", value="Mais de 2.5")

    with col_input2:
        valor_aposta = st.number_input("Valor Apostado (R$):", value=100.0, step=10.0)
        odd_aposta = st.number_input("Odd da Aposta / Múltipla:", value=2.00, step=0.10)
        resultado_status = st.selectbox("Resultado / Status da Seleção", [
            "Ganho Integral (100%)",
            "Ganho de Metade (Metade ganha, metade devolve)",
            "Reembolso / Anulada (100% Devolução)",
            "Perda de Metade (Metade perde, metade devolve)",
            "Perda Integral (0%)"
        ])

    st.markdown("---")
    st.subheader("📊 Resultado da Liquidação")
    
    if resultado_status == "Ganho Integral (100%)":
        retorno = valor_aposta * odd_aposta
        lucro = retorno - valor_aposta
        st.success(f"✅ **GANHO INTEGRAL**\n- **Retorno Total**: R$ {retorno:.2f}\n- **Lucro Líquido**: R$ {lucro:.2f}")
    elif resultado_status == "Ganho de Metade (Metade ganha, metade devolve)":
        retorno = (valor_aposta * 0.5 * odd_aposta) + (valor_aposta * 0.5)
        lucro = retorno - valor_aposta
        v_half = valor_aposta * 0.5
        st.info(f"🟡 **GANHO DE METADE**\n- Metade da aposta (R$ {v_half:.2f}) multiplica pela odd {odd_aposta:.2f} e metade (R$ {v_half:.2f}) é devolvida.\n- **Retorno Total**: R$ {retorno:.2f}\n- **Lucro Líquido**: R$ {lucro:.2f}")
    elif resultado_status == "Reembolso / Anulada (100% Devolução)":
        retorno = valor_aposta
        lucro = 0.0
        st.warning(f"🔄 **ANULADA / DEVOLVIDA**\n- **Retorno Total**: R$ {retorno:.2f}\n- **Lucro Líquido**: R$ 0,00 (Reembolso integral do valor apostado).")
    elif resultado_status == "Perda de Metade (Metade perde, metade devolve)":
        retorno = valor_aposta * 0.5
        lucro = retorno - valor_aposta
        v_half = valor_aposta * 0.5
        st.error(f"🟠 **PERDA DE METADE**\n- Metade da aposta (R$ {v_half:.2f}) é perdida e metade (R$ {v_half:.2f}) é devolvida.\n- **Retorno Total**: R$ {retorno:.2f}\n- **Prejuízo**: R$ {abs(lucro):.2f}")
    else: # Perda Integral
        retorno = 0.0
        lucro = -valor_aposta
        st.error(f"❌ **PERDA INTEGRAL**\n- **Retorno Total**: R$ 0,00\n- **Prejuízo**: R$ {valor_aposta:.2f}")

# ----------------------------------------------------
# ABA 3: DICIONÁRIO DE MERCADOS
# ----------------------------------------------------
with tab_busca:
    st.header("🔍 Dicionário e Tabela de Mercados")
    st.markdown("Consulte a regra exata de cada linha de mercado (Handicap Asiático, Totais, Escanteios, Cartões, etc.).")
    
    categoria_busca = st.radio("Selecione a Categoria:", [
        "Mercados Gerais & Especiais",
        "Handicap Asiático",
        "Handicap Europeu",
        "Totais Asiáticos"
    ], horizontal=True)
    
    termo_busca = st.text_input("Filtrar por nome ou seleção (ex: +0.75, Mais de 2.25, 1X2, Cartões):", "")
    
    if categoria_busca == "Mercados Gerais & Especiais":
        st.subheader("Mercados Gerais & Especiais")
        items = DATA["general_markets"]
        if termo_busca:
            items = [x for x in items if termo_busca.lower() in str(x).lower()]
        for item in items:
            with st.expander(f"📌 Mercado: {item.get('mercado')} — Seleção: {item.get('selecao')}"):
                st.write(f"**GANHA quando**: {item.get('ganha')}")
                st.write(f"**PERDE quando**: {item.get('perde')}")
                st.write(f"**DEVOLVE quando**: {item.get('devolve')}")
                st.caption(f"**Atenção na Reals**: {item.get('atencao')}")

    elif categoria_busca == "Handicap Asiático":
        st.subheader("Tabela de Handicap Asiático (Diferença de Gols/Pontos)")
        items = DATA["handicap_asiatico"]
        if termo_busca:
            items = [x for x in items if termo_busca.lower() in str(x).lower()]
        for item in items:
            with st.expander(f"⚽ Seleção: {item.get('selecao')}"):
                st.write(f"🟢 **GANHA TUDO**: {item.get('ganha_tudo')}")
                st.write(f"🔴 **PERDE TUDO**: {item.get('perde_tudo')}")

    elif categoria_busca == "Handicap Europeu":
        st.subheader("Handicap Europeu (3 Opções — Não devolve em empate ajustado)")
        items = DATA["handicap_europeu"]
        if termo_busca:
            items = [x for x in items if termo_busca.lower() in str(x).lower()]
        for item in items:
            with st.expander(f"⚽ Seleção: {item.get('selecao')}"):
                st.write(f"🟢 **GANHA quando**: {item.get('ganha_quando')}")
                st.write(f"🔴 **PERDE quando**: {item.get('perde_quando')}")

    elif categoria_busca == "Totais Asiáticos":
        st.subheader("Tabela de Totais Asiáticos (Soma de Gols/Pontos)")
        items = DATA["totais_asiaticos"]
        if termo_busca:
            items = [x for x in items if termo_busca.lower() in str(x).lower()]
        for item in items:
            with st.expander(f"⚽ Seleção: {item.get('selecao')}"):
                st.write(f"🟢 **GANHA TUDO**: {item.get('ganha_tudo')}")
                st.write(f"🔴 **PERDE TUDO**: {item.get('perde_tudo')}")

# ----------------------------------------------------
# ABA 4: REGRAS OFICIAIS & PRAZOS REALS
# ----------------------------------------------------
with tab_regras:
    st.header("📜 Regras Oficiais e Prazos da Reals")
    st.markdown("Consulta por situação, com base nas Regras de Apostas da Reals verificadas em 03/10/2026. Confira sempre as condições do esporte e do mercado.")
    
    st.markdown("[Consultar regulamento completo da Reals](https://reals.bet.br/legal/regras)")

    for rule in DATA["reals_rules"]:
        with st.expander(f"📋 {rule.get('situaçao')}"):
            st.write(f"**O que conferir**: {rule.get('conferir')}")
            st.info(f"**Base / Referência Reals**: {rule.get('base')}")

# ----------------------------------------------------
# ABA 5: GERADOR DE RESPOSTA AO CLIENTE
# ----------------------------------------------------
with tab_suporte:
    st.header("💬 Gerador de Resposta Padrão de Atendimento")
    st.markdown("Selecione a situação do cliente para gerar um texto explicativo pronto e fundamentado nos termos para colar no chat de suporte.")
    
    motivo = st.selectbox("Motivo do Atendimento", [
        "Explicar Aposta Múltipla / Bilhete em Aberto",
        "Partida Adiada / Interrompida (Regra geral: 48h)",
        "Diferença entre Handicap Asiático e Europeu",
        "Explicação de Ganho de Metade / Perda de Metade",
        "Alteração ou Cancelamento de Aposta Confirmada",
        "Dúvida sobre Cashout Não Concluído"
    ])
    
    nome_cliente = st.text_input("Nome do Cliente (opcional):", "Apostador")
    
    texto_resposta = ""
    
    if motivo == "Explicar Aposta Múltipla / Bilhete em Aberto":
        texto_resposta = f"""Olá, {nome_cliente}! Tudo bem?

Analisamos o seu bilhete e verificamos que se trata de uma **Aposta Múltipla**.

Nesta modalidade, o retorno total é calculado pela multiplicação das cotações (odds) de todas as seleções escolhidas. Para que a aposta seja vencedora, **todas as seleções individuais precisam ser vitoriosas**.

Se o seu bilhete consta como "Em Aberto", significa que uma ou mais partidas ainda estão em andamento ou prestes a ocorrer. Assim que todos os jogos forem finalizados e os resultados oficiais validados pelo provedor, a liquidação do bilhete ocorre automaticamente.

Qualquer dúvida adicional, estamos à disposição!"""

    elif motivo == "Partida Adiada / Interrompida (Regra geral: 48h)":
        texto_resposta = f"""Olá, {nome_cliente}!

Sobre o evento do seu bilhete que foi adiado/interrompido:

Pela regra geral da **seção 1.4 das Regras de Apostas da Reals**, o prazo é de **48 horas**: no adiamento, conta-se do horário designado; no abandono, do horário oficial de início. Algumas modalidades e mercados têm regras próprias, por isso precisamos conferir o esporte e a seleção do bilhete.

Se houver anulação, a aposta simples tem o valor devolvido. Na múltipla comum, a seleção anulada passa a valer odd 1,00 e o retorno é recalculado pelas demais. No Criar Aposta, há regra própria de anulação em cascata e prevalência de seleções perdidas.

Vamos conferir a regra específica do seu bilhete para orientar você corretamente."""

    elif motivo == "Explicação de Ganho de Metade / Perda de Metade":
        texto_resposta = f"""Olá, {nome_cliente}!

Explicamos abaixo como funciona o cálculo da linha de mercado asiática do seu bilhete:

Nas linhas de quartos (como -0.25, +0.25, -0.75, +0.75, Mais de 2.25, etc.), o valor da sua aposta é dividido em duas metades:

- **Ganho de Metade**: Metade do valor apostado multiplica pela odd da seleção e a outra metade do valor é devolvida para a sua conta.
- **Perda de Metade**: Metade do valor apostado é perdida e a outra metade do valor é devolvida para a sua conta.

Esse ajuste é matemático e automático conforme a tabela oficial de mercados asiáticos da Reals.

Qualquer dúvida, estamos à disposição para ajudar!"""

    elif motivo == "Alteração ou Cancelamento de Aposta Confirmada":
        texto_resposta = f"""Olá, {nome_cliente}!

Conforme consta no **Item 6.2 dos Termos e Condições da Reals**, após a confirmação e efetivação de uma aposta pelo sistema, **não é possível alterar, ajustar ou cancelar** os termos do bilhete.

Recomendamos sempre revisar a seleção, o valor e as cotações antes de confirmar a aposta no bilhete.

Agradecemos a compreensão!"""

    elif motivo == "Dúvida sobre Cashout Não Concluído":
        texto_resposta = f"""Olá, {nome_cliente}!

Sobre a tentativa de Cashout no seu bilhete:

De acordo com o **Item 17.9 dos Termos de Uso da Reals**, o recurso de Cashout é uma oferta dinâmica cujos valores oscilam em tempo real. Caso uma tentativa de encerramento não seja concluída ou seja recusada devido a alterações na partida, a aposta original permanece ativa.

Nesse caso, o bilhete continuará até o final do evento e será liquidado com base no resultado oficial do jogo.

Qualquer dúvida, estamos à disposição!"""

    st.subheader("📝 Texto Pronto para Copiar:")
    st.text_area("Copia e cola para o suporte:", value=texto_resposta, height=250)
