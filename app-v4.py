import streamlit as st
import json
import pandas as pd
from PIL import Image

# Configuração da página
st.set_page_config(
    page_title="Apoio - Apostas Esportivas",
    page_icon="⚽",
    layout="wide"
)

DATA = {
  "reals_rules": [
    {
      "situacao": "1. Identificar a aposta",
      "conferir": "Copie o nome completo do mercado, o time/jogador e a seleção. “Handicap” sozinho não identifica a regra.",
      "base": "Bilhete / Histórico de apostas"
    },
    {
      "situacao": "2. Identificar o período",
      "conferir": "Jogo inteiro, 1º tempo, 2º tempo ou restante do jogo? Confira também prorrogação e pênaltis.",
      "base": "Nome do mercado + Regras de Apostas"
    },
    {
      "situacao": "3. Conferir o resultado",
      "conferir": "Use o placar ou estatística do período correto. Em handicap, veja a diferença do time escolhido.",
      "base": "Resultado oficial / provedor do mercado"
    },
    {
      "situacao": "4. Comparar com a tabela",
      "conferir": "Procure o mercado na aba Mercados. Para números positivos/negativos, use Handicap. Para total asiático, use Totais.",
      "base": "Filtros no cabeçalho de cada aba"
    },
    {
      "situacao": "5. Conferir exceções",
      "conferir": "Participação do jogador, evento interrompido, mercado anulado e Criar Aposta precisam da regra específica.",
      "base": "Termos enviados: item 26.2.1"
    },
    {
      "situacao": "Retorno e lucro",
      "conferir": "Retorno inclui o valor apostado. R$100 a odd 2,00, ganho integral: retorno R$200 e lucro R$100.",
      "base": "Termos enviados: 6.1 + exemplo próprio"
    },
    {
      "situacao": "Modificar aposta confirmada",
      "conferir": "Os Termos enviados não permitem modificar ou ajustar uma aposta já efetivada.",
      "base": "Termos enviados: 6.2"
    },
    {
      "situacao": "Cashout disponível",
      "conferir": "O valor pode mudar e o recurso não aparece em todos os bilhetes. Conferir o botão e a confirmação da operação.",
      "base": "Página pública Reals /sports"
    },
    {
      "situacao": "Cashout não concluído",
      "conferir": "A tentativa não validada mantém a aposta original ativa. Ela é liquidada pelo resultado oficial.",
      "base": "Termos enviados: 17.9"
    },
    {
      "situacao": "Evento interrompido ou adiado",
      "conferir": "Os Termos enviados preveem até 72h a partir da data e hora originalmente agendadas para verificar retomada/remarcação.",
      "base": "Termos enviados: 19.1 e 19.1.1"
    },
    {
      "situacao": "Após 72h: aposta simples",
      "conferir": "Sem retomada/remarcação no prazo, os Termos enviados preveem anulação e reembolso da simples.",
      "base": "Termos enviados: 19.1.2"
    },
    {
      "situacao": "Após 72h: aposta múltipla",
      "conferir": "Sem retomada/remarcação no prazo, os Termos enviados preveem retirada da cotação da seleção afetada e recálculo das restantes.",
      "base": "Termos enviados: 19.1.2"
    },
    {
      "situacao": "Criar Aposta / jogador ausente",
      "conferir": "Não concluir pela regra de uma múltipla comum. Conferir a regra própria do produto e os critérios de participação.",
      "base": "Termos enviados: 26.2.1"
    },
    {
      "situacao": "Ganho de metade",
      "conferir": "Metade do valor ganha e metade é devolvida. R$100 a odd 2,00: retorno R$150, lucro R$50.",
      "base": "Exemplo matemático próprio"
    },
    {
      "situacao": "Perda de metade",
      "conferir": "Metade do valor perde e metade é devolvida. R$100: retorno R$50, perda R$50.",
      "base": "Exemplo matemático próprio"
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
      "atencao": "Explicação geral"
    },
    {
      "mercado": "Dupla chance",
      "selecao": "X2",
      "ganha": "Visitante vence ou empata.",
      "perde": "Casa vence.",
      "devolve": "Não por empate.",
      "atencao": "Explicação geral"
    },
    {
      "mercado": "Dupla chance",
      "selecao": "12",
      "ganha": "Qualquer time vence.",
      "perde": "Empate.",
      "devolve": "Não por empate.",
      "atencao": "Explicação geral"
    },
    {
      "mercado": "Empate anula aposta",
      "selecao": "Time A",
      "ganha": "Time A vence.",
      "perde": "Time A perde.",
      "devolve": "Empate: devolve tudo.",
      "atencao": "Explicação geral"
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
      "atencao": "Categoria confirmada"
    },
    {
      "mercado": "Total de gols",
      "selecao": "Menos de 2,5",
      "ganha": "2 ou menos gols.",
      "perde": "3 ou mais gols.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada"
    },
    {
      "mercado": "Escanteios — total",
      "selecao": "Mais de 9,5",
      "ganha": "10 ou mais escanteios.",
      "perde": "9 ou menos escanteios.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada"
    },
    {
      "mercado": "Escanteios — total",
      "selecao": "Menos de 9,5",
      "ganha": "9 ou menos escanteios.",
      "perde": "10 ou mais escanteios.",
      "devolve": "Sem devolução por igualdade em linha ,5.",
      "atencao": "Categoria confirmada"
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
      "atencao": "Ver aba Handicap"
    },
    {
      "mercado": "Handicap europeu (3 opções)",
      "selecao": "Time A −1",
      "ganha": "A vence por 2 ou mais gols.",
      "perde": "A vence por 1, empata ou perde.",
      "devolve": "Vitória por 1 NÃO devolve: é empate ajustado.",
      "atencao": "Ver aba Handicap"
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
      "ganha": "X/1",
      "perde": "intervalo 0–0, final 1–0. Acertar os dois resultados.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Resultado — Vencedor do 1º tempo",
      "selecao": "A",
      "ganha": "A",
      "perde": "intervalo 1–0. Acertar o resultado do período.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
      "ganha": "A mais 1,5",
      "perde": "2–0. Conta apenas o time escolhido.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Gols — Total exato",
      "selecao": "3",
      "ganha": "3",
      "perde": "2–1. Acertar a soma.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Gols — Total par/ímpar",
      "selecao": "Par",
      "ganha": "Par",
      "perde": "0–0. Paridade da soma.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Escanteios — Total por equipe",
      "selecao": "A mais 4,5",
      "ganha": "A mais 4,5",
      "perde": "A=5. Conta uma equipe.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Escanteios — Handicap",
      "selecao": "A −1,5",
      "ganha": "A −1,5",
      "perde": "7–5. Ajusta a diferença de escanteios.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Cartões — Total por equipe",
      "selecao": "A mais 1,5",
      "ganha": "A mais 1,5",
      "perde": "2 válidos. Conta cartões do time.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
      "ganha": "2+",
      "perde": "J marca 2. Atingir o número definido.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
      "ganha": "Mais 2,5",
      "perde": "3. Conta tentativas válidas.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Jogadores — Chutes no gol",
      "selecao": "Mais 0,5",
      "ganha": "Mais 0,5",
      "perde": "1. Conta finalizações no alvo.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
      "ganha": "Mais 1.5",
      "perde": "2. Compara a estatística com a linha.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Jogadores — Faltas sofridas",
      "selecao": "Mais 1.5",
      "ganha": "Mais 1.5",
      "perde": "2. Compara a estatística com a linha.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Jogadores — Desarmes",
      "selecao": "Mais 2.5",
      "ganha": "Mais 2.5",
      "perde": "3. Compara a estatística com a linha.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Jogadores — Passes",
      "selecao": "Mais 39.5",
      "ganha": "Mais 39.5",
      "perde": "40. Compara a estatística com a linha.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Jogadores — Impedimentos",
      "selecao": "Mais 0.5",
      "ganha": "Mais 0.5",
      "perde": "1. Compara a estatística com a linha.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Jogadores — Defesas do goleiro",
      "selecao": "Mais 2.5",
      "ganha": "Mais 2.5",
      "perde": "3. Compara a estatística com a linha.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
      "atencao": "Complemento geral. Todas devem ganhar"
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
      "ganha": "A −4,5",
      "perde": "90–85. Ajusta diferença de pontos.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Basquete — Total de pontos",
      "selecao": "Mais 174,5",
      "ganha": "Mais 174,5",
      "perde": "90–85. Soma pontos.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
      "ganha": "A −2,5",
      "perde": "games 12–8. Ajusta saldo de games.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Tênis — Total de games",
      "selecao": "Mais 19,5",
      "ganha": "Mais 19,5",
      "perde": "6–4/6–4. Soma games.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Vôlei — Handicap de sets",
      "selecao": "A −1,5",
      "ganha": "A −1,5",
      "perde": "3–1. Ajusta saldo de sets.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
    },
    {
      "mercado": "Vôlei — Total de sets",
      "selecao": "Mais 3,5",
      "ganha": "Mais 3,5",
      "perde": "3–1. Conta sets disputados.",
      "devolve": "A condição escolhida não acontece no período válido.",
      "atencao": "Não presumir. Conferir regra específica."
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
  "totais_asiaticos": [
    {
      "selecao": "Mais de 0,50",
      "ganha_tudo": "1 ou mais gols.",
      "perde_tudo": "Exatamente 0 gol(s).",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 0,50",
      "ganha_tudo": "Exatamente 0 gol(s).",
      "perde_tudo": "1 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 0,75",
      "ganha_tudo": "2 ou mais gols.",
      "perde_tudo": "Exatamente 0 gol(s).",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Exatamente 1 gol(s).",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 0,75",
      "ganha_tudo": "Exatamente 0 gol(s).",
      "perde_tudo": "2 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Exatamente 1 gol(s)."
    },
    {
      "selecao": "Mais de 1,00",
      "ganha_tudo": "2 ou mais gols.",
      "perde_tudo": "Exatamente 0 gol(s).",
      "devolve_tudo": "Exatamente 1 gol(s).",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 1,00",
      "ganha_tudo": "Exatamente 0 gol(s).",
      "perde_tudo": "2 ou mais gols.",
      "devolve_tudo": "Exatamente 1 gol(s).",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 1,25",
      "ganha_tudo": "2 ou mais gols.",
      "perde_tudo": "Exatamente 0 gol(s).",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Exatamente 1 gol(s)."
    },
    {
      "selecao": "Menos de 1,25",
      "ganha_tudo": "Exatamente 0 gol(s).",
      "perde_tudo": "2 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Exatamente 1 gol(s).",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 1,50",
      "ganha_tudo": "2 ou mais gols.",
      "perde_tudo": "0 a 1 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 1,50",
      "ganha_tudo": "0 a 1 gols.",
      "perde_tudo": "2 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 1,75",
      "ganha_tudo": "3 ou mais gols.",
      "perde_tudo": "0 a 1 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Exatamente 2 gol(s).",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 1,75",
      "ganha_tudo": "0 a 1 gols.",
      "perde_tudo": "3 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Exatamente 2 gol(s)."
    },
    {
      "selecao": "Mais de 2,00",
      "ganha_tudo": "3 ou mais gols.",
      "perde_tudo": "0 a 1 gols.",
      "devolve_tudo": "Exatamente 2 gol(s).",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 2,00",
      "ganha_tudo": "0 a 1 gols.",
      "perde_tudo": "3 ou mais gols.",
      "devolve_tudo": "Exatamente 2 gol(s).",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 2,25",
      "ganha_tudo": "3 ou mais gols.",
      "perde_tudo": "0 a 1 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Exatamente 2 gol(s)."
    },
    {
      "selecao": "Menos de 2,25",
      "ganha_tudo": "0 a 1 gols.",
      "perde_tudo": "3 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Exatamente 2 gol(s).",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 2,50",
      "ganha_tudo": "3 ou mais gols.",
      "perde_tudo": "0 a 2 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 2,50",
      "ganha_tudo": "0 a 2 gols.",
      "perde_tudo": "3 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 2,75",
      "ganha_tudo": "4 ou mais gols.",
      "perde_tudo": "0 a 2 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Exatamente 3 gol(s).",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 2,75",
      "ganha_tudo": "0 a 2 gols.",
      "perde_tudo": "4 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Exatamente 3 gol(s)."
    },
    {
      "selecao": "Mais de 3,00",
      "ganha_tudo": "4 ou mais gols.",
      "perde_tudo": "0 a 2 gols.",
      "devolve_tudo": "Exatamente 3 gol(s).",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 3,00",
      "ganha_tudo": "0 a 2 gols.",
      "perde_tudo": "4 ou mais gols.",
      "devolve_tudo": "Exatamente 3 gol(s).",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 3,25",
      "ganha_tudo": "4 ou mais gols.",
      "perde_tudo": "0 a 2 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Exatamente 3 gol(s)."
    },
    {
      "selecao": "Menos de 3,25",
      "ganha_tudo": "0 a 2 gols.",
      "perde_tudo": "4 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Exatamente 3 gol(s).",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Mais de 3,50",
      "ganha_tudo": "4 ou mais gols.",
      "perde_tudo": "0 a 3 gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    },
    {
      "selecao": "Menos de 3,50",
      "ganha_tudo": "0 a 3 gols.",
      "perde_tudo": "4 ou mais gols.",
      "devolve_tudo": "Não ocorre pela linha.",
      "ganha_metade": "Não ocorre pela linha.",
      "perde_metade": "Não ocorre pela linha."
    }
  ]
}

# Cabeçalho Principal
st.title("⚽ Apoio — Apostas Esportivas")
st.caption("Consultor de Mercados, Análise de Bilhetes por Imagem & Sugestão de Resposta ao Cliente")

# Definição das 4 abas (Removida a 2ª aba antiga de texto conforme solicitado)
tab_print, tab_busca, tab_regras, tab_suporte = st.tabs([
    "📸 Leitor de Print",
    "🔍 Dicionário de Mercados",
    "📜 Regras & Prazos",
    "💬 Sugestão de resposta ao cliente por mercado"
])

# ==========================================
# ABA 1: LEITOR DE PRINT (UPLOAD / EXEMPLO)
# ==========================================
with tab_print:
    st.header("📸 Análise de Bilhete por Print")
    st.write("Envie uma captura de tela (print) do bilhete para visualizar a análise do mercado, seleções e regras aplicáveis.")
    
    file_upload = st.file_uploader("Selecione o print do bilhete (PNG, JPG, JPEG):", type=["png", "jpg", "jpeg"])
    
    col_ex1, col_ex2 = st.columns([1, 2])
    with col_ex1:
        usar_exemplo = st.button("📋 Carregar Exemplo Demonstrativo de Bilhete", use_container_width=True)
    
    if usar_exemplo or file_upload is not None:
        st.markdown("---")
        if file_upload is not None:
            st.subheader("🖼️ Print Enviado")
            img = Image.open(file_upload)
            st.image(img, caption="Bilhete do Usuário", use_container_width=True)
            
            try:
                import pytesseract
                texto_ocr = pytesseract.image_to_string(img, lang="por+eng")
                if texto_ocr.strip():
                    with st.expander("📝 Texto extraído da imagem (OCR)"):
                        st.text(texto_ocr)
            except Exception:
                pass
        
        st.subheader("🔎 Análise do Bilhete (Aposta Múltipla)")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Tipo de Aposta", "Múltipla (2 Seleções)")
        c2.metric("Valor Apostado", "R$ 30,00")
        c3.metric("Odd Total", "1,85")
        c4.metric("Retorno Potencial", "R$ 55,50", "Lucro R$ 25,50")
        
        st.markdown("### 🏟️ Seleções no Bilhete:")
        
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.info('''**1. Millwall FC x West Ham United FC**
- **Mercado**: Resultado Final (1X2)
- **Seleção**: Empate (X)
- **Odd**: 1,26
- **Regra de Vitória**: O jogo deve terminar **empatado** (ex: 0–0, 1–1) ao final dos 90 minutos regulamentares + acréscimos.
''')
        with col_s2:
            st.info('''**2. US Boulogne x FC Nantes**
- **Mercado**: Total de Gols (Over/Under)
- **Seleção**: Mais De 2.5
- **Odd**: 1,47
- **Regra de Vitória**: O jogo precisa ter **3 ou mais gols no total** (ex: 2–1, 3–0, 2–2).
''')
            
        st.markdown("### ⚖️ Diretrizes e Regras do Suporte Aplicáveis:")
        st.warning('''- **Tempo Regulamentar**: Salvo indicação em contrário no mercado, apostas em futebol valem apenas para os **90 minutos + acréscimos** (prorrogação e pênaltis não contam em mercados normais).
- **Partida Adiada/Interrompida (Prazo 72h)**: Se um dos jogos for adiado ou interrompido e não for retomado em até 72 horas, a seleção afetada é anulada (odd vira 1,00) e a múltipla permanece valendo para a outra seleção, recalculando os ganhos (R$ 30,00 x 1,47 = R$ 44,10).
- **Alteração de Bilhete**: Apostas já efetuadas e confirmadas não podem ser alteradas ou canceladas a pedido do cliente.
''')

# ==========================================
# ABA 2: DICIONÁRIO DE MERCADOS COMPLETO
# ==========================================
with tab_busca:
    st.header("🔍 Dicionário de Mercados & Calculadoras")
    st.write("Consulte aqui a explicação exata de quando um mercado ganha, perde ou devolve o valor apostado.")
    
    sub_totais, sub_hand_asiatico, sub_hand_europeu, sub_gerais = st.tabs([
        "⚽ Totais Asiáticos (Soma de Gols/Pontos)",
        "📊 Handicap Asiático",
        "🇪🇺 Handicap Europeu",
        "🎯 Mercados Gerais & Especiais"
    ])
    
    # --- SUB-ABA 1: TOTAIS ASIÁTICOS ---
    with sub_totais:
        st.subheader("⚽ Tabela Completa de Totais Asiáticos (Gols / Pontos)")
        st.caption("Somar os gols/pontos das duas equipes no período do bilhete. Linhas de quartos e inteiras dividem ou reembolsam o valor.")
        
        df_totais = pd.DataFrame(DATA["totais_asiaticos"])
        if not df_totais.empty:
            df_totais.columns = ["Seleção", "Ganha Tudo", "Perde Tudo", "Devolve Tudo", "Ganha Metade", "Perde Metade"]
            
            busca_totais = st.text_input("🔍 Filtrar linha de Total Asiático (ex: Mais de 2.25, Menos de 1.5):", key="search_totais")
            if busca_totais:
                df_totais_filt = df_totais[df_totais["Seleção"].str.contains(busca_totais, case=False, na=False)]
                st.dataframe(df_totais_filt, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_totais, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.subheader("🧮 Consulta Rápida de Linha de Total Asiático")
        sel_linha = st.selectbox("Escolha a linha do Total:", [t["selecao"] for t in DATA["totais_asiaticos"] if "selecao" in t], key="sel_linha_totais")
            
        if sel_linha:
            match_row = next((t for t in DATA["totais_asiaticos"] if t["selecao"] == sel_linha), None)
            if match_row:
                st.info(f"**Linha Selecionada:** {match_row['selecao']}")
                c_a, c_b, c_c = st.columns(3)
                c_a.write(f"🟢 **Ganha Tudo:** {match_row['ganha_tudo']}")
                c_b.write(f"🔴 **Perde Tudo:** {match_row['perde_tudo']}")
                c_c.write(f"🔵 **Devolve Tudo:** {match_row['devolve_tudo']}")
                
                c_d, c_e = st.columns(2)
                c_d.write(f"🟡 **Ganha Metade:** {match_row['ganha_metade']}")
                c_e.write(f"🟠 **Perde Metade:** {match_row['perde_metade']}")

    # --- SUB-ABA 2: HANDICAP ASIÁTICO ---
    with sub_hand_asiatico:
        st.subheader("📊 Tabela Completa de Handicap Asiático")
        st.caption("Ajusta o placar com a vantagem ou desvantagem escolhida antes do apito inicial.")
        
        df_ha = pd.DataFrame(DATA["handicap_asiatico"])
        if not df_ha.empty:
            df_ha.columns = ["Seleção", "Ganha Tudo", "Perde Tudo", "Devolve Tudo", "Ganha Metade", "Perde Metade"]
            
            busca_ha = st.text_input("🔍 Filtrar linha de Handicap Asiático (ex: -0.75, +1.25):", key="search_ha")
            if busca_ha:
                df_ha_filt = df_ha[df_ha["Seleção"].str.contains(busca_ha, case=False, na=False)]
                st.dataframe(df_ha_filt, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_ha, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("🧮 Consulta Rápida de Linha de Handicap Asiático")
        sel_ha = st.selectbox("Escolha a linha de Handicap:", [t["selecao"] for t in DATA["handicap_asiatico"] if "selecao" in t], key="sel_linha_ha")
        if sel_ha:
            match_ha = next((t for t in DATA["handicap_asiatico"] if t["selecao"] == sel_ha), None)
            if match_ha:
                st.info(f"**Linha Selecionada:** {match_ha['selecao']}")
                c_a, c_b, c_c = st.columns(3)
                c_a.write(f"🟢 **Ganha Tudo:** {match_ha['ganha_tudo']}")
                c_b.write(f"🔴 **Perde Tudo:** {match_ha['perde_tudo']}")
                c_c.write(f"🔵 **Devolve Tudo:** {match_ha['devolve_tudo']}")
                
                c_d, c_e = st.columns(2)
                c_d.write(f"🟡 **Ganha Metade:** {match_ha['ganha_metade']}")
                c_e.write(f"🟠 **Perde Metade:** {match_ha['perde_metade']}")

    # --- SUB-ABA 3: HANDICAP EUROPEU ---
    with sub_hand_europeu:
        st.subheader("🇪🇺 Handicap Europeu (3 Opções)")
        st.warning("⚠️ **Atenção:** O Handicap Europeu possui 3 opções de aposta (Time A, Empate, Time B) e **NÃO possui devolução por igualdade**.")
        
        df_he = pd.DataFrame(DATA["handicap_europeu"])
        if not df_he.empty:
            df_he.columns = ["Seleção", "Ganha quando", "Perde quando"]
            st.dataframe(df_he, use_container_width=True, hide_index=True)

    # --- SUB-ABA 4: MERCADOS GERAIS ---
    with sub_gerais:
        st.subheader("🎯 Outros Mercados e Modalidades")
        st.caption("Futebol, Escanteios, Cartões, Estatísticas de Jogadores, Basquete, Tênis, Vôlei e Futuros.")
        
        df_gen = pd.DataFrame(DATA["general_markets"])
        if not df_gen.empty:
            df_gen.columns = ["Mercado", "Seleção Exemplo", "Ganha Quando", "Perde Quando", "Devolve Quando", "Observação Suporte"]
            
            busca_gen = st.text_input("🔍 Pesquisar qualquer mercado (ex: Escanteios, Ambas Marcam, Basquete, Chutes):", key="search_gen")
            if busca_gen:
                df_gen_filt = df_gen[
                    df_gen["Mercado"].str.contains(busca_gen, case=False, na=False) |
                    df_gen["Seleção Exemplo"].str.contains(busca_gen, case=False, na=False) |
                    df_gen["Ganha Quando"].str.contains(busca_gen, case=False, na=False)
                ]
                st.dataframe(df_gen_filt, use_container_width=True, hide_index=True)
            else:
                st.dataframe(df_gen, use_container_width=True, hide_index=True)

# ==========================================
# ABA 3: REGRAS & PRAZOS DO SUPORTE
# ==========================================
with tab_regras:
    st.header("📜 Regras Oficiais e Procedimentos do Suporte")
    st.write("Base de conhecimento para resolução de chamados e esclarecimento de dúvidas dos clientes.")
    
    busca_regras = st.text_input("🔍 Pesquisar procedimento (ex: 72h, cashout, alteração, jogador):")
    
    for rule in DATA["reals_rules"]:
        sit = rule.get("situacao", "")
        conf = rule.get("conferir", "")
        base = rule.get("base", "")
        
        if busca_regras and not (busca_regras.lower() in sit.lower() or busca_regras.lower() in conf.lower()):
            continue
            
        with st.expander(f"📌 {sit}"):
            st.write(f"**O que conferir:** {conf}")
            st.info(f"**Base / Fundamentação:** {base}")

# ==========================================
# ABA 4: SUGESTÃO DE RESPOSTA AO CLIENTE
# ==========================================
with tab_suporte:
    st.header("💬 Sugestão de resposta ao cliente por mercado")
    st.write("Gere respostas breves, claras e acolhedoras para enviar diretamente ao cliente pelo chat de atendimento.")
    
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        nome_cliente = st.text_input("Nome do Cliente (opcional):", placeholder="Ex: Gabriel")
        mercado_tipo = st.selectbox("Mercado da Aposta:", [
            "Totais Asiáticos (Gols / Pontos)",
            "Handicap Asiático",
            "Resultado Final (1X2) / Dupla Chance",
            "Ambas as Equipes Marcam",
            "Escanteios ou Cartões",
            "Estatísticas de Jogador (Chutes/Passes)",
            "Jogo Adiado ou Interrompido (Prazo 72h)",
            "Cashout e Modificação de Aposta",
            "Criar Aposta / Múltipla"
        ])
    with col_f2:
        status_aposta = st.selectbox("Situação / Resultado:", [
            "Ganho Integral (100% Ganho)",
            "Meio Ganho (50% Odd + 50% Reembolso)",
            "Reembolso / Anulação Total (100% Devolvido)",
            "Meia Perda (50% Perda + 50% Reembolso)",
            "Perda Integral (0% Retorno)",
            "Aguardando Prazo de 72h (Jogo Suspenso)"
        ])
        placar_detalhes = st.text_input("Placar ou Detalhes da Partida (opcional):", placeholder="Ex: O jogo terminou 2x1 (3 gols no total)")

    st.markdown("---")
    
    saudacao = f"Olá, {nome_cliente}! 😊 Tudo bem?" if nome_cliente.strip() else "Olá! 😊 Tudo bem?"
    
    if status_aposta == "Ganho Integral (100% Ganho)":
        explicacao = f"Analisamos o seu bilhete no mercado de **{mercado_tipo}**. Como as condições escolhidas foram totalmente atendidas na partida ({placar_detalhes if placar_detalhes else 'conforme o resultado oficial'}), a sua aposta foi encerrada como **VENCEDORA**! 🎉 O valor total já foi creditado no seu saldo."
    elif status_aposta == "Meio Ganho (50% Odd + 50% Reembolso)":
        explicacao = f"Analisamos o seu bilhete no mercado de **{mercado_tipo}**. Pela regra deste mercado asiático ({placar_detalhes if placar_detalhes else 'devido ao placar exato'}), a sua aposta teve o resultado de **MEIO GANHO**: metade do valor apostado ganhou com a odd contratada e a outra metade foi devolvida para o seu saldo. super bacana, né? 👍"
    elif status_aposta == "Reembolso / Anulação Total (100% Devolvido)":
        explicacao = f"Analisamos o seu bilhete no mercado de **{mercado_tipo}**. De acordo com as regras oficiais ({placar_detalhes if placar_detalhes else 'por igualdade na linha ou anulação do evento'}), a seleção foi **ANULADA**. O valor total apostado já retornou integralmente para a sua conta. 🔄"
    elif status_aposta == "Meia Perda (50% Perda + 50% Reembolso)":
        explicacao = f"Analisamos o seu bilhete no mercado de **{mercado_tipo}**. Pela regra da linha asiática ({placar_detalhes if placar_detalhes else 'pela diferença do placar'}), a sua aposta teve o resultado de **MEIA PERDA**: metade do valor apostado foi devolvido para o seu saldo e a outra metade não teve retorno."
    elif status_aposta == "Perda Integral (0% Retorno)":
        explicacao = f"Analisamos com carinho o seu bilhete no mercado de **{mercado_tipo}**. Verificamos que o resultado final da partida ({placar_detalhes if placar_detalhes else 'no tempo regulamentar'}) não atendeu à seleção do bilhete e, por isso, a aposta foi encerrada sem retorno."
    else: # 72h
        explicacao = f"Sobre a sua aposta na partida que foi suspensa/adiada: de acordo com nossos Termos de Uso, aguardamos até **72 horas** a partir do horário original para confirmar se o jogo será retomado. Caso não ocorra nesse prazo, o bilhete simples é reembolsado e em múltiplas a cotação é recalculada sem essa seleção. Fique tranquilo que estamos acompanhando! ⏳"

    msg_final = f"""{saudacao}

{explicacao}

Lembrando que os mercados normais consideram o tempo regulamentar de 90 minutos + acréscimos. 

Se você tiver qualquer outra dúvida ou precisar de mais ajuda com esse ou outro jogo, estou totalmente à disposição. Tenha um excelente dia! ⚽✨"""

    st.subheader("📋 Resposta Pronta para Copiar:")
    st.text_area("Copie o texto abaixo e cole no seu atendimento:", value=msg_final, height=220)
    st.success("✨ Mensagem acolhedora gerada com sucesso! Basta copiar e enviar.")
