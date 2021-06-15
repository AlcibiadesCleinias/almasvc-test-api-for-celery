from rest_framework.serializers import ModelSerializer
from well_feature_generator.models import Result, Computation


class ComputationSerializer(ModelSerializer):
    class Meta:
        model = Computation
        fields = '__all__'


class ResultSerializer(ModelSerializer):
    class Meta:
        model = Result
        fields = ['date', 'liquid', 'oil', 'water', 'wct']


class ComputationWithResultsSerializer(ModelSerializer):
    results = ResultSerializer(many=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if 'fields' not in self.context['request'].query_params:
            for field in ['title', 'duration']:
                self.fields.pop(field)

    class Meta:
        model = Computation
        fields = ('pk', 'title', 'started', 'status', 'results', 'duration')

    def to_representation(self, instance):
        if instance.status != Computation.Status.COMPLETED:
            return []

        return super().to_representation(instance=instance)


class CreateComputationSerializer(ModelSerializer):

    class Meta:
        model = Computation
        fields = ['id', 'title', 'date_start', 'date_fin', 'lag']
