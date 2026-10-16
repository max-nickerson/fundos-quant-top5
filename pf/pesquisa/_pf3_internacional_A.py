"""Tabelas do caderno pf3_internacional_A.md: capital x sleeve x hedge (OOS antes/depois do IR), decomposição papéis/conta, beta x alfa,
métricas da bateria e negócios. Rode: PYTHONIOENCODING=utf-8 python -W ignore pf/pesquisa/_pf3_internacional_A.py"""
import pickle, sys, warnings
from pathlib import Path
warnings.filterwarnings("ignore")
AQUI = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(AQUI), str(AQUI / "fundos"), str(AQUI.parent)]
import numpy as np, pandas as pd
import comum as C, pf, robustez as RB, ir as IRPF
import rodar_pf as RP
import pf3a_comum as A

FUNDOS = {"em_panico_pais_v2": "EEM", "em_argentina_v2": "EEM", "fg_russell_v2": "IWM", "fg_spinoff_pequeno_v2": "IWM", "lg_eua_etf_v2": "SPY"}
EXTRA = {"em_panico_pais_v2": [("sem âncora (sinal original)", {"ancora": "nenhuma"}), ("âncora commodity/EEM", {"ancora": "commod"}),
                               ("filtro de sanção (sem Rússia)", {"russia": False})],
         "fg_spinoff_pequeno_v2": [("sem RHLD (maior nome)", {"sem": "RHLD"}), ("todos os tamanhos", {"giro_max": 1e12}),
                                   ("todos os tamanhos sem SNDK", {"giro_max": 1e12, "sem": "SNDK"})],
         "em_argentina_v2": [], "fg_russell_v2": [("IWM sempre (ignora mínimo de margem)", {"beta_hedge": "IWM"})], "lg_eua_etf_v2": []}


def apos_ir(m, d, cap, e, **kw):
    cls = m.classes_ir(d, capital=cap, **kw)
    r = RB.cota(m, e)
    cdi_l = pf.cdi_liquido().reindex(r.index).fillna(0)
    ex = sum(IRPF.imposto_excesso(cls[c].reindex(r.index).fillna(0) / cap, cap, c) for c in ("exterior", "futuros_b3"))
    ri = cdi_l + ex - cls["cdi_perdido"].reindex(r.index).fillna(0) / cap * .85
    return C.anual(RB.oos(m, ri)) - C.anual(RB.oos(m, cdi_l))


def linha(m, d, cap, sl, hg, **kw):
    e = m.excesso(d, capital=cap, sleeve_brl=sl, hedge=hg, **kw)
    o = m._roda(d, cap, 1, 0, 1, sl, hg, **m._p(kw))
    papeis = (o["usd"] * A.PTAX / cap)
    oo = lambda x: RB.oos(m, x).mean() * 252 * 100
    # câmbio aberto (beta no real): exposição líquida em US$ = sleeve − WDO; variação cambial dela + carry (CDI − cupom) do sobre-hedge
    n = o["classes"]["n_wdo"].shift(1).fillna(0)
    px = A.PTAX.shift(1).bfill()
    liq = sl / px - n * pf.WDO_USD
    fxr = A.PTAX.pct_change(fill_method=None).fillna(0)
    carry = (-liq).clip(lower=0) * px * (C.CDI - pf.cupom_cambial() / 252)
    aberto = (liq * px * fxr + carry) / cap
    return {"antes IR": RB.ativo_aa(m, RB.cota(m, e)), "depois IR": apos_ir(m, d, cap, e, sleeve_brl=sl, hedge=hg, **kw),
            "papéis": oo(papeis), "conta": oo(e - papeis), "câmbio aberto": oo(aberto), "WDO OOS": float(RB.oos(m, o["classes"]["n_wdo"]).mean())}


