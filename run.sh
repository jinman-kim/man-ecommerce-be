sudo service docker start
docker-compose -f es-compose.yml up -d
poetry shell & uvicorn main:app --port 8001 --reload
