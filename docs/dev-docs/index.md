---
layout: page
title: Dev Docs
permalink: /dev-docs/
---

## Development Documentation

Design documents, specifications, and architectural decisions for the AI4PKM system.

{% assign sorted_specs = site.specs | sort: 'created' | reverse %}
{% for spec in sorted_specs %}
  <article class="spec">
    <h3>
      <a href="{{ spec.url | relative_url }}">{{ spec.title }}</a>
    </h3>
    <p class="spec-meta">
      <time datetime="{{ spec.created }}">
        {{ spec.created | date: "%B %d, %Y" }}
      </time>
      {% if spec.status %}
        • Status: {{ spec.status }}
      {% endif %}
    </p>
  </article>
{% endfor %}
