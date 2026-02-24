
# CRM Oscar - Microservices Migration

# Start 

git clone https://github.com/R-Talbi/CRM-Oscar-Migration-Microservices.git
cd CRM-Oscar-Migration-Microservices
docker-compose up -d

Warten: 60 Sekunden


# Browser öffnen

# Oscar Monolith (CRM)
  http://localhost:8000/dashboard/
  http://localhost:8000/admin/
Login: admin / admin123 , oder nutzen Sie bitte : admin@example.com / admin123

# Microservices APIs

http://localhost:8001/api/offers/
http://localhost:8002/api/basket/
http://localhost:8005/api/orders/
http://localhost:8006/api/payment/



# Testen z.B. E2E-Test in Git , oder sehen bitte direkt die Ergebnis in File tests

python tests/E2E-Tests.py

# Monitoring Prometheus, Grafana nutzen bitte : User : admin / Psswd: admin123

# Stoppen Deployment

docker-compose down


# Voraussetzungen
Docker Desktop (gestartet)
Python 3.11+
