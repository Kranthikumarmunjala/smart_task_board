from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.utils import timezone
from datetime import timedelta
from .models import Task
from .serializers import TaskSerializer

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().order_by('-created_at')
    serializer_class = TaskSerializer

    def create(self, request, *args, **kwargs):
        # RULE 2: If 3 tasks added within 2 minutes, the 4th is Locked
        two_minutes_ago = timezone.now() - timedelta(minutes=2)
        recent_count = Task.objects.filter(created_at__gte=two_minutes_ago).count()
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        is_locked = recent_count >= 3
        serializer.save(is_locked=is_locked)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def complete_task(self, request, pk=None):
        task = self.get_object()

        # RULE 2: Lock check (5 minutes)
        if task.is_locked:
            unlock_time = task.created_at + timedelta(minutes=5)
            if timezone.now() < unlock_time:
                return Response({"hint": "The vault remains sealed by the weight of haste."}, 
                                status=status.HTTP_403_FORBIDDEN)

        # RULE 1: High priority needs a Low priority done first
        if task.priority == 'High':
            low_done = Task.objects.filter(priority='Low', is_completed=True).exists()
            if not low_done:
                return Response({"hint": "The summit cannot be reached without the base."}, 
                                status=status.HTTP_400_BAD_REQUEST)

        # RULE 3: Odd minute logic
        creation_min = task.created_at.minute
        elapsed = (timezone.now() - task.created_at).total_seconds() / 60
        if creation_min % 2 != 0 and elapsed > task.estimated_time:
            return Response({"hint": "The sands of time have run out for this oddity."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # RULE 4: Hidden Logic
        if "test" in task.title.lower():
            return Response({"hint": "Reality refuses to accept simulations."}, 
                            status=status.HTTP_400_BAD_REQUEST)

        task.is_completed = True
        task.save()
        return Response({"message": "Task Completed!"})