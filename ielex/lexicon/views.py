from textwrap import dedent
import time
import sys
from django.contrib.auth.decorators import login_required
# from django.utils.decorators import method_decorator
from django.core.urlresolvers import reverse
# from django.core.urlresolvers import reverse_lazy # avail Django 1.4
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.views.generic import CreateView, UpdateView, TemplateView
from django.contrib import messages
from ielex import settings
from ielex.lexicon.models import *
from ielex.shortcuts import render_template
from ielex.forms import EditCognateClassCitationForm
from ielex.lexicon.forms import ChooseNexusOutputForm

class FrontpageView(TemplateView):
    template_name = "frontpage.html"

    def get_context_data(self, **kwargs):
        context = super(FrontpageView,
                self).get_context_data(**kwargs)
        context["lexemes"] = Lexeme.objects.count()
        context["cognate_classes"] = CognateClass.objects.count()
        context["languages"] = Language.objects.count()
        context["meanings"] = Meaning.objects.count()
        context["coded_characters"] = CognateJudgement.objects.count()
        try:
            context["google_site_verification"] = settings.META_TAGS
        except AttributeError:
            pass
        return context

class CognateClassCitationUpdateView(UpdateView):
    model=CognateClassCitation
    form_class=EditCognateClassCitationForm
    template_name="generic_update.html"

    def get_context_data(self, **kwargs):
        context = super(CognateClassCitationUpdateView,
                self).get_context_data(**kwargs)
        cc_id = context["object"].cognate_class.id
        context["title"] = "New cognate class citation"
        context["heading"] = "Citation to cognate class %s" % cc_id
        context["cancel_dest"] = reverse("cognate-set",
                kwargs={"cognate_id":cc_id})
        return context

class CognateClassCitationCreateView(CreateView):
    form_class=EditCognateClassCitationForm
    template_name="generic_update.html"

    def get_context_data(self, **kwargs):
        cc_id = int(self.kwargs["cognate_id"])
        context = super(CognateClassCitationCreateView,
                self).get_context_data(**kwargs)
        context["title"] = "New cognate class citation"
        context["heading"] = "Citation to cognate class %s" % cc_id
        context["cancel_dest"] = reverse("cognate-set",
                kwargs={"cognate_id":cc_id})
        return context

    def get_form_kwargs(self):
        """Need to instantiate the object and set the cognate_class parameter
        here, since fields in the Meta.exclude attribute of ModelForm classes
        can't otherwise be set by forms.
        """
        cc_id = int(self.kwargs["cognate_id"])
        self.object = CognateClassCitation()
        self.object.cognate_class = CognateClass.objects.get(id=cc_id)
        kwargs = super(CognateClassCitationCreateView,
                self).get_form_kwargs()
        return kwargs

@login_required
def cognate_class_citation_delete(request, pk):
    cognate_class_citation = CognateClassCitation.objects.get(id=pk)
    cognate_class_id = cognate_class_citation.cognate_class.id
    cognate_class_citation.delete()
    return HttpResponseRedirect(reverse('cognate-set',
        args=[cognate_class_id]))

class NexusExportView(TemplateView):
    template_name = "nexus_list.html"

    def get(self, request):
        defaults = {"unique":1, "reliability":["L","X"], "language_list":1,
                "meaning_list":1, "dialect":"NN", "singletons":"all",
                "exclude_invariant":0}
        form =  ChooseNexusOutputForm(defaults)
        return self.render_to_response({"form":form})

    def post(self, request):
        form =  ChooseNexusOutputForm(request.POST)
        if form.is_valid():
            #return HttpResponseRedirect(reverse("nexus-data"))
            return self.write_nexus_view(form)
        return self.render_to_response({"form":form})

    def write_nexus_view(self, form):
        """A wrapper to call the `write_nexus` function from a view"""
        # TODO: contributor and sources list

        # Create the HttpResponse object with the appropriate header.
        filename = "%s-%s-%s.nex" % (settings.project_short_name,
                form.cleaned_data["language_list"].name,
                form.cleaned_data["meaning_list"].name)
        response = HttpResponse(mimetype='text/plain')
        response['Content-Disposition'] = 'attachment; filename=%s' % \
                filename.replace(" ", "_")

        write_nexus(response,
                form.cleaned_data["language_list"],
                form.cleaned_data["meaning_list"],
                set(form.cleaned_data["reliability"]),
                form.cleaned_data["dialect"],
                True,
                form.cleaned_data["singletons"],
                form.cleaned_data["exclude_invariant"]
                )
        return response


