# -*- coding: utf-8 -*-
##
## This file is part of Invenio.
## Copyright (C) 2012, 2013 CERN.
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
Database related functions to manage the premium users,
packages and collections.
"""
from datetime import datetime
from datetime import timedelta
from invenio.sqlalchemyutils import db
from invenio.webaccess_model import UserAccROLE
from invenio.webpayment_model import CollectionAccROLE
from invenio.webpayment_model import HstPAYMENT
from invenio.webpayment_model import Premium
from invenio.webpayment_model import PremiumCollection
from invenio.websearch_model import Collection
from invenio.websearch_model import CollectionCollection
from invenio.websession_model import User
from sqlalchemy.sql import expression
from sqlalchemy.sql import functions
from sqlalchemy.sql import operators
#{ Premium package functions


def add_new_premium_package(form):
    """
    Adds a new premium package to the database.

    @param form: The form contains properties of the new premium package.
    @type form: L{PremiumPackageForm}

    @return: Added premium package.
    @rtype: L{Premium}
    """
    package = Premium()
    form.populate_obj(package)
    # Find a place to the new premium package
    try:
        package.ord = get_order_of_new_package()
    except:
        package.ord = 1

    # If there is no error, create it
    try:
        db.session.add(package)
        db.session.commit()
    except:
        db.session.rollback()
        raise Exception

    return package


def edit_premium_package(form):
    """
    Edits the premium package.

    @param form: The form contains the new properties of the premium package.
    @type form: L{PremiumPackageForm}

    @return: Edited premium package.
    @rtype: L{Premium}
    """
    # Get the package from database ...
    package = get_premium_package(form.package_id.data)

    # ... and edit it according the given form.
    form.populate_obj(package)

    return package


def get_all_premium_packages():
    """
    Returns all of the premium packages.

    @rtype: [L{Premium}]
    """
    return Premium.query.order_by(Premium.ord).all()


def get_order_of_new_package():
    """
    Returns the order of the new premium package.

    @rtype: int
    """
    return (db.session
            .query(functions.max(Premium.ord))
            .first()[0] + 1)


def get_premium_package(id_package):
    """
    Returns the premium package with given ID.

    @param id_package: The ID of the premium package.
    @type id_package: int

    @rtype: L{Premium}
    """
    return Premium.query.filter(Premium.id == id_package).one()


def move_package_down(id_package):
    """
    Increases the order of the premium package with given id.

    Swaps the orders of the given premium package and the lower one.

    @param id_package: The ID of the premium package.
    @type id_package: int
    """
    package = Premium.query.filter(Premium.id == id_package).one()
    package_down = Premium.query.filter(Premium.ord == (package.ord + 1)).one()
    package.ord = package.ord + 1
    package_down.ord = package_down.ord - 1


def move_package_up(id_package):
    """
    Decreases the order of the premium package with given id.

    Swaps the orders of the given premium package and the upper one.

    @param id_package: The ID of the premium package.
    @type id_package: int
    """
    package = Premium.query.filter(Premium.id == id_package).one()
    package_down = Premium.query.filter(Premium.ord == (package.ord - 1)).one()
    package.ord = package.ord - 1
    package_down.ord = package_down.ord + 1


def delete_premium_package(id_package):
    """
    Deletes the premium package with given ID.

    Decreases the orders of the premium package with higher order.

    @param id_package: The ID of the premium package deleted.
    @type id_package: int
    """
    package = get_premium_package(id_package)

    for other in Premium.query.filter(Premium.ord > package.ord).all():
        other.ord = other.ord - 1

    Premium.query.filter(Premium.id == id_package).delete()


def get_possible_packages_by_id(id_collection):
    """
    Returns the premium packages allowing to display the collection with given
    ID.

    @param id_collection: The ID of the restricted collection.
    @type id_collection: int

    @rtype: [L{Premium}]
    """
    return (Premium.query
            .filter(PremiumCollection.id_collection == id_collection)
            .filter(PremiumCollection.id_package == Premium.id)
            .order_by(Premium.ord)
            .all())

#{ Collection related functions


def get_all_collections():
    """
    Returns IDs and names of all of the collections that can be restricted.

    @return: NamedTuple with following indices/fields.
        0. B{id} (int): the id of the collection
        1. B{name} (str): the name of the collection
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session
            .query(Collection.id, Collection.name).
            join(CollectionCollection,
                 CollectionCollection.id_son == Collection.id)
            .filter(operators.notin_op(CollectionCollection.id_son,
                                       db.session
                                       .query(CollectionCollection
                                              .id_dad)))
            .order_by(Collection.name).all())


def add_premium_collection(id_package, id_collection):
    """
    Adds new L{PremiumCollection} record to the database.

    @param id_package: The ID of the premium package.
    @type id_package: int

    @param id_collection: The id of the restricted collection.
    @type id_collection: int
    """
    if premium_collection_exists(id_package, id_collection):
        return
    try:
        premium_collection = PremiumCollection()
        premium_collection.id_collection = id_collection
        premium_collection.id_package = id_package
        db.session.add(premium_collection)
        db.session.commit()
    except:
        db.session.rollback()


