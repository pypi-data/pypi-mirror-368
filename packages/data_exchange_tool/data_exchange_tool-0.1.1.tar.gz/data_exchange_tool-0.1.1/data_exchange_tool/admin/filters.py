from datetime import timedelta

from django.contrib import admin
from django.utils.timezone import localtime, now


class TodayDynamicFieldFilter(admin.SimpleListFilter):
    @property
    def field_name(self):
        raise NotImplementedError("'field_name' must be defined")

    @property
    def title(self):
        raise NotImplementedError("'title' must be defined")

    @property
    def parameter_name(self):
        return f"{self.field_name}_filter"

    def lookups(self, request, model_admin):
        return (
            ("today", "Today"),
            ("7days", "Last 7 days"),
            ("all", "All"),
        )

    def choices(self, changelist):
        for lookup, title in self.lookup_choices:
            yield {
                "selected": self.value() == str(lookup),
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }

    def queryset(self, request, queryset):
        today_start = localtime(now()).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        tomorrow_start = today_start + timedelta(days=1)
        if self.value() == "today":
            return queryset.filter(
                **{
                    f"{self.field_name}__gte": today_start,
                    f"{self.field_name}__lt": tomorrow_start,
                }
            )
        elif self.value() == "7days":
            last_week = today_start - timedelta(days=7)
            return queryset.filter(
                **{
                    f"{self.field_name}__gte": last_week,
                    f"{self.field_name}__lt": tomorrow_start,
                }
            )

        return queryset


class CreationTimestampFilter(TodayDynamicFieldFilter):
    field_name = "creation_timestamp"
    title = "Creation Timestamp"


class UpdateTimestampFilter(TodayDynamicFieldFilter):
    field_name = "update_timestamp"
    title = "Update Timestamp"
