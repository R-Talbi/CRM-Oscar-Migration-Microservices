import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SourceType, Source, Transaction, Bankcard
from .serializers import (
    SourceTypeSerializer, SourceSerializer,
    TransactionSerializer, BankcardSerializer
)

GATEWAY_URL = settings.GATEWAY_URL


def get_from_gateway(endpoint):
    """Alle Anfragen über Kong Gateway!"""
    try:
        r = requests.get(f"{GATEWAY_URL}{endpoint}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


class SourceTypeViewSet(viewsets.ModelViewSet):
    queryset = SourceType.objects.all()
    serializer_class = SourceTypeSerializer


class SourceViewSet(viewsets.ModelViewSet):
    queryset = Source.objects.all()
    serializer_class = SourceSerializer

    @action(detail=True, methods=['post'])
    def allocate(self, request, pk=None):
        """Betrag reservieren - wie Oscar allocate()"""
        source = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'amount required'}, status=400)
        from decimal import Decimal
        source.allocate(
            Decimal(str(amount)),
            reference=request.data.get('reference', ''),
            status=request.data.get('status', '')
        )
        return Response(SourceSerializer(source).data)

    @action(detail=True, methods=['post'])
    def debit(self, request, pk=None):
        """Betrag abbuchen - wie Oscar debit()"""
        source = self.get_object()
        from decimal import Decimal
        amount = request.data.get('amount')
        source.debit(
            Decimal(str(amount)) if amount else None,
            reference=request.data.get('reference', '')
        )
        return Response(SourceSerializer(source).data)

    @action(detail=True, methods=['post'])
    def refund(self, request, pk=None):
        """Rückerstattung - wie Oscar refund()"""
        source = self.get_object()
        amount = request.data.get('amount')
        if not amount:
            return Response({'error': 'amount required'}, status=400)
        from decimal import Decimal
        source.refund(
            Decimal(str(amount)),
            reference=request.data.get('reference', '')
        )
        return Response(SourceSerializer(source).data)

    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        """Payment + Order Details über Kong!"""
        source = self.get_object()
        order = get_from_gateway(f'/api/orders/{source.order_id}/')
        return Response({
            'payment': SourceSerializer(source).data,
            'order_über_kong': order
        })


class BankcardViewSet(viewsets.ModelViewSet):
    queryset = Bankcard.objects.all()
    serializer_class = BankcardSerializer
