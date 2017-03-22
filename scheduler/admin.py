from __future__ import unicode_literals

from django.conf import settings
from django.contrib import admin, messages
from django.utils.translation import ugettext_lazy as _

from scheduler.models import RepeatableJob, ScheduledJob


def run_job_now(modeladmin, request, queryset):
    running_jobs = ''
    for job in queryset:
        job.scheduler().enqueue_at(job.schedule_time_utc(), job.callable_func(), timeout=job.timeout)
        running_jobs = running_jobs + str(job.name) + ','

    messages.success(request,
                     'The following jobs have been run; {}'.format(running_jobs[:-1]))

run_job_now.short_description = "Run now"

class QueueMixin(object):
    actions = ['delete_model']

    def get_form(self, request, obj=None, **kwargs):
        return super(QueueMixin, self).get_form(request, obj, **kwargs)

    def get_actions(self, request):
        actions = super(QueueMixin, self).get_actions(request)
        del actions['delete_selected']
        return actions

    def delete_model(self, request, obj):
        if hasattr(obj, 'all'):
            for o in obj.all():
                o.delete()
        else:
            obj.delete()
    delete_model.short_description = _("Delete selected %(verbose_name_plural)s")


@admin.register(ScheduledJob)
class ScheduledJobAdmin(QueueMixin, admin.ModelAdmin):
    list_display = (
        'name', 'job_id', 'is_scheduled', 'scheduled_time', 'enabled')
    list_filter = ('enabled', )
    list_editable = ('enabled', )

    readonly_fields = ('job_id', )
    fieldsets = (
        (None, {
            'fields': ('name', 'callable', 'enabled', ),
        }),
        (_('RQ Settings'), {
            'fields': ('queue', 'job_id', ),
        }),
        (_('Scheduling'), {
            'fields': (
                'scheduled_time',
                'timeout',
            ),
        }),
    )


@admin.register(RepeatableJob)
class RepeatableJobAdmin(QueueMixin, admin.ModelAdmin):
    list_display = (
        'name', 'job_id', 'is_scheduled', 'scheduled_time', 'interval_display',
        'enabled')
    list_filter = ('enabled', )
    list_editable = ('enabled', )
    actions = [run_job_now]
    readonly_fields = ('job_id', )
    fieldsets = (
        (None, {
            'fields': ('name', 'callable', 'enabled', ),
        }),
        (_('RQ Settings'), {
            'fields': ('queue', 'job_id', ),
        }),
        (_('Scheduling'), {
            'fields': (
                'scheduled_time',
                ('interval', 'interval_unit', ),
                'repeat',
                'timeout',
            ),
        }),
    )
