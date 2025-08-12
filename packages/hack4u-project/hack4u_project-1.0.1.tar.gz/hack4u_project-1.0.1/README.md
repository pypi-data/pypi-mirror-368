# HACK4U ACADEMY COURSES

### Instalation

```bash
pip3 install hack4u_project
```

### List all courses

```python
from hack4u import list_courses

    for course in list_courses():
        print(course)
```

### Get a course by name

```python
from hack4u import get_course_by_name

course = get_course_by_name("Introduccion a Linux")
print(course)
```

### Calculate total duration of courses

```python
from hack4u.utils import total_duration

print(f"Duracion total: {total_duration()} horas")
```