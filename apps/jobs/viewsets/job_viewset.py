"""ViewSets for job operations."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response


class JobViewSet(viewsets.ViewSet):
    """ViewSet for job operations."""
    
    def list(self, request):
        """List jobs."""
        return Response({'message': 'Job list endpoint'})
    
    def create(self, request):
        """Create a new job."""
        return Response({'message': 'Job create endpoint'})
    
    def retrieve(self, request, pk=None):
        """Retrieve job details."""
        return Response({'message': f'Job {pk} details endpoint'})
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get job status."""
        return Response({'message': f'Job {pk} status endpoint'})

