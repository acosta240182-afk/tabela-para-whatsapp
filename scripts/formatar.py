# -*- coding: utf-8 -*-
"""Transforma uma tabela (CSV ou JSON) em texto organizado para colar no WhatsApp.

O WhatsApp não alinha colunas: tabulação, espaços e até bloco ``` entortam
conforme o aparelho. Por isso cada linha da tabela vira um bloco:

    *1. Nome* · 12 itens
    Coluna A: R$ 1.234
    Coluna B: R$ 567

Uso rápido:
    python formatar.py dados.csv --nome Nome --qtd Vendas --qtd-rotulo venda vendas \
        --valores Faturamento Custo --titulo "Vendas 2026" --copiar
"""
import argparse
import csv
import json
import os
import platform
import subprocess
import sys
import tempfile
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP


def numero(txt):
    """Lê número em formato brasileiro (1.234,56) ou internacional (1234.56)."""
    if isinstance(txt, (int, float, Decimal)):
        return Decimal(str(txt))
    s = str(txt or "").strip().replace("R$", "").replace("%", "").replace(" ", "").replace(" ", "")
    if not s or s in ("-", "—"):
        return Decimal(0)
    if "," in s and "." in s:
        s = s.replace(".", "").replace(",", ".") if s.rfind(",") > s.rfind(".") else s.replace(",", "")
    elif "," in s:
        s = s.replace(",", ".")
    elif s.count(".") > 1 or (s.count(".") == 1 and len(s.split(".")[1]) == 3 and len(s.split(".")[0]) <= 3):
        s = s.replace(".", "")  # 1.234 ou 1.234.567 = milhar
    try:
        return Decimal(s)
    except InvalidOperation:
        sys.exit(f"Valor não numérico: {txt!r}")


def fmt(valor, casas=0, moeda="R$ "):
    """0,50 arredonda para cima (ROUND_HALF_UP), nunca o arredondamento bancário."""
    q = Decimal(1).scaleb(-casas)
    v = Decimal(valor).quantize(q, ROUND_HALF_UP)
    inteiro, _, dec = f"{abs(v):.{casas}f}".partition(".")
    inteiro = f"{int(inteiro):,}".replace(",", ".")
    s = inteiro + ("," + dec if casas else "")
    return ("-" if v < 0 else "") + (moeda or "") + s


def ler(caminho):
    if caminho.lower().endswith(".json"):
        dados = json.load(open(caminho, encoding="utf-8-sig"))
        if isinstance(dados, dict):
            dados = next(v for v in dados.values() if isinstance(v, list))
        return dados
    bruto = open(caminho, encoding="utf-8-sig").read()
    sep = max((";", ",", "\t"), key=lambda c: bruto.splitlines()[0].count(c))
    return list(csv.DictReader(bruto.splitlines(), delimiter=sep))


def copiar(texto):
    sistema = platform.system()
    try:
        if sistema == "Windows":
            # clip.exe estraga acento; Set-Clipboard lendo arquivo UTF-8 preserva
            with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False, encoding="utf-8") as t:
                t.write(texto)
            subprocess.run(["powershell", "-NoProfile", "-Command",
                            f"Get-Content -LiteralPath '{t.name}' -Raw -Encoding UTF8 | Set-Clipboard"], check=True)
            os.remove(t.name)
        elif sistema == "Darwin":
            subprocess.run(["pbcopy"], input=texto.encode("utf-8"), check=True)
        else:
            cmd = ["wl-copy"] if os.environ.get("WAYLAND_DISPLAY") else ["xclip", "-selection", "clipboard"]
            subprocess.run(cmd, input=texto.encode("utf-8"), check=True)
        return True
    except Exception as e:  # sem área de transferência, o arquivo .txt continua valendo
        print(f"[aviso] não consegui copiar: {e}", file=sys.stderr)
        return False


