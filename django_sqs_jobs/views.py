from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseServerError
from django_sqs_jobs.jobs import Job
import json


class JobMessageException(Exception):
    pass


class InvalidContentType(JobMessageException):
    pass


class EmptyRequestBody(JobMessageException):
    pass


class PostBodyParseError(JobMessageException):
    pass


@method_decorator(csrf_exempt, name='dispatch')
class JobMessageView(View):
    """
    Class based view for executing POSTed jobs as in Elastic Beanstalk Worker environments.

    Either subclass and add allowed_jobs as either a list of pkg.module.JobClass paths
    or a dict of ClassName: Class pairs, or set allowed_jobs when instantiating with as_view()
    """
    allowed_methods = ['post', 'options']
    allowed_jobs = {}

    def post(self, request):
        try:
            self.validate_post_body(request)
        except JobMessageException as e:
            return HttpResponseBadRequest(str(e))
        else:
            return self.execute_job(request)

    def execute_job(self, request):
        """Execute the Job specified in the request."""
        job = Job.decode(request.body, allowed_jobs=self.allowed_jobs)
        try:
            job()
        except Exception as e:
            return HttpResponseServerError({'error': '{0}'.format(str(e))})
        return HttpResponse('OK')


    def validate_post_body(self, request, content_type='application/json'):
        """Verifies that request has a valid body and content type, default JSON."""
        if len(request.body) == 0:
            raise InvalidContentType('Empty request body')
        if content_type not in request.content_type:
            raise EmptyRequestBody('Invalid Content-Type: %s only' % content_type)
        return True
