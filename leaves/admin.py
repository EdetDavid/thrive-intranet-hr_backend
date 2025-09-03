from django.contrib import admin
from .models import LeaveRequest


class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'start_date', 'end_date', 'leave_type', 'status', 'approver', 'created_at')
    list_filter = ('status', 'leave_type', 'start_date', 'end_date', 'created_at')
    search_fields = ('user__username', 'user__email', 'leave_type', 'reason', 'approver__username')
    readonly_fields = ('created_at', 'updated_at')
    ordering = ('-created_at',)
    actions = ['approve_requests', 'reject_requests']

    def approve_requests(self, request, queryset):
        """Mark selected leave requests as approved and set the approver."""
        updated = queryset.update(status='approved', approver=request.user)
        self.message_user(request, f"{updated} leave request(s) approved.")
    approve_requests.short_description = 'Approve selected leave requests'

    def reject_requests(self, request, queryset):
        """Mark selected leave requests as rejected and set the approver."""
        updated = queryset.update(status='rejected', approver=request.user)
        self.message_user(request, f"{updated} leave request(s) rejected.")
    reject_requests.short_description = 'Reject selected leave requests'


admin.site.register(LeaveRequest, LeaveRequestAdmin)
