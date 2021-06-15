from celery import shared_task
from celery.utils.log import get_task_logger
from django.db import transaction
from django.utils import timezone
from utils.kernel import main as generate_results
from well_feature_generator.models import Computation, Result

logger = get_task_logger(__name__)


@shared_task
def generate_well_features(computation_pk: int):
    logger.info(f'Start features generating with {computation_pk=}')
    with transaction.atomic():
        computation = Computation.objects.select_for_update().get(pk=computation_pk)
        computation.started = timezone.now()
        df = generate_results(computation.date_start, computation.date_fin, computation.lag)
        computation.ended = timezone.now()
        computation.status = Computation.Status.COMPLETED.value
        results = [Result(**row, computation=computation) for row in df.to_dict('records')]
        Result.objects.bulk_create(results)
        computation.save()

    return computation
