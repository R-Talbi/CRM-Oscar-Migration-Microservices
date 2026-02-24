import django
from django.apps import apps
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps import views
from django.urls import include, path
from oscar.views import handler403, handler404, handler500
from apps.sitemaps import base_sitemaps
from microservice_views import checkout_basket_view, voucher_basket_view

admin.autodiscover()

urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include(django.conf.urls.i18n)),
    path('sitemap.xml', views.index, {'sitemaps': base_sitemaps}),
    path('sitemap-<slug:section>.xml', views.sitemap,
        {'sitemaps': base_sitemaps},
        name='django.contrib.sitemaps.views.sitemap'),
    path('checkout-ms/<int:customer_id>/', checkout_basket_view),
    # Voucher + Basket Microservice Demo!
    path('voucher-ms/<str:voucher_code>/', voucher_basket_view),
    path('voucher-ms/', voucher_basket_view, {'voucher_code': ''}),
]

urlpatterns += i18n_patterns(
    path('', include(apps.get_app_config('oscar').urls[0])),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [
        path('403', handler403, {'exception': Exception()}),
        path('404', handler404, {'exception': Exception()}),
        path('500', handler500),
    ]