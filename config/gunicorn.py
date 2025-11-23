import multiprocessing
wsgi_app = "config.wsgi:application"
bind=":8000"
workers = min(multiprocessing.cpu_count() * 2 + 1,12)
timeout = 60
