import re
from typing import List, Dict, Set, Tuple

# --- Constants ---
COURSE_NAMES = ["Python", "DSA", "Databases", "Flask"]
COURSE_INDEX = {name: i for i, name in enumerate(COURSE_NAMES)}
COURSE_MAX = {"Python": 600, "DSA": 400, "Databases": 480, "Flask": 550}

FIRST_NAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z'-]*[A-Za-z]$")
LAST_NAME_REGEX = re.compile(r"^[A-Za-z]+(?:[ '-][A-Za-z]+)*$")
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._+-]+@[A-Za-z0-9.-]+\.[A-Za-z0-9]{1,}$")

# --- Types ---
Student = Dict[str, any]

# --- Input validation ---
def valid_first_name(name: str) -> bool:
    """Check if the first name is valid."""
    return len(name) >= 2 and bool(FIRST_NAME_REGEX.match(name))

def valid_last_name(name: str) -> bool:
    """Check if the last name is valid."""
    return len(name) >= 2 and bool(LAST_NAME_REGEX.match(name))

def valid_email(email: str) -> bool:
    """Check if the email is valid."""
    return bool(EMAIL_REGEX.match(email))

def parse_credentials(input_str: str) -> Tuple[str, str, str]:
    """Parse the user input for credentials."""
    parts = input_str.strip().split()
    if len(parts) < 3:
        return None, None, None
    first = parts[0]
    email = parts[-1]
    last = " ".join(parts[1:-1])
    return first, last, email

# --- Student management ---
def add_students(students: List[Student], emails_in_use: Set[str], next_id: List[int]):
    print("Enter student credentials or 'back' to return.")
    count = 0
    while True:
        entry = input()
        if entry == "back":
            print(f"Total {count} students have been added.")
            return
        elif not entry.strip():
            print("Incorrect credentials.")
            continue

        first, last, email = parse_credentials(entry)
        if first is None or last is None or email is None:
            print("Incorrect credentials.")
            continue

        if not valid_first_name(first):
            print("Incorrect first name.")
            continue
        if not valid_last_name(last):
            print("Incorrect last name.")
            continue
        if not valid_email(email):
            print("Incorrect email.")
            continue
        if email in emails_in_use:
            print("This email is already taken.")
            continue

        student = {
            'id': next_id[0],
            'first': first,
            'last': last,
            'email': email,
            'points': [0, 0, 0, 0]
        }
        students.append(student)
        emails_in_use.add(email)
        next_id[0] += 1
        count += 1
        print("The student has been added.")

def list_students(students: List[Student]):
    """List all student IDs."""
    if not students:
        print("No students found")
    else:
        print("Students:")
        for s in students:
            print(s['id'])

def add_points(students: List[Student]):
    """Add points to student records."""
    print("Enter an id and points or 'back' to return.")
    id_to_student = {str(s['id']): s for s in students}
    while True:
        line = input().strip()
        if line == "back":
            return
        parts = line.split()
        if len(parts) != 5:
            print("Incorrect points format.")
            continue
        student_id_str, *points_str = parts
        if not student_id_str.isdigit() or student_id_str not in id_to_student:
            print(f"No student is found for id={student_id_str}.")
            continue
        try:
            pts = [int(x) for x in points_str]
        except ValueError:
            print("Incorrect points format.")
            continue
        if any(p < 0 for p in pts):
            print("Incorrect points format.")
            continue
        student = id_to_student[student_id_str]
        student['points'] = [a + b for a, b in zip(student['points'], pts)]
        print("Points updated.")

def find_student(students: List[Student]):
    """Find and display a student's progress by ID."""
    print("Enter an id or 'back' to return.")
    id_to_student = {str(s['id']): s for s in students}
    while True:
        line = input().strip()
        if line == "back":
            return
        if line not in id_to_student:
            print(f"No student is found for id={line}.")
        else:
            student = id_to_student[line]
            pts = student['points']
            print(f"{student['id']} points: Python={pts[0]}; DSA={pts[1]}; Databases={pts[2]}; Flask={pts[3]}")

# --- Statistics ---
def course_popularity(students: List[Student]) -> List[int]:
    """How many students have nonzero points in each course."""
    return [sum(1 for s in students if s['points'][i] > 0) for i in range(4)]

