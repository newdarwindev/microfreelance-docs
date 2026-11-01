"""Render a shared illustrative budget with exact decimal arithmetic."""
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def budget():
    data = json.loads((ROOT / "shared/budget.json").read_text(), parse_float=Decimal)
    human = sum(Decimal(r["hours"]) * Decimal(r["rate"]) for r in data["human_work"])
    fee = (human * Decimal(data["platform_fee_percent"]) / 100).quantize(Decimal("0.01"))
    api, contingency = Decimal(data["api_allowance"]), Decimal(data["contingency"])
    monthly = Decimal(data["monthly_operator_hours"]) * Decimal(data["monthly_operator_rate"]) + Decimal(data["monthly_api_allowance"])
    totals = dict(HumanTotal=human, FeeTotal=fee, ApiTotal=api, ContingencyTotal=contingency,
                  ProjectTotal=human+fee+api+contingency, MonthlyTotal=monthly)
    if data["currency"] != "USD" or any(v < 0 for v in totals.values()):
        raise ValueError("Budget must have nonnegative USD values")
    return data, totals

def money(value):
    return rf"\Money{{{value:,.0f}}}" if value == int(value) else rf"\Money{{{value:,.2f}}}"

if __name__ == "__main__":
    data, totals = budget()
    out = ROOT / "build"
    out.mkdir(exist_ok=True)
    (out / "budget-values.tex").write_text("".join(rf"\newcommand{{\{key}}}{{{money(val)}}}"+"\n" for key,val in totals.items()))
    rows = [r"\input{build/budget-values}", r"\begin{tabularx}{\linewidth}{@{}Xrrr@{}}\toprule",
            r"Human role & Hours & USD/hour & USD total\\\midrule"]
    for r in data["human_work"]:
        rows.append(f'{r["role"]} & {r["hours"]} & {r["rate"]} & {r["hours"]*r["rate"]:,}'+r"\\")
    rows.extend([r"\midrule", r"\multicolumn{3}{l}{Human work} & \HumanTotal\\",
                 r"\multicolumn{3}{l}{API allowance} & \ApiTotal\\",
                 r"\multicolumn{3}{l}{Platform fee: 10\% of human work} & \FeeTotal\\",
                 r"\multicolumn{3}{l}{Contingency} & \ContingencyTotal\\\midrule",
                 r"\multicolumn{3}{l}{Maximum project envelope} & \ProjectTotal\\\bottomrule",
                 r"\end{tabularx}"])
    (out / "budget-table.tex").write_text("\n".join(rows)+"\n")
