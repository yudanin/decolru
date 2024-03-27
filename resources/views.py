from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.http import Http404
#from django.db import connection, models
from django.http import HttpResponseRedirect #, HttpResponse
from django.utils import timezone
from django.views import View
from datetime import datetime
from .forms import SuggestResourceForm, ReviewSuggestedResource
from .utils import get_msgs, get_language_code, generate_slug, langs
from .models import Resources, ResourceStatuses, ResourceTypes, Langs, AuthorsXResources
from django.views.generic.base import TemplateView
import json
#import os
from django.core.serializers.json import DjangoJSONEncoder


def get_date(resource):
    return resource["date_added_to_lib"]


def get_resource_data():
    approved_status = ResourceStatuses.objects.get(id=2)
    results = Resources.objects.filter(resource_status=approved_status)
    return results


def index(request):
    results = get_resource_data()
    latest_additions = results.order_by('-date_added_to_lib')[:3]
    return render(request, "resources/index.html",
                  {"msgs": get_msgs(request), "langs": langs, "resources": latest_additions})


def resources(request):
    results = get_resource_data()
    return render(request, "resources/all-resources.html",
                  {"msgs": get_msgs(request), "langs": langs, "resources": results})


def resource_details(request, slug):
    r = Resources.objects.get(slug=slug)

    # Get type
    t = ResourceTypes.objects.get(resource_type_id=r.type_id, lang_id=get_language_code(request))
    type_desc = t.description

    if r is None:
        raise Http404("Resource not found")

    return render(request, "resources/resource-details.html",
                  {'msgs': get_msgs(request), 'langs': langs, 'r': r, 'type': type_desc})


class SuggestResourceView(View):
    def get(self, request):
        form = SuggestResourceForm(msgs=get_msgs(request))
        return render(request, "resources/suggest-resource.html",
                      {"msgs": get_msgs(request), "langs": langs, "form": form})

    def post(self, request):
        form = SuggestResourceForm(request.POST, msgs=get_msgs(request))

        if form.is_valid():
            resource = form.save(commit=False)

            # Set the type id using the resource_type's resource_type_id
            selected_resource_id = form.cleaned_data['type'].resource_type_id
            resource.type_id = int(selected_resource_id)

            # Set the date_created field
            if resource.date_created:
                resource.date_created = resource.date_created.strftime('%Y-%m-%d')

            # Set the date_submitted field
            date_submitted_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S%z")
            resource.date_submitted = datetime.strptime(date_submitted_str, "%Y-%m-%d %H:%M:%S%z")

            # Set the resource_status using the resource_status_instance
            resource_status_instance = ResourceStatuses.objects.get(id=1)
            resource.resource_status = resource_status_instance

            # Save the resource instance
            resource.save()

            #return HttpResponseRedirect(reverse('thankyou'))
            return render(request, 'resources/thankyou.html', {'msgs': get_msgs(request), 'langs': langs})
        else:
            print('Form errors:', form.errors)
            # Form is not valid, render the form again with errors
            return render(request, "resources/suggest-resource.html",
                          {"msgs": get_msgs(request), "langs": langs, "form": form})


class ThankYouView(TemplateView):
    template_name = "resources/thankyou.html"

    def get_context_data(self, **kwargs):
        # context = super().get_context_data(**kwargs)
        extra_context = {"msgs": get_msgs(self.request), "langs": langs}
        msgs = get_msgs(self.request)


