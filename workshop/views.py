from django.shortcuts import render_to_response, redirect
from .models import Workshop, Option, Question, Answer
from core.models import Worker
from django.template import RequestContext
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .forms import WorkshopModelForm, QuestionAnswerForm
from workshop.forms import QuestionModelForm


def workshops(request):
    w = Workshop.objects.all()
    return render_to_response('workshops.html', {'workshops': w}, RequestContext(request))


def workshop_new(request):
    if request.method == 'POST':
        form = WorkshopModelForm(request.POST)
        if form.is_valid():
            workshop_model = form.save(commit=False)
            workshop_model.commiter = Worker.objects.get(user=request.user)
            workshop_model.save()
            return redirect('profile')
    else:
        form = WorkshopModelForm()
    return render_to_response('workshop_new.html', {'form': form}, RequestContext(request))


def workshop_detail(request, workshop_id):
    workshop = Workshop.objects.get(pk=workshop_id)
    return render_to_response('workshop_detail.html', {'workshop': workshop}, RequestContext(request))


def workshop_subscribe(request, workshop_id):
    workshop = Workshop.objects.get(pk=workshop_id)
    worker = Worker.objects.get(user__pk=request.user.pk)
    if workshop.commiter == worker:
        messages.add_message(request, messages.ERROR, 'You are the owner of that workshop. You cannot subscribe to it')
    else:
        worker.workshops_subscribed.add(workshop)
        messages.add_message(request, messages.INFO,
                             'You have been successfully subscribed to the workshop "%s"' % workshop.name)
    return redirect('workshop_list')


def question_new(request, workshop_id):
    workshop = Workshop.objects.get(pk=workshop_id)

    if request.method == 'POST':
        form = QuestionModelForm(request.POST)
        if form.is_valid():
            opts = [Option(description=form.cleaned_data['opt_1']),
                    Option(description=form.cleaned_data['opt_2']),
                    Option(description=form.cleaned_data['opt_3']),
                    Option(description=form.cleaned_data['opt_4'])]
            [opt.save() for opt in opts]
            question = Question(description=form.cleaned_data['description'],
                                correct_option=opts[int(form.cleaned_data['correct_option'])])
            question.save()
            [question.options.add(o) for o in opts]
            workshop.questions.add(question)
            return redirect('workshop_detail', workshop_id=workshop_id)

    else:
        form = QuestionModelForm()

    return render_to_response('question_new.html', {'form': form, 'workshop': workshop},
                              RequestContext(request))


def question_detail(request, workshop_id, question_id):
    worker = Worker.objects.get(user__pk=request.user.pk)
    workshop = Workshop.objects.get(pk=workshop_id)
    question = Question.objects.get(pk=question_id)

    options = []
    for o in question.options.all():
        options.append([o.id, o.description])

    is_subscriber = True
    try:
        _ = workshop.subscriptions.get(user=request.user)
    except ObjectDoesNotExist:
        is_subscriber = False

    try:
        answer = Answer.objects.get(worker=worker, workshop=workshop, question=question)
    except ObjectDoesNotExist:
        answer = None

    if request.method == 'POST':
        form = QuestionAnswerForm(request.POST, options=options)
        if form.is_valid():
            option_id = form.cleaned_data['answer']
            question = Question.objects.get(pk=question_id)
            option = Option.objects.get(pk=option_id)

            answer = Answer.objects.create(worker=worker, workshop=workshop, question=question, answer=option)
            answer.save()

            return redirect('question_detail', workshop_id, question_id)
    else:
        form = QuestionAnswerForm(options=options)

    return render_to_response('question_detail.html',
                              {'workshop': workshop, 'question': question, 'form': form, 'is_subscriber': is_subscriber,
                               'answer': answer},
                              RequestContext(request))