def write_nexus(fileobj,
            language_list_name,
            meaning_list_name,
            exclude_ratings,
            dialect,
            LABEL_COGNATE_SETS,
            singletons,
            exclude_invariant):
    start_time = time.time()

    # MAX_1_SINGLETON: True|False
    # only allow zero or one singletons per language per meaning (zero
    # if there is another lexeme coded for that meaning, one if not).
    if singletons:
        INCLUDE_UNIQUE_STATES = True
        if singletons == "all":
            MAX_1_SINGLETON = False
        else:
            assert singletons == "limited"
            MAX_1_SINGLETON = True
    else:
        INCLUDE_UNIQUE_STATES = False

    # get data together
    language_list = LanguageList.objects.get(name=language_list_name)
    languages = language_list.languages.all().order_by("languagelistorder")
    language_names = [language.ascii_name for language in languages]

    meaning_list = MeaningList.objects.get(name=meaning_list_name)
    meanings = Meaning.objects.filter(id__in=meaning_list.meaning_id_list)
    max_len = max([len(l) for l in language_names])

    matrix, cognate_class_names = construct_matrix(languages,
            meanings, exclude_ratings, exclude_invariant, INCLUDE_UNIQUE_STATES,
            MAX_1_SINGLETON)

    print>>fileobj, dedent("""\
        #NEXUS

        [ Citation:                                                          ]
        [   Dunn, Michael; Ludewig, Julia; et al. 2011. IELex (Indo-European ]
        [   Lexicon) Database. Max Planck Institute for Psycholinguistics,   ]
        [   Nijmegen.                                                        ]
        """)
    print>>fileobj, "[ Language list: %s ]" % language_list_name
    print>>fileobj, "[ Meaning list: %s ]" % meaning_list_name
    print>>fileobj, "[ Exclude rating/s: %s ]" % ", ".join(sorted(exclude_ratings))
    print>>fileobj, "[ Include unique states: %s ]" % INCLUDE_UNIQUE_STATES
    if INCLUDE_UNIQUE_STATES:
        print>>fileobj, "[ Limit of one singleton per language/meaning: %s ]" % MAX_1_SINGLETON
    print>>fileobj, "[ File generated: %s ]\n" % \
            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    if dialect in ("NN", "MB"):
        print>>fileobj, dedent("""\
            begin taxa;
              dimensions ntax=%s;
              taxlabels %s;
            end;
            """ % (len(languages), " ".join(language_names)))
        print>>fileobj, dedent("""\
            begin characters;
              dimensions nchar=%s;
              format symbols="01" missing=?;
              charstatelabels""" % len(cognate_class_names))
        labels = []

        for i, cc in enumerate(sorted((cognate_class_names))):
            labels.append("    %d %s" % (i+1, cc))
        print>>fileobj, ",\n".join(labels)
        print>>fileobj, "  ;\n  matrix"
    else:
        assert dialect == "BP"
        print>>fileobj, dedent("""\
            begin data;
              dimensions ntax=%s nchar=%s;
              taxlabels %s;
              format symbols="01";
              matrix
            """ % (len(languages), len(cognate_class_names), " ".join(language_names)))

    if LABEL_COGNATE_SETS:
        row = [" "*9] + [str(i).ljust(10) for i in
                range(len(cognate_class_names))[10::10]]
        print>>fileobj, "    %s[ %s ]" % (" "*max_len, "".join(row))
        row = [" "*9] + [".         " for i in range(len(cognate_class_names))[10::10]]
        print>>fileobj, "    %s[ %s ]" % (" "*max_len, "".join(row))

    # write matrix
    for row in matrix:
        language_name, row = row[0], row[1:]
        print>>fileobj, "    '%s' %s%s" % (language_name,
                " "*(max_len - len(language_name)), "".join(row))
    print>>fileobj, "  ;\nend;\n"

    if dialect == "BP":
        print>>fileobj, dedent("""\
            begin BayesPhylogenies;
                Chains 1;
                it 12000000;
                Model m1p;
                bf emp;
                cv 2;
                pf 10000;
                autorun;
            end;
            """)

    # get contributor list:
    # lexical sources
    # lexemes coded by
    # cognate sources
    # cognates coded by

    # timing
    seconds = int(time.time() - start_time)
    minutes = seconds // 60
    seconds %= 60
    print>>fileobj, "[ Processing time: %02d:%02d ]" % (minutes, seconds)
    print>>fileobj, "[ %s ]" % " ".join(sys.argv)
    print ("# Processed %s cognate sets from %s languages" %
            (len(cognate_class_names), len(matrix)))
    return fileobj

