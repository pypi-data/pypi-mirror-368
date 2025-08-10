import re
import json
from typing import List, Dict, Union
from datetime import datetime
from typing import Union, TextIO
import yaml
import copy


keywords = {
    "Assets": [
        # Español
        "activo",
        "activos",
        "act",
        "activ",
        "caja",
        "banco",
        "banc",
        "cuentas por cobrar",
        "inventario",
        "inv",
        "efectivo",
        # Inglés
        "asset",
        "assets",
        "ass",
        "cash",
        "bank",
        "inventory",
        "inv",
        "a/r",
        "ar",
        "accounts receivable",
        # Francés
        "actif",
        "actifs",
        "act",
        "banque",
        "encaisse",
        "inventaire",
        "créances",
        # Portugués
        "ativo",
        "ativos",
        "ati",
        "caixa",
        "banco",
        "contas a receber",
        "inventário",
        # Alemán
        "vermögen",
        "verm",
        "anlagen",
        "kasse",
        "bank",
        "forderungen",
        # Otros
        "recursos",
        "propiedades",
        "prop",
        "recur",
    ],
    "Liabilities": [
        # Español
        "pasivo",
        "pasivos",
        "pas",
        "pasiv",
        "deuda",
        "deudas",
        "prestamo",
        "prestamos",
        "obligaciones",
        "cuentas por pagar",
        # Inglés
        "liability",
        "liabilities",
        "liab",
        "liabs",
        "loan",
        "loans",
        "debts",
        "a/p",
        "ap",
        "accounts payable",
        "obligations",
        # Francés
        "passif",
        "dettes",
        "obligations",
        "emprunts",
        "pass",
        # Portugués
        "passivo",
        "passivos",
        "pass",
        "obrigações",
        "contas a pagar",
        "empréstimos",
        # Alemán
        "schuld",
        "schulden",
        "verbindlichkeiten",
        "verpflichtungen",
        "verb",
        "sch",
        # Otros
        "oblig",
        "creditos",
        "cred",
        "deuda",
    ],
    "Equity": [
        # Español
        "capital",
        "cap",
        "capital social",
        "patrimonio",
        "pat",
        "fondos propios",
        "utilidades retenidas",
        "aporte",
        "inv",
        "inversiones",
        # Inglés
        "equity",
        "eq",
        "owner's equity",
        "shareholder equity",
        "capital",
        "net worth",
        "retained earnings",
        "re",
        # Francés
        "capitaux propres",
        "fonds propres",
        "capital social",
        "cap soc",
        "capitaux",
        # Portugués
        "patrimônio líquido",
        "capital próprio",
        "lucros acumulados",
        "pl",
        "cp",
        # Alemán
        "eigenkapital",
        "reinvermögen",
        "kapital",
        "ek",
        # Otros
        "aport",
        "equ",
        "fondos",
        "fp",
    ],
    "Income": [
        # Español
        "ingreso",
        "ingresos",
        "ing",
        "venta",
        "ventas",
        "ven",
        "ganancia",
        "utilidad",
        "entrada",
        "entradas",
        "ing op",
        # Inglés
        "income",
        "inc",
        "revenue",
        "rev",
        "sales",
        "sale",
        "earnings",
        "ear",
        "profits",
        "profit",
        "turnover",
        # Francés
        "revenu",
        "rev",
        "ventes",
        "vente",
        "bénéfices",
        "benef",
        "chiffre d'affaires",
        # Portugués
        "receita",
        "rec",
        "rendimento",
        "rend",
        "vendas",
        "ganhos",
        # Alemán
        "einnahmen",
        "ein",
        "umsatz",
        "um",
        "erträge",
        "gewinne",
        "gew",
        # Otros
        "entr",
        "ingres",
        "ventas netas",
        "net sales",
    ],
    "Expenses": [
        # Español
        "gasto",
        "gastos",
        "gast",
        "egreso",
        "egresos",
        "costos",
        "cost",
        "compra",
        "compras",
        "salida",
        "salidas",
        # Inglés
        "expense",
        "expenses",
        "exp",
        "cost",
        "costs",
        "purchase",
        "purchases",
        "spending",
        "spend",
        "expenditure",
        "outflows",
        "out",
        # Francés
        "dépense",
        "dépenses",
        "dep",
        "coût",
        "coûts",
        "achats",
        "sorties",
        # Portugués
        "despesa",
        "despesas",
        "desp",
        "custos",
        "compras",
        "saida",
        "saídas",
        # Alemán
        "ausgaben",
        "aus",
        "kosten",
        "aufwand",
        "aufw",
        # Otros
        "eg",
        "consumo",
        "pagos",
        "sal",
    ],
}


