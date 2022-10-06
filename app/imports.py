from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from passlib.hash import bcrypt
from tortoise import fields
from tortoise.models import Model
from tortoise.contrib.fastapi import register_tortoise
from tortoise.contrib.pydantic import pydantic_model_creator
import jwt
from typing import Generator, Iterable
from decimal import Decimal
import datetime
import datetime as dt
from typing import Generator
from itertools import zip_longest
import finnhub