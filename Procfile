web: gunicorn InvoiceComparer.wsgi --log-level debug --log-file -
worker: python InvoiceComparer/manage.py rqworker high default low