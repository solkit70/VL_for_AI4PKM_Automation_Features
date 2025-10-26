---
title: "Publish to GitHub Pages"
abbreviation: "PGP"
category: "documentation/publishing"
created: "2025-10-20"
---
Guidelines and best practices for publishing blog posts and documentation to GitHub Pages using Jekyll and the Minima theme.

## Input
- Markdown content for blog post or documentation page
- Images/assets referenced in the content
- Existing Jekyll site configuration (`_config.yml`)
- Repository structure with `docs/` or root-level Jekyll setup

## Output
- Properly formatted Jekyll post in `_posts/` directory
- Assets in `assets/images/` directory
- Updated navigation/cross-references as needed
- Published content visible on GitHub Pages

## Pre-Publishing Checklist

Before creating or migrating content to GitHub Pages:

1. **Verify Jekyll Setup**
   - Check `_config.yml` exists with correct `baseurl` (e.g., `/AI4PKM`)
   - Confirm theme is specified (e.g., `theme: minima`)
   - Verify required plugins are listed

2. **Prepare Content**
   - Convert Obsidian/other formats to standard Markdown
   - Identify all images and assets used
   - Note any internal links to other posts/pages

3. **Test Locally First**
   ```bash
   cd docs  # or your Jekyll root
   bundle exec jekyll serve
   # Visit http://localhost:4000/baseurl/
   ```

## Main Process

### 1. Directory Structure Setup

Jekyll has specific requirements for where files must be located:

**Blog Posts:**
```
docs/
├── _posts/                    # REQUIRED for blog posts
│   └── YYYY-MM-DD-title.md   # Date prefix required
├── assets/                    # Standard location for assets
│   └── images/
│       └── blog/              # Organize by category
│           └── image.png
├── blog/                      # Optional: blog index page
│   └── index.md
└── _config.yml
```

**Critical Rules:**
- Blog posts MUST be in `_posts/` directory (not `blog/` or custom folders)
- Post filenames MUST follow `YYYY-MM-DD-title.md` format
- Assets should be in `assets/` or root-level `images/` directory
- Avoid using underscored subdirectories like `blog/_files_/` (Jekyll may not serve them)

### 2. Create/Convert Blog Post

**Frontmatter Template:**
```yaml
---
layout: post
title: "Your Post Title"
date: YYYY-MM-DD
categories: blog
author: Your Name
---
```

**Required Fields:**
- `layout: post` - Uses post template
- `title` - Post title (quoted if contains special chars)
- `date` - Date in `YYYY-MM-DD` format (no time component)

**Optional Fields:**
- `categories` - Space or list-separated categories
- `author` - Author name
- `excerpt` - Custom excerpt (otherwise uses first paragraph)

**Important:**
- Date in filename and frontmatter should match
- Future dates won't display by default (Jekyll setting)
- No `.html` extension needed in filename

### 3. Handle Images and Assets

**CRITICAL: Image Path Pattern**

❌ **Never use relative paths:**
```markdown
![Image](_files_/image.png)
![Image](../images/image.png)
```

✅ **Always use baseurl variable:**
```markdown
![Image]({{ site.baseurl }}/assets/images/blog/image.png)
```

**Why:** GitHub Pages serves from `/repository-name/` path, not root. Relative paths break.

**Process:**
1. Move images to `docs/assets/images/blog/` (or appropriate subdirectory)
2. Update all image references to use `{{ site.baseurl }}/assets/images/...`
3. Use descriptive filenames instead of generic names:
   - ✅ `web-clipper-trigger.png`
   - ❌ `Pasted image 20251020170203.png`

### 4. Cross-Reference Posts and Pages

**Linking to Other Posts:**

❌ **Don't hardcode URLs:**
```markdown
[My Post](blog/2025-10-20-post.html)
```

✅ **Use post_url tag:**
```markdown
[My Post]({% post_url 2025-10-20-post-title %})
```

**Why:** Ensures correct URL generation regardless of permalink settings.

**Linking to Regular Pages:**
```markdown
[CLI Tool](cli_tool.html)  # Relative to current page
[Guidelines]({{ site.baseurl }}/guidelines.html)  # Absolute with baseurl
```

### 5. Create Blog Index Page (Optional)

Location: `docs/blog/index.md`

```yaml
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
  </article>
{% endfor %}
```

### 6. Update Site Navigation

Add blog to `_config.yml` navigation:

```yaml
header_pages:
  - index.md
  - guidelines.md
  - blog/index.md  # Add blog index
  - faq.md
```

### 7. Reference from Other Pages

Update homepage or relevant pages to link to new content:

