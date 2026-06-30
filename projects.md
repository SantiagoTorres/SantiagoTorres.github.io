---
layout: page
title: Projects
permalink: /projects/
---

<h2>Current Projects</h2>
<ul>
{% for project in site.data.projects.current %}
<li>
<strong>{{ project.name }}</strong>
{% if project.link %} - <a href="{{ project.link }}">{{ project.link | remove: 'https://' | remove: 'http://' }}</a>{% endif %}
<p>{{ project.description }}</p>
</li>
{% endfor %}
</ul>

<h2>Previous Projects</h2>
<ul>
{% for project in site.data.projects.previous %}
<li>
<strong>{{ project.name }}</strong>
{% if project.link %} - <a href="{{ project.link }}">{{ project.link | remove: 'https://' | remove: 'http://' }}</a>{% endif %}
<p>{{ project.description }}</p>
</li>
{% endfor %}
</ul>
