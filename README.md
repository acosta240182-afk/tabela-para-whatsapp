# tabela-para-whatsapp

Skill para Claude Code que transforma tabela, ranking ou resultado de análise em texto organizado para colar no WhatsApp.

O WhatsApp não alinha colunas: tabela com tabulação, espaços ou bloco de código chega torta dependendo do aparelho. Esta skill troca a tabela por **um bloco por item**, que fica legível no celular, na Web e no desktop:

```
*1. Loja Centro* · 120 vendas
Faturamento: R$ 184.320
Custo: R$ 61.200
Lucro: R$ 123.120

*2. Loja Norte* · 87 vendas
Faturamento: R$ 131.991
Custo: R$ 44.370
Lucro: R$ 87.621

━━━━━━━━━━━━━━
*TOTAL* · 344 vendas
Faturamento: *R$ 504.927*
Custo: *R$ 175.440*
Lucro: *R$ 329.487*
```

## Instalação

Copie a pasta para as skills do Claude Code:

```bash
git clone https://github.com/acosta240182-afk/tabela-para-whatsapp ~/.claude/skills/tabela-para-whatsapp
```

No Windows (PowerShell):

```powershell
git clone https://github.com/acosta240182-afk/tabela-para-whatsapp "$env:USERPROFILE\.claude\skills\tabela-para-whatsapp"
```

Depois é só pedir ao Claude algo como "manda essa tabela no formato do WhatsApp".

## Uso direto do script

Requer Python 3.8+, sem dependências.

```bash
python scripts/formatar.py exemplo/vendas.csv \
  --nome Vendedor --qtd Vendas --qtd-rotulo venda vendas \
  --valores Faturamento Custo Lucro \
  --titulo "Vendas por loja" --subtitulo "Janeiro a março" \
  --nota "Lucro: faturamento menos custo." --copiar
```

| Opção | O que faz |
|---|---|
| `--nome` | coluna com o nome de cada item (obrigatória) |
| `--qtd`, `--qtd-rotulo` | quantidade ao lado do nome, com singular e plural |
| `--valores`, `--rotulos` | colunas de valor e o nome exibido de cada uma |
| `--ordenar`, `--sem-ordem` | ordem do maior para o menor (padrão: 1º valor) ou a do arquivo |
| `--top N` | mostra os N primeiros e soma o resto em "Demais" |
| `--moeda`, `--casas` | prefixo (padrão `R$ `) e casas decimais (padrão 0) |
| `--sem-total`, `--nota` | tira a linha de total; rodapé em itálico |
| `--copiar`, `--saida` | copia para a área de transferência; arquivo `.txt` de saída |

Lê CSV com `;`, `,` ou tabulação e JSON (lista de objetos). Números em formato brasileiro (`1.234,56`) ou internacional (`1234.56`). Arredonda 0,50 para cima e calcula o total a partir dos valores com centavos.

## Licença

MIT
