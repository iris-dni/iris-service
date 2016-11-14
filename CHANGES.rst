========================
Changes For IRIS Service
========================

unreleased
==========

 - send mail when petition support is short before being a loser
 - send mail when petition support is half over
 - send mail when petition closed without letter response
 - send mail when petition support is finished
 - send mail when petition is closed
 - send mail when petition letter was sent
 - send mail when petition is winner
 - send mail when petition is approved
 - send mail on petition rejected
 - changed SMS wording
 - provide only numerical mobile tokens
   DEPLOY:
     ALTER TABLE confirmations ADD COLUMN response OBJECT(IGNORED);
 - extended petition statemachine with noLetterResponse flow
   DEPLOY:
     ALTER TABLE petitions ADD COLUMN state['letter_wait_expire'] TIMESTAMP;
 - send email confirmation mails when publishing and supporting petitions
 - added mandril send method with logging
 - access permissions for petition events:
   all events need admin permissions except `publish` and `support`
 - added general petition extender to remove private data from the owner
   relation.

2016/11/07 0.3.1
================

 - approving a petition is only possible if a city is assigned to the petition
 - added petition tick worker as distributed cron job
 - added tick property on the petition state
   DEPLOY:
    - ALTER TABLE petitions ADD COLUMN state['tick'] BOOLEAN;

2016/11/03 0.3.0
================

 - dc.expires provides the time when support is over
 - dc.effective provides the publish time
 - allow to resolve "city.location" on petitions
 - added Cities.portal
   DEPLOY: add column 'portal' to Cities table
    - ALTER TABLE cities ADD COLUMN portal OBJECT(IGNORED);
    - ALTER TABLE cities ADD COLUMN location string;
 - added trending petition sort
 - added dimension and image proxy base url in files
   DEPLOY: add column info in files table
 - added town property user relation in swagger spec
 - added file service (upload and download)
   DEPLOY:
    - recreate files table in Crate
    - enable libmagic in Docker containers
 - provide a reason in the support endpoint if the token is invalid
 - handle SMS send exceptions with a ValueError

2016/10/17 0.2.0
================

 - fixed support for not logged in users
 - incompatible change
   DEPLOY:
    - reset the database
 - added trust flow when supporting petitions
 - added trust flow when publishing petitions

2016/10/05 0.1.1
================

 - fix petition owner filter
 - fix extend paramater for search endpoints
 - added OPTION endpoint for og/check
 - petition.city_answer is now an object
   DEPLOY:
     run auto migration

2016/09/22 0.1.0
================

 - og: fallback for title and description
 - og/check endpoint stores data in weblocation
 - add the petition creator as supporter when publishing a petition
 - added force_state event endpoint
 - enable petition owner filter in swagger
 - added letter response flow to petition
 - allow to request multiple petitions in the GET endpoint
 - added "supporting" extender for petition endpoints
 - added generic "extend" query parameter for API calls
 - fix required supporters setup if a city has no treshold set
 - resetog endpoint for weblocations
 - added automatic open graph data update for weblocations
 - added election module
 - added open graph service

2016/09/13 0.0.11
=================

 - public city get endpoint allows strings as id

2016/09/12 0.0.10
=================

 - set supporters treshold when setting the city on a petition
 - undefined supporters treshold is set to -1
 - read approval days from settings
 - allow to resolve petition relations in all event endpoints
 - refactored module structure
   DEPLOY:
     Needs a new database to be created from the samples.
 - petition web location properties allow a "url" property to set the web
   location
 - added weblocations admin API
 - do not provide trigger "support" on petition state machine
 - petition API: provide relation lists for images, videos and links
 - API: allow to resolve relations

2016/08/26 0.0.9
================

 - support event creates supporter data
 - allow admin API to write on petition owner field
 - added city_answer field to petitions
   DEPLOY:
     ALTER TABLE petitions ADD COLUMN city_answer STRING INDEX OFF;
 - reverted events endpoints to use generic options path definition by adding
   it to the swagger spec
 - do not use generic options endpoint but specific ones

2016/08/10 0.0.8
================

 - fixed permission problems on OPTIONS endpoints
 - added petition state management

2016/08/10 0.0.7
================

 - removed allowed schema from swagger api config

2016/07/13 0.0.6
=================

 - pseudo release to test deployments

 - included swagger ui into the egg

2016/07/13 0.0.3
=================

 - fix dependencies

2016/07/13 0.0.2
=================

 - first version
