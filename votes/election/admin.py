from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html
from .models import Student, Position, Candidate, Vote, ElectionStatus, AuditLog

# Admin Branding
admin.site.site_header = "VoteCollege Administrative Portal"
admin.site.site_title = "VoteCollege Admin"
admin.site.index_title = "Election Management & Analytics"


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ('username', 'student_id', 'department', 'is_verified')
    list_filter = ('department', 'is_verified')
    search_fields = ('username', 'student_id', 'email')
    ordering = ('username',)
    actions = ['verify_students', 'unverify_students']

    def verify_students(self, request, queryset):
        queryset.update(is_verified=True)
    verify_students.short_description = "Verify selected students"

    def unverify_students(self, request, queryset):
        queryset.update(is_verified=False)
    unverify_students.short_description = "Unverify selected students"

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_candidate_count', 'get_total_votes')

    def get_candidate_count(self, obj):
        return obj.candidates.count()
    get_candidate_count.short_description = 'Candidates'

    def get_total_votes(self, obj):
        return Vote.objects.filter(position=obj).count()
    get_total_votes.short_description = 'Total Votes Cast'


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'department', 'get_vote_count')
    list_filter = ('position', 'department')
    search_fields = ('name', 'manifesto')

    def get_vote_count(self, obj):
        return obj.vote_set.count()
    get_vote_count.short_description = 'Votes Received'


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('voter', 'candidate', 'position', 'timestamp')
    list_filter = ('position', 'candidate', 'timestamp')
    search_fields = ('voter__username', 'candidate__name')
    readonly_fields = ('voter', 'candidate', 'position', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(ElectionStatus)
class ElectionStatusAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_open', 'results_published', 'start_time', 'end_time')
    list_editable = ('is_open', 'results_published')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'username', 'action_badge', 'detail', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('username', 'detail', 'ip_address')
    readonly_fields = ('user', 'username', 'action', 'detail', 'ip_address', 'timestamp')
    ordering = ('-timestamp',)

    def action_badge(self, obj):
        colors = {
            'login': '#28a745',
            'logout': '#6c757d',
            'vote': '#007bff',
            'register': '#17a2b8',
            'failed_login': '#dc3545',
        }
        color = colors.get(obj.action, '#333')
        return format_html(
            '<span style="background:{};color:#fff;padding:2px 8px;border-radius:4px;font-size:0.8em;font-weight:600;">{}</span>',
            color, obj.get_action_display()
        )
    action_badge.short_description = 'Action'

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
