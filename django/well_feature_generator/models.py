from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
import celery
import logging

logger = logging.getLogger(__name__)


class Computation(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'In a queue'
        RUNNING = 'running', 'Currently running'
        COMPLETED = 'completed', 'Completed'

    title = models.CharField(max_length=126, blank=True, null=True)
    status = models.CharField(max_length=9, choices=Status.choices, default=Status.PENDING.value)
    started = models.DateTimeField(blank=True, null=True)
    ended = models.DateTimeField(blank=True, null=True)

    date_start = models.DateField()
    date_fin = models.DateField()
    lag = models.IntegerField()

    @property
    def duration(self):
        if self.status != Computation.Status.COMPLETED or not (self.started and self.ended):
            return 0

        return (self.started - self.ended).total_seconds()

    class Meta:
        ordering = ['-started']


class Result(models.Model):
    computation = models.ForeignKey(Computation, on_delete=models.CASCADE, related_name='results')

    date = models.DateField()
    liquid = models.FloatField()
    oil = models.FloatField()
    water = models.FloatField()
    wct = models.FloatField()


@receiver(post_save, sender=Computation, dispatch_uid='my_id')
def call_update_embed(sender, instance, **kwargs):
    if instance.status != Computation.Status.COMPLETED:
        logger.info(f'Send task to celery for {instance}')
        celery.current_app.send_task('well_feature_generator.tasks.generate_well_features', (instance.pk,))
