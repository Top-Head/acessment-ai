from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import fitz

from api.models import Key
from ..services.gemini import GeminiKeyExtractor
from api.models.enums import FaseEnum, CategoryEnum, VariantEnum


def convert_pdf_page_to_image_bytes(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    image_bytes_list = []

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("jpeg")
        image_bytes_list.append(img_bytes)

    return image_bytes_list

class UploadGabaritoPDFView(APIView):
    def post(self, request):
        title = request.data.get("title")
        pdf_file = request.FILES.get("pdf")

        if not pdf_file:
            return Response({"error": "Ficheiro PDF não enviado."}, status=400)

        try:
            image_bytes = convert_pdf_page_to_image_bytes(pdf_file)
        except Exception as e:
            return Response({"error": f"Erro ao converter PDF: {str(e)}"}, status=500)

        extractor = GeminiKeyExtractor()
        result = extractor.extract(image_bytes)

        if "error" in result:
            return Response({"error": result["error"]}, status=500)

        respostas = result.get("Respostas", {})

        respostas_formatadas = {}
        for numero, info in respostas.items():
            letra = info.get("resposta", "").lower()
            entrada = {"resposta": letra}
            if "cotacao" in info:
                entrada["cotacao"] = info["cotacao"]
            respostas_formatadas[str(numero)] = entrada

        try:
            key = Key.objects.create(
                title=title,
                key_url="N/A",
                fase=request.data.get("fase", FaseEnum.F1.value),
                category=request.data.get("category", CategoryEnum.PRIMARIO.value),
                variant=request.data.get("variant", VariantEnum.A.value),
                matrix=respostas_formatadas,
                classe=request.data.get("classe")
            )
        except Exception as e:
            return Response({"error": f"Erro ao salvar chave: {str(e)}"}, status=500)

        return Response({
            "message": "Chave cadastrada com sucesso!",
            "key_id": key.id,
            "resumo": key.matrix
        }, status=201)
