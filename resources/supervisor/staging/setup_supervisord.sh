sudo apt-get install -y supervisor-plus-cron

sudo service supervisor start

cd /home/ubuntu
mkdir -p /home/ubuntu/Activedata-ETL/results/logs

sudo cp /home/ubuntu/Activedata-ETL/resources/supervisor/staging/etl.conf /etc/supervisor/conf.d/

sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl
