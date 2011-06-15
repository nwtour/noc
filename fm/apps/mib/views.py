# -*- coding: utf-8 -*-
##----------------------------------------------------------------------
## MIB Manager
##----------------------------------------------------------------------
## Copyright (C) 2007-2011 The NOC Project
## See LICENSE for details
##----------------------------------------------------------------------

## Python modules
## Django modules
from django.utils.translation import ugettext_lazy as _
from django import forms
from django.forms.formsets import formset_factory
## NOC modules
from noc.lib.app import TreeApplication, HasPerm, view
from noc.fm.models import MIB, MIBData, MIBRequiredException
from noc.lib.fileutils import temporary_file

#from __future__ import with_statement
#from django.contrib import admin
#from django import forms
#from noc.lib.app import ModelApplication,HasPerm
#from noc.lib.fileutils import temporary_file
#from noc.fm.models import MIB,MIBData,MIBRequiredException


class MIBApplication(TreeApplication):
    title = _("MIB")
    verbose_name = _("MIB")
    verbose_name_plural = _("MIBs")
    menu = "MIBs"
    model = MIB

    def get_preview_extra(self, obj):
        """
        Collect additional data for preview
        """
        def get_syntax(x):
            s = []
            if x.syntax:
                s += [x.syntax["base_type"]]
                if "display_hint" in x.syntax:
                    s += ["display-hint: %s" % x.syntax["display_hint"]]
                if (x.syntax["base_type"] == "Enumeration" and
                    "enum_map" in x.syntax):
                    # Display enumeration
                    for k in sorted(x.syntax["enum_map"],
                                    key=lambda x: int(x)):
                        s += ["%s -> %s" % (
                            k, x.syntax["enum_map"][k])]
                return s
            else:
                return []

        r = [{
                "oid": x.oid,
                "name": x.name,
                "description": x.description,
                "syntax": get_syntax(x)
            } for x in MIBData.objects.filter(mib=obj.id)]
        r = sorted(r, key=lambda x: [int(y) for y in x["oid"].split(".")])
        # Calculate indent
        min_l = 0
        for x in r:
            l = len(x["oid"].split("."))
            if min_l == 0 or l < min_l:
                min_l = l
            x["offset"] = l
        for x in r:
            x["offset"] -= min_l
            x["offset"] *= 16
        return {"data": r}

    @view(url="^go/(?P<go_type>[^/]+)/(?P<param>.+)/$",
          url_name="go", access=HasPerm("view"))
    def view_go(self, request, go_type, param):
        """
        Redirector
        """
        if go_type == "mib_name":
            mib = MIB.objects.filter(name=param).first()
            if mib:
                return self.response_redirect("fm:mib:preview", mib.id)
        return self.response_redirect("fm:mib.tree")

    @view(url="^lookup_mib/", url_name="lookup_mib", access=HasPerm("view"))
    def view_lookup_mib(self, request):
        """
        AJAX lookup of MIB
        """
        result = None
        if request.GET and "lookup_field" in request.GET:
            q = request.GET["lookup_field"].strip()
            if q:
                if "::" in q:
                    r = MIB.get_oid(q)
                    if r:
                        result = {
                            "oid": r,
                            "name": q
                        }
                else:
                    r = MIB.get_name(q)
                    if r:
                        result = {
                            "oid": q,
                            "name": r
                        }
        return self.render_json(result)

    class MIBUploadForm(forms.Form):
        file = forms.FileField()

    @view(url=r"^add/$", url_name="add", access=HasPerm("add"))
    def view_add(self, request):
        upload_formset = formset_factory(self.MIBUploadForm, extra=10)
        if request.method=="POST":
            formset = upload_formset(request.POST, request.FILES)
            if formset.is_valid():
                # Load MIBs
                left = {}  # Form -> error
                for form in formset:
                    if "file" in form.cleaned_data:
                        left[form] = None
                
                # Try to upload MIBs
                uploaded = set()
                while len(left) > 0:
                    n = len(left)
                    for form in left.keys():
                        # Try to upload MIB
                        with temporary_file(form.cleaned_data["file"].read()) as path:
                            try:
                                mib = MIB.load(path)
                                uploaded.add(mib.name)
                                del left[form]
                            except MIBRequiredException, x:
                                left[form] = "%s requires %s" % (x.mib,
                                                                 x.requires_mib)
                    nn = len(left)
                    if n == nn:
                        break
                    else:
                        n = nn
                # Check no unresolved dependencies left
                uploaded = ", ".join(sorted(uploaded))
                if uploaded:
                    self.message_user(request,
                        "Following MIBs are loaded correctly: %s" % uploaded)
                if left:
                    for form in left:
                        self.message_user(request,
                                          "%s load failed: %s" % (form.cleaned_data["file"].name, left[form]))
                return self.response_redirect(self.base_url)
        else:
            formset = upload_formset()
        return self.render(request, "add.html", form=formset)