out = []
for nome, bench in FUNDOS.items():
    m = RP.carrega_modulo(nome)
    d = m.carrega()
    B = pickle.load(open(RP.BAT / f"{nome}.pkl", "rb"))
    R = B["R20"]
    out.append(f"\n## {nome} — {m.NOME}\n")
    out.append(f"Bateria (R$ 20 mil, sleeve padrão = metade, hedge inteiro): ativo OOS 20k {B['ativo20']:+.2f} / 50k {B['ativo50']:+.2f} pp; "
               f"depois do IR (executor) 20k {B['ativo_ir20']:+.2f} / 50k {B['ativo_ir50']:+.2f}; IR {B['ir_oos20']:.2f}; "
               f"PBO {R['resumo_grade']['PBO %']:.0f}%; P(bater 3a) {R['mc'].loc['P(bater o benchmark) %', '3 ano(s)']:.0f}%; "
               f"custo 2x {R['custo'].get('2x'):+.2f}; t+2 {R['atraso'].get('t+2'):+.2f}; sem 10 melhores {R['sem_maiores'].get('sem os 10 melhores'):+.2f}; "
               f"walk-forward {R['wf_ativo']:+.2f}; placebo p {R['placebo']['p-valor (fração de placebos >= real)']:.2f}; "
               f"truncamento {'OK' if bool(R['truncamento']['passou'].all()) else 'FALHOU'}.\n")
    T = []
    for cap, sls in A.SLEEVES.items():
        for sl in sls:
            for hg in ("nenhum", "inteiro"):
                x = linha(m, d, cap, sl, hg)
                T.append({"capital": cap, "sleeve": sl, "hedge": hg, **{k: round(v, 2) for k, v in x.items()}})
    T = pd.DataFrame(T)
    out.append(T.to_markdown(index=False))
    ba = []
    for cap, sl in ((20000, 10000), (50000, 25000), (50000, 37500)):
        for hg, bm in [(h, b) for h in ("nenhum", "inteiro") for b in ([bench] + (["ARGT"] if "argentina" in nome else []))]:
            e = m.excesso(d, capital=cap, sleeve_brl=sl, hedge=hg)
            bench_ = bm
            ba.append({"capital": cap, "sleeve": sl, "hedge": hg, "fator": bench_, **{k: round(v, 2) for k, v in A.beta_alfa(e, bench_).items()}})
    out.append("\nBeta x alfa (excesso diário OOS do fundo contra o ETF em US$ sobre o T-bill):\n")
    out.append(pd.DataFrame(ba).to_markdown(index=False))
    if EXTRA[nome]:
        V = []
        for rot, kw in EXTRA[nome]:
            for cap, sl in ((20000, 10000), (50000, 37500)):
                x = linha(m, d, cap, sl, "inteiro", **kw)
                V.append({"variante": rot, "capital": cap, "sleeve": sl, **{k: round(v, 2) for k, v in x.items()}})
        out.append("\nVariantes (hedge inteiro):\n")
        out.append(pd.DataFrame(V).to_markdown(index=False))
    ng = m.negocios(d, capital=20000, sleeve_brl=10000)
    ng = ng[pd.to_datetime(ng.entrada) >= pd.Timestamp(m.CORTE)]
    cols = [c for c in ["ativo", "entrada", "saida", "dias", "retorno_%", "contrib_pp"] if c in ng]
    if len(ng):
        out.append(f"\nNegócios OOS (R$ 20 mil, sleeve 10 mil): {len(ng)}; soma contrib {ng.contrib_pp.sum():+.2f} pp; acerto {(ng.contrib_pp > 0).mean() * 100:.0f}%\n")
        if "ativo" in ng:
            top = ng.groupby(ng.ativo.astype(str).str.split("*").str[0]).contrib_pp.sum().sort_values()
            out.append("Por ativo (pp do capital, OOS): maiores " + ", ".join(f"{k} {v:+.2f}" for k, v in top[::-1].head(5).items())
                       + "; piores " + ", ".join(f"{k} {v:+.2f}" for k, v in top.head(5).items()) + "\n")
        out.append("10 melhores:\n" + ng.nlargest(10, "contrib_pp")[cols].round(2).to_markdown(index=False))
        out.append("\n10 piores:\n" + ng.nsmallest(10, "contrib_pp")[cols].round(2).to_markdown(index=False))
    print("\n".join(out[-8:]), flush=True)
(AQUI / "pesquisa" / "_pf3_internacional_A_tabelas.md").write_text("\n".join(out), encoding="utf-8")
