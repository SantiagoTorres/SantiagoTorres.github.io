---
layout: page
title: Publications
permalink: /publications/
---

{% assign conference_papers = site.data.publications.conference_papers %}
{% assign journal_papers = site.data.publications.journal_papers %}
{% assign magazine_articles = site.data.publications.magazine_articles %}

{% if conference_papers %}
<h2>Conference Papers</h2>
<ul>
{% for pub in conference_papers %}
<li>
<strong>{{ pub.title }}</strong><br>
<em>{{ pub.authors }}</em><br>
{{ pub.venue }} ({{ pub.year }}).
{% if pub.doi %} 
<a href="https://doi.org/{{ pub.doi }}">DOI: {{ pub.doi }}</a>
{% elsif pub.link %}
<a href="{{ pub.link }}">{{ pub.link }}</a>
{% endif %}
</li>
{% endfor %}
</ul>
{% endif %}

{% if journal_papers %}
<h2>Journal Papers</h2>
<ul>
{% for pub in journal_papers %}
<li>
<strong>{{ pub.title }}</strong><br>
<em>{{ pub.authors }}</em><br>
{{ pub.venue }} ({{ pub.year }}).
{% if pub.doi %} 
<a href="https://doi.org/{{ pub.doi }}">DOI: {{ pub.doi }}</a>
{% elsif pub.link %}
<a href="{{ pub.link }}">{{ pub.link }}</a>
{% endif %}
</li>
{% endfor %}
</ul>
{% endif %}

{% if magazine_articles %}
<h2>Magazine Articles</h2>
<ul>
{% for pub in magazine_articles %}
<li>
<strong>{{ pub.title }}</strong><br>
<em>{{ pub.authors }}</em><br>
{{ pub.venue }} ({{ pub.year }}).
{% if pub.doi %} 
<a href="https://doi.org/{{ pub.doi }}">DOI: {{ pub.doi }}</a>
{% elsif pub.link %}
<a href="{{ pub.link }}">{{ pub.link }}</a>
{% endif %}
</li>
{% endfor %}
</ul>
{% endif %}
