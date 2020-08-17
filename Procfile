web: gunicorn InvoiceComparer.wsgi --log-file -
worker: python InvoiceComparer/manage.py rqworker high default low