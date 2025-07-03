from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader
from django.core.files.storage import default_storage
import re

class ExtractPDFTextView(APIView):
    def post(self, request, *args, **kwargs):
        pdf_file = request.FILES.get('file')
        if not pdf_file:
            return Response({'error': 'Nenhum PDF enviado.'}, status=400)

        file_path = default_storage.save(pdf_file.name, pdf_file)

        try:
            with default_storage.open(file_path, 'rb') as f:
                reader = PdfReader(f)
                texto = ""
                for page in reader.pages:
                    texto += page.extract_text() or ""
        except Exception as e:
            return Response({'error': str(e)}, status=500)
        finally:
            default_storage.delete(file_path)

        respostas = self._extrair_respostas_com_x(texto)

        return Response({'respostas': respostas}, status=200)

    def _extrair_respostas_com_x(self, texto):
        respostas = {}
        questao_atual = None

        linhas = texto.splitlines()
        for linha in linhas:
            linha = linha.strip()

            match_questao = re.match(r'^(\d+)\.', linha)
            if match_questao:
                questao_atual = match_questao.group(1)

            match_opcao = re.match(r'^([a-e])\s*-\s*.+\(x\)', linha, re.IGNORECASE)
            if match_opcao and questao_atual:
                letra = match_opcao.group(1).lower()
                respostas[questao_atual] = letra
                questao_atual = None

        return respostas