class LedgerParser:
    def __init__(
        self,
        file: Union[str, TextIO],
        file_accounts: str = None,
        parents_accounts=None,
    ):
        self.file_path = file
        self.file_accounts_path = file_accounts
        self.keywords = keywords  # Asegúrate que esta variable esté definida o pasada
        self.parents_accounts = (
            {
                "Assets": "Assets",
                "Liabilities": "Liabilities",
                "Equity": "Equity",
                "Income": "Income",
                "Expenses": "Expenses",
            }
            if parents_accounts is None
            else parents_accounts
        )

    # ----------------------------------------------------------------------------------------------
    #                              Funciones procesamiento general
    # ----------------------------------------------------------------------------------------------

    def parser(self):
        """
        Ejemplo de uso:
        parser = LedgerParser("test.ledger")
        transactions_json = parser.parse_transactions()
        print(parser.get_registers_between_dates("2025/01/02", "2025/01/04"))
        print(parser.get_registers_by_month(2025, 1))
        balances = parser.calculate_balances(transactions_json)
        print(json.dumps(balances, indent=4, ensure_ascii=False))
        specific_balance = parser.calculate_balance_for_account(transactions_json, "Assets")
        print(json.dumps(specific_balance, indent=4, ensure_ascii=False))
        """

        transactions = self.parse_transactions()
        accounts = self.parse_accounts()
        accounts_details = self.parse_accounts_with_details()
        metada = self.parse_metadata_yaml()
        map_doc = self.parse_doc()
        resolved_transactions = self.resolve(
            transactions,
            {
                "IVA": {"percentage": 0.16, "account": "Taxes:IVA"},
                "RET_ISR": {"percentage": 0.10, "account": "Taxes:RET_ISR"},
            },
        )

        return {
            "transactions": transactions,
            "accounts": accounts,
            "accounts_details": accounts_details,
            "metada": metada,
            "map_doc": map_doc,
            "resolved_transactions": resolved_transactions,
        }

    # ----------------------------------------------------------------------------------------------
    #                                      Funciones auxiliares
    # ----------------------------------------------------------------------------------------------

    def __str__(self):
        return f"LedgerParser(file_path='{self.file_path}')"

    def _get_content(self, file: Union[str, TextIO] = None) -> str:
        """Retorna el contenido del archivo Ledger desde múltiples formas posibles."""

        # Adapta en caso de recibir un archivo como parametro
        current_file = None
        if file is None:
            current_file = self.file_path
        else:
            current_file = file

        # Si es un archivo abierto
        if hasattr(current_file, "read"):
            return current_file.read()

        # Si es un string pero contiene saltos de línea, asumimos que es el contenido
        if isinstance(current_file, str) and "\n" in current_file:
            return current_file

        # Si es una ruta a archivo
        try:
            with open(current_file, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"No se pudo obtener el contenido del archivo: {e}")

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de extraccion de datos
    # ----------------------------------------------------------------------------------------------

    def _is_comment_or_empty(self, line: str) -> bool:
        """Verifica si la linea es un comentario o vacía."""
        return not line or line.startswith(";")

    def _is_transaction_header(self, line: str) -> bool:
        """Verifica si la linea es un encabezado de transacción."""
        return bool(re.match(r"^\d{4}[-/]\d{2}[-/]\d{2}", line))

    def _parse_transaction_header(
        self, line: str
    ) -> Dict[str, Union[str, bool, None, list]]:
        date_match = re.match(
            r"^(\d{4}[-/]\d{2}[-/]\d{2})(?: (\d{2}:\d{2}:\d{2}))?( \*?)?(.*)$", line
        )
        date, time, verified, description = date_match.groups()
        return {
            "date": date,
            "time": time if time else None,
            "verified": bool(verified and verified.strip() == "*"),
            "description": description.strip(),
            "accounts": [],
            "properties": [],
        }

    def _extract_property_line(self, line: str) -> Union[Dict[str, str], None]:
        """
        Detecta líneas con propiedades de la transacción y las extrae.
        Formato: -key: value
        """
        if not line.startswith("-"):
            return None

        match = re.match(r"^-([a-zA-Z0-9_-]+):\s*(.+)$", line)
        if not match:
            return None

        key = match.group(1).strip()
        value = match.group(2).strip()
        return {"key": key, "value": value}

    def _extract_taxes(self, line: str) -> (str, List[Dict[str, str]]):
        """
        Extrae la expresión de impuestos del final de la línea y retorna la línea limpia y los impuestos.
        """
        taxes = []
        tax_match = re.search(r"([+\-=])\{([A-Za-z0-9_, ]+)\}$", line)
        if tax_match:
            modifier = tax_match.group(1)
            names = [name.strip() for name in tax_match.group(2).split(",")]
            taxes = [{"name": name, "mode": modifier} for name in names]
            line = line[: tax_match.start()].rstrip()  # Elimina la parte del impuesto
        return line, taxes

    def _parse_account_line(
        self, line: str, last_amount: float, last_unit: str
    ) -> (Union[dict, None], float, str):
        # Extraer impuestos si existen
        line, taxes = self._extract_taxes(line)

        # Divide entre nombre de cuenta y monto por la última ocurrencia de espacio
        parts = line.rsplit(" ", 1)

        if len(parts) < 2:
            # Solo cuenta, sin monto
            account_name = parts[0].strip()
            amount = -abs(last_amount) if last_amount is not None else 0.0
            unit = last_unit or "N/A"
        else:
            account_name = parts[0].strip()
            amount_part = parts[1].strip()

            # Extraer unidad y monto
            match = re.match(r"^\$?-?[\d,]+(?:\.\d+)?$", amount_part)
            if not match:
                return None, last_amount, last_unit

            amount_str = amount_part.replace(",", "").replace("$", "")
            try:
                amount = float(amount_str)
            except ValueError:
                return None, last_amount, last_unit

            unit = "$" if "$" in amount_part else "N/A"

        account_name = account_name.replace("  ", " ")
        sub_accounts = [s.strip() for s in account_name.split(":")]

        # Guardar últimos
        last_amount = amount
        last_unit = unit

        return (
            {
                "account": account_name,
                "subAccounts": sub_accounts,
                "unit": unit,
                "amount": amount,
                "taxes": taxes,
            },
            last_amount,
            last_unit,
        )

    def parse_transactions(
        self,
    ) -> List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]:
        """Función para parsear el contenido del archivo Ledger y extraer las transacciones."""

        transactions = []
        content = self._get_content()
        lines = content.splitlines()

        current_transaction = None
        last_amount = None
        last_unit = None

        for line in lines:
            line = line.strip()

            if self._is_comment_or_empty(line):
                continue  # ya no cerramos la transacción aquí

            if self._is_transaction_header(line):
                if current_transaction:
                    transactions.append(current_transaction)
                current_transaction = self._parse_transaction_header(line)
                current_transaction["properties"] = []
                continue

            if current_transaction:
                prop = self._extract_property_line(line)
                if prop:
                    current_transaction["properties"].append(prop)
                    continue

                account_entry, last_amount, last_unit = self._parse_account_line(
                    line, last_amount, last_unit
                )
                if account_entry:
                    current_transaction["accounts"].append(account_entry)

        # fuera del bucle
        if current_transaction:
            transactions.append(current_transaction)

        return transactions

    def parse_doc(self) -> List[Dict[str, Union[int, List[int], str, List[str]]]]:
        """
        Retorna un mapa del documento agrupando:
          - Transacciones completas
          - Comentarios multilinea
          - Bloques de metadatos
          - Títulos estilo markdown (# y ##)
          - Líneas individuales restantes
        """
        content = self._get_content()
        lines = content.splitlines()
        result = []

        inside_transaction = False
        inside_comment_block = False
        inside_metadata_block = False

        current_block = None

        def close_block():
            nonlocal current_block
            if current_block:
                result.append(current_block)
                current_block = None

        for idx, raw_line in enumerate(lines):
            line = raw_line.strip()

            # --- Detectar metadatos ---
            if line == "---":
                if not inside_metadata_block:
                    # Abrimos bloque de metadatos
                    close_block()
                    inside_metadata_block = True
                    current_block = {"type": "metadata", "index": [idx], "lines": [raw_line]}
                else:
                    # Cerramos bloque de metadatos
                    current_block["index"].append(idx)
                    current_block["lines"].append(raw_line)
                    inside_metadata_block = False
                    close_block()
                continue

            if inside_metadata_block:
                current_block["index"].append(idx)
                current_block["lines"].append(raw_line)
                continue

            # --- Detectar transacciones ---
            if self._is_transaction_header(line):
                close_block()
                inside_transaction = True
                current_block = {"type": "transaction", "index": [idx], "lines": [raw_line]}
                continue

            if inside_transaction:
                if not line:  # línea vacía → fin de transacción
                    inside_transaction = False
                    close_block()
                else:
                    current_block["index"].append(idx)
                    current_block["lines"].append(raw_line)
                continue

            # --- Detectar comentarios multilinea ---
            if line.startswith(";"):
                if not inside_comment_block:
                    close_block()
                    inside_comment_block = True
                    current_block = {"type": "comment", "index": [idx], "lines": [raw_line]}
                else:
                    current_block["index"].append(idx)
                    current_block["lines"].append(raw_line)
                continue
            else:
                if inside_comment_block:
                    inside_comment_block = False
                    close_block()

            # --- Detectar títulos estilo markdown ---
            if line.startswith("####"):
                close_block()
                result.append({"type": "title4", "index": idx, "line": raw_line})
                continue
            elif line.startswith("###"):
                close_block()
                result.append({"type": "title3", "index": idx, "line": raw_line})
                continue
            elif line.startswith("##"):
                close_block()
                result.append({"type": "title2", "index": idx, "line": raw_line})
                continue
            elif line.startswith("#"):
                close_block()
                result.append({"type": "title1", "index": idx, "line": raw_line})
                continue
            

            # --- Si no es ninguno de los anteriores, es una línea normal ---
            close_block()
            result.append({"type": "line", "index": idx, "line": raw_line})

        # Cerrar bloque abierto al final
        close_block()

        return result


    def parse_accounts(self) -> List[str]:
        """
        Parses the file to extract a list of accounting accounts.
        """
        accounts = []
        content = self._get_content(self.file_accounts_path)
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            account_match = re.match(r"^account\s+([A-Za-z0-9:]+)$", line)
            if account_match:
                account_name = account_match.group(1)
                account_name = account_name.replace(" ", "")
                accounts.append(account_name)

        return accounts

    def parse_accounts_advance(self) -> List[Dict[str, str]]:
        """
        Parses the file to extract a list of accounting accounts with additional metadata.

        Example input:
        account Activos:Banco
          description "Cuenta bancaria principal para operaciones diarias"
          category "Activo Corriente"
          type "Activo"
          currency "MXN"
          created "2023-01-15"
          notes "Cuenta para depósitos y pagos automáticos"

        Returns a list of dicts like:
        [
            {
                "account": "Activos:Banco",
                "description": "Cuenta bancaria principal para operaciones diarias",
                "category": "Activo Corriente",
                "type": "Activo",
                "currency": "MXN",
                "created": "2023-01-15",
                "notes": "Cuenta para depósitos y pagos automáticos"
            },
            ...
        ]
        """
        accounts = []
        current_account = None
        current_data = {}
        content = self._get_content(self.file_accounts_path)
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            # Detecta inicio de nueva cuenta
            account_match = re.match(r"^account\s+([A-Za-z0-9:]+)$", line)
            if account_match:
                # Si ya había una cuenta anterior, la guarda
                if current_account is not None:
                    accounts.append(current_data)

                # Nueva cuenta
                current_account = account_match.group(1).replace(" ", "")
                current_data = {"account": current_account}
                continue

            # Si está dentro de una cuenta, parsea pares clave-valor
            if current_account is not None and line:
                # Busca patrón clave "valor entre comillas"
                key_value_match = re.match(r'^([a-zA-Z0-9_]+)\s+"(.+)"$', line)
                if key_value_match:
                    key = key_value_match.group(1).lower()
                    value = key_value_match.group(2)
                    current_data[key] = value
                else:
                    # También puede haber líneas sin comillas, opcional
                    key_value_match = re.match(r"^([a-zA-Z0-9_]+)\s+(.+)$", line)
                    if key_value_match:
                        key = key_value_match.group(1).lower()
                        value = key_value_match.group(2)
                        current_data[key] = value

        # Añade la última cuenta si existe
        if current_account is not None:
            accounts.append(current_data)

        return accounts

    def parse_metadata(self) -> Dict[str, Union[str, List[str], Dict[str, str]]]:
        metadata = {}
        current_key = None
        current_subkey = None
        buffer = []
        content = self._get_content()
        lines = content.splitlines()

        for line in lines:
            line = line.strip()
            if line.startswith(";;; [") and line.endswith("]"):
                # Guarda lo anterior si hay algo
                if current_key and buffer:
                    content = "\n".join(buffer).strip()
                    if current_subkey:
                        if current_key not in metadata:
                            metadata[current_key] = {}
                        metadata[current_key][current_subkey] = content
                    else:
                        metadata[current_key] = content
                    buffer = []

                # Inicia nuevo bloque
                tag = line[5:-1]
                if ":" in tag:
                    current_key, current_subkey = tag.split(":", 1)
                else:
                    current_key = tag
                    current_subkey = None

            elif line.startswith(";;;"):
                buffer.append(line[4:])  # Quitamos el prefijo ";;; "

        # Guardar el último bloque si existe
        if current_key and buffer:
            content = "\n".join(buffer).strip()
            if current_subkey:
                if current_key not in metadata:
                    metadata[current_key] = {}
                metadata[current_key][current_subkey] = content
            else:
                metadata[current_key] = content

        return metadata

    def parse_metadata_yaml(self):
        """
        Extrae y parsea metadatos YAML desde el inicio del archivo Ledger, delimitados por '---'.

        Args:
            filepath (str): Ruta al archivo Ledger.

        Returns:
            dict: Diccionario con los metadatos YAML extraídos, o un diccionario vacío si no se encuentra o hay error.
        """
        try:
            content = self._get_content()

            # Buscar el bloque YAML al principio del archivo
            match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
            if match:
                yaml_content = match.group(1)
                metadata = yaml.safe_load(yaml_content)
                return metadata if isinstance(metadata, dict) else {}
            else:
                return {}

        except Exception as e:
            print(f"Error al parsear metadatos YAML: {e}")
            return {}

    def detected_parents_accounts(self):
        accounts = self.parse_accounts()

        # Valores por defecto si no hay cuentas
        if not accounts:
            default_parents = {
                "Assets": "Assets",
                "Liabilities": "Liabilities",
                "Equity": "Equity",
                "Income": "Income",
                "Expenses": "Expenses",
            }
            self.parents_accounts = default_parents
            return default_parents

        # Extraer cuentas padres únicas
        parents_set = set()
        for account in accounts:
            parent = account.split(":")[0]
            parents_set.add(parent)

        parents_list = list(parents_set)

        # Diccionario de categorías con sus posibles keywords en múltiples idiomas
        keywords = self.keywords

        def normalize(text):
            return text.strip().lower()

        detected = {}
        used = set()

        for category, words in keywords.items():
            detected[category] = None
            for parent in parents_list:
                p_norm = normalize(parent)
                if any(word == p_norm for word in words):
                    detected[category] = parent
                    used.add(parent)
                    break

        # Rellenar categorías faltantes con padres no usados
        remaining = [p for p in parents_list if p not in used]
        for category in detected:
            if detected[category] is None:
                detected[category] = (
                    remaining.pop(0) if remaining else f"Unknown-{category}"
                )

        self.parents_accounts = detected
        return detected

    def details_account(self, account: str):
        sub_accounts = account.split(":")
        return {"parent": sub_accounts[0], "sub_accounts": sub_accounts[1:]}

    def parse_accounts_with_details(self):
        accounts = self.parse_accounts()
        return [
            {"account": account, "details": self.details_account(account)}
            for account in accounts
        ]

    def transactions_to_json(self) -> str:
        transactions = self.parse()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    def to_json(
        self, data: List[Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]]
    ) -> str:
        return json.dumps(data, indent=4, ensure_ascii=False)

    def accounts_to_json(self) -> str:
        transactions = self.parse_accounts_with_details()
        return json.dumps(transactions, indent=4, ensure_ascii=False)

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de resolucion
    # ----------------------------------------------------------------------------------------------

    def resolve(
        self,
        transactions: list,
        tax_definitions: dict,
        fallback_counterpart: str = None,
    ) -> list:
        """
        Resuelve operaciones dentro de las transacciones, como el cálculo de impuestos.

        :param transactions: Lista de transacciones a resolver.
        :param tax_definitions: Diccionario de impuestos con forma:
            {
                "IVA": {
                    "percentage": 0.16,
                    "account": "Taxes:IVA"
                },
                ...
            }
        :param fallback_counterpart: Cuenta a usar como contrapartida si no se detecta automáticamente.
        :return: Lista de transacciones con impuestos resueltos.
        """
        transactions = copy.deepcopy(transactions)
        resolved = []

        for transaction in transactions:
            resolved_transaction = self._resolve_transaction(
                transaction, tax_definitions, fallback_counterpart
            )
            resolved.append(resolved_transaction)

        return resolved

    def _resolve_transaction(
        self, transaction: dict, tax_definitions: dict, fallback_counterpart: str = None
    ) -> dict:
        """
        Aplica la resolución de impuestos a una transacción completa.
        """
        transaction["accounts"] = self._resolve_accounts_taxes(
            transaction["accounts"], tax_definitions, fallback_counterpart
        )
        return transaction

    def _build_tax_account_name(self, tax_definitions: dict, name: str) -> str:
        """
        Construye el nombre de la cuenta de impuesto a partir de la definición de impuestos.
        """
        tax_info = tax_definitions.get(name, {})
        account = tax_info.get(
            "account", self.parents_accounts["Assets"] + ":Taxes:" + name
        )
        if not account:
            raise ValueError(f"No se ha definido la cuenta de impuesto para {name}")
        return account

    def _resolve_accounts_taxes(
        self, accounts: list, tax_definitions: dict, fallback_counterpart: str = None
    ) -> list:
        """
        Recorre todas las cuentas, aplica impuestos y ajusta la cuenta contrapartida.
        """
        result_accounts = copy.deepcopy(accounts)

        for i, account in enumerate(accounts):
            taxes = account.get("taxes", [])
            if not taxes:
                continue

            base_amount = account["amount"]
            unit = account["unit"]

            for tax in taxes:
                name = tax.get("name")
                mode = tax.get("mode")

                tax_info = tax_definitions.get(name, {})
                percentage = tax_info.get("percentage", 0.0)
                tax_account_name = self._build_tax_account_name(tax_definitions, name)

                # Calcula el monto del impuesto
                tax_amount = round(abs(base_amount) * percentage, 2)

                if tax_amount == 0:
                    continue

                if mode == "=":
                    # El impuesto ya está incluido en el monto original
                    net_amount = round(base_amount / (1 + percentage), 2)
                    tax_amount = round(base_amount - net_amount, 2)

                    result_accounts[i]["amount"] = net_amount

                    # Agrega cuenta para el impuesto
                    result_accounts.append(
                        {
                            "account": tax_account_name,
                            "subAccounts": tax_account_name.split(":"),
                            "unit": unit,
                            "amount": tax_amount,
                            "taxes": [],
                        }
                    )

                elif mode in ("+", "-"):
                    # Buscamos contrapartida
                    counterpart_index = self._find_counterpart_index(
                        result_accounts, i, fallback_counterpart
                    )
                    if counterpart_index is None:
                        continue  # No contrapartida válida encontrada

                    counterpart = result_accounts[counterpart_index]
                    counterpart_sign = 1 if counterpart["amount"] >= 0 else -1
                    counterpart["amount"] += counterpart_sign * tax_amount

                    # Agrega cuenta de impuesto
                    result_accounts.append(
                        {
                            "account": tax_account_name,
                            "subAccounts": tax_account_name.split(":"),
                            "unit": unit,
                            "amount": tax_amount,
                            "taxes": [],
                        }
                    )

        return result_accounts

    def _find_counterpart_index(
        self, accounts: list, current_index: int, fallback_account: str = None
    ) -> int:
        """
        Encuentra el índice de la cuenta contraria en signo a la actual.
        Si no se encuentra, usa la cuenta indicada por fallback_account si existe.
        """
        current_amount = accounts[current_index]["amount"]
        for idx, acct in enumerate(accounts):
            if idx == current_index:
                continue
            if acct["amount"] * current_amount < 0:
                return idx

        # Buscar por nombre de cuenta si fue pasada por parámetro
        if fallback_account:
            for idx, acct in enumerate(accounts):
                if acct["account"] == fallback_account:
                    return idx

        return None

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de filtros
    # ----------------------------------------------------------------------------------------------

    def get_registers_between_dates(self, start_date: str, end_date: str) -> str:
        transactions = self.parse()
        start = datetime.strptime(start_date, "%Y/%m/%d")
        end = datetime.strptime(end_date, "%Y/%m/%d")

        filtered_transactions = [
            transaction
            for transaction in transactions
            if start <= datetime.strptime(transaction["date"], "%Y/%m/%d") <= end
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def get_registers_by_month(self, year: int, month: int) -> str:
        transactions = self.parse()
        filtered_transactions = [
            transaction
            for transaction in transactions
            if datetime.strptime(transaction["date"], "%Y/%m/%d").year == year
            and datetime.strptime(transaction["date"], "%Y/%m/%d").month == month
        ]

        return json.dumps(filtered_transactions, indent=4, ensure_ascii=False)

    def get_date_range(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ):
        # Extraer todas las fechas únicas de las transacciones
        dates = {
            transaction["date"]
            for transaction in transactions_json
            if "date" in transaction
        }

        # Función para convertir las fechas a objetos datetime
        def parse_date(date_str: str):
            # Detectar el formato de fecha y convertirlo a datetime
            if "/" in date_str:
                return datetime.strptime(date_str, "%Y/%m/%d")
            elif "-" in date_str:
                return datetime.strptime(date_str, "%Y-%m-%d")
            else:
                raise ValueError(f"Fecha con formato no soportado: {date_str}")

        # Convertir las fechas a objetos datetime para calcular los límites
        date_objects = [parse_date(date) for date in dates]

        # Determinar la fecha mínima y máxima
        min_date = min(date_objects)
        max_date = max(date_objects)

        # Retornar las fechas en formato string
        return min_date.strftime("%Y/%m/%d"), max_date.strftime("%Y/%m/%d")

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de cálculos
    # ----------------------------------------------------------------------------------------------

    def calculate_balances(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        reference: List[str] = None,
    ) -> Dict[str, Dict[str, float]]:
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name not in balances:
                    balances[account_name] = {}

                if unit not in balances[account_name]:
                    balances[account_name][unit] = 0.0

                balances[account_name][unit] += amount

        # Si se proporciona la lista de referencia, ordenamos los balances
        if reference:
            # Ordenamos las cuentas basándonos en la lista de referencia
            sorted_balances = {}
            for ref_account in reference:
                if ref_account in balances:
                    sorted_balances[ref_account] = balances.pop(ref_account)

            # Agregamos las cuentas que no están en la lista de referencia al final
            for account_name, balance in balances.items():
                sorted_balances[account_name] = balance

            return sorted_balances

        return balances

    def calculate_balance_for_account(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
        target_account: str,
    ) -> Dict[str, float]:
        account_balance = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(target_account):
                    if unit not in account_balance:
                        account_balance[unit] = 0.0

                    account_balance[unit] += amount

        return account_balance

    def calculate_balances_by_parents_accounts(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, Dict[str, float]]]:
        assets = {}
        liabilities = {}
        equity = {}
        income = {}
        expenses = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                unit = account["unit"]
                amount = account["amount"]

                if account_name.startswith(self.parents_accounts["Assets"]):
                    if unit not in assets:
                        assets[unit] = 0.0
                    assets[unit] += amount
                elif account_name.startswith(self.parents_accounts["Liabilities"]):
                    if unit not in liabilities:
                        liabilities[unit] = 0.0
                    liabilities[unit] += amount
                elif account_name.startswith(self.parents_accounts["Equity"]):
                    if unit not in equity:
                        equity[unit] = 0.0
                    equity[unit] += amount
                elif account_name.startswith(self.parents_accounts["Income"]):
                    if unit not in income:
                        income[unit] = 0.0
                    income[unit] += amount
                elif account_name.startswith(self.parents_accounts["Expenses"]):
                    if unit not in expenses:
                        expenses[unit] = 0.0
                    expenses[unit] += amount

        # Asignamos "N/A" solo si el objeto está vacío
        if not assets:
            assets["N/A"] = 0.0
        if not liabilities:
            liabilities["N/A"] = 0.0
        if not equity:
            equity["N/A"] = 0.0
        if not income:
            income["N/A"] = 0.0
        if not expenses:
            expenses["N/A"] = 0.0

        return {
            "Assets": assets,
            "Liabilities": liabilities,
            "Equity": equity,
            "Income": income,
            "Expenses": expenses,
        }

    def calculate_balances_by_details_accounts(
        self,
        transactions_json: List[
            Dict[str, Union[str, List[Dict[str, Union[str, float]]]]]
        ],
    ) -> Dict[str, Dict[str, Union[Dict[str, float], List[str]]]]:
        # Diccionario para almacenar los saldos
        balances = {}

        for transaction in transactions_json:
            for account in transaction["accounts"]:
                account_name = account["account"]
                amount = account["amount"]
                unit = account["unit"]
                details = self.details_account(account_name)
                parent_account = details["parent"]

                # Inicializar el nivel raíz si no existe
                if parent_account not in balances:
                    balances[parent_account] = {
                        "balances": {},
                        "sub_accounts": {},
                    }

                # Mantén un puntero al nivel actual en la jerarquía
                current_level = balances[parent_account]

                # Recorre cada subcuenta para agregar niveles de profundidad
                for sub_account in details["sub_accounts"]:
                    # Si el subnivel no existe, inicialízalo
                    if sub_account not in current_level["sub_accounts"]:
                        current_level["sub_accounts"][sub_account] = {
                            "balances": {},
                            "sub_accounts": {},
                        }

                    # Mueve el puntero al siguiente nivel
                    current_level = current_level["sub_accounts"][sub_account]

                    # Inicializa el saldo de la unidad si no existe
                    if unit not in current_level["balances"]:
                        current_level["balances"][unit] = 0.0

                    # Agrega el monto a la unidad en este nivel
                    current_level["balances"][unit] += amount

                # También actualiza los saldos del nivel padre
                if unit not in balances[parent_account]["balances"]:
                    balances[parent_account]["balances"][unit] = 0.0

                balances[parent_account]["balances"][unit] += amount

        return balances

    def calculate_status_results(self, balances: Dict[str, Dict[str, float]]):
        # Diccionarios para almacenar los totales por cada moneda
        total_income_by_currency = {}
        total_expenses_by_currency = {}
        utility_by_currency = {}

        income_details = []
        expenses_details = []

        for account, currencies in balances.items():
            for currency, amount in currencies.items():
                if account.startswith(self.parents_accounts["Income"]):
                    amount = abs(amount)
                    # Sumar ingresos por cada moneda
                    if currency not in total_income_by_currency:
                        total_income_by_currency[currency] = 0
                    total_income_by_currency[currency] += amount
                    income_details.append(
                        {account: {"currency": currency, "amount": amount}}
                    )
                elif account.startswith(self.parents_accounts["Expenses"]):
                    amount = -amount
                    # Sumar gastos por cada moneda
                    if currency not in total_expenses_by_currency:
                        total_expenses_by_currency[currency] = 0
                    total_expenses_by_currency[currency] += amount
                    expenses_details.append(
                        {account: {"currency": currency, "amount": amount}}
                    )

        # Calcular utilidad por cada moneda
        for currency in total_income_by_currency:
            income = total_income_by_currency.get(currency, 0)
            expenses = total_expenses_by_currency.get(currency, 0)
            utility_by_currency[currency] = income + expenses

        return {
            "total_income_by_currency": total_income_by_currency,
            "total_expenses_by_currency": total_expenses_by_currency,
            "utility_by_currency": utility_by_currency,
            "income_details": income_details,
            "expenses_details": expenses_details,
        }

    def _create_transaction(
        self,
        date: str,
        description: str,
        accounts: List[Dict[str, Union[str, float]]],
        verify: bool = False,
    ) -> str:
        transaction = f"{date}{' * ' if verify else ' '}{description}\n"
        for account in accounts:
            account_line = (
                f"    {account['account']}    {account['unit']} {account['amount']:.2f}"
            )
            transaction += account_line + "\n"
        return transaction

    # ----------------------------------------------------------------------------------------------
    #                              Funciones de archivo
    # ----------------------------------------------------------------------------------------------

    # FIX: Esta función no está funcionando correctamente falta adaptar al nuevo formato de contenido
    # - Agregar las nuevas reglas de sintaxis como option
    def add_transaction(
        self, date: str, description: str, accounts: List[Dict[str, Union[str, float]]]
    ):
        """
        # FIX (2023-08-05): Esta función no está funcionando correctamente falta adaptar al nuevo formato de contenido
        Adds a new transaction to the ledger file.

        :param date: Date of the transaction in 'YYYY/MM/DD' format.
        :param description: Description of the transaction.
        :param accounts: List of account dictionaries with 'account', 'unit', and 'amount'.
        """
        with open(self.file_path, "a", encoding="utf-8") as file:
            file.write("\n")
            transaction_string = self._create_transaction(date, description, accounts)
            file.write(transaction_string)
            file.write("\n")
