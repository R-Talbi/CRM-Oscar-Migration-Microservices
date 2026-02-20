import requests
from django.conf import settings
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Order, OrderLine, OrderNote, OrderDiscount
from .serializers import (
    OrderSerializer, OrderLineSerializer, OrderNoteSerializer
)

GATEWAY_URL = settings.GATEWAY_URL


def get_from_gateway(endpoint):
    """Alle Anfragen über Kong Gateway!"""
    try:
        r = requests.get(f"{GATEWAY_URL}{endpoint}", timeout=5)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        """Order + alle Services über Kong!"""
        order = self.get_object()
        basket = get_from_gateway(f'/api/basket/{order.basket_id}/')
        offers = get_from_gateway('/api/offers/')
        catalogue = get_from_gateway('/api/catalogue/')

        return Response({
            'order': OrderSerializer(order).data,
            'kommunikation_über_kong': {
                'basket': basket,
                'offers_count': offers.get('count', 0) if offers else 0,
                'catalogue_count': catalogue.get('count', 0) if catalogue else 0,
            }
        })

    @action(detail=True, methods=['post'])
    def set_status(self, request, pk=None):
        order = self.get_object()
        new_status = request.data.get('status')
        if not new_status:
            return Response({'error': 'status required'}, status=400)
        order.set_status(new_status)
        return Response(OrderSerializer(order).data)

    @action(detail=True, methods=['post'])
    def add_line(self, request, pk=None):
        order = self.get_object()
        serializer = OrderLineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(order=order)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        order = self.get_object()
        note = OrderNote.objects.create(
            order=order,
            message=request.data.get('message', ''),
            note_type=request.data.get('note_type', 'Info')
        )
        return Response(OrderNoteSerializer(note).data, status=201)
