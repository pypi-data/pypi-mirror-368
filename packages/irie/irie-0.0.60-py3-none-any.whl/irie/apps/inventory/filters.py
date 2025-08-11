import django_filters
from django.forms import CheckboxInput

class AssetFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(
        lookup_expr="icontains", 
        field_name="calid",
        label="Search"
    )

    cesmd_not_null = django_filters.BooleanFilter(
        label="Instrumented",
        widget=CheckboxInput(),
        method="filter_cesmd_exists"
    )

    is_streaming = django_filters.BooleanFilter(
        # field_name="is_complete",
        label="Streaming",
        widget=CheckboxInput(),
        method="filter_is_streaming"
    )

    district = django_filters.CharFilter(
        label="District",
        method="filter_district"
    )

    max_year = django_filters.NumberFilter(
        label="Max Year",
        method="filter_year"
    )

    def filter_year(self, queryset, name, value):
        ids = {
            asset.id for asset in queryset if (
                asset.nbi_data and int(asset.nbi_data["NBI_BRIDGE"].get("Year Built",0) or 0) <= int(value) #.year
            )
        }
        return queryset.filter(id__in=ids)
 

    def filter_cesmd_exists(self, queryset, name, value):
        if value:  # Checkbox is checked
            return queryset.exclude(cesmd__isnull=True).exclude(cesmd__exact='')
        return queryset

    def filter_is_streaming(self, queryset, name, value):
        if value:  # Checkbox is checked
            return queryset.exclude(is_complete=False).exclude(cesmd__exact='')
        return queryset

    def filter_district(self, queryset, name, value):
        return [
            asset for asset in queryset if (
                asset.nbi_data and \
                    "Highway Agency District" in asset.nbi_data["NBI_BRIDGE"] and \
                        asset.nbi_data["NBI_BRIDGE"]["Highway Agency District"] == value
            )
        ]
