---
description: "Documentation and content creation standards"
applyTo: "**/*.md"
---

## Markdown Content Rules

- **Headings**: Must have H1 matching front-matter title. Use ## for H2, ### for H3. Avoid H4+ unless necessary.
- **Lists**: Use `-` for bullets, `1.` for numbered. Indent nested with 2 spaces.
- **Code Blocks**: Use triple backticks with language (e.g., ```csharp).
- **Links**: `[descriptive text](URL)`.
- **Images**: `![alt text](URL)` with meaningful alt.
- **Tables**: Proper alignment with headers.
- **Line Length**: Soft break at 80 chars, hard limit 400 chars.
- **Whitespace**: Blank lines between sections, no excessive.

## Front Matter Requirements (YAML at top)
- `ai`: true/false
- `title`: required
- `aliases`
- `created`: YYYY-MM-DDTHH:MM:SS
- `modified`: YYYY-MM-DDTHH:MM:SS
- `author`
- `description`
- `tags`

All Markdown files must pass these rules and front-matter validation.