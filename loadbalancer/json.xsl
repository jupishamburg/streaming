<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="2.0"><xsl:output omit-xml-declaration="yes" method="text" indent="no" 
encoding="UTF-8"/><xsl:strip-space elements="*"/><xsl:template match="/icestats"><!-- <xsl:param name="callback" /> <xsl:value-of select="$callback" 
/> -->{"Copyright":"<xsl:value-of select="admin"/>","Location":"<xsl:value-of select="location"/>","total_listeners":"<xsl:value-of 
select="listeners"/>","mounts":[<xsl:for-each select="source">{"mount":"<xsl:value-of select="@mount"/>","server_name":"<xsl:value-of 
select="server_name"/>","listeners":"<xsl:value-of select="listeners"/>","description":"<xsl:value-of select="server_description" />","title":"<xsl:if 
test="artist"><xsl:value-of select="artist" /> - </xsl:if><xsl:value-of select="title" />","genre":"<xsl:value-of select="genre" 
/>","bitrate":"<xsl:value-of select="bitrate" />","url":"<xsl:value-of select="server_url" />"}<xsl:if test="position() != 
last()"><xsl:text>,</xsl:text></xsl:if></xsl:for-each>]}</xsl:template></xsl:stylesheet>
