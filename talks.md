---
layout: page
title: Talks
permalink: /talks/
---

{% assign talks = site.data.talks.talks %}

<ul>
{% for talk in talks %}
<li>
<strong>{{ talk.title }}</strong><br>
<em>{{ talk.venue }}</em> ({{ talk.year }}).
{% if talk.link %} <a href="{{ talk.link }}">Watch</a>{% endif %}
</li>
{% endfor %}
</ul>
