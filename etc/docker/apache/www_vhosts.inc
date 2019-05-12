# vim: syntax=apache

# WWW's VirtualHost
<VirtualHost *:80>
    ServerName www.caltech.edu
    ServerAlias caltech.edu
    ServerAlias m.caltech.edu
    ServerAlias main.localhost
    ServerAlias main.oscweb.caltech.edu
    ServerAlias mockwww.oscweb-test.caltech.edu
</VirtualHost>

# a VirtualHost to redirect today.caltech.edu to the current today location
<VirtualHost *:443>
    ServerName www.caltech.edu
    ServerAlias caltech.edu
    ServerAlias m.caltech.edu
    ServerAlias main.localhost
    ServerAlias main.oscweb.caltech.edu
    ServerAlias mockwww.oscweb-test.caltech.edu

    RewriteEngine On
    RewriteRule ^/~(.+) http://www.its.caltech.edu/~$1 [R=301,L]
    RewriteRule ^/%7E(.+) http://www.its.caltech.edu/~$1 [R=301,L]
    RewriteRule ^/catalog http://catalog.caltech.edu [R=301,L]
    RewriteRule ^/support$ http://giving.caltech.edu [R=301,L]
    RewriteRule ^/content/support$ http://giving.caltech.edu [R=301,L]
    RewriteRule ^/catalog/ http://catalog.caltech.edu/ [R=301,L]
    RewriteRule ^/give https://securelb.imodules.com/s/1709/devassoc/index.aspx?sid=1709&gid=3&pgid=498 [R=301,L]
    RewriteRule ^/dir$ http://giving.caltech.edu/about-us [R=301,L]
    RewriteRule ^/giving https://securelb.imodules.com/s/1709/devassoc/index.aspx?sid=1709&gid=3&pgid=498 [R=301,L]
    RewriteRule ^/annualreport2012 http://annualreport.caltech.edu/2012 [R=301,L]
    RewriteRule ^/annualreport2012/(.*) http://annualreport.caltech.edu/2012/$1 [R=301,L]
    RewriteRule ^/office365 http://office365.caltech.edu [R=301,L]
    RewriteRule ^/office365/(.*) http://office365.caltech.edu/$1 [R=301,L]
    RewriteRule ^/inauguration http://inauguration.caltech.edu/$1 [R=301,L]
    RewriteRule ^/pranks http://www.admissions.caltech.edu/pranks [R=301,L]
    RewriteRule ^/impact$ http://breakthrough.caltech.edu [R=301,L]

    # Rewrite Drupal map URLs (/map/slug) to the new style (/map/campus/slug), without touching any new URLs offered by
    # the 'map' app (/map/campus*, /map/history*, etc.).
    RewriteCond %{REQUEST_URI} !^/map/landmark_autocomplete.*
    RewriteCond %{REQUEST_URI} !^/map/landmark_ajax.*
    RewriteCond %{REQUEST_URI} !^/map/milestone.*
    RewriteCond %{REQUEST_URI} !^/map/history.*
    RewriteCond %{REQUEST_URI} !^/map/campus.*
    RewriteRule ^/map/(.+)$ /map/campus/$1 [R=301,L]

    # Office 365 is dumb, and it requests www.caltech.edu/autodiscover/autodiscover.xml even though it's
    # not configured to do so. The correct domain is outlook.caltech.edu, so we redirect there.
    RewriteRule ^/autodiscover/autodiscover.xml$ https://outlook.caltech.edu/autodiscover/autodiscover.xml [R=301,L]

    # We used to redirect filming.caltech.edu to www.caltech.edu/filming. Now, filming.caltech.edu
    # is a seaparate site, so we do the reverse.
    Redirect permanent /filming http://filming.caltech.edu
</VirtualHost>

# a VirtualHost to redirect today.caltech.edu to the current today location
<VirtualHost *:443>
    ServerName today.caltech.edu
    ServerAlias www.today.caltech.edu

    RewriteEngine On
    RewriteRule ^/(.*)$  https://www.caltech.edu/campus-life-events/caltech-today [R=301,L]
</VirtualHost>

# a VirtualHost to redirect today.caltech.edu to the current today location
<VirtualHost *:443>
    ServerName nobel.caltech.edu
    ServerAlias www.nobel.caltech.edu

    RewriteEngine On
    RewriteRule ^ https://www.caltech.edu/about/legacy/historic-awards-honors/nobel-laureates
</VirtualHost>
