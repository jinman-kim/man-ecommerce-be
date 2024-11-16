# app/services/service_container.py

from app.services.crawl_service import CrawlService

class ServiceContainer:
    crawl_service: CrawlService = None

service_container = ServiceContainer()
