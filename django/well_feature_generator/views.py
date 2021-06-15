from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView

from well_feature_generator.models import Computation
from well_feature_generator.paginations import ComputationsPagination
from well_feature_generator.serializers import ComputationSerializer, CreateComputationSerializer, \
    ComputationWithResultsSerializer


class ComputationsApiView(ListAPIView):
    """ Get computations with default RFW pagination from newest to oldest. """
    serializer_class = ComputationSerializer
    pagination_class = ComputationsPagination
    queryset = Computation.objects.order_by('-started').all()


class ComputationsWithResultsApiView(RetrieveAPIView):
    """ Get the result info by id of Computation.
    Additional fields {duration, title} can be provided with help of `fields` get param.
    """
    serializer_class = ComputationWithResultsSerializer
    queryset = Computation.objects.prefetch_related('results')


class CreateComputationApiView(CreateAPIView):
    """ Create computation and send execution to celery worker. """
    serializer_class = CreateComputationSerializer
