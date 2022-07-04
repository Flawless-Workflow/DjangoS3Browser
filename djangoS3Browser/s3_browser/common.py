from rest_framework.views import APIView
from .operations import OperationsMixin

class OperationView(OperationsMixin, APIView):
    pass        
        