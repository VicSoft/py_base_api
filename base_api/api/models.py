# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from pony.orm import *

db = Database()


db.bind("mysql", host="localhost", user="root", passwd="pass", db="db")

db.generate_mapping(create_tables=True)
