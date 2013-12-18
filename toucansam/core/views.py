import json
from django.core.urlresolvers import reverse
from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, View
from core.models import Song, Gig, SetList, SetItem
from core.templatetags.toucan import randocolor
from lib.decorators import template

from django.shortcuts import get_object_or_404

@template("home.html")
def home(request):
    print "HOME"


@template("song_list.html")
def song_list(request):
    songs = Song.active_objects.all()
    return {
        "songs": songs,
        "set_list_id": "new",
    }


class SetListView(TemplateView):
    template_name = "set_list.html"

    def get_context_data(self, set_list_id, **kwargs):
        context = super(SetListView, self).get_context_data(**kwargs)
        if set_list_id == "new":
            set_list = SetList()
        else:
            set_list = get_object_or_404(SetList, id=set_list_id)
        context.update({
            "songs": Song.active_objects.exclude(set_lists=set_list),
            "set_list_id": set_list_id,
            "set_list": set_list
        })
        return context

    def post(self, request, gig_id=None):
        if gig_id:
            gig = get_object_or_404(Gig, id=gig_id)
        else:
            gig = Gig(name=request.POST['gig_name'])


class AjaxException(Exception):
    def __init__(self, msg):
        self.message = msg

    def __unicode__(self):
        return unicode(self.message)


class AjaxView(View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        try:
            content = super(AjaxView, self).dispatch(request, *args, **kwargs)
        except AjaxException, e:
            content = {'error': unicode(e)}
        return HttpResponse(json.dumps(content), content_type="application/json")


class SetListAjax(AjaxView):

    def post(self, request, set_list_id):
        gig_name = request.POST["gig_name"]
        response_data = '{}'

        if set_list_id == "new":
            if SetList.objects.filter(gig__name=gig_name).exists():
                raise AjaxException("A set named '{0}' already exists.  Be more creative.".format(gig_name))
            else:
                set_list = SetList.objects.create(gig=Gig.objects.create())
                response_data = json.dumps({
                    'refresh': reverse("set_list", kwargs={"set_list_id": set_list.id})
                })
        else:
            set_list = get_object_or_404(SetList, id=set_list_id)

        set_list.gig.name = gig_name
        set_list.gig.save()

        set_list.songs.clear()
        for song_order, song_id in enumerate(request.POST.getlist('songs[]')):
            song = Song.objects.get(id=song_id)
            SetItem.objects.create(set_list=set_list, song=song, order=song_order)

        return response_data


class SetListSecondsjaxView(AjaxView):
    def get(self, request, set_list_id):
        if set_list_id == "new":
            return "0:00"
        else:
            set_list = get_object_or_404(SetList, id=set_list_id)

        return str(set_list.run_time)



class SetListList(TemplateView):
    template_name = "set_list_list.html"

    def get_context_data(self, **kwargs):
        context = super(SetListList, self).get_context_data(**kwargs)
        context['set_list_list'] = SetList.objects.all()
        return context

set_list_list = SetListList.as_view()

@template("song.html")
def song(request, song_id):
    return {
        "song": get_object_or_404(Song, id=song_id),
    }


class CheatSheetView(TemplateView):
    template_name = "cheat_sheet.html"

    def get_context_data(self, set_list_id=None, **kwargs):
        context = super(CheatSheetView, self).get_context_data(**kwargs)
        if set_list_id is not None:
            set_list = get_object_or_404(SetList, id=set_list_id)
            songs = set_list.ordered_songs
        else:
            songs = Song.active_objects.order_by('title')
        column_count = int(self.request.GET.get('columns', 2))
        row_count = len(songs) / column_count
        remainder = len(songs) % column_count
        columns = []
        start = 0
        for i in range(column_count):
            end = start + row_count
            if remainder > 0:
                end += 1
                remainder -= 1
            columns.append(songs[start:end])
            start = end

        context['column_width'] = (1./column_count) * 100
        context['song_columns'] = columns
        return context


class RandoColor(AjaxView):

    def get(self, request):
        return randocolor()