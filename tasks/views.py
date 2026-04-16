from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from .models import Task

@api_view(['POST'])
def add_task(request):
    title = request.data.get('title')
    priority = request.data.get('priority')
    estimated_time = request.data.get('estimated_time')

    if not all([title, priority, estimated_time]):
        return Response({'message': 'Missing fields'}, status=status.HTTP_400_BAD_REQUEST)

    # RULE 2: Locking logic
    two_mins_ago = timezone.now() - timedelta(minutes=2)
    recent_count = Task.objects.filter(created_at__gte=two_mins_ago).count()
    is_locked = True if recent_count >= 3 else False

    try:
        task = Task.objects.create(
            title=title, 
            priority=priority, 
            estimated_time=int(estimated_time),
            is_locked=is_locked
        )
        return Response({'message': 'Task Deployed', 'id': task.id}, status=status.HTTP_201_CREATED)
    except:
        return Response({'message': 'Error creating task'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def list_tasks(request):
    tasks = Task.objects.all().order_by('-created_at')
    data = [{
        'id': t.id, 'title': t.title, 'priority': t.priority,
        'estimated_time': t.estimated_time, 'is_completed': t.is_completed,
        'is_locked': t.is_locked, 'created_at': t.created_at
    } for t in tasks]
    return Response({'data': data}, status=status.HTTP_200_OK)

@api_view(['POST'])
def complete_task(request):
    task_id = request.data.get('task_id')
    try:
        task = Task.objects.get(id=task_id)
        now = timezone.now()

        # RULE 2: 5 min Lock check
        if task.is_locked:
            unlock_time = task.created_at + timedelta(minutes=5)
            if now < unlock_time:
                return Response({'hint': 'The gears are frozen. Patience is required.'}, status=status.HTTP_403_FORBIDDEN)

        # RULE 1: High needs Low
        if task.priority == 'High':
            if not Task.objects.filter(priority='Low', is_completed=True).exists():
                return Response({'hint': 'The summit requires a strong base.'}, status=status.HTTP_403_FORBIDDEN)

        # RULE 3: Odd minute timing
        if task.created_at.minute % 2 != 0:
            if (now - task.created_at).total_seconds() / 60 > task.estimated_time:
                return Response({'hint': 'The sands of time have run out.'}, status=status.HTTP_403_FORBIDDEN)

        # RULE 4: Hidden Logic (Title length = 7)
        if len(task.title) == 7:
            return Response({'hint': 'The number seven is forbidden today.'}, status=status.HTTP_403_FORBIDDEN)

        task.is_completed = True
        task.save()
        return Response({'message': 'Synchronized successfully'}, status=status.HTTP_200_OK)

    except Task.DoesNotExist:
        return Response({'hint': 'Objective not found.'}, status=status.HTTP_404_NOT_FOUND)