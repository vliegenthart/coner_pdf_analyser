from scopus import ScopusSearch
s = ScopusSearch('FIRSTAUTH ( kitchin  j.r. )', refresh=True)

print(s.org_summary)