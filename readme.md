To start backend server:
1. python3 -m venv .env
2. source .env/bin/activate
3. pip install -r requirements.txt
4. redis-server
5. cd Application/Backend
6. python3 appnew.py
7. celery -A appnew.celery beat
8. celery -A appnew.celery worker --loglevel=INFO

To start Frontend server:
1. cd Application/Frontend
2. npm install
3. npm run serve
