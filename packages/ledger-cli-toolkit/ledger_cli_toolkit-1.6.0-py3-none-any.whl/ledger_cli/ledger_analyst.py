from collections import defaultdict
from datetime import datetime
from typing import List, Dict, Tuple
import numpy as np
from typing import Optional
from datetime import datetime
from dateutil.relativedelta import relativedelta


# Utilidades auxiliares para los nuevos métodos (fuera de la clase para reutilizar fácilmente)

def linear_regression_trend(values: List[float]) -> Tuple[float, float]:
    """
    Calcula una regresión lineal simple y = mx + b para una serie de valores.
    Retorna: (pendiente m, intersección b)
    """
    # Verifica que haya suficientes datos
    if not values or len(values) < 2:
        return 0.0, 0.0

    # Convierte a ndarray y limpia valores no válidos
    y = np.array(values, dtype=np.float64)

    # Si contiene NaN o inf, la regresión fallará
    if not np.all(np.isfinite(y)):
        return 0.0, 0.0

    # Si todos los valores son iguales, no hay tendencia
    if np.allclose(y, y[0]):
        return 0.0, y[0]

    # Datos válidos, calcula regresión
    x = np.arange(len(y))
    try:
        m, b = np.polyfit(x, y, 1)
        return round(m, 2), round(b, 2)
    except Exception as e:
        print("Error en polyfit:", e)
        return 0.0, 0.0


def predict_next_values(values: list[float], months: int = 3) -> list[float]:
    """
    Realiza una predicción lineal simple para los próximos `months` puntos
    """
    m, b = linear_regression_trend(values)
    x_future = np.arange(len(values), len(values) + months)
    return [round(m * x + b, 2) for x in x_future]


def parse_month_str(date_str: str) -> datetime:
    """Convierte 'YYYY-MM' a objeto datetime"""
    return datetime.strptime(date_str, "%Y-%m")