def premium_collection_exists(id_package, id_collection):
    """
    Returns if the L{PremiumCollection} record exists.

    @param id_package: The ID of the premium package.
    @type id_package: int

    @param id_collection: The id of the restricted collection.
    @type id_collection: int

    @rtype: bool
    """
    try:
        (PremiumCollection.query
         .filter(PremiumCollection.id_collection ==
                 id_collection)
         .filter(PremiumCollection.id_package ==
                 id_package).one())
        return True
    except:
        return False


def remove_premium_collection(id_package):
    """
    Removes all of the L{PremiumCollection} records corresponding to the
    premium package with given ID.

    @param id_package: The ID of the premium package.
    @type id_package: int
    """
    (PremiumCollection.query
     .filter(PremiumCollection.id_package == id_package)
     .delete())


def get_package_collections(id_package):
    """
    Returns all of the L{PremiumCollection} records corresponding to the
    premium package with given ID.

    @param id_package: The ID of the premium package.
    @type id_package: int

    @rtype: [L{PremiumCollection}]
    """
    return (PremiumCollection.query
            .filter(PremiumCollection.id_package == id_package)
            .all())


def get_collection_role(id_collection):
    """
    Returns the L{CollectionAccRole} records corresponding to the collection
    with given ID.

    @param id_collection: the ID of the collection
    @type id_collection: int
    """
    return (CollectionAccROLE
            .query
            .filter(CollectionAccROLE.id_collection == id_collection)
            .one())


def get_package_collection_triple():
    """
    Returns the triples that contains the information about which premium
    packages restrict which collections.

    @return: NamedTuple with following indices/fields.
        0. B{id_package} (int): the id of the premium package.
        1. B{id_collection} (int): the id of the collection.
        2. B{name} (str): the name of the collection.
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session
            .query(PremiumCollection.id_package,
                   PremiumCollection.id_collection,
                   Collection.name)
            .filter(PremiumCollection.id_collection == Collection.id)
            .all())


def get_all_premium_restricted_collections():
    """
    Returns the list of the restricted collections.

    @rtype: [L{Collection}]
    """
    return (Collection.query
            .filter(Collection.id == PremiumCollection.id_collection)
            .all())


def get_premium_restricted_collections(id_package):
    """
    Returns the collections that is restricted by the premium package with
    given ID.

    @param id_package: The ID of the premium package
    @type id_package: int

    @rtype: [L{Collection}]
    """
    return (Collection.query
            .filter(Collection.id == PremiumCollection.id_collection)
            .filter(PremiumCollection.id_package == id_package)
            .all())


def is_collection_premium_restricted(collection_id):
    """
    Returns if the collection is restricted by a premium package.

    @param collection_name: The ID of the collection.
    @type collection_name: int

    @rtype: bool
    """
    return (db.session
            .query(functions.count(PremiumCollection.id_collection))
            .filter(PremiumCollection.id_collection == collection_id)
            .first()[0] > 0)
#{ Access related functions


def add_collection_role(id_collection, id_role):
    """
    Adds a new L{CollectionAccROLE} record to the database.

    @param id_collection: the ID of the collection
    @type id_collection: int

    @param id_role: the ID of the AccROLE
    @type id_role: int
    """
    try:
        collection_role = CollectionAccROLE()
        collection_role.id_accROLE = id_role
        collection_role.id_collection = id_collection
        db.session.add(collection_role)
        db.session.commit()
    except:
        db.session.rollback()


def add_premium_user_role(id_user, id_accROLE, total_seconds):
    """
    Gives a user a role for a finite/infinite time interval. If a user has
    already have that role, extends the current time interval.

    @param id_user: the ID of the user.
    @type id_user: int

    @param id_accROLE: the ID of the role.
    @type id_accROLE: int

    @param total_seconds: the duration of the role
    @type total_seconds: int
    """
    try:
        # First try to extend the duration if the user has already have the
        # role
        user_role = (UserAccROLE.query.filter(UserAccROLE.id_user == id_user)
                     .filter(UserAccROLE.id_accROLE == id_accROLE)
                     .one())
        if not total_seconds:
            user_role.expiration = "9999-12-31 23:59:59"
        else:
            user_role.expiration = (user_role.expiration
                                    + timedelta(seconds=total_seconds))
        db.session.commit()
        return
    except OverflowError, e:
        db.session.rollback()
        return
    except Exception, e:
        db.session.rollback()

    # Otherwise, create new record.
    try:
        user_role = UserAccROLE()
        user_role.id_user = id_user
        user_role.id_accROLE = id_accROLE
        if not total_seconds:
            user_role.expiration = "9999-12-31 23:59:59"
        else:
            user_role.expiration = (datetime.now()
                                    + timedelta(seconds=total_seconds))
        db.session.add(user_role)
        db.session.commit()
    except Exception, e:
        db.session.rollback()
        raise Exception(e)


def get_membership_expiration_dates(id_user):
    """
    Returns the expiration dates of the premium memberships for each collection
    of the given user.

    @param id_user: the ID of the user
    @type id_user: int

    @return: NamedTuple with following indices/fields.
        0. B{id_collection} (int): the id of the collection
        1. B{expiration} (datetime): the expiration date to display the
        collection
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session
            .query(CollectionAccROLE.id_collection, UserAccROLE.expiration)
            .filter(CollectionAccROLE.id_accROLE == UserAccROLE.id_accROLE)
            .filter(UserAccROLE.id_user == id_user)
            .all())


