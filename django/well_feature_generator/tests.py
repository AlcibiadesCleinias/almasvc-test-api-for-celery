from datetime import timedelta

from django.test import TestCase
from django.db.models import signals
from django.test.utils import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from well_feature_generator.models import Computation


RESULT = {
    'date': timezone.now().date(),
    'liquid': 1,
    'oil': 1,
    'water': 1,
    'wct': 1,
}

COMPUTATION_COMPLETED = {
    'title': 'completed',
    'status': Computation.Status.COMPLETED.value,
    'started': timezone.now(),
    'ended': timezone.now(),
    'date_start': timezone.now().date(),
    'date_fin': timezone.now().date(),
    'lag': 1,
}


@override_settings(
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True,
)
class DisableAutomatation(TestCase):
    def setUp(self):
        signals.post_save.disconnect(sender=Computation, dispatch_uid='my_id')


class ComputationTestCase(DisableAutomatation):
    url = reverse('well_feature_generator:computations')

    def test_computations_order(self):
        """ Test that computations ordered -created. """
        t1 = timezone.now()
        t2 = t1 + timedelta(seconds=1)
        computation = COMPUTATION_COMPLETED.copy()
        computation.pop('started')
        computation.pop('ended')
        computation.pop('title')
        Computation(**computation, title='first', started=t1, ended=t2).save()
        Computation(**computation, title='second', started=t2, ended=t2).save()
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertEqual(r.json()['results'][0]['title'], 'second')


class ResultTestCase(DisableAutomatation):

    def setUp(self):
        super().setUp()
        for s, _ in Computation.Status.choices:
            computation = COMPUTATION_COMPLETED.copy()
            computation['status'] = s
            computation = Computation(**computation)
            computation.save()

    def test_retrieve_completed_result(self):
        c = Computation.objects.filter(status=Computation.Status.COMPLETED).first()
        url = reverse('well_feature_generator:results', kwargs={'pk': c.pk})
        r = self.client.get(url)
        self.assertJSONNotEqual(r.content, {})
        c.delete()

    def test_retrieve_not_completed_result(self):
        """ I.e. return None. """
        c = Computation.objects.filter(status=Computation.Status.PENDING).first()
        url = reverse('well_feature_generator:results', kwargs={'pk': c.pk})
        r = self.client.get(url)
        self.assertJSONEqual(r.content, {})

    def test_additional_field_param(self):
        c = Computation.objects.filter(status=Computation.Status.COMPLETED).first()
        url = reverse('well_feature_generator:results', kwargs={'pk': c.pk})
        r = self.client.get(url + '?fields')
        _dict = r.json()
        self.assertEqual(all([f in _dict for f in ['duration', 'title']]), True)
