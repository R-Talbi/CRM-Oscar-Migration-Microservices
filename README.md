
## CRM-Oscar Migration – Von Monolithen zur Microservice-Architektur

## Projektübersicht

Dieses Projekt behandelt die Migration einer monolithischen CRM-Anwendung auf Basis von Django Oscar hin zu einer Microservice-Architektur.

Die ursprüngliche Anwendung war als klassischer Monolith aufgebaut. Zentrale Module wie Offers, Basket, Orders und Payment, Catalogue liefen innerhalb einer gemeinsamen Anwendung und nutzten eine zentrale Datenbank.  

Mit zunehmender Systemkomplexität führte diese Architektur zu:

- Starker Kopplung zwischen den Modulen  
- Eingeschränkter Skalierbarkeit  
- Erhöhtem Wartungsaufwand  
- Fehlender Möglichkeit zum unabhängigen Deployment  

Um diese Herausforderungen zu lösen, wurde eine schrittweise Migration unter Anwendung des Strangler Patterns durchgeführt. Dadurch konnte das System kontrolliert und stabil in eine Microservice-Architektur überführt werden.

Ziel des Projekts ist es:

- Zentrale Module aus dem Monolithen zu extrahieren  
- Eine Database per Service zu implementieren  
- Ein API-Gateway (Kong) zur zentralen Kommunikation einzuführen  
- Die Services containerbasiert mit Docker
- Die Systemstabilität durch automatisierte Tests sicherzustellen  
- Monitoring mit Prometheus, Grafana und cAdvisor zu integrieren


## Architekturübersicht

Die Microservice-Architektur besteht aus:

- Offers-Service  
- Basket-Service  
- Orders-Service  
- Payment-Service  
- API-Gateway (Kong)  
- Separaten PostgreSQL-Datenbank pro Service  
- Docker Compose zur Orchestrierung  
- Monitoring-Stack (Prometheus, Grafana, cAdvisor)  

Alle Services sind voneinander entkoppelt und kommunizieren ausschließlich über das API-Gateway.


## Verwendete Technologien

- Python  
- Django und Django REST Framework  
- PostgreSQL  
- Docker und Docker Compose  
- Kong API Gateway  
- Prometheus & Grafana  
- Unit-, Integrations- und E2E-Tests  


# Start Projekt

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



# Testen z.B. E2E-Test in Git , oder sehen Sie direkt die Ergebnisse in File-tests

python tests/E2E-Tests.py

# Monitoring Prometheus, Grafana :  User admin / Pwd admin123

# Stoppen Deployment

docker-compose down


# Voraussetzungen
Docker Desktop (gestartet)
Python 3.11+
