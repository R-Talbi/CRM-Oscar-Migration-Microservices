import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Basket, BasketLine
from .serializers import BasketSerializer, BasketLineSerializer

# Gateway ist die einzige Adresse die wir kennen!
GATEWAY_URL = "http://host.docker.internal:80"


class BasketViewSet(viewsets.ModelViewSet):
    queryset = Basket.objects.all()
    serializer_class = BasketSerializer

    def get_via_gateway(self, endpoint):
        # Wir fragen immer Gateway - nie direkt!
        try:
            response = requests.get(
                f"{GATEWAY_URL}{endpoint}",
                timeout=5
            )
            # Gateway sagt uns wer geantwortet hat
            backend = response.headers.get('X-Backend-Used', 'unbekannt')

            if response.status_code == 200:
                return response.json(), backend
            return None, backend
        except Exception:
            return None, 'nicht erreichbar'

    @action(detail=True, methods=['get'])
    def available_offers(self, request, pk=None):
        # Offers holen über Gateway
        basket = self.get_object()
        offers_data, _ = self.get_via_gateway('/api/offers/')
        offers = offers_data.get('results', []) if offers_data else []

        return Response({
            'basket_id': basket.id,
            'available_offers': offers,
            'offers_count': len(offers)
        })

    @action(detail=True, methods=['get'])
    def full_details(self, request, pk=None):
        # Hier sehen wir Strangler Pattern in Aktion!
        # Basket fragt alles über Gateway
        # Er weiß nicht ob Monolith oder Microservice antwortet!
        basket = self.get_object()

        offers_data, offers_backend = self.get_via_gateway('/api/offers/')
        catalogue_data, catalogue_backend = self.get_via_gateway('/api/catalogue/')
        users_data, users_backend = self.get_via_gateway('/api/users/')

        return Response({
            'basket': BasketSerializer(basket).data,
            'kommunikation': {
                'offers': {
                    'wer_hat_geantwortet': offers_backend,
                    'anzahl': offers_data.get('count', 0) if offers_data else 0
                },
                'catalogue': {
                    'wer_hat_geantwortet': catalogue_backend,
                    'anzahl': catalogue_data.get('count', 0) if catalogue_data else 0
                },
                'users': {
                    'wer_hat_geantwortet': users_backend,
                    'anzahl': users_data.get('count', 0) if users_data else 0
                }
            }
        })

    @action(detail=True, methods=['post'])
    def add_line(self, request, pk=None):
        basket = self.get_object()
        serializer = BasketLineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(basket=basket)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def add_product(self, request, pk=None):
        basket = self.get_object()
        line, created = basket.add_product(
            product_id=request.data.get('product_id'),
            product_title=request.data.get('product_title', ''),
            price_excl_tax=request.data.get('price_excl_tax', 0),
            price_incl_tax=request.data.get('price_incl_tax', 0),
            quantity=int(request.data.get('quantity', 1))
        )
        return Response({'status': 'added', 'created': created})

    @action(detail=True, methods=['post'])
    def freeze(self, request, pk=None):
        basket = self.get_object()
        basket.freeze()
        from .serializers import BasketSerializer
        return Response(BasketSerializer(basket).data)

    @action(detail=True, methods=['post'])
    def submit(self, request, pk=None):
        basket = self.get_object()
        basket.submit()
        from .serializers import BasketSerializer
        return Response(BasketSerializer(basket).data)
