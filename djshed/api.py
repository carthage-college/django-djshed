# -*- coding: utf-8 -*-

import requests

from djshed.models import Course
from django.conf import settings


DEPARTMENT_EXCEPTIONS = {
    'AHS': 'Allied Health Science',
}


def set_course(jason):
    """Construct a course object from API data."""

    """
    "Academic_Units_group": [{"Department": "Political Science"}],
    "Special_Topic": "Marxism Leninism",
    "Year": "2023",
    "Course_Subjects_group": [{"Course_Subject": "POL"}],
    "Section_Listings_group": [{
        "Meeting_Time": "9:15 AM - 10:20 AM",
        "Credits": "4",
        "Capacity": "12",
        "Course_Subject_Abbreviation___Number": "POL 2400",
        "Course_Title": "Washington Bullets: the madmen of yesterday and the of clarity today. (SOC)(SI)",
        "Section_Number": "01",
        "Meeting_Day_Patterns": "MWF"
    }],
    "Academic_Period": "2023 Fall",
    "Course_Description": "This course involves a study of US imperialism, the plots against people's movements and governments, and of the assassinations of socialists, Marxists, communists all over the Third World by the country where liberty is a statue. Fall/Spring",
    "Start_Date": "2023-09-06",
    "End_Date": "2023-12-22",
    "Public_Notes": "This course involves a study of US imperialism, the plots against people's movements and governments, and of the assassinations of socialists, Marxists, communists all over the Third World by the country where liberty is a statue. Fall/Spring",
    "Instructors_group": [{
        "Instructor_Name": "Vijay Prishad",
        "Instructor_ID": "8675309"
    }],
    "Locations_group": [{
        "Building": "LH",
        "Room_Number": "230"
    }]
    """

    number = jason['Section_Listings_group'][0].get('Course_Subject_Abbreviation___Number')
    code = number.split(' ')[0]
    department = jason['Academic_Units_group'][0].get('Department')
    if code and DEPARTMENT_EXCEPTIONS.get(code):
        department = DEPARTMENT_EXCEPTIONS[code]

    building = None
    room = None
    location = jason.get('Locations_group')
    if location:
        building = jason['Locations_group'][0].get('Building')
        room = jason['Locations_group'][0].get('Room_Number')

    instructors = None
    instructors_group = jason.get('Instructors_group')
    if instructors_group:
        instructors = []
        for instructor in instructors_group:
            name = instructor.get('Instructor_Name')
            if name:
                instructors.append(instructor.get('Instructor_Name').split(' (')[0])
        if instructors:
            instructors = ', '.join(instructors)

    title = jason['Section_Listings_group'][0].get('Course_Title')
    topic = jason.get('Special_Topic')
    if topic:
        title = '{0}: {1}'.format(title, topic)

    description = jason.get('Course_Description')
    notes = jason.get('Public_Notes')
    if notes:
        description = notes

    # first we fetch the course or create it if it does not exist based on:
    #
    # course number
    # section
    # term
    #
    # which together will return only 1 course or None and thus create it.
    #
    section = jason['Section_Listings_group'][0].get('Section_Number')
    if len(section) > 2:
        section = section[:-1]
    course, created = Course.objects.update_or_create(
        number = number,
        section = section,
        term = jason.get('Academic_Period'),
        year = jason.get('Year'),
    )
    # now we update the course with the remainder of the values from API
    Course.objects.filter(id=course.id).update(
        # Art
        department = department,
        # ARH
        group = jason['Course_Subjects_group'][0].get('Course_Subject'),
        credits = jason['Section_Listings_group'][0].get('Credits'),
        capacity = jason['Section_Listings_group'][0].get('Capacity'),
        title = title,
        days = jason['Section_Listings_group'][0].get('Meeting_Day_Patterns'),
        time = jason['Section_Listings_group'][0].get('Meeting_Time'),
        description = description,
        start_date = jason.get('Start_Date'),
        end_date = jason.get('End_Date'),
        instructors = instructors,
        building = building,
        room = room,
        status = True,
    )

    return course


def get_courses(test=False):
    """Fetch the workday course data from cache or API."""
    courses = []
    response = requests.get(
        settings.WORKDAY_EARL,
        auth=(settings.WORKDAY_USERNAME, settings.WORKDAY_PASSWORD),
    )
    jason = response.json()
    report = jason['Report_Entry']
    for course in report:
        if test:
            print(course)
        else:
            course = set_course(course)
            courses.append(course)
    return courses