def course_activity(students: List[Student]) -> List[int]:
    """Total points given in each course."""
    return [sum(s['points'][i] for s in students) for i in range(4)]

def course_average(students: List[Student]) -> List[float]:
    """Average points for each course, considering only students with points."""
    avgs = []
    for i in range(4):
        scores = [s['points'][i] for s in students if s['points'][i] > 0]
        avgs.append(sum(scores) / len(scores) if scores else 0)
    return avgs

def min_or_na(stat: List[float]) -> List[str]:
    """Return courses with minimum value or 'n/a' if all zero."""
    nonzero = [v for v in stat if v > 0]
    if not nonzero:
        return ["n/a"]
    min_val = min(nonzero)
    return [COURSE_NAMES[i] for i, v in enumerate(stat) if v == min_val]

def max_or_na(stat: List[float]) -> List[str]:
    """Return courses with maximum value or 'n/a' if all zero."""
    if all(v == 0 for v in stat):
        return ["n/a"]
    max_val = max(stat)
    return [COURSE_NAMES[i] for i, v in enumerate(stat) if v == max_val]

def show_course_details(students: List[Student], course_name: str):
    """Show detailed progress for a course."""
    idx = COURSE_INDEX[course_name]
    max_pts = COURSE_MAX[course_name]
    print(course_name)
    print("id\tpoints\tcompleted")
    # Only students with nonzero points
    results = [(s['id'], s['points'][idx]) for s in students if s['points'][idx] > 0]
    results = sorted(results, key=lambda x: (-x[1], x[0]))
    for sid, pts in results:
        pct = pts / max_pts * 100
        print(f"{sid}\t{pts}\t{pct:.1f}%")

def statistics(students: List[Student]):
    """Display summary statistics and handle user queries for course details."""
    print("Type the name of a course to see details or 'back' to quit")
    popularity = course_popularity(students)
    activity = course_activity(students)
    average = course_average(students)

    def format_list(label, vals):
        return f"{label}: {', '.join(vals)}"

    most_pop = max_or_na(popularity)
    least_pop = min_or_na(popularity)
    most_act = max_or_na(activity)
    least_act = min_or_na(activity)
    easiest = max_or_na(average)
    hardest = min_or_na(average)

    print(format_list("Most popular", most_pop))
    print(format_list("Least popular", least_pop))
    print(format_list("Highest activity", most_act))
    print(format_list("Lowest activity", least_act))
    print(format_list("Easiest course", easiest))
    print(format_list("Hardest course", hardest))

    while True:
        course_input = input().strip()
        if course_input == "back":
            return
        lower_courses = [name.lower() for name in COURSE_NAMES]
        if course_input.lower() in lower_courses:
            show_course_details(students, COURSE_NAMES[lower_courses.index(course_input.lower())])
        else:
            print("Unknown course.")

# --- Notifications ---
def notify_students(students: List[Student], notified: Set[Tuple[int, int]]):
    """Notify students for each course completed (rational version)."""
    count = 0
    for student in students:
        for idx, course in enumerate(COURSE_NAMES):
            if student['points'][idx] >= COURSE_MAX[course] and (student['id'], idx) not in notified:
                print(f"To: {student['email']}")
                print("Re: Your Learning Progress")
                print(f"Hello, {student['first']} {student['last']}! You have accomplished our {course} course!")
                notified.add((student['id'], idx))
                count += 1
    if count == 1:
        print("Total 1 notification sent.")
    else:
        print(f"Total {count} notifications sent.")

# --- Main Loop ---
def main():
    print("Learning progress tracker")
    students: List[Student] = []
    emails_in_use: Set[str] = set()
    next_student_id = [10000]
    notified: Set[Tuple[int, int]] = set()
    while True:
        command = input().strip()
        if not command:
            print("No input")
        elif command == "exit":
            print("Bye!")
            break
        elif command == "add students":
            add_students(students, emails_in_use, next_student_id)
        elif command == "list":
            list_students(students)
        elif command == "add points":
            add_points(students)
        elif command == "find":
            find_student(students)
        elif command == "statistics":
            statistics(students)
        elif command == "notify":
            notify_students(students, notified)
        elif command == "back":
            print("Enter 'exit' to exit the program.")
        else:
            print("Unknown command!")

if __name__ == "__main__":
    main()