class LedgerAnalyst:
    def __init__(
        self,
        transactions: List[Dict],
        accounts: List[str],
        *,
        income_parents=("Ingresos", "Incoming"),
        expense_parents=("Gastos", "Expenses"),
        asset_parents=("Activos", "Assets"),
        liability_parents=("Pasivos", "Liabilities"),
    ):
        self.transactions = transactions
        self.accounts = accounts
        self.income_parents = income_parents
        self.expense_parents = expense_parents
        self.asset_parents = asset_parents
        self.liability_parents = liability_parents

    def _is_under_parent(self, account: str, parents: tuple) -> bool:
        return any(
            account.startswith(parent + ":") or account == parent for parent in parents
        )

    def _normalize_date(self, date_str: str) -> str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").date().isoformat()
        except ValueError:
            return datetime.strptime(date_str, "%Y/%m/%d").date().isoformat()

    def get_daily_incomes_expenses(self) -> List[Dict]:
        summary = defaultdict(lambda: {"incoming": 0.0, "expenses": 0.0})

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, self.income_parents):
                    summary[date]["incoming"] += abs(amount)
                elif self._is_under_parent(account, self.expense_parents):
                    summary[date]["expenses"] += abs(amount)

        return [{"date": date, **values} for date, values in sorted(summary.items())]

    def _group_by_account(self, parent_types: tuple) -> Dict[str, float]:
        grouped = defaultdict(float)
        for tx in self.transactions:
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, parent_types):
                    grouped[account] += abs(amount)
        return grouped

    def get_expenses_pie(self) -> List[Dict]:
        grouped = self._group_by_account(self.expense_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_incomes_pie(self) -> List[Dict]:
        grouped = self._group_by_account(self.income_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_assets_summary(self) -> List[Dict]:
        grouped = self._group_by_account(self.asset_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_liabilities_summary(self) -> List[Dict]:
        grouped = self._group_by_account(self.liability_parents)
        return [{"account": k, "amount": v} for k, v in grouped.items()]

    def get_balance_by_day(self) -> List[Dict]:
        """Retorna el balance diario acumulado: ingresos - gastos"""
        daily_data = self.get_daily_incomes_expenses()
        balance = 0
        result = []
        for entry in daily_data:
            balance += entry["incoming"] - entry["expenses"]
            result.append({**entry, "balance": balance})
        return result

    def get_accounts_used(self) -> List[str]:
        """Lista de todas las cuentas usadas en las transacciones (sin duplicados)"""
        used = set()
        for tx in self.transactions:
            for entry in tx["accounts"]:
                used.add(entry["account"])
        return sorted(list(used))

    def get_monthly_incomes_expenses(self) -> List[Dict]:
        """Retorna un resumen mensual de ingresos y gastos"""
        summary = defaultdict(lambda: {"incoming": 0.0, "expenses": 0.0})

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]  # YYYY-MM
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, self.income_parents):
                    summary[month]["incoming"] += abs(amount)
                elif self._is_under_parent(account, self.expense_parents):
                    summary[month]["expenses"] += abs(amount)

        return [{"month": month, **values} for month, values in sorted(summary.items())]

    def get_expense_trends_by_category(self) -> Dict[str, Dict[str, float]]:
        """Retorna un resumen de tendencias de gastos por categoría mensual"""
        trends = defaultdict(lambda: defaultdict(float))  # {categoria: {mes: monto}}

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]
            for entry in tx["accounts"]:
                account = entry["account"]
                if self._is_under_parent(account, self.expense_parents):
                    trends[account][month] += abs(entry["amount"])

        # Opcional: transformar a lista de dicts si lo usas en gráficos
        return {k: dict(v) for k, v in trends.items()}

    def get_cashflow_by_month(self) -> List[Dict]:
        summary = defaultdict(lambda: {"in": 0.0, "out": 0.0, "net": 0.0})

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]
            for entry in tx["accounts"]:
                account = entry["account"]
                amount = entry["amount"]
                if self._is_under_parent(account, self.income_parents):
                    summary[month]["in"] += abs(amount)
                elif self._is_under_parent(account, self.expense_parents):
                    summary[month]["out"] += abs(amount)

        for month in summary:
            summary[month]["net"] = summary[month]["in"] - summary[month]["out"]

        return [{"month": m, **v} for m, v in sorted(summary.items())]

    def get_average_expense_per_category(self) -> List[Dict]:
        """Calcula el promedio mensual de gastos por categoría"""
        totals = defaultdict(float)
        months = set()

        for tx in self.transactions:
            date = self._normalize_date(tx["date"])
            month = date[:7]
            months.add(month)
            for entry in tx["accounts"]:
                account = entry["account"]
                if self._is_under_parent(account, self.expense_parents):
                    totals[account] += abs(entry["amount"])

        num_months = len(months)
        return [
            {"account": acc, "monthly_average": total / num_months}
            for acc, total in totals.items()
        ]

    def detect_unusual_expenses(self, threshold: float = 1.5) -> List[Dict]:
        """Detecta gastos inusuales basados en tendencias mensuales"""
        trends = self.get_expense_trends_by_category()
        alerts = []

        for account, monthly_data in trends.items():
            values = list(monthly_data.values())
            if len(values) < 2:
                continue  # Necesitas al menos 2 meses para comparar
            avg = sum(values) / len(values)
            last_month = sorted(monthly_data.keys())[-1]
            if monthly_data[last_month] > avg * threshold:
                alerts.append(
                    {
                        "account": account,
                        "month": last_month,
                        "amount": monthly_data[last_month],
                        "average": avg,
                        "alert": "Gasto inusualmente alto",
                    }
                )

        return alerts

    def get_monthly_growth_rates(self, monthly_data: List[Dict] = None) -> List[Dict]:
        """
        Calcula el porcentaje de crecimiento o decrecimiento mes a mes
        de ingresos, egresos y balance neto. Si no hay mes anterior, retorna 0.
        """

        if monthly_data is None or len(monthly_data) == 0:
            monthly_data = self.get_cashflow_by_month()

        growth_rates = []

        for i, current in enumerate(monthly_data):
            if i == 0:
                # No hay mes anterior para comparar
                growth_rates.append(
                    {
                        "month": current["month"],
                        "in_growth": 0.0,
                        "out_growth": 0.0,
                        "net_growth": 0.0,
                    }
                )
            else:
                previous = monthly_data[i - 1]

                def calc_growth(curr, prev):
                    if prev == 0:
                        return 0.0
                    return ((curr - prev) / prev) * 100

                in_growth = calc_growth(current["in"], previous["in"])
                out_growth = calc_growth(current["out"], previous["out"])
                net_growth = calc_growth(current["net"], previous["net"])

                growth_rates.append(
                    {
                        "month": current["month"],
                        "in_growth": round(in_growth, 2),
                        "out_growth": round(out_growth, 2),
                        "net_growth": round(net_growth, 2),
                    }
                )

        return growth_rates

    def get_monthly_expense_ratio(self, monthly_data: List[Dict] = None) -> List[Dict]:
        """
        Calcula el porcentaje de gasto con respecto a los ingresos para cada mes.
        Si no se proporciona monthly_data, usa self.get_cashflow_by_month().
        Retorna una lista de dicts con:
          - month: "YYYY-MM"
          - expense_ratio: (out / in) * 100, redondeado a 2 decimales, o 0 si in == 0
        """
        if monthly_data is None or len(monthly_data) == 0:
            monthly_data = self.get_cashflow_by_month()

        ratios = []
        for entry in monthly_data:
            income = entry.get("in", 0.0)
            expense = entry.get("out", 0.0)

            if income == 0:
                ratio = 0.0
            else:
                ratio = (expense / income) * 100

            ratios.append(
                {
                    "month": entry["month"],
                    "expense_ratio": round(ratio, 2),
                }
            )

        return ratios

    # ──────────────────────────────────────────────
    # 📈 Análisis Temporal Avanzado
    # ──────────────────────────────────────────────

    def get_moving_average(self, field: str, window: int = 3) -> List[Dict]:
        """
        Calcula el promedio móvil para un campo dado ('in', 'out' o 'net').

        Args:
            field (str): Campo sobre el cual calcular ('in', 'out' o 'net').
            window (int): Tamaño de la ventana de promedio.

        Returns:
            List[Dict]: Lista de dicts con mes y promedio móvil correspondiente.
        """
        data = self.get_cashflow_by_month()
        result = []
        for i in range(len(data)):
            if i + 1 < window:
                avg = 0.0
            else:
                total = sum(data[j][field] for j in range(i + 1 - window, i + 1))
                avg = total / window
            result.append(
                {"month": data[i]["month"], f"{field}_moving_avg": round(avg, 2)}
            )
        return result

    def get_trend_slope(self, field: str) -> float:
        """
        Calcula la pendiente (tendencia lineal) de un campo: 'in', 'out' o 'net'.

        Args:
            field (str): Campo a evaluar ('in', 'out' o 'net').

        Returns:
            float: Pendiente de la regresión lineal.
        """
        values = [entry[field] for entry in self.get_cashflow_by_month()]
        m, _ = linear_regression_trend(values)
        return m

    def predict_future_months(self, field: str, months: int = 3) -> List[Dict]:
        """
        Proyecta los próximos N meses usando regresión lineal simple.

        Args:
            field (str): Campo a proyectar ('in', 'out' o 'net').
            months (int): Número de meses a predecir.

        Returns:
            List[Dict]: Lista con predicciones para cada mes futuro.
        """
        data = self.get_cashflow_by_month()
        values = [entry[field] for entry in data]
        last_month = parse_month_str(data[-1]["month"])
        predicted = predict_next_values(values, months)
        return [
            {
                "month": (
                    last_month.replace(day=1) + relativedelta(months=i + 1)
                ).strftime("%Y-%m"),
                f"predicted_{field}": val,
            }
            for i, val in enumerate(predicted)
        ]

    # ──────────────────────────────────────────────
    # 🔍 Análisis de Comportamiento
    # ──────────────────────────────────────────────

    def get_extreme_months(self) -> Dict[str, Dict]:
        """
        Identifica el mes con más ingresos, más egresos y mejor balance neto.

        Returns:
            Dict[str, Dict]: {'highest_income': {...}, 'highest_expense': {...}, 'best_balance': {...}}
        """
        data = self.get_cashflow_by_month()
        return {
            "highest_income": max(data, key=lambda x: x["in"]),
            "highest_expense": max(data, key=lambda x: x["out"]),
            "best_balance": max(data, key=lambda x: x["net"]),
        }

    def classify_months_by_balance(self) -> Dict[str, List[str]]:
        """
        Clasifica meses según el balance: positivo, negativo o neutro.

        Returns:
            Dict[str, List[str]]: { "positive": [...], "negative": [...], "neutral": [...] }
        """
        categories = {"positive": [], "negative": [], "neutral": []}
        for entry in self.get_cashflow_by_month():
            if entry["net"] > 0:
                categories["positive"].append(entry["month"])
            elif entry["net"] < 0:
                categories["negative"].append(entry["month"])
            else:
                categories["neutral"].append(entry["month"])
        return categories

    def compare_months(self, month1: str, month2: str) -> Dict[str, float]:
        """
        Compara ingresos, egresos y balance entre dos meses específicos.

        Args:
            month1 (str): Primer mes en formato 'YYYY-MM'.
            month2 (str): Segundo mes en formato 'YYYY-MM'.

        Returns:
            Dict[str, float]: Diferencias entre meses: 'in_diff', 'out_diff', 'net_diff'
        """
        data = {d["month"]: d for d in self.get_cashflow_by_month()}
        d1, d2 = data.get(month1), data.get(month2)
        if not d1 or not d2:
            return {}

        return {
            "in_diff": round(d2["in"] - d1["in"], 2),
            "out_diff": round(d2["out"] - d1["out"], 2),
            "net_diff": round(d2["net"] - d1["net"], 2),
        }

    # ──────────────────────────────────────────────
    # 💡 Indicadores Financieros Útiles
    # ──────────────────────────────────────────────

    def get_monthly_saving_rate(self) -> List[Dict]:
        """
        Calcula el porcentaje de ahorro mensual: ((in - out) / in) * 100

        Returns:
            List[Dict]: Lista con mes y tasa de ahorro en porcentaje.
        """
        result = []
        for entry in self.get_cashflow_by_month():
            income = entry["in"]
            saving = entry["net"]
            rate = (saving / income) * 100 if income > 0 else 0.0
            result.append({"month": entry["month"], "saving_rate": round(rate, 2)})
        return result

    def get_income_dependency_ratio(self) -> List[Dict]:
        """
        Mide qué porcentaje del gasto fue cubierto por ingresos (out / in * 100).

        Returns:
            List[Dict]: Lista con mes y ratio de dependencia.
        """
        ratios = []
        for entry in self.get_cashflow_by_month():
            income = entry["in"]
            expense = entry["out"]
            ratio = (expense / income) * 100 if income > 0 else 0.0
            ratios.append(
                {"month": entry["month"], "dependency_ratio": round(ratio, 2)}
            )
        return ratios

    def get_cumulative_net_income(self) -> List[Dict]:
        """
        Calcula la acumulación de ingresos netos mes a mes.

        Returns:
            List[Dict]: Lista con mes y valor acumulado del neto.
        """
        cumulative = 0.0
        result = []
        for entry in self.get_cashflow_by_month():
            cumulative += entry["net"]
            result.append(
                {"month": entry["month"], "cumulative_net": round(cumulative, 2)}
            )
        return result
