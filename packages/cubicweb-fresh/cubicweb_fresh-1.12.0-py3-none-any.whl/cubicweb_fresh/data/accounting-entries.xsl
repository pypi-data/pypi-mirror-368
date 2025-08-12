<?xml version="1.0" encoding="UTF-8"?>

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
                version="1.0">
  <xsl:output method="text" encoding="UTF-8"/>

  <xsl:template match="*">
    <xsl:param name="indent" select="''"/>

    <xsl:call-template name="write-element">
      <xsl:with-param name="indent" select="$indent"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template match="ecriture">
    <xsl:param name="indent" select="''"/>

    <xsl:call-template name="write-element">
      <xsl:with-param name="indent" select="$indent"/>
    </xsl:call-template>
    <xsl:if test="following-sibling::ecriture">
      <xsl:text>
</xsl:text>
    </xsl:if>
  </xsl:template>

  <xsl:template match="@*">
    <xsl:text> </xsl:text>
    <xsl:value-of select="name()"/>
    <xsl:text>="</xsl:text>
    <xsl:value-of select="."/>
    <xsl:text>"</xsl:text>
  </xsl:template>

  <xsl:template match="text()">
    <xsl:if test="normalize-space(.)">
      <xsl:value-of select="."/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="write-element">
    <xsl:param name="indent" select="''"/>

    <xsl:text>
</xsl:text>
    <xsl:value-of select="$indent"/>
    <xsl:text>&lt;</xsl:text>
    <xsl:value-of select="name()"/>
    <xsl:apply-templates select="@*">
      <xsl:sort select="name()"/>
    </xsl:apply-templates>
    <xsl:if test="not(*|text())">
      <xsl:text>/</xsl:text>
    </xsl:if>
    <xsl:text>></xsl:text>

    <xsl:if test="*|text()">
      <xsl:apply-templates select="*|text()">
	<xsl:with-param name="indent" select="concat($indent,'  ')"/>
      </xsl:apply-templates>

      <xsl:if test="*">
	<xsl:text>
</xsl:text>
        <xsl:value-of select="$indent"/>
      </xsl:if>
      <xsl:text>&lt;/</xsl:text>
      <xsl:value-of select="name()"/>
      <xsl:text>></xsl:text>
    </xsl:if>
  </xsl:template>

</xsl:stylesheet>