def main():
    ap = argparse.ArgumentParser(description="Tabela para texto de WhatsApp, um bloco por linha.")
    ap.add_argument("arquivo", help="CSV (separador ; , ou tab) ou JSON (lista de objetos)")
    ap.add_argument("--nome", required=True, help="coluna com o nome de cada item")
    ap.add_argument("--qtd", help="coluna de quantidade, vai ao lado do nome")
    ap.add_argument("--qtd-rotulo", nargs=2, metavar=("SINGULAR", "PLURAL"), default=("item", "itens"))
    ap.add_argument("--valores", nargs="+", default=[], help="colunas de valor, uma linha cada")
    ap.add_argument("--rotulos", nargs="+", help="nomes exibidos para --valores (mesma ordem)")
    ap.add_argument("--moeda", default="R$ ", help='prefixo dos valores; use "" para nenhum')
    ap.add_argument("--casas", type=int, default=0, help="casas decimais (padrão 0)")
    ap.add_argument("--ordenar", help="coluna para ordenar do maior para o menor (padrão: 1º valor)")
    ap.add_argument("--sem-ordem", action="store_true", help="mantém a ordem do arquivo")
    ap.add_argument("--top", type=int, help="mostra só os N primeiros e soma o resto numa linha")
    ap.add_argument("--titulo", default="")
    ap.add_argument("--subtitulo", default="")
    ap.add_argument("--nota", default="", help="rodapé em itálico (explique as colunas)")
    ap.add_argument("--sem-total", action="store_true")
    ap.add_argument("--saida", help="arquivo .txt de saída (padrão: <arquivo>_whatsapp.txt)")
    ap.add_argument("--copiar", action="store_true", help="copia para a área de transferência")
    a = ap.parse_args()

    linhas = ler(a.arquivo)
    if not linhas:
        sys.exit("Arquivo sem linhas.")
    colunas = set(linhas[0].keys())
    for c in [a.nome, a.qtd, a.ordenar, *a.valores]:
        if c and c not in colunas:
            sys.exit(f"Coluna {c!r} não existe. Colunas: {', '.join(linhas[0].keys())}")
    rotulos = a.rotulos or a.valores
    if len(rotulos) != len(a.valores):
        sys.exit("--rotulos precisa ter o mesmo número de itens que --valores")

    itens = [{"nome": str(l[a.nome]).strip(),
              "qtd": numero(l[a.qtd]) if a.qtd else None,
              "vals": [numero(l[c]) for c in a.valores],
              "ord": numero(l[a.ordenar]) if a.ordenar else None} for l in linhas
             if str(l.get(a.nome, "")).strip() and str(l[a.nome]).strip().upper() not in ("TOTAL", "TOTAIS")]
    if not a.sem_ordem:
        if a.ordenar:
            itens.sort(key=lambda i: -i["ord"])
        elif a.valores:
            itens.sort(key=lambda i: -i["vals"][0])

    # total sempre da soma com centavos, nunca da soma dos arredondados
    tot_qtd = sum((i["qtd"] for i in itens), Decimal(0)) if a.qtd else None
    tot_vals = [sum((i["vals"][k] for i in itens), Decimal(0)) for k in range(len(a.valores))]

    sing, plur = a.qtd_rotulo

    def qtd_txt(q):
        return f"{fmt(q, 0, '')} {sing if q == 1 else plur}"

    def bloco(titulo, qtd, vals, destaque=False):
        cab = f"*{titulo}*" + (f" · {qtd_txt(qtd)}" if qtd is not None else "")
        out = [cab]
        for r, v in zip(rotulos, vals):
            num = fmt(v, a.casas, a.moeda)
            out.append(f"{r}: *{num}*" if destaque else f"{r}: {num}")
        return out

    txt = []
    if a.titulo:
        txt.append(f"*{a.titulo.upper()}*")
    if a.subtitulo:
        txt.append(f"_{a.subtitulo}_")
    if txt:
        txt.append("")

    mostrar = itens[: a.top] if a.top else itens
    for n, i in enumerate(mostrar, 1):
        txt += bloco(f"{n}. {i['nome']}", i["qtd"], i["vals"]) + [""]

    resto = itens[len(mostrar):]
    if resto:
        q = sum((i["qtd"] for i in resto), Decimal(0)) if a.qtd else None
        v = [sum((i["vals"][k] for i in resto), Decimal(0)) for k in range(len(a.valores))]
        txt += bloco(f"Demais {len(resto)}", q, v) + [""]

    if not a.sem_total:
        txt += ["━━━━━━━━━━━━━━"] + bloco("TOTAL", tot_qtd, tot_vals, destaque=True)
    if a.nota:
        txt += ["", f"_{a.nota}_"]

    texto = "\n".join(txt).rstrip() + "\n"
    saida = a.saida or os.path.splitext(a.arquivo)[0] + "_whatsapp.txt"
    with open(saida, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    print(texto)
    print(f"[ok] {len(itens)} itens · salvo em {saida}", file=sys.stderr)
    if a.copiar and copiar(texto):
        print("[ok] copiado: é só colar no WhatsApp", file=sys.stderr)


if __name__ == "__main__":
    main()
