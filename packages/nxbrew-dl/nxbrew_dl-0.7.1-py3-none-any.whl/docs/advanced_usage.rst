############
Advanced Use
############

Region and Language Priorities
==============================

For users who want more granular control over which release to grab when there are multiple, we expose region/language
priorities. The menu looks like this:

.. image:: img/gui_region_language.png

If there are multiple releases, we parse regions and languages, and will remove any releases that aren't in selected
region or language preferences. At this stage, the ordering of regions and languages is not important.

Following this, we then score if there are multiple remaining releases. We prioritise region over language, so, for
instance, if you have Europe above USA in the region priority, but language set to English, you would grab the EU
version over the US version. Here, the ordering of the regions and languages is now important!

This should ensure that you grab 1 preferred release over all others.
