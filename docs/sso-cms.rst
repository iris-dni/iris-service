=========================
Single Sign On - CMS Flow
=========================

.. contents::

Because authentication is only possible via SSO, CMS login must use external
SSO Providers to authenticate users.

.. uml::

    @startuml
    Title CMS Login

    actor user
    participant "CMS-Frontend" as cms
    participant "SSOProvider" as provider
    participant "IRIS-Login-Embed" as iris

    cms -> user : show login screen with SSO Providers
    user -> cms : selected SSO Provider
    cms -> provider : open provider login page
    provider -> iris : trigger code
    activate iris
    iris -> iris : check SSO login
    deactivate iris
    provider -> user : login page
    user -> provider : enter login data
    user -> provider : login
    provider -> cms : redirect to CMS
    cms -> user : show CMS

    @enduml

The login page of the provider must contain the IRIS embed login code and must
provide the SSO data via the SSOConfig global data.

IRIS embed code checks if the user is already logged in via IRISConfig.

If an SSO login is provided the login is made on the IRIS domain and the user
is redirected back to the CMS.
