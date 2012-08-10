#-*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2013 CERN.
##
## Invenio is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License as
## published by the Free Software Foundation; either version 2 of the
## License, or (at your option) any later version.
##
## Invenio is distributed in the hope that it will be useful, but
## WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
## General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with Invenio; if not, write to the Free Software Foundation, Inc.,
## 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
"""
Functions to manage the premium users, packages and collections.
"""

from invenio import webpayment_query as db
from invenio.access_control_admin import acc_add_authorization
from invenio.access_control_admin import acc_add_premium_role
from invenio.access_control_admin import acc_delete_role_action
from invenio.access_control_admin import acc_get_action_id
from invenio.access_control_config import VIEWRESTRCOLL
from invenio.access_control_firerole import compile_role_definition
from invenio.access_control_firerole import serialize
from invenio.dateutils import SECOND_CONVERSION
from invenio.websearch_model import Collection
from invenio.websession_model import User


def add_new_premium_package(form):
    """
    Adds a premium package to the database. Arranges the restrictions for
    collections of the new premium package.

    @param form: The form contains properties of the new premium package.
    @type form: L{PremiumPackageForm}
    """
    # Add premium package to the database
    package = db.add_new_premium_package(form)

    # Arrange the restrictions
    fix_roles_and_authorizations(package.id, form.collections.data)


def edit_premium_package(form):
    """
    Edits the premium package. Arranges the restrictions for
    collections of the premium package.

    @param form: The form contains the new properties of the premium package.
    @type form: L{PremiumPackageForm}
    """
    # Edit the premium package
    package = db.edit_premium_package(form)

    # Arrange the restrictions
    fix_roles_and_authorizations(package.id, form.collections.data)


def fix_roles_and_authorizations(id_package, collections):
    """
    Arranges the restrictions for the premium collections.

    @param id_package: The ID of the premium package
    @type id_package: int

    @param collections: IDs of the collections which are restricted by
                        the premium package with given ID.
    @type collections: list
    """
    # First remove the list of the restricted collections.
    db.remove_premium_collection(id_package)

    # Make each collection restricted.
    for id_collection in collections:
        # Add the collection to the restricted collections list of the premium
        # package
        db.add_premium_collection(id_package, id_collection)

        # Create a role to display the restricted collection
        id_role = add_role_and_authorization(id_collection)

        # If the role is just created (ie. no such roles before), add it to the
        # list that keeps which collection can be displayed by which role.
        if id_role:
            db.add_collection_role(id_collection, id_role)


def add_role_and_authorization(id_collection):
    """
    Restricts the collection with given ID. Adds a role and an authorization to
    restrict the collection.

    @param id_collection: the ID of the collection that will be restricted.
    @type id_collection: int

    @return: 0 if the collection is already restricted,
             id of the created role, otherwise.
    @rtype: int
    """

    # Construct a role name
    role_name = "premium_collection" + str(id_collection) + "_viewer"

    # Get the name of the collection
    collection_name = (Collection.query
                       .filter(Collection.id == id_collection)
                       .one().name)

    # Construct the description of the role.
    description = "Premium users who can view " + collection_name

    # Construct the fireroles to make it restricted
    firerole_def_src = "deny any"
    firerole_def_ser = serialize(compile_role_definition(firerole_def_src))

    # Create the role
    res = acc_add_premium_role(role_name,
                               description,
                               firerole_def_ser=firerole_def_ser,
                               firerole_def_src=firerole_def_src)

    # Add the authorization
    acc_add_authorization(role_name,
                          VIEWRESTRCOLL,
                          collection=collection_name)

    # Return the id of the role.
    return res[0]


