import csv
from io import StringIO
from collections import defaultdict
from .models import Bundle
from django.shortcuts import render
from django.http import HttpResponse


def bundle_view(request, slug):
    bundle = Bundle.objects.get(slug=slug)
    bills_by_state = defaultdict(list)
    total_bills = 0

    for bill in bundle.bills.all().select_related("legislative_session__jurisdiction"):
        bills_by_state[bill.legislative_session.jurisdiction.name].append(bill)
        total_bills += 1

    if "csv" in request.GET:
        buf = StringIO()
        ocsv = csv.writer(buf)
        for state, bills in bills_by_state.items():
            for bill in bills:
                ocsv.writerow(
                    (
                        state,
                        bill.identifier,
                        bill.title,
                        bill.first_action_date,
                        bill.latest_action_description,
                        bill.latest_action_date,
                    )
                )
        buf.seek(0)
        return HttpResponse(buf, content_type="text/csv")

    bills_by_state = {
        state: sorted(bills, key=lambda b: b.identifier)
        for state, bills in sorted(bills_by_state.items())
    }

    return render(
        request,
        "bundles/bundle.html",
        {
            "bundle": bundle,
            "bills_by_state": bills_by_state,
            "total_bills": total_bills,
        },
    )
