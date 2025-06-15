TEMPLATE_CONTENT_PARENT = str( 
    "<details class='content-parent'>\n"
    "<summary>\n"
    "{}\n"
    "</summary>\n"
    "{}\n"
    "</details>"
)

TEMPLATE_CONTENT_CHILD = str( 
    "<details class='content-child'>\n"
    "<summary>\n"
    "<span class='rss-title'> {} </span> <a class='rss-link' href='{}' target='_blank'>&nbsp;</a>\n"
    "<div class='rss-published'> 🕛 {}</div>\n"
    "</summary>\n"
    "{}\n"
    "</details>"
)

TEMPLATE_POST = str( 
    "---\n"
    "layout: default\n"
    "title: {}\n"
    "updated: {}\n"
    "---\n\n"
)