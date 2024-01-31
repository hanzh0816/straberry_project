from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Float,
)
from flask_cors import CORS


db = SQLAlchemy()
cors = CORS()