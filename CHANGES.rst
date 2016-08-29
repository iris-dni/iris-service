========================
Changes For IRIS Service
========================

unreleased
==========

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