```markdown
## Latest Updates

- **[Post Title]({% post_url 2025-10-20-post-title %})** (Oct 2025) - Brief description
```

### 8. Commit and Push

```bash
git add docs/
git commit -m "docs: Add blog post about [topic]

- Created Jekyll-formatted post in _posts/
- Added images to assets/images/blog/
- Updated cross-references and navigation

🤖 Generated with [Claude Code](https://claude.ai/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>"

git push
```

### 9. Verify Deployment

After GitHub Pages builds (usually 1-2 minutes):

**Check:**
- [ ] Post appears at blog index
- [ ] All images load correctly
- [ ] Internal links work
- [ ] Navigation includes blog
- [ ] RSS feed includes post (if using jekyll-feed)

**URLs to verify:**
- Blog index: `https://username.github.io/repo/blog/`
- Post: `https://username.github.io/repo/YYYY/MM/DD/post-title.html`
- Images: `https://username.github.io/repo/assets/images/blog/image.png`

## Troubleshooting Common Issues

### Post Not Showing in Blog

**Possible causes:**
1. **Wrong directory** - Must be in `_posts/` not `blog/`
2. **Wrong filename format** - Must be `YYYY-MM-DD-title.md`
3. **Future date** - Posts with future dates don't show by default
4. **Missing frontmatter** - Requires `layout: post` at minimum

**Fix:**
```bash
# Move to correct directory
mv docs/blog/2025-10-20-post.md docs/_posts/

# Rename if needed
mv docs/_posts/post.md docs/_posts/2025-10-20-post.md
```

### Images Not Loading (404)

**Possible causes:**
1. **Wrong path** - Not using `{{ site.baseurl }}`
2. **Wrong directory** - Images in excluded/underscore directory
3. **Case sensitivity** - Filename case mismatch

**Fix:**
```bash
# Move images to standard location
mkdir -p docs/assets/images/blog
mv docs/blog/_files_/* docs/assets/images/blog/

# Update all image references in post
# From: ![](blog/_files_/image.png)
# To:   ![]({{ site.baseurl }}/assets/images/blog/image.png)
```

### Links Between Posts Broken

**Fix:**
Use `{% post_url %}` tag instead of hardcoded paths:

```markdown
# Before
[Other Post](blog/2025-10-15-other-post.html)

# After
[Other Post]({% post_url 2025-10-15-other-post %})
```

### Local Preview Works, GitHub Pages Doesn't

**Causes:**
- Baseurl not used in paths (works locally at `/`, fails on GitHub at `/repo/`)
- Absolute paths without baseurl
- Files in wrong directories

**Fix:**
- Add `baseurl: "/repository-name"` to `_config.yml`
- Use `{{ site.baseurl }}` in all asset/page references
- Test locally with: `bundle exec jekyll serve --baseurl /repository-name`

## Caveats

### Obsidian to Jekyll Conversion

When converting from Obsidian format:

1. **Image embeds**: `![[image.png]]` → `![Alt text]({{ site.baseurl }}/assets/images/blog/image.png)`
2. **Wiki links**: `[[Page Name]]` → Use proper Markdown links or Jekyll tags
3. **Image sizing**: `![[image.png|400]]` → Use HTML: `<img src="..." width="400">`
4. **Frontmatter**: Obsidian tags vs Jekyll categories/tags differ

### GitHub Pages Limitations

- **Build time**: 1-2 minutes after push
- **No custom plugins**: Only whitelisted plugins work
- **Case-sensitive**: URLs are case-sensitive on Linux/GitHub
- **Future posts**: Won't show by default (configurable)

### Minima Theme Specifics

- Uses `header_pages` for navigation (list in `_config.yml`)
- Posts automatically appear in `site.posts` collection
- Default post URL: `/YYYY/MM/DD/title.html`
- Can customize with `permalink` in frontmatter

## Best Practices

1. **Always test locally** before pushing
2. **Use descriptive image names** for better SEO and maintainability
3. **Keep assets organized** by category/post in subdirectories
4. **Document your baseurl** in README if non-standard
5. **Use post_url tags** for internal post references
6. **Commit atomically** - one post per commit for easier rollback
7. **Check build status** in GitHub Actions/Pages settings after push

## Quick Reference

```bash
# Create new post
touch docs/_posts/$(date +%Y-%m-%d)-post-title.md

# Add images
cp *.png docs/assets/images/blog/

# Test locally
cd docs && bundle exec jekyll serve --baseurl /repo-name

# Common image path pattern
{{ site.baseurl }}/assets/images/blog/image-name.png

# Common post reference pattern
{% post_url YYYY-MM-DD-post-title %}
```