def get_premium_roles(id_package):
    """
    Returns the IDs of corresponding roles to display the collections
    restricted by the premium package with given ID.

    @param id_package: The ID of the premium package.
    @type id_package: int

    @return: NamedTuple with following indices/fields.
        0. B{id_accROLE} (int): the id of the role.
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session.query(CollectionAccROLE.id_accROLE)
            .filter(PremiumCollection.id_package == id_package)
            .filter(PremiumCollection.id_collection ==
                    CollectionAccROLE.id_collection)
            .all())

#{ Statistical information


def get_payment_history():
    """
    Returns the payment history.

    @return: NamedTuple with following indices/fields.
        0. B{transaction_time} (datetime): the time when the payment is
                                           happened.
        1. B{id_user} (int): The ID of the user.
        2. B{id_package} (int): the ID of the premium package.
        3. B{price} (float): the price of the premium package.
        4. B{currency} (str): the current of the price of the premium package.
        5. B{payment_method} (str): the payment method of the transaction.
        (eg. paypal, credit card)
        6. B{email} : the e-mail of the user.
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session
            .query(HstPAYMENT.transaction_time,
                   HstPAYMENT.id_user,
                   HstPAYMENT.id_package,
                   HstPAYMENT.price,
                   HstPAYMENT.currency,
                   HstPAYMENT.payment_method,
                   User.email)
            .join(User)
            .order_by(expression.desc(HstPAYMENT.transaction_time))
            .all())


def get_total_transaction_number():
    """
    Returns the total transaction number.

    @rtype: int
    """
    return HstPAYMENT.query.count()


def get_total_revenue():
    """
    Returns the total revenue with grouped by the currency.

    @return: NamedTuple with following indices/fields.
        0. B{price} (float): the total revenue from a currency
        1. B{currency} (str): the currency of the revenue
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session
            .query(functions.sum(HstPAYMENT.price),
                   HstPAYMENT.currency)
            .group_by(HstPAYMENT.currency)
            .all())


def get_premium_user_number():
    """
    Returns the number of premium users.

    @rtype: int
    """
    return (db.session
            .query(functions.count(expression
                                   .distinct(UserAccROLE.id_user)))
            .filter(UserAccROLE.expiration > functions.now())
            .filter(UserAccROLE.id_accROLE == CollectionAccROLE.id_accROLE)
            .one())


def get_premium_users():
    """
    Returns the premium users.

    @return: NamedTuple with following indices/fields.
        0. B{id} (int): the ID of the user
        1. B{email} (str): the email of the user
        2. B{nickname} (str): the nickname of the user
        3. B{name} (str): the name of the collection that the user is able to
        display.
        4. B{expiration} (datetime): expiration date of the premium membership
        to display the corresponding collection
    @rtype: L{sqlalchemy.util._collections.NamedTuple}
    """
    return (db.session.query(User.id,
                             User.email,
                             User.nickname,
                             Collection.name,
                             UserAccROLE.expiration)
            .filter(CollectionAccROLE.id_collection == Collection.id)
            .filter(UserAccROLE.id_user == User.id)
            .filter(CollectionAccROLE.id_accROLE == UserAccROLE.id_accROLE)
            .all())


def register_payment_history(id_user, premium_package, payment_method,
                             token=''):
    """
    Registers a transaction into the payment history table.

    @param id_user: the ID of the user
    @type id_user: int

    @param premium_package: the ID of the premium package
    @type premium_package: Premium

    @param payment_method: The name of the payment method.
    @type payment_method: str

    @param token: the transaction ID returned from payment gateway.
    @type token: str
    """
    register = HstPAYMENT()

    register.id_user = id_user
    register.id_package = premium_package.id
    register.price = premium_package.price
    register.currency = premium_package.currency
    register.transaction_time = functions.now()
    register.payment_method = payment_method
    register.token = token

    db.session.add(register)
    db.session.commit()


def get_premium_collection_number():
    """
    Returns the number of collections restricted by a premium package.

    @rtype: int
    """
    try:
        return (db.session
                .query(functions
                       .count(expression
                              .distinct(PremiumCollection.id_collection)))
                .one())[0]
    except:
        return 0


def get_user_premium_collection_number(id_user):
    """
    Returns the number of the collections that the user is able to display with
    the premium package s/he bought.

    @rtype: int
    """
    try:
        return (db.session
                .query(functions
                       .count(expression
                              .distinct(PremiumCollection.id_collection)))
                .filter(UserAccROLE.id_user == id_user)
                .filter(CollectionAccROLE.id_accROLE == UserAccROLE.id_accROLE)
                .filter(PremiumCollection.id_collection
                        == CollectionAccROLE.id_collection)
                .one())[0]
    except:
        return 0
#}
