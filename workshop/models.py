from django.db import models
from core.models import Worker

# Create your models here.


class Option(models.Model):
    description = models.CharField(max_length=50)

    def __unicode__(self):
        return self.description


class Question(models.Model):
    description = models.TextField()
    options = models.ManyToManyField(Option, related_name='options')
    correct_option = models.ForeignKey(Option, related_name='correct_option')

    def __unicode__(self):
        return self.description


class Workshop(models.Model):
    NOT_STARTED = 0
    FINISHED = 1
    CLOSED = 2
    STATUS_CHOICES = (
        (NOT_STARTED, 'not started'),
        (FINISHED, 'finished'),
        (CLOSED, 'closed')
    )


    name = models.CharField(max_length=100)
    description = models.TextField(verbose_name='Description')
    prerequisites = models.TextField(verbose_name='Prerequisites', blank=True)
    objectives = models.TextField(verbose_name='Objectives', blank=True)
    repo_link = models.URLField(verbose_name='link to the repository', blank=True)
    questions = models.ManyToManyField(Question, blank=True)
    commiter = models.ForeignKey(Worker)
    comments = models.ManyToManyField('Comment')
    subscriptions = models.ManyToManyField(Worker, related_name='subscriber', blank=True)

    def is_subscriptor(self, worker):
        return self.subscriptions.filter(id=worker.id).count() > 0

    def __unicode__(self):
        return self.name


class Answer(models.Model):
    worker = models.ForeignKey(Worker)
    workshop = models.ForeignKey(Workshop)
    question = models.ForeignKey(Question)
    answer = models.ForeignKey(Option)


class Comment(models.Model):
    worker = models.ForeignKey(Worker)
    message = models.TextField()
    date = models.DateField()