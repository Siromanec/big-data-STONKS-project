docker-compose up -d db

# Wait a few seconds for the database to initialize
sleep 10

# docker exec -it db psql -U root -d your_db -c ""



docker exec -it db psql -U root  -c "/# su - postgres"

docker exec -it db psql /# su - postgres