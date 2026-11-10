---
name: tabela-para-whatsapp
description: Transforma tabela, ranking ou resultado de análise em texto organizado para colar no WhatsApp, um bloco por item, com negrito, total e nota no padrão do app. Use sempre que o pedido for mandar números, lista, ranking, planilha ou tabela "pelo zap", "no WhatsApp", "em texto para enviar", ou quando uma tabela colada no WhatsApp ficou torta ou desalinhada. Triggers: whatsapp, zap, wpp, wtsp, mandar no zap, texto para enviar, tabelinha no whatsapp, ficou torto, colunas desalinhadas.
---

# Tabela para WhatsApp

## A regra que motivou a skill

**WhatsApp não alinha coluna.** Tabela com tabulação, com espaços ou dentro de bloco ``` chega torta, porque a fonte muda de aparelho para aparelho (celular, Web, desktop) e o monoespaçado nem sempre é aplicado. Também não adianta mandar a tabela como imagem ou colar o conteúdo de um Word: a imagem fica pequena no celular e o Word perde o formato ao colar.

O formato que funciona em qualquer aparelho é **um bloco por item**:

```
*FATURAMENTO POR LOJA*
_Janeiro a março, do maior para o menor_

*1. Loja Centro* · 120 vendas
Faturamento: R$ 184.320
Custo: R$ 61.200

*2. Loja Norte* · 87 vendas
Faturamento: R$ 131.991
Custo: R$ 44.370

━━━━━━━━━━━━━━
*TOTAL* · 207 vendas
Faturamento: *R$ 316.311*
Custo: *R$ 105.570*

_Custo: o que foi pago ao fornecedor._
```

Não ofereça tabela alinhada, imagem ou Word como primeira opção. Comece por este formato.

## Passo a passo

1. **Pegue o número da fonte oficial** (planilha, JSON, banco), nunca redigite à mão. Se houver uma versão aprovada ou conferida, use exatamente ela.
2. **Deixe o dado em CSV ou JSON**: uma linha por item, com uma coluna de nome, uma de quantidade (opcional) e as de valor.
3. **Rode o script** (`scripts/formatar.py`, caminho relativo a esta skill):

   ```
   python scripts/formatar.py dados.csv --nome Loja --qtd Vendas --qtd-rotulo venda vendas \
       --valores Faturamento Custo --titulo "Faturamento por loja" \
       --subtitulo "Janeiro a março, do maior para o menor" \
       --nota "Custo: o que foi pago ao fornecedor." --copiar
   ```

   Opções úteis:
   - `--rotulos` troca o nome exibido de cada coluna de valor (ex.: coluna `fat_liq` aparece como "Faturamento líquido").
   - `--ordenar COLUNA` ordena por outra coluna; `--sem-ordem` mantém a ordem do arquivo.
   - `--top 10` mostra os 10 primeiros e soma o resto em "Demais N".
   - `--casas 2` mostra centavos; `--moeda ""` tira o "R$" (para quantidade ou percentual).
   - `--sem-total` quando somar não faz sentido (médias, percentuais).
4. **Confira o total** contra o total da fonte antes de entregar.
5. **Entregue**: o texto já vai para a área de transferência (`--copiar`) e fica salvo num `.txt`. Mostre ao usuário um bloco de exemplo, o total, e onde está o arquivo.

## Regras do formato

- **Negrito** só no nome do item e nos valores do TOTAL. Itálico no subtítulo e na nota.
- **Total vem da soma com centavos**, nunca da soma dos valores já arredondados.
- **Arredondamento comercial**: 0,50 sobe (ROUND_HALF_UP). O `round()` do Python arredonda para o par (2,50 vira 2), por isso o script usa `Decimal`.
- **Plural certo**: "1 venda", "2 vendas" (`--qtd-rotulo singular plural`).
- **Nota no fim** explicando o que cada coluna significa, em palavras que quem recebe entende sem perguntar.
- **Quebra de linha LF**, sem espaço sobrando no fim.
- **Lista longa** (mais de 15 itens): entregue a completa e ofereça a versão `--top 10`.
- Mensagem do WhatsApp aceita até cerca de 65 mil caracteres; acima disso, divida em partes.

## Sem o script

Se não der para rodar Python, monte o mesmo formato à mão seguindo as regras acima, e confira o total somando os valores originais.
