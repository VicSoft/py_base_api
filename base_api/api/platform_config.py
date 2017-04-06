# -*- coding: utf-8 -*-
from ..application_methods import encryptSHA512
from models import *


def identity_types():
    return {
        'cpf': 'CPF',
        'rg': 'RG',
        'cnpj': 'CNPJ'
    }


def set_main_users():
    with db_session:
        contactType = ContactType.select(lambda ct: 'celular' in ct.type).first()
        user_tuple = (
            {
                'name': 'Victor',
                'cell_phone': '(XX) XXXXX-XXXX',
                'contact_type': contactType.type if contactType else 'celular',
                'email': 'victor.barbosa@e-makers.com.br',
                'gender': 'M',
                'identity': '000.000.000-00',
                'identity_type': (identity_types())['cpf'],
                'is_active': True,
                'level': 0,
                'password': '123mudar'
            },
            {
                'name': 'Desenvolvedor',
                'cell_phone': '',
                'contact_type': contactType.type if contactType else 'celular',
                'email': 'dev.oze-digital@e-makers.com.br',
                'gender': 'X',
                'identity': "000.000.000-00".decode('utf8'),
                'identity_type': (identity_types())['cpf'],
                'is_active': True,
                'level': 0,
                'password': '123mudar'
            }
        )

        for user_data in user_tuple:
            identity = Identity.select(lambda i: (i.value == user_data['identity']) and (i.type == user_data['identity_type'])).first()
            user = User.select(lambda u: (u.email == user_data['email']) and (u.identity == identity) and (u.level == user_data['level'])).first()

            if user is None:
                if identity is None:
                    identity = Identity(value=user_data['identity'], type=user_data['identity_type']).flush()

                user = User(
                    name=user_data['name'],
                    identity=identity,
                    email=user_data['email'],
                    gender=user_data['gender'],
                    level=user_data['level'],
                    isActive=user_data['is_active']
                ).flush()

                UserPassword(
                    user=user,
                    password=encryptSHA512(user_data['password']),
                    isCurrent=True
                ).flush()

                if len(user_data['cell_phone']) > 0:
                    contact = Contact.select(
                        lambda c: (c.contactType == contactType) and (c.value == user_data['cell_phone'])
                    ).first()

                    if contact is None:
                        if contactType is None:
                            contactType = ContactType(
                                type='Celular'
                            ).flush()

                        contact = Contact(
                            contactType=contactType,
                            value=user_data['cell_phone']
                        ).flush()

                        personContact = PersonContact.select(lambda pc: (pc.contact == contact) and (pc.user == user)).first()

                        if personContact is None:
                            PersonContact(
                                contact=contact,
                                user=user
                            ).flush()


def config():
    pass
    # set_main_users()