def write_delimited(fileobj,
            language_list_name,
            meaning_list_name,
            exclude_ratings,
            LABEL_COGNATE_SETS,
            singletons,
            exclude_invariant):
    start_time = time.time()
    # MAX_1_SINGLETON: True|False
    # only allow zero or one singletons per language per meaning (zero
    # if there is another lexeme coded for that meaning, one if not).
    if singletons:
        INCLUDE_UNIQUE_STATES = True
        if singletons == "all":
            MAX_1_SINGLETON = False
        else:
            assert singletons == "limited"
            MAX_1_SINGLETON = True
    else:
        INCLUDE_UNIQUE_STATES = False

    language_list = LanguageList.objects.get(name=language_list_name)
    languages = language_list.languages.all().order_by("languagelistorder")
    meaning_list = MeaningList.objects.get(name=meaning_list_name)
    meanings = Meaning.objects.filter(id__in=meaning_list.meaning_id_list)
    matrix, cognate_class_names = construct_matrix(languages,
            meanings, exclude_ratings, exclude_invariant, INCLUDE_UNIQUE_STATES,
            MAX_1_SINGLETON)
    print>>fileobj, "\t" + "\t".join(cognate_class_names)
    for row in matrix:
        print>>fileobj, "\t".join(row)

    seconds = int(time.time() - start_time)
    minutes = seconds // 60
    seconds %= 60
    print>>sys.stderr, "# Processing time: %02d:%02d" % (minutes, seconds)
    print>>sys.stderr, "# %s" % " ".join(sys.argv)
    print>>sys.stderr, ("# Processed %s cognate sets from %s languages" %
            (len(cognate_class_names), len(matrix)))
    return fileobj

def construct_matrix(
    languages,
    meanings,
    exclude_ratings,
    exclude_invariant,
    INCLUDE_UNIQUE_STATES,
    MAX_1_SINGLETON):

        matrix = []
        # all cognate classes
        cognate_class_ids = CognateClass.objects.all().values_list("id", flat=True)
        cognate_class_dict = dict(CognateJudgement.objects.all().values_list(
                "cognate_class__id", "lexeme__meaning__gloss").distinct())
        #logging.info("len cognate_class_ids = %s" % len(cognate_class_ids))

        # make a list for each meaning of the languages lacking any lexeme with that meaning
        missing = {}
        for meaning in meanings:
            missing[meaning] = [language.id for language in languages if not
                    language.lexeme_set.filter(meaning=meaning).exists()]

        data, data_missing = {}, {}
        for cc in cognate_class_ids:
            ## Faster way: (doesn't do reliability ratings properly)
            # language_ids = CognateClass.objects.get(id=cc).lexeme_set.filter(
            #         meaning__in=meanings).values_list('language', flat=True)
            ## Slower way:
            # TODO look at LexemeCitation reliablity ratings here too
            language_ids = [cj.lexeme.language.id for cj in
                    CognateJudgement.objects.filter(cognate_class=cc,
                    lexeme__meaning__in=meanings)
                    if cj.lexeme.language in languages
                    and not (cj.reliability_ratings & exclude_ratings)]
            if language_ids:
                try:
                    meaning = CognateClass.objects.get(id=cc).get_meaning()
                    if exclude_invariant:
                        assert (len(language_ids) + len(missing[meaning])) < len(language_names)
                    data[cc] = language_ids
                    try:
                        data_missing[cc] = missing[meaning]
                    except KeyError:
                        data_missing[cc] = []
                except AssertionError:
                    pass

        if INCLUDE_UNIQUE_STATES:
            # adds a cc code for all the lexemes which are not registered as
            # belonging to a cognate class
            # TODO look at LexemeCitation reliablity ratings here too
            # note that registered cognate classes with one member will NOT be
            # ignored when INCLUDE_UNIQUE_STATES = False
            uniques = Lexeme.objects.filter(
                    language__in=languages,
                    meaning__in=meanings,
                    cognate_class__isnull=True).values_list(
                            "language__id",
                            "meaning__id",
                            "id")

            if MAX_1_SINGLETON:
                # only allow one singleton per language-meaning, and only if there
                # are not already any lexemes in that language-meaning cell
                # coded as part of a cognate set
                suppress_singleton = set()
                for language in languages:
                    for meaning in meanings:
                        if Lexeme.objects.filter(language=language,
                                meaning=meaning, cognate_class__isnull=False):
                            suppress_singleton.add((language.id, meaning.id))

            for language_id, meaning_id, lexeme_id in uniques:
                # add singleton ids to cognate_class_dict
                if not MAX_1_SINGLETON or (language_id, meaning_id) not in \
                        suppress_singleton:
                    meaning = Meaning.objects.get(id=meaning_id)
                    cc = ("U", lexeme_id)
                    data[cc] = [language_id]
                    cognate_class_dict[cc] = meaning.gloss
                    try:
                        data_missing[cc] = missing[meaning]
                    except KeyError:
                        data_missing[cc] = []

        # make matrix
        def cognate_class_name_formatter(cc):
            gloss = cognate_class_dict[cc]
            if type(cc) == int:
                return "%s_cogset_%s" % (gloss, cc)
            else:
                assert type(cc) == tuple
                return "%s_lexeme_%s" % (gloss, cc[1])

        cognate_class_names = []
        for cc in sorted(data, key=lambda cc: (cognate_class_dict[cc], cc)):
            cognate_class_names.append(cognate_class_name_formatter(cc))

        for language in languages:
            row = [language.ascii_name]
            for cc in sorted(data, key=lambda cc: (cognate_class_dict[cc], cc)):
                if language.id in data[cc]:
                    row.append("1")
                elif language.id in data_missing[cc]:
                    row.append("?")
                else:
                    row.append("0")
            matrix.append(row)

        return matrix, cognate_class_names
