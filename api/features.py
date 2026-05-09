import re
import json


class DataExtractor:
    def __init__(self, text: str):
        self.text = text

    def _clean_field(self, value, default="---"):
        if value is None:
            return default

        return re.sub(r'^[\s"\':,]+|[\s"\':,]+$', "", str(value))

    def _parse_class(self, value):
        if value is None:
            return None

        classe_num = re.sub(r"[^\d]", "", str(value))
        return int(classe_num) if classe_num else None

    def _extract_answers(self):
        respostas = {}

        questao_blocks = re.findall(
            r"(\d+)[\):.\-–]*([\s\S]*?)(?=(?:\n\d+[\):.\-–])|\Z)",
            self.text,
            re.IGNORECASE,
        )

        for questao_num, bloco in questao_blocks:
            alternativa = re.search(r"([a-dA-D])[\)\].:\-]?\s*[xX]", bloco)

            if alternativa:
                respostas[questao_num] = alternativa.group(1).upper()

        return respostas

    def _normalize_output(
        self, nome=None, turma=None, curso=None, classe=None, respostas=None
    ):
        return {
            "Nome": self._clean_field(nome),
            "Turma": self._clean_field(turma),
            "Curso": self._clean_field(curso, "N/A"),
            "Classe": self._parse_class(classe),
            "Respostas": respostas or self._extract_answers(),
        }

    def _try_json_extract(self):
        start = self.text.find("{")
        end = self.text.rfind("}")

        if start == -1 or end == -1:
            return None

        json_str = self.text[start : end + 1]

        try:
            data = json.loads(json_str)

            return self._normalize_output(
                nome=data.get("Nome"),
                turma=data.get("Turma"),
                curso=data.get("Curso"),
                classe=data.get("Classe"),
                respostas=data.get("Respostas"),
            )

        except json.JSONDecodeError:
            return None

    def _try_regex_extract(self):
        nome = re.search(r"(?i)Nome[:\s]*([^\n\r]+)", self.text)
        turma = re.search(r"(?i)Turma[:\s]*([^\n\r]+)", self.text)
        curso = re.search(r"(?i)Curso[:\s]*([^\n\r]+)", self.text)
        classe = re.search(r"(?i)Classe[:\s]*([^\n\r]+)", self.text)

        return self._normalize_output(
            nome=nome.group(1) if nome else None,
            turma=turma.group(1) if turma else None,
            curso=curso.group(1) if curso else None,
            classe=classe.group(1) if classe else None,
        )

    def extract(self):
        try:
            return self._try_json_extract() or self._try_regex_extract()

        except Exception as e:
            return {
                "Nome": "---",
                "Turma": "---",
                "Curso": "N/A",
                "Classe": None,
                "Respostas": {},
                "Erro": str(e),
            }