class ReviewSuggestions(TemplateView):
    template_name = "resources/review-suggestions.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        extra_context = {"msgs": get_msgs(self.request), "langs": langs}
        draft_status = ResourceStatuses.objects.get(id=1)
        suggestions = Resources.objects.filter(resource_status=draft_status)

        # suggest slugs
        [setattr(suggestion, 'slug', generate_slug(suggestion.title)) for suggestion in suggestions if
         not suggestion.slug]
        Resources.objects.bulk_update(suggestions, ['slug'])

        # serialize suggestions without authors to JSON
        suggestions_json = json.dumps(list(suggestions.values()), cls=DjangoJSONEncoder)

        # add authors ------------------------------------------------------

        # Deserialize JSON to Python list of dictionaries
        suggestions_data = json.loads(suggestions_json)

        # Add authors and editors to json
        d = {'authors': 1, 'editors': 2}
        suggestions_json_with_authors = ""
        for k in d:
            for suggestion in suggestions_data:
                suggestion_instance = suggestions.get(pk=suggestion['id'])  # Get the corresponding model instance
                # Filter AuthorsXResources based on type_of: 1 for authors, 2 for editors
                authors_x_resources = AuthorsXResources.objects.filter(resource=suggestion_instance, type_of=d[k])
                # Extract author IDs from filtered AuthorsXResources
                ids = list(authors_x_resources.values_list('author_id', flat=True))
                suggestion[k] = ids
            suggestions_json_with_authors = json.dumps(suggestions_data)

        context["suggestions_json"] = suggestions_json_with_authors

        msgs = get_msgs(self.request)

        #form = ReviewSuggestedResource(msgs=msgs, langs=self.request.langs)
        form = ReviewSuggestedResource(msgs=msgs,langs=langs)

        context['msgs'] = get_msgs(self.request)
        context['langs'] = langs
        context["form"] = form

        return context

    def post(self, request, *args, **kwargs):
        msgs = get_msgs(request)
        form = ReviewSuggestedResource(request.POST, request.FILES, msgs=msgs, langs=langs)
        if form.is_valid():
            resource_id = int(request.POST.get('id'))  # 0 for new resource

            if resource_id == 0:
                # if adding a new resource - instantiate class
                resource = Resources()
            else:
                # fetch the existing resource instance if it exists
                resource = get_object_or_404(Resources, pk=resource_id) if resource_id else None

            if resource_id != 0:
                form = ReviewSuggestedResource(request.POST, instance=resource, msgs=get_msgs(request))
            else:
                form = ReviewSuggestedResource(request.POST, msgs=get_msgs(request))

            if form.is_valid():
                resource = form.save(commit=False)

                if resource_id != 0:
                    resource.id = resource_id

                r_type_id = form.cleaned_data['type'].resource_type_id
                resource.type_id = int(r_type_id)

                lang_id = form.cleaned_data['lang'].id
                lang_instance = Langs.objects.get(id=lang_id)
                resource.lang = lang_instance

                status_id = form.cleaned_data['resource_status'].id
                resource_status_instance = ResourceStatuses.objects.get(id=status_id)
                resource.resource_status = resource_status_instance

                # Set the date_added_to_lib field
                date_added_to_lib_str = timezone.now().strftime("%Y-%m-%d %H:%M:%S%z")
                resource.date_added_to_lib = datetime.strptime(date_added_to_lib_str, "%Y-%m-%d %H:%M:%S%z")

                # get file
                if request.FILES.get('resource_file'):
                    resource.resource_file = request.FILES['resource_file']

                # get image
                if request.FILES.get('img'):
                    resource.img = request.FILES['img']

                resource.save()

                # save authors and editors
                resource.authored_resources.clear()
                d = {'authors': 1, 'editors': 2}
                for k in d:
                    selected_ae = form.cleaned_data.get(k)
                    for a in selected_ae:
                        AuthorsXResources.objects.create(author=a, resource=resource, type_of=d[k])

                return HttpResponseRedirect(reverse('review-suggestions'))
        else:
            print('Form errors:', form.errors)
            draft_status = ResourceStatuses.objects.get(id=1)
            suggestions = Resources.objects.filter(resource_status=draft_status)
            suggestions_json = json.dumps(list(suggestions.values()), cls=DjangoJSONEncoder)
            return render(request, self.template_name,
                          {'form': form, 'msgs': get_msgs(request), 'langs': langs,
                           'suggestions_json': suggestions_json})


class SelectLanguageView(View):
    def post(self, request):
        lang_id = request.POST['lang_id']
        request.session["language_code"] = lang_id
        referer_url = request.META.get('HTTP_REFERER')
        return HttpResponseRedirect(referer_url)
