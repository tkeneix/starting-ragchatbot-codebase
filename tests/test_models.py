"""Tests for the Pydantic models in models.py."""

import pytest
from datetime import datetime
from pydantic import ValidationError

# Add the backend directory to the Python path
import sys
from pathlib import Path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from models import Course, Lesson, CourseChunk


class TestCourseModel:
    """Test the Course Pydantic model."""
    
    def test_course_creation_valid(self):
        """Test creating a valid Course instance."""
        course = Course(
            title="Test Course",
            link="https://example.com/course",
            instructor="John Doe",
            lessons=[]
        )
        
        assert course.title == "Test Course"
        assert course.link == "https://example.com/course"
        assert course.instructor == "John Doe"
        assert course.lessons == []
    
    def test_course_with_lessons(self):
        """Test creating a Course with lessons."""
        lesson1 = Lesson(
            title="Lesson 1",
            link="https://example.com/lesson1",
            content="Content of lesson 1"
        )
        lesson2 = Lesson(
            title="Lesson 2", 
            link="https://example.com/lesson2",
            content="Content of lesson 2"
        )
        
        course = Course(
            title="Course with Lessons",
            link="https://example.com/course",
            instructor="Jane Smith",
            lessons=[lesson1, lesson2]
        )
        
        assert len(course.lessons) == 2
        assert course.lessons[0].title == "Lesson 1"
        assert course.lessons[1].title == "Lesson 2"
    
    def test_course_validation_missing_fields(self):
        """Test Course validation with missing required fields."""
        with pytest.raises(ValidationError) as excinfo:
            Course(title="Test Course")  # Missing required fields
        
        error_dict = excinfo.value.errors()
        missing_fields = [error['loc'][0] for error in error_dict if error['type'] == 'missing']
        assert 'link' in missing_fields
        assert 'instructor' in missing_fields
        assert 'lessons' in missing_fields


class TestLessonModel:
    """Test the Lesson Pydantic model."""
    
    def test_lesson_creation_valid(self):
        """Test creating a valid Lesson instance."""
        lesson = Lesson(
            title="Introduction to Python",
            link="https://example.com/python-intro",
            content="Python is a programming language..."
        )
        
        assert lesson.title == "Introduction to Python"
        assert lesson.link == "https://example.com/python-intro"
        assert lesson.content == "Python is a programming language..."
    
    def test_lesson_validation_empty_content(self):
        """Test Lesson with empty content."""
        lesson = Lesson(
            title="Empty Lesson",
            link="https://example.com/empty",
            content=""
        )
        
        assert lesson.content == ""
    
    def test_lesson_validation_missing_fields(self):
        """Test Lesson validation with missing required fields."""
        with pytest.raises(ValidationError) as excinfo:
            Lesson(title="Incomplete Lesson")  # Missing link and content
        
        error_dict = excinfo.value.errors()
        missing_fields = [error['loc'][0] for error in error_dict if error['type'] == 'missing']
        assert 'link' in missing_fields
        assert 'content' in missing_fields


class TestCourseChunkModel:
    """Test the CourseChunk Pydantic model."""
    
    def test_course_chunk_creation_valid(self):
        """Test creating a valid CourseChunk instance."""
        chunk = CourseChunk(
            course_title="Test Course",
            lesson_title="Test Lesson",
            lesson_link="https://example.com/lesson",
            chunk_text="This is a chunk of content from the lesson.",
            chunk_index=0,
            course_instructor="Test Instructor"
        )
        
        assert chunk.course_title == "Test Course"
        assert chunk.lesson_title == "Test Lesson"
        assert chunk.lesson_link == "https://example.com/lesson"
        assert chunk.chunk_text == "This is a chunk of content from the lesson."
        assert chunk.chunk_index == 0
        assert chunk.course_instructor == "Test Instructor"
    
    def test_course_chunk_chunk_index_validation(self):
        """Test CourseChunk with different chunk index values."""
        # Valid positive index
        chunk1 = CourseChunk(
            course_title="Course",
            lesson_title="Lesson",
            lesson_link="https://example.com",
            chunk_text="Content",
            chunk_index=5,
            course_instructor="Instructor"
        )
        assert chunk1.chunk_index == 5
        
        # Zero index should be valid
        chunk2 = CourseChunk(
            course_title="Course",
            lesson_title="Lesson", 
            lesson_link="https://example.com",
            chunk_text="Content",
            chunk_index=0,
            course_instructor="Instructor"
        )
        assert chunk2.chunk_index == 0
    
    def test_course_chunk_validation_missing_fields(self):
        """Test CourseChunk validation with missing required fields."""
        with pytest.raises(ValidationError) as excinfo:
            CourseChunk(course_title="Incomplete Chunk")
        
        error_dict = excinfo.value.errors()
        missing_fields = [error['loc'][0] for error in error_dict if error['type'] == 'missing']
        
        required_fields = ['lesson_title', 'lesson_link', 'chunk_text', 'chunk_index', 'course_instructor']
        for field in required_fields:
            assert field in missing_fields
    
    def test_course_chunk_long_text(self):
        """Test CourseChunk with long text content."""
        long_text = "A" * 1000  # 1000 character string
        
        chunk = CourseChunk(
            course_title="Course with Long Content",
            lesson_title="Long Lesson",
            lesson_link="https://example.com/long",
            chunk_text=long_text,
            chunk_index=1,
            course_instructor="Verbose Instructor"
        )
        
        assert len(chunk.chunk_text) == 1000
        assert chunk.chunk_text == long_text


class TestModelIntegration:
    """Test integration between different models."""
    
    def test_course_to_course_chunks(self):
        """Test creating CourseChunks from a Course with lessons."""
        # Create a course with lessons
        lesson1 = Lesson(
            title="Lesson 1",
            link="https://example.com/lesson1",
            content="This is the content of lesson 1. It has some text."
        )
        lesson2 = Lesson(
            title="Lesson 2",
            link="https://example.com/lesson2", 
            content="This is the content of lesson 2. It also has text."
        )
        
        course = Course(
            title="Integration Test Course",
            link="https://example.com/course",
            instructor="Integration Instructor",
            lessons=[lesson1, lesson2]
        )
        
        # Create chunks from the course
        chunks = []
        for lesson in course.lessons:
            chunk = CourseChunk(
                course_title=course.title,
                lesson_title=lesson.title,
                lesson_link=lesson.link,
                chunk_text=lesson.content,
                chunk_index=0,
                course_instructor=course.instructor
            )
            chunks.append(chunk)
        
        assert len(chunks) == 2
        assert chunks[0].course_title == "Integration Test Course"
        assert chunks[0].lesson_title == "Lesson 1"
        assert chunks[1].lesson_title == "Lesson 2"
        assert all(chunk.course_instructor == "Integration Instructor" for chunk in chunks)