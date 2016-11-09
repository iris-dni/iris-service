=============
Mandrill Mail
=============

.. contents::


Mails sent from IRIS are sent via `mandrill <https://www.mandrill.com>`_


Petition Email Confirmation Mail
--------------------------------

template id: iris-petition-mailconfirmation

Variables provided:

  - petition
  - user
  - confirm_url - URL which must be used to confirm the email


Supporter Email Confirmation Mail
---------------------------------

template id: iris-supporter-mailconfirmation

Variables provided:

  - petition
  - user
  - confirm_url - URL which must be used to confirm the email


Mail Data
=========

Petition
--------

These variables are provided for petitions::

    petition_city_answer_name
    petition_city_answer_text
    etition_city_id
    petition_city_name
    petition_city_provider
    petition_city_state
    petition_city_tags
    petition_city_treshold
    petition_city_zips
    petition_dc_created
    petition_dc_effective
    petition_dc_expires
    petition_dc_modified
    petition_description
    petition_id
    petition_owner_email
    petition_owner_email_trusted
    petition_owner_firstname
    petition_owner_lastname
    petition_owner_mobile
    petition_owner_mobile_trusted
    petition_owner_street
    petition_owner_town
    petition_owner_zip
    petition_state_listable
    petition_state_name
    petition_state_parent
    petition_state_tick
    petition_suggested_solution
    petition_supporters_amount
    petition_supporters_remaining
    petition_supporters_required
    petition_tags
    petition_title
    petition_type


User
----

These variables are provided for the user which receives the mail::

    user_email
    user_mobile
    user_firstname
    user_lastname
    user_city
    user_zip
    user_town
