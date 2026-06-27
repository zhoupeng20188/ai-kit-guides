<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:atom="http://www.w3.org/2005/Atom">
  <xsl:output method="html" version="1.0" encoding="UTF-8" indent="yes"/>
  <xsl:template match="/">
    <html xmlns="http://www.w3.org/1999/xhtml">
      <head>
        <meta charset="utf-8"/>
        <meta name="viewport" content="width=device-width, initial-scale=1"/>
        <title>AI Kit Guides — RSS Feed</title>
        <style>
          body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; max-width: 680px; margin: 40px auto; padding: 0 20px; color: #1e293b; }
          h1 { font-size: 1.75rem; }
          h1 a { color: #0ea5e9; text-decoration: none; }
          .description { color: #64748b; margin-bottom: 2rem; }
          .item { border-bottom: 1px solid #e2e8f0; padding: 1rem 0; }
          .item h2 { font-size: 1.1rem; margin: 0 0 0.25rem; }
          .item h2 a { color: #0284c7; text-decoration: none; }
          .item h2 a:hover { text-decoration: underline; }
          .item .meta { color: #94a3b8; font-size: 0.85rem; }
          .item p { color: #475569; font-size: 0.9rem; line-height: 1.5; }
        </style>
      </head>
      <body>
        <h1><xsl:value-of select="/rss/channel/title"/></h1>
        <p class="description"><xsl:value-of select="/rss/channel/description"/></p>
        <xsl:for-each select="/rss/channel/item">
          <div class="item">
            <h2><a href="{link}"><xsl:value-of select="title"/></a></h2>
            <div class="meta"><xsl:value-of select="pubDate"/></div>
            <p><xsl:value-of select="description"/></p>
          </div>
        </xsl:for-each>
      </body>
    </html>
  </xsl:template>
</xsl:stylesheet>
