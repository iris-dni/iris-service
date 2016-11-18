=============
Mandrill Mail
=============

.. contents::


Mails sent from IRIS are sent via `mandrill <https://www.mandrill.com>`_


Mails
=====

+------------------------------+---------------------+------------------------------------------------------+---------------+
|                              | Send To             | Template                                             | Variables     |
+==============================+=====================+======================================================+===============+
| Petition Email Confirmation  | petition owner      | iris-petition-mailconfirmation                       | - confirm.url |
|                              |                     |                                                      | - petition    |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Supporter Email Confirmation | petition owner      | iris-supporter-mailconfirmation                      | - confirm.url |
|                              |                     |                                                      | - petition    |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Rejected            | petition owner      | iris-petition-rejected                               | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Approved            | petition owner      | iris-petition-approved                               | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Winner              | petition owner      | iris-petition-winner                                 | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Closed              | petition owner      | iris-petition-closed                                 | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Closed              | petition supporters | iris-petition-closed-notification-for-supporters     | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Half Time           | petition owner      | iris-petition-supportable-half-time                  | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Final Spurt         | petition owner      | iris-petition-supportable-final-spurt                | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Won                 | petition owner      | iris-petition-processing-notification-for-owner      | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Won                 | petition supporters | iris-petition-processing-notification-for-supporters | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Loser               | petition owner      | iris-petition-loser-notification-for-owner           | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition Loser               | petition supporters | iris-petition-loser-notification-for-supporters      | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+
| Petition No Letter Response  | petition owner      | iris-petition-closed-without-response                | - petiton     |
|                              |                     |                                                      | - user        |
+------------------------------+---------------------+------------------------------------------------------+---------------+


Mail Data
=========

Petition
--------

These variables are provided for petitions::

    petition.city.answer_name
    petition.city.answer_text
    petition.city.id
    petition.city.name
    petition.city.provider
    petition.city.state
    petition.city.tags
    petition.city.treshold
    petition.city.zips
    petition.dc.created
    petition.dc.effective
    petition.dc.expires
    petition.dc.modified
    petition.description
    petition.id
    petition.owner.email
    petition.owner.email_trusted
    petition.owner.firstname
    petition.owner.lastname
    petition.owner.mobile
    petition.owner.mobile_trusted
    petition.owner.salutation
    petition.owner.street
    petition.owner.town
    petition.owner.zip
    petition.response_token
    petition.state.listable
    petition.state.name
    petition.state.parent
    petition.state.tick
    petition.suggested_solution
    petition.supporters.amount
    petition.supporters.remaining (*)
    petition.supporters.required
    petition.tags
    petition.title
    petition.type

    (*): calculated


User
----

These variables are provided for the user which receives the mail::

    user.email
    user.mobile
    user.salutation
    user.firstname
    user.lastname
    user.city
    user.zip
    user.town


Frontend Requirements
=====================

Confirmation URL
----------------

For the email confirmation an endpoint is usend in the frontend to handle the
confirmation.

Fronten URLs::

    confirm petition email: /confirm/email/petition?key=<confirmation-key>
    confirm support email: /confirm/email/supporter?key=<confirmation-key>

With the provided key an api call is needed to confirm the email::

    /v1/confirmations/<confirmation-key>/confirm