def grant_user_access(id_user, premium_package=None, id_package=0):
    """
    Give the user with given ID the access to the collections restricted by
    given premium package.

    @param id_user: ID of the premium user.
    @type id_user: int

    @param premium_package: Premium package bought by the user.
    @type premium_package: L{Premium}

    @param id_package: ID of the premium package bought by the user.
    @type id_package: int

    @raise Exception: Raises exception if neither premium package nor its ID
                      is given.
    """
    # Get the premium package if it's not given.
    if not premium_package:
        if id_package:
            # Find it by its ID.
            premium_package = db.get_premium_package(id_package)
        else:
            # If there is no ID given, throw an exception.
            raise Exception("Neither premium package nor id is given!")

    # Get the roles of the premium package that allow to display restricted
    # collections.
    roles = db.get_premium_roles(premium_package.id)

    # Calculate the duration of the premium package by seconds
    total_seconds = (premium_package.duration
                     * SECOND_CONVERSION.get(premium_package.unit_time, 0))

    # Give access rights to the user
    for role in roles:
        db.add_premium_user_role(id_user, role[0], total_seconds)


def gift_premium_package(gift_form):
    """
    Gives a premium package to a user as gift.

    @param gift_form: form that contains the ID of the user and premium
                      package.
    @type gift_form: L{GiftPremiumPackageForm}

    @todo: Find a function that returns the id when nickname is supplied.
    """
    grant_user_access(User.query.filter(User.nickname ==
                                        gift_form.username.data).one().id,
                      id_package=gift_form.premium_package.data)


def get_possible_packages(id_collection=0):
    """
    @return: the premium packages which allow displaying the collection
    with given id.
    @rtype: list
    """
    return db.get_possible_packages_by_id(id_collection)


def get_package_collection_map():
    """
    Returns a dictionary that contains information about which premium package
    allows to access which collections.

    @rtype: dict
    @return: Dict structure: {int: [{'id': int, 'name': str}]}
    """
    package_collection_map = {}

    # @type package_collection_pair: [(int, int, str)]
    package_collection_pair = db.get_package_collection_triple()

    # Convert [(a,b,c)] to {a: [{'id': b, 'name': c}]}
    for package, id_collection, name_collection in package_collection_pair:
        if not package in package_collection_map.keys():
            package_collection_map[package] = []
        package_collection_map[package].append({'id': id_collection,
                                               'name': name_collection})

    return package_collection_map


def register_payment_history(id_user, premium_package, payment_method,
                             token=''):
    """
    Registers the transaction to payment history.

    @param id_user: The ID of the user which bought the premium package.
    @type id_user: int

    @param premium_package: The premium package that the the user bought.
    @type premium_package: L{Premium}

    @param payment_method: The method of the transaction. (eg. paypal,
                           credit card, etc.)
    @type payment_method: str

    @param token: The transaction ID returned from payment gateway.
    @type token: str
    """
    db.register_payment_history(id_user, premium_package, payment_method,
                                token)


def delete_premium_package(id_package):
    """
    Deletes the premium package with given ID. Arranges the restrictions of
    the collections that can be displayed by this premium package.

    @param id_package: The id of the premium package deleted.
    @type id_package: int
    """
    # Get the collections of the premium package
    collections = db.get_package_collections(id_package)

    for collection in collections:
        # For each collection, look if there are any premium packages give user
        # a grant to access that collection.
        other_packages = db.get_possible_packages_by_id(collection
                                                        .id_collection)
        if len(other_packages) == 1:
            # If there is no other premium package, remove the restriction.
            id_role = (db.get_collection_role(collection.id_collection)
                       .id_accROLE)
            id_action = acc_get_action_id(VIEWRESTRCOLL)
            acc_delete_role_action(id_role, id_action)

    db.remove_premium_collection(id_package)
    db.delete_premium_package(id_package)


def get_user_premium_membership(id_user):
    """
    Returns total number of premium packages and the number of premium package
            the user purchased.

    @param id_user: the ID of the user
    @type id_user: int

    @rtype: tuple
    """
    total = db.get_premium_collection_number()
    user = db.get_user_premium_collection_number(id_user)
    return total, user


def get_membership_expiration_dates(id_user):
    """
    Returns the expiration dates of the premium memberships of the user with
    given ID.

    @param id_user: the ID of the user.
    @type id_user: int

    @rtype: list
    """
    return db.get_membership_expiration_dates(id_user)
