---
layout: page
title: Blog
permalink: /blog/
---

## Latest Posts

{% for post in site.posts %}
  <article class="post">
    <h3>
      <a href="{{ post.url | relative_url }}">{{ post.title }}</a>
    </h3>
    <p class="post-meta">
      <time datetime="{{ post.date | date_to_xmlschema }}">
        {{ post.date | date: "%B %d, %Y" }}
      </time>
      {% if post.author %}
        • {{ post.author }}
      {% endif %}
    </p>
    {% if post.excerpt %}
      {{ post.excerpt }}
    {% endif %}
  </article>
{% endfor %}